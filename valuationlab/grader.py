"""Track 1 grader: valuation accuracy of a recipe versus baselines.

Error for a firm-year is e = ln(estimate / actual). We report
  - median |e|                      (lower is better)
  - share with |estimate/actual - 1| <= 15%
  - coverage: estimates / eligible targets

Recipes are compared with a baseline on the firm-years both cover. For each
year we take the cross-sectional mean of |e_baseline| - |e_recipe|, then test
the time-series mean with a Newey-West t-statistic (Fama-MacBeth style).
Firms in the same year share shocks, so a pooled paired t-test would overstate
significance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .engine import apply_recipe
from .recipe import Recipe

WITHIN = 0.15
MIN_YEARS_FOR_T = 6  # a Newey-West t over fewer yearly means is not meaningful


@dataclass(frozen=True)
class Protocol:
    """Fixed period split. The holdout stays sealed unless explicitly unlocked."""
    explore: tuple[int, ...]
    validate: tuple[int, ...]
    holdout: tuple[int, ...]

    def years(self, period: str, allow_holdout: bool = False) -> list[int]:
        if period == "holdout" and not allow_holdout:
            raise PermissionError("holdout years are sealed; pass allow_holdout=True only for the final, frozen evaluation")
        return list(getattr(self, period))


def add_errors(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["error"] = np.log(est["estimate"] / est["actual"])
    est["abs_error"] = est["error"].abs()
    return est


def summarize(est: pd.DataFrame) -> dict:
    est = add_errors(est) if "abs_error" not in est else est
    covered = est["estimate"].notna()
    ratio = np.exp(est.loc[covered, "error"])
    return {
        "n_eligible": int(len(est)),
        "n_covered": int(covered.sum()),
        "coverage": float(covered.mean()) if len(est) else np.nan,
        "median_abs_error": float(est.loc[covered, "abs_error"].median()),
        "mean_abs_error": float(est.loc[covered, "abs_error"].mean()),
        "within_15pct": float((np.abs(ratio - 1) <= WITHIN).mean()),
        "median_peers": float(est.loc[covered, "n_peers"].median()),
        "fallback_share": float((est.loc[covered, "fallback_level"] > 0).mean()),
    }


def by_year(est: pd.DataFrame) -> pd.DataFrame:
    est = add_errors(est) if "abs_error" not in est else est
    g = est.groupby("fiscal_year")
    return pd.DataFrame({
        "median_abs_error": g["abs_error"].median(),
        "coverage": g["estimate"].apply(lambda s: s.notna().mean()),
    }).reset_index()


def newey_west_t(x: np.ndarray, lags: int) -> float:
    """t-statistic of the mean of x with Newey-West (Bartlett) standard errors."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    T = len(x)
    if T < 3:
        return np.nan
    u = x - x.mean()
    var = u @ u / T
    for L in range(1, min(lags, T - 1) + 1):
        w = 1 - L / (lags + 1)
        var += 2 * w * (u[L:] @ u[:-L]) / T
    se = np.sqrt(var / T)
    return float(x.mean() / se) if se > 0 else np.nan


def compare(est: pd.DataFrame, base: pd.DataFrame, lags: int = 2) -> dict:
    """Improvement of `est` over `base` on commonly covered firm-years (positive = est better)."""
    a = add_errors(est)[["id", "fiscal_year", "abs_error"]]
    b = add_errors(base)[["id", "fiscal_year", "abs_error"]]
    m = a.merge(b, on=["id", "fiscal_year"], suffixes=("", "_base")).dropna()
    m["gain"] = m["abs_error_base"] - m["abs_error"]
    yearly = m.groupby("fiscal_year")["gain"].mean()
    return {
        "n_common": int(len(m)),
        "n_years": int(len(yearly)),
        "mean_gain": float(yearly.mean()) if len(yearly) else np.nan,
        "t_stat": newey_west_t(yearly.to_numpy(), lags) if len(yearly) >= MIN_YEARS_FOR_T else np.nan,
        "share_years_better": float((yearly > 0).mean()) if len(yearly) else np.nan,
        "share_firms_better": float((m["gain"] > 0).mean()) if len(m) else np.nan,
    }


_CACHE: dict[tuple, pd.DataFrame] = {}


def estimate(panel: pd.DataFrame, method, years: list[int] | None = None) -> pd.DataFrame:
    """Estimates from a Recipe (comps engine) or any benchmark object with .apply(panel, years).

    Results are cached per (panel, method, years) because every recipe is compared with
    the same baselines. A Recipe is keyed by its full definition, not its name: two different
    recipes that share a name must never share estimates (a name-only key did that before
    2026-11-04 and mis-scored 16 archived recipes).
    """
    ident = (json.dumps(method.to_dict(), sort_keys=True, default=str) if isinstance(method, Recipe)
             else (method.name, getattr(method, "mode", ""), getattr(method, "k", "")))
    key = (id(panel), len(panel), method.multiple, ident, tuple(years or ()))
    if key not in _CACHE:
        _CACHE[key] = apply_recipe(panel, method, years) if isinstance(method, Recipe) else method.apply(panel, years)
    return _CACHE[key]


def grade(panel: pd.DataFrame, recipe, baselines: dict, protocol: Protocol,
          period: str = "explore", allow_holdout: bool = False) -> dict:
    """Apply a recipe (or benchmark) and its baselines on one period and return the full scorecard."""
    years = protocol.years(period, allow_holdout)
    est = estimate(panel, recipe, years)
    card = {"recipe": recipe.name, "multiple": recipe.multiple, "period": period, **summarize(est)}
    card["vs"] = {}
    for bname, brecipe in baselines.items():
        if brecipe.multiple != recipe.multiple:
            continue
        card["vs"][bname] = compare(est, estimate(panel, brecipe, years))
    return card
