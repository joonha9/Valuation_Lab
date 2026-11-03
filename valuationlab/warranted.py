"""Warranted-multiple benchmarks in the spirit of Bhojraj & Lee (2002, JAR).

Bhojraj and Lee regress a valuation multiple on firm characteristics each year and
call the fitted value the firm's "warranted multiple". It can be used two ways:

  1. Regression valuation: estimate = warranted multiple x the target's driver.
  2. Warranted peers: the k firms whose warranted multiples are closest to the
     target's; estimate = median of those peers' actual multiples x driver.

Choices made here (fixed before looking at results, applied identically to every year):
  - Dependent variable: log multiple (multiples are right-skewed; our error metric
    is in logs, so exp(fitted log) is the matching central estimate).
  - Regressors: log leave-one-out industry harmonic-mean multiple (SIC3, falling
    back to SIC2, then market), EBITDA margin, ROIC, 1-year sales growth, R&D
    intensity, debt to assets, log sales, and a loss indicator. Bhojraj and Lee
    use analyst long-term growth; we have no consensus data, so 1-year sales
    growth stands in.
  - Coefficients are estimated on the PRIOR fiscal year's cross-section and applied
    to the current year's characteristics, so a target's current market value never
    enters its own estimate. The first panel year therefore has no estimate.
  - Ratio regressors are bounded to economic ranges (BOUNDS) and missing
    characteristics are filled with that year's cross-sectional median (or 0 when a
    characteristic is missing for every firm that year).
  - The industry multiple uses peers' current market values (as any comps method
    does) but always excludes the target itself.

Outputs use the same columns as engine.apply_recipe, so the grader treats these
benchmarks exactly like recipes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .panel import MULTIPLES

REGRESSORS = [
    "log_ind_multiple", "ebitda_margin", "roic", "sales_growth_1y",
    "rnd_intensity", "debt_to_assets", "log_sales", "loss",
]
MIN_INDUSTRY_PEERS = 3

# Economic bounds for ratio regressors. Panel features are only winsorized at 1/99%,
# which still leaves margins of -5,000% for pre-revenue firms; in a linear regression
# those points dominate the fit (the first, unbounded specification gave EV/Sales a
# near-zero, negative margin coefficient). Bounds follow the usual trimming in the
# valuation literature and were set once, not tuned on results.
BOUNDS = {
    "ebitda_margin": (-1.0, 1.0),
    "roic": (-1.0, 1.0),
    "sales_growth_1y": (-0.5, 1.0),
    "rnd_intensity": (0.0, 1.0),
    "debt_to_assets": (0.0, 1.5),
}


def _eligible(panel: pd.DataFrame, multiple: str) -> pd.DataFrame:
    value_col, driver_col = MULTIPLES[multiple]
    d = panel[(panel[value_col] > 0) & (panel[driver_col] > 0)].copy()
    d["multiple"] = d[value_col] / d[driver_col]
    d = d[np.isfinite(d["multiple"])]
    d["actual"] = d[value_col]
    d["driver"] = d[driver_col]
    return d


def _loo_harmonic(d: pd.DataFrame, group: str | None) -> tuple[pd.Series, pd.Series]:
    """Leave-one-out harmonic mean of `multiple` within (fiscal_year, group) and the peer count."""
    keys = ["fiscal_year"] + ([group] if group else [])
    inv = 1.0 / d["multiple"]
    s = inv.groupby([d[k] for k in keys]).transform("sum") - inv
    n = inv.groupby([d[k] for k in keys]).transform("count") - 1
    hm = (n / s).where(n > 0)
    if group:
        hm = hm.where(d[group].notna())
        n = n.where(d[group].notna(), 0)
    return hm, n


def characteristics(panel: pd.DataFrame, multiple: str) -> pd.DataFrame:
    """Eligible firm-years with the regressors used for the warranted multiple."""
    d = _eligible(panel, multiple)
    ind = pd.Series(np.nan, index=d.index)
    for group in ("industry_l3", "industry_l2", None):
        hm, n = _loo_harmonic(d, group)
        ind = ind.fillna(hm.where(n >= MIN_INDUSTRY_PEERS))
    d["log_ind_multiple"] = np.log(ind)
    d["loss"] = (d["net_income"] < 0).astype(float)
    for c, (lo, hi) in BOUNDS.items():
        d[c] = d[c].clip(lo, hi)
    for c in REGRESSORS:
        d[c] = d[c].fillna(d.groupby("fiscal_year")[c].transform("median"))
    # A regressor missing for every firm in a year (1-year growth in the first panel
    # year) becomes a constant 0 column: it gets no weight in that year's regression.
    d[REGRESSORS] = d[REGRESSORS].fillna(0.0)
    return d


def fit_year(d: pd.DataFrame) -> np.ndarray | None:
    """OLS of log multiple on the regressors for one cross-section (with intercept)."""
    d = d.dropna(subset=REGRESSORS)
    if len(d) < 3 * (len(REGRESSORS) + 1):
        return None
    X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in REGRESSORS])
    y = np.log(d["multiple"].to_numpy(float))
    lo, hi = np.quantile(y, [0.01, 0.99])
    beta, *_ = np.linalg.lstsq(X, np.clip(y, lo, hi), rcond=None)
    return beta


def warranted(panel: pd.DataFrame, multiple: str) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    """Characteristics plus `warranted` (fitted log multiple from prior-year coefficients)."""
    d = characteristics(panel, multiple)
    d["warranted"] = np.nan
    betas: dict[int, np.ndarray] = {}
    years = sorted(d["fiscal_year"].unique())
    for prev, cur in zip(years[:-1], years[1:]):
        if cur != prev + 1:
            continue
        beta = fit_year(d[d["fiscal_year"] == prev])
        if beta is None:
            continue
        betas[int(prev)] = beta
        rows = (d["fiscal_year"] == cur) & d[REGRESSORS].notna().all(axis=1)
        X = np.column_stack([np.ones(rows.sum())] + [d.loc[rows, c].to_numpy(float) for c in REGRESSORS])
        d.loc[rows, "warranted"] = X @ beta
    return d, betas


@dataclass(frozen=True)
class WarrantedBenchmark:
    """A benchmark the grader can apply like a recipe (see grader.estimate)."""
    name: str
    multiple: str
    mode: str = "regression"   # "regression" or "peers"
    k: int = 8

    def to_dict(self) -> dict:
        return {"name": self.name, "multiple": self.multiple, "method": "Bhojraj-Lee warranted multiple",
                "mode": self.mode, "k": self.k if self.mode == "peers" else None,
                "regressors": REGRESSORS, "coefficients": "estimated on the prior fiscal year"}

    def apply(self, panel: pd.DataFrame, years: list[int] | None = None, keep_peers: bool = False) -> pd.DataFrame:
        d, _ = warranted(panel, self.multiple)
        if years is not None:
            d = d[d["fiscal_year"].isin(years)]
        out = []
        for fy, year in d.groupby("fiscal_year", sort=True):
            year = year.sort_values("id").reset_index(drop=True)
            w = year["warranted"].to_numpy(float)
            mult = year["multiple"].to_numpy(float)
            ids = year["id"].to_numpy()
            ok = ~np.isnan(w)
            for i in range(len(year)):
                row = {"id": ids[i], "fiscal_year": fy, "actual": year.at[i, "actual"]}
                peers = None
                if ok[i]:
                    if self.mode == "regression":
                        pm, n = float(np.exp(w[i])), 0
                    else:
                        cand = np.flatnonzero(ok)
                        cand = cand[cand != i]
                        cand = cand[np.argsort(np.abs(w[cand] - w[i]), kind="stable")[: self.k]]
                        pm, n, peers = float(np.median(mult[cand])), len(cand), cand
                    row.update(estimate=pm * year.at[i, "driver"], peer_multiple=pm, n_peers=n, fallback_level=0)
                else:
                    row.update(estimate=np.nan, peer_multiple=np.nan, n_peers=0, fallback_level=-1)
                if keep_peers:
                    row["peers"] = [] if peers is None else ids[peers].tolist()
                out.append(row)
        return pd.DataFrame(out)
