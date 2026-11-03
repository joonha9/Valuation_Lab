"""Sanity-check FactSet yearly exports before they enter the panel.

    python3 scripts/check_exports.py                         # checks data/raw/factset_*.xlsx
    python3 scripts/check_exports.py data/raw data/holdout   # also the sealed holdout files

Files in data/holdout/ (FY2024-2025) are never read by run_comps.py; this script only
checks that their FactSet settings are right.

For each file factset_YYYY.xlsx (market data as of June YYYY, statements for FY YYYY-1):
  - fiscal year-ends should mostly fall in YYYY-1 (or early YYYY for Jan-Mar year-ends)
  - market values must differ from every other file (catches a market-value date
    left on another year)
  - a few large companies are printed for a quick eyeball check
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NA = ["#N/A", "@NA", "NA", "-", ""]
WATCH = ["AAPL", "MSFT", "NVDA", "KO"]


def load(path: Path) -> pd.DataFrame:
    probe = pd.read_excel(path, header=None, nrows=30)
    header = next(i for i, v in enumerate(probe.iloc[:, 0].astype(str)) if v.strip() == "Symbol")
    return pd.read_excel(path, header=header, na_values=NA).dropna(how="all")


def main() -> int:
    folders = [Path(a) if Path(a).is_absolute() else ROOT / a for a in sys.argv[1:]] or [ROOT / "data/raw"]
    files = sorted((f for d in folders for f in d.glob("factset_*.xlsx")), key=lambda f: f.name)
    files = [f for f in files if not f.name.startswith("~$")]
    if not files:
        print("no factset_YYYY.xlsx files found in", ", ".join(str(d) for d in folders))
        return 1

    frames, problems = {}, []
    for f in files:
        year = int(re.search(r"(\d{4})", f.stem).group(1))
        df = load(f)
        frames[year] = df
        fye = pd.to_datetime(df["Fiscal Period End Date"], format="%m/%d/%Y", errors="coerce")
        share_ok = fye.dt.year.isin([year - 1, year]).mean() / max(fye.notna().mean(), 1e-9)
        main_year = int(fye.dt.year.mode().iloc[0]) if fye.notna().any() else None
        print(f"\n{f.name}: FY{year - 1} statements, market data June {year}")
        print(f"  rows {len(df):,}  with sales {df['Net Sales'].notna().sum():,}  with market value {df['MktVal Co'].notna().sum():,}")
        print(f"  most common fiscal year-end: {main_year}  (share in {year - 1}-{year}: {share_ok:.0%})")
        if main_year != year - 1:
            problems.append(f"{f.name}: fiscal year-ends center on {main_year}, expected {year - 1} (check the Year setting)")
        for s in WATCH:
            r = df[df["Symbol"] == s]
            if len(r):
                r = r.iloc[0]
                print(f"  {s:5s} FYE {r['Fiscal Period End Date']}  sales {r['Net Sales']:>10,.0f}  market value {r['MktVal Co']:>12,.0f}")

    # Any value column identical across two files -> that column's Year (or date) was left
    # on a fixed period, usually the latest fiscal year. That is look-ahead, so every
    # time-varying column is checked, not just market value.
    years = sorted(frames)
    static = {"Symbol", "Name", "Entity ID", "Sec Type", "SIC Code", "Exchange Country Name", "Fiscal Period End Date"}
    value_cols = [c for c in frames[years[0]].columns if c not in static]
    stuck: dict[str, list[str]] = {}
    for i, a in enumerate(years):
        for b in years[i + 1:]:
            for c in value_cols:
                if c not in frames[b].columns:
                    continue
                m = frames[a][["Entity ID", c]].merge(frames[b][["Entity ID", c]], on="Entity ID").dropna()
                m = m[(m[c + "_x"] != 0)]
                if len(m) >= 50 and (m[c + "_x"] == m[c + "_y"]).mean() > 0.5:
                    stuck.setdefault(c, []).append(f"{a}/{b}")
    for c, pairs in stuck.items():
        problems.append(f"'{c}' is identical across {len(pairs)} file pair(s) (e.g. {', '.join(pairs[:3])}): "
                        f"its Year/date setting was not changed per file")

    print("\n" + ("\n".join("PROBLEM: " + p for p in problems) if problems else f"All {len(files)} files look consistent."))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
