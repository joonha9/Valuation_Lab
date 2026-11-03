"""Grade comps recipes against baselines and write JSON + HTML results.

Synthetic data (pipeline test):
    python3 scripts/run_comps.py --synthetic

FactSet export(s):
    python3 scripts/run_comps.py --data data/raw/factset_*.xlsx --column-map config/factset_columns.json

The holdout years are never touched by this script.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from valuationlab.baselines import baselines_for  # noqa: E402
from valuationlab.factset import read_exports  # noqa: E402
from valuationlab.grader import Protocol, by_year, estimate, grade  # noqa: E402
from valuationlab.panel import build_panel  # noqa: E402
from valuationlab.recipe import validate  # noqa: E402
from valuationlab.report import write as write_html  # noqa: E402
from valuationlab.synthetic import generate  # noqa: E402


BASELINE_SHORT = {"market_median": "Market median", "industry_median": "Industry median",
                  "bl_regression": "B&L regression", "bl_peers": "B&L peers"}


def years_arg(text: str) -> tuple[int, ...]:
    a, b = (int(x) for x in text.split("-"))
    return tuple(range(a, b + 1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--synthetic", action="store_true", help="use generated data")
    src.add_argument("--data", nargs="+", help="FactSet Excel/CSV export(s)")
    ap.add_argument("--column-map", default=str(ROOT / "config/factset_columns.json"),
                    help="JSON mapping FactSet headers to internal names")
    ap.add_argument("--value-date", help="valuation date for files not named factset_YYYY.xlsx (YYYY-MM-DD)")
    ap.add_argument("--recipes", default=str(ROOT / "recipes/examples.json"))
    ap.add_argument("--explore", type=years_arg, default=years_arg("2008-2016"))
    ap.add_argument("--validate", type=years_arg, default=years_arg("2017-2020"))
    ap.add_argument("--holdout", type=years_arg, default=years_arg("2021-2024"))
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    if args.synthetic:
        raw, dataset = generate(n_firms=3000), "synthetic (3,000 firms)"
    else:
        vdate = pd.Timestamp(args.value_date) if args.value_date else None
        raw, logs = read_exports(args.data, args.column_map, vdate)
        for log in logs:
            print("loaded", log)
        dataset = f"FactSet ({len(logs)} snapshot{'s' if len(logs) > 1 else ''})"
    panel = build_panel(raw)
    protocol = Protocol(args.explore, args.validate, args.holdout)
    shown_years = list(args.explore) + list(args.validate)

    specs = json.loads(Path(args.recipes).read_text())
    cols = set(panel.columns)
    multiples: dict[str, list] = {}
    for spec in specs:
        recipe = validate(spec, cols)
        multiples.setdefault(recipe.multiple, []).append((spec, recipe))

    out_multiples = []
    for multiple, entries in multiples.items():
        base = baselines_for(multiple)
        rows = []
        for rid, recipe, spec, kind in (
            [(bid, b, None, "baseline") for bid, b in base.items()]
            + [(f"recipe_{i}", r, s, "recipe") for i, (s, r) in enumerate(entries)]
        ):
            explore = grade(panel, recipe, base, protocol, "explore")
            valid = grade(panel, recipe, base, protocol, "validate")
            yearly = by_year(estimate(panel, recipe, shown_years))
            rows.append({
                "id": rid, "kind": kind, "name": recipe.name,
                "short": (spec or {}).get("short", BASELINE_SHORT.get(rid, rid)),
                "mechanism": (spec or {}).get("mechanism"), "spec": recipe.to_dict(),
                "explore": explore, "validate": valid,
                "yearly": [[int(y), round(float(v), 4)] for y, v in zip(yearly["fiscal_year"], yearly["median_abs_error"])],
            })
            print(f"{multiple:10s} {recipe.name:38s} explore {explore['median_abs_error']:.3f}  validate {valid['median_abs_error']:.3f}")
        out_multiples.append({"multiple": multiple, "rows": rows})

    # One-sentence headline from the validation period.
    first = out_multiples[0]
    ind = next(r for r in first["rows"] if r["id"] == "industry_median")
    best = min((r for r in first["rows"] if r["kind"] == "recipe"), key=lambda r: r["validate"]["median_abs_error"])
    headline = (f"For {first['multiple']}, the best recipe ({best['name']}) has a median error of "
                f"{best['validate']['median_abs_error']:.3f} in the validation years, against "
                f"{ind['validate']['median_abs_error']:.3f} for the industry median.")

    # Data caveats: years in which a ranking feature is missing for every firm, so the
    # recipe silently ranks on its remaining features (e.g. 3-year growth needs 3 prior years).
    notes = []
    rank_vars = sorted({v for entries in multiples.values() for _, r in entries for v in r.rank})
    for v in rank_vars:
        empty = [y for y in shown_years if panel.loc[panel["fiscal_year"] == y, v].isna().all()]
        if empty:
            notes.append(f"{v} is unavailable in FY {empty[0]}–{empty[-1]} (not enough prior years); "
                         f"recipes that rank on it use their other features in those years.")

    results = {
        "headline": headline, "dataset": dataset, "synthetic": bool(args.synthetic), "notes": notes,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_rows": int(len(panel)),
        "protocol": {"explore": list(args.explore), "validate": list(args.validate), "holdout": list(args.holdout)},
        "multiples": out_multiples,
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "comps_results.json").write_text(json.dumps(results, indent=2, default=float))
    html_path = write_html(results, out / "comps_report.html")
    print(f"\nWrote {out / 'comps_results.json'} and {html_path}")


if __name__ == "__main__":
    main()
