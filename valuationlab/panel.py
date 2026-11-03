"""Build the firm-year panel used by the comps engine.

Raw rows (FactSet export or synthetic data) are renamed to internal names,
cleaned, and extended with derived characteristics. Market-based columns are
kept separately because recipes may never use a target firm's own market value
as an input.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

# Columns the engine cannot work without.
REQUIRED = [
    "id", "fiscal_year", "industry_l2", "industry_l3",
    "sales", "ebitda", "ebit", "net_income", "book_equity",
    "total_debt", "cash", "mkt_cap",
]

# Market-based columns: allowed as valuation targets, never as recipe features.
MARKET_COLUMNS = {"price", "shares", "mkt_cap", "ev", "value_date"}

# Multiples the engine supports: name -> (value column, driver column).
MULTIPLES = {
    "EV/Sales": ("ev", "sales"),
    "EV/EBITDA": ("ev", "ebitda"),
    "EV/EBIT": ("ev", "ebit"),
    "P/E": ("mkt_cap", "net_income"),
    "P/B": ("mkt_cap", "book_equity"),
    "EV/EBITDA_FY1": ("ev", "ebitda_fy1"),
    "P/E_FY1": ("mkt_cap", "net_income_fy1"),
}

# Derived accounting characteristics that recipes may filter or rank on.
FEATURES = [
    "log_sales", "log_assets",
    "sales_growth_1y", "sales_growth_3y",
    "gross_margin", "ebitda_margin", "ebit_margin", "net_margin",
    "roic", "roe", "asset_turnover",
    "net_debt_to_ebitda", "debt_to_assets",
    "rnd_intensity", "capex_intensity",
]

TAX_RATE = 0.25  # flat rate for NOPAT in ROIC; a fixed protocol choice


def load_raw(paths: list[str | Path], column_map: dict[str, str] | None = None) -> pd.DataFrame:
    """Read one or more Excel/CSV files, stack them, and rename columns."""
    frames = []
    for p in map(Path, paths):
        if p.suffix.lower() in {".xlsx", ".xls"}:
            frames.append(pd.read_excel(p))
        else:
            frames.append(pd.read_csv(p))
    raw = pd.concat(frames, ignore_index=True)
    if column_map:
        raw = raw.rename(columns=column_map)
    return raw


def load_column_map(path: str | Path) -> dict[str, str]:
    """Load a {source header: internal name} mapping, ignoring comment keys."""
    mapping = json.loads(Path(path).read_text())
    return {k: v for k, v in mapping.items() if not k.startswith("_") and v}


def _add_sic_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Derive sic2/sic3/sic4 from a SIC code; fill industry levels from SIC when no other scheme is given."""
    if "sic" not in df.columns:
        return df
    code = pd.to_numeric(df["sic"], errors="coerce")
    code = code.where(code > 0)
    sic4 = code.map(lambda c: f"{int(c):04d}" if pd.notna(c) else np.nan)
    df["sic4"], df["sic3"], df["sic2"] = sic4, sic4.str[:3], sic4.str[:2]
    for level, src in (("industry_l2", "sic2"), ("industry_l3", "sic3"), ("industry_l4", "sic4")):
        if level not in df.columns:
            df[level] = df[src]
    return df


def build_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean raw rows and add EV, multiples inputs, and derived features.

    Industry levels come from RBICS (or any scheme) when supplied as
    industry_l1..l4; with only a SIC code, levels 2-4 are its 2-, 3- and 4-digit prefixes.
    """
    df = _add_sic_levels(raw.copy())
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")

    df["fiscal_year"] = df["fiscal_year"].astype(int)
    df = df.drop_duplicates(subset=["id", "fiscal_year"], keep="last")
    df = df.sort_values(["id", "fiscal_year"]).reset_index(drop=True)

    for col in ("minority_interest", "preferred", "rnd", "capex", "gross_profit", "total_assets"):
        if col not in df.columns:
            df[col] = np.nan

    # Enterprise value is always built from market cap at the valuation date plus the
    # latest balance sheet. Vendor EV fields can be dated at fiscal year-end instead
    # (FactSet's "Entrpr Value Diluted" is), which would mix two dates in one multiple.
    if "ev" in df.columns:
        df = df.rename(columns={"ev": "ev_vendor"})
    df["ev"] = (
        df["mkt_cap"] + df["total_debt"].fillna(0) + df["minority_interest"].fillna(0)
        + df["preferred"].fillna(0) - df["cash"].fillna(0)
    )

    # Forward net income from consensus EPS, when available.
    if "eps_fy1" in df.columns and "shares" in df.columns:
        df["net_income_fy1"] = df["eps_fy1"] * df["shares"]

    df = _add_features(df)
    return df


def _lag(df: pd.DataFrame, col: str, years: int) -> pd.Series:
    """Gap-aware lag: the value from exactly `years` fiscal years earlier, else NaN."""
    prior = df[["id", "fiscal_year", col]].copy()
    prior["fiscal_year"] = prior["fiscal_year"] + years
    merged = df[["id", "fiscal_year"]].merge(prior, on=["id", "fiscal_year"], how="left")
    return merged[col].to_numpy()


def _safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    out = a / b
    return out.where(np.isfinite(out) & (b != 0))


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    pos = lambda s: s.where(s > 0)  # noqa: E731 - small helper

    df["log_sales"] = np.log(pos(df["sales"]))
    df["log_assets"] = np.log(pos(df["total_assets"]))

    sales_l1 = _lag(df, "sales", 1)
    sales_l3 = _lag(df, "sales", 3)
    df["sales_growth_1y"] = _safe_div(df["sales"], pd.Series(sales_l1).where(sales_l1 > 0)) - 1
    df["sales_growth_3y"] = (_safe_div(df["sales"], pd.Series(sales_l3).where(sales_l3 > 0))) ** (1 / 3) - 1

    sales = pos(df["sales"])
    df["gross_margin"] = _safe_div(df["gross_profit"], sales)
    df["ebitda_margin"] = _safe_div(df["ebitda"], sales)
    df["ebit_margin"] = _safe_div(df["ebit"], sales)
    df["net_margin"] = _safe_div(df["net_income"], sales)

    invested = pos(df["book_equity"] + df["total_debt"].fillna(0) - df["cash"].fillna(0))
    df["roic"] = _safe_div(df["ebit"] * (1 - TAX_RATE), invested)
    df["roe"] = _safe_div(df["net_income"], pos(df["book_equity"]))
    df["asset_turnover"] = _safe_div(df["sales"], pos(df["total_assets"]))

    net_debt = df["total_debt"].fillna(0) - df["cash"].fillna(0)
    df["net_debt_to_ebitda"] = _safe_div(net_debt, pos(df["ebitda"]))
    df["debt_to_assets"] = _safe_div(df["total_debt"], pos(df["total_assets"]))
    df["rnd_intensity"] = _safe_div(df["rnd"].fillna(0), sales)
    df["capex_intensity"] = _safe_div(df["capex"].abs(), sales)

    # Winsorize ratio features within each fiscal year at 1% / 99% (paper's convention).
    for col in FEATURES:
        if col.startswith("log_"):
            continue
        q = df.groupby("fiscal_year")[col].transform
        df[col] = df[col].clip(q(lambda s: s.quantile(0.01)), q(lambda s: s.quantile(0.99)))
    return df


def split_years(df: pd.DataFrame, years: list[int] | range) -> pd.DataFrame:
    return df[df["fiscal_year"].isin(list(years))]
