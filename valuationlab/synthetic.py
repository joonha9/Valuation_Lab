"""Synthetic firm-year data for testing the pipeline before real data arrives.

The data-generating process is known, so we can check that the engine and
grader recover it: multiples depend on industry, year, growth and ROIC, so
peers matched on those should beat the market-wide median.

Results on synthetic data say nothing about real markets.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SECTORS = ["Industrials", "Consumer", "Technology", "Healthcare", "Energy", "Materials"]


def generate(n_firms: int = 1200, years: range = range(2005, 2025), seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_years = len(years)

    sector_idx = rng.integers(0, len(SECTORS), n_firms)
    sub_idx = rng.integers(0, 3, n_firms)
    sector_effect = rng.normal(0, 0.25, len(SECTORS))
    sub_effect = rng.normal(0, 0.15, (len(SECTORS), 3))
    year_effect = np.cumsum(rng.normal(0, 0.08, n_years))

    rows = []
    for f in range(n_firms):
        s, j = sector_idx[f], sub_idx[f]
        start = rng.integers(0, n_years // 2)            # staggered entry
        life = rng.integers(6, n_years + 1)              # some firms exit (delist)
        sales = np.exp(rng.normal(6.0, 1.3))             # USD millions
        g_mean = rng.normal(0.06 + 0.03 * (SECTORS[s] == "Technology"), 0.04)
        margin_mean = np.clip(rng.normal(0.16, 0.07), 0.02, 0.45)
        cap_intensity = np.exp(rng.normal(-0.2, 0.4))    # invested capital / sales
        g = g_mean
        for t in range(start, min(start + life, n_years)):
            g = 0.6 * g + 0.4 * g_mean + rng.normal(0, 0.06)
            sales *= 1 + g
            margin = np.clip(margin_mean + rng.normal(0, 0.03), -0.10, 0.55)
            ebitda = sales * margin
            ebit = ebitda - 0.04 * sales
            invested = sales * cap_intensity
            debt = invested * np.clip(rng.normal(0.35, 0.15), 0, 0.9)
            cash = sales * np.clip(rng.normal(0.10, 0.05), 0.0, 0.5)
            equity = invested - debt + cash
            net_income = (ebit - 0.05 * debt) * 0.75
            rows.append(dict(
                id=f"F{f:05d}", ticker=f"T{f:05d}", name=f"Synthetic Co {f}",
                fiscal_year=years[t], industry_l1=SECTORS[s], industry_l2=SECTORS[s],
                industry_l3=f"{SECTORS[s]}-{j + 1}",
                sales=sales, gross_profit=sales * (margin + 0.20), ebitda=ebitda, ebit=ebit,
                net_income=net_income, total_assets=invested + cash, book_equity=equity,
                total_debt=debt, cash=cash, minority_interest=0.0,
                rnd=sales * 0.08 * (SECTORS[s] in ("Technology", "Healthcare")),
                capex=sales * 0.05 * cap_intensity,
                _g=g, _s=s, _j=j, _t=t,
            ))

    df = pd.DataFrame(rows)
    # Simple ROIC proxy known to the DGP (the panel recomputes its own).
    roic_true = (df["ebit"] * 0.75) / (df["book_equity"] + df["total_debt"] - df["cash"]).clip(lower=1e-6)
    log_ev_ebitda = (
        np.log(9.0) + sector_effect[df["_s"]] + sub_effect[df["_s"], df["_j"]]
        + year_effect[df["_t"]] + 3.0 * df["_g"] + 1.0 * roic_true.clip(-0.3, 0.6)
        + rng.normal(0, 0.22, len(df))
    )
    ev = np.where(df["ebitda"] > 0, np.exp(log_ev_ebitda) * df["ebitda"], 0.8 * df["sales"])
    df["mkt_cap"] = np.maximum(ev - df["total_debt"] + df["cash"], 0.05 * ev)
    df["ev"] = df["mkt_cap"] + df["total_debt"] - df["cash"]
    return df.drop(columns=["_g", "_s", "_j", "_t"])
