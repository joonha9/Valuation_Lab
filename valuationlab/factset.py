"""Read FactSet Universal Screening exports into raw rows for panel.build_panel.

Each export is one cross-section: every company's latest fiscal year as of the
screen date, with market data as of that date. Several exports (one per June 30)
stack into a panel. The cross-section is labelled by `fiscal_year` = year of the
valuation date minus one, matching the June convention (FY y valued at June 30, y+1).

Filters applied here, each counted in the returned log:
  - ordinary shares only (drops ADRs, units, preferred)
  - financial firms dropped (SIC 6000-6999), as in the paper
  - market capitalization at the valuation date of at least MIN_MKT_CAP
    (USD millions); drops microcaps and most OTC shells, in the spirit of the
    paper's NYSE-10th-percentile screen
  - fiscal year-end no more than 18 months before the valuation date (drops
    stale statements of companies that stopped reporting)
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .panel import load_column_map

NA_VALUES = ["#N/A", "@NA", "NA", "-", ""]
MAX_STATEMENT_AGE_DAYS = 548  # about 18 months
MIN_MKT_CAP = 100.0           # USD millions; fixed protocol choice


def _find_header_row(path: Path) -> int:
    """FactSet puts a title block above the table; the header is the row starting with 'Symbol'."""
    probe = pd.read_excel(path, header=None, nrows=30)
    for i, first in enumerate(probe.iloc[:, 0].astype(str)):
        if first.strip() == "Symbol":
            return i
    raise ValueError(f"{path.name}: no header row starting with 'Symbol' in the first 30 rows")


def value_date_from_name(path: Path) -> pd.Timestamp | None:
    """factset_2024.xlsx -> 2024-06-30; factset_2024-06-30.xlsx -> that date."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", path.stem)
    if m:
        return pd.Timestamp(m.group(0))
    m = re.search(r"(?<!\d)(19|20)\d{2}(?!\d)", path.stem)
    return pd.Timestamp(f"{m.group(0)}-06-30") if m else None


def read_export(path: str | Path, column_map: dict[str, str], value_date: pd.Timestamp | None = None
                ) -> tuple[pd.DataFrame, dict]:
    path = Path(path)
    value_date = value_date or value_date_from_name(path)
    if value_date is None:
        raise ValueError(f"{path.name}: cannot infer the valuation date; name the file factset_YYYY.xlsx or pass value_date")

    df = pd.read_excel(path, header=_find_header_row(path), na_values=NA_VALUES)
    df = df.dropna(how="all").rename(columns=column_map)
    log = {"file": path.name, "value_date": str(value_date.date()), "rows": len(df)}

    df["value_date"] = value_date
    df["fye_date"] = pd.to_datetime(df["fye_date"], format="%m/%d/%Y", errors="coerce")
    df["fiscal_year"] = value_date.year - 1 if value_date.month <= 6 else value_date.year

    steps = [
        ("ordinary_shares", df["sec_type"].eq("SHARE")),
        ("non_financial", ~pd.to_numeric(df["sic"], errors="coerce").between(6000, 6999)),
        ("min_mkt_cap", df["mkt_cap"].ge(MIN_MKT_CAP)),
        ("fresh_statements", df["fye_date"].le(value_date)
            & df["fye_date"].ge(value_date - pd.Timedelta(days=MAX_STATEMENT_AGE_DAYS))),
    ]
    for name, keep in steps:
        df = df[keep.reindex(df.index, fill_value=False)]
        log[name] = len(df)
    return df.reset_index(drop=True), log


def read_exports(paths: list[str | Path], column_map_path: str | Path,
                 value_date: pd.Timestamp | None = None) -> tuple[pd.DataFrame, list[dict]]:
    cmap = load_column_map(column_map_path)
    frames, logs = [], []
    for p in paths:
        df, log = read_export(p, cmap, value_date)
        frames.append(df)
        logs.append(log)
    return pd.concat(frames, ignore_index=True), logs
