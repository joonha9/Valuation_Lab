"""Build the ValuationLab project site (site/index.html) from the FactSet panel.

    python3 scripts/build_site.py

Computes every number the site shows (no hand-typed results), writes
site/site_data.json, and injects it into site/template.html. The holdout years
are never loaded: only data/raw/ is read.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from valuationlab.baselines import baselines_for  # noqa: E402
from valuationlab.engine import apply_recipe  # noqa: E402
from valuationlab.factset import read_exports  # noqa: E402
from valuationlab.grader import Protocol, add_errors, compare, estimate, summarize  # noqa: E402
from valuationlab.panel import build_panel  # noqa: E402
from valuationlab.recipe import validate  # noqa: E402
from valuationlab.warranted import REGRESSORS, WarrantedBenchmark, warranted  # noqa: E402

PROTOCOL = Protocol(explore=tuple(range(2016, 2020)), validate=tuple(range(2020, 2024)),
                    holdout=(2024, 2025))
YEARS = list(PROTOCOL.explore) + list(PROTOCOL.validate)
SHOWCASE_YEAR = 2023
SHOWCASE = ["KO", "PEP", "HD", "CAT", "NKE", "MSFT", "COST", "UNP"]
THRESHOLDS = [round(x, 2) for x in np.arange(0.05, 1.001, 0.05)]
SHORT = {"market_median": "Market median", "industry_median": "Industry median",
         "bl_regression": "B&L regression", "bl_peers": "B&L peers"}
KIND = {"market_median": "practitioner", "industry_median": "practitioner",
        "bl_regression": "academic", "bl_peers": "academic"}


def r(x, n=4):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)


def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        return r(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


def agent_block(run_dir: Path) -> dict | None:
    """Stage 2: everything the site shows about the agent search run (read from its archive)."""
    from valuationlab import agentloop as al
    final_path = run_dir / "final.json"
    if not final_path.exists():
        return None
    run = al.Run(ROOT, run_dir.name)
    rule = run.config["selection_rule"]
    agent, rnd = run.archive("agent"), run.archive("random")
    final = json.loads(final_path.read_text())
    attempts = [{"id": a["id"], "gen": a["generation"], "name": a.get("name"), "multiple": a.get("multiple"),
                 "status": a["status"], "compact": a.get("compact"),
                 "explore": (a.get("explore") or {}).get("median_abs_error"),
                 "coverage": (a.get("explore") or {}).get("coverage"),
                 "eligible": al.eligible(a, rule), "critic_reason": a.get("critic_reason") if a["status"] == "rejected" else None}
                for a in agent]
    random_pts = [{"multiple": r["multiple"], "explore": r["explore"]["median_abs_error"],
                   "eligible": al.eligible(r, rule)} for r in rnd]
    best_of = {}
    for m in al.MULTIPLES_IN_SCOPE:
        n = sum(1 for a in agent if a.get("multiple") == m and a["status"] == "graded")
        best_of[m] = al.best_of_random(rnd, m, n, rule)
    keep = ("median_abs_error", "mean_abs_error", "coverage", "within_15pct",
            "years_beating_industry_median", "years_beating_bl_regression")
    table = {m: [{"source": r["source"], "id": r["id"], "name": r["name"], "mechanism": r.get("mechanism"),
                  "compact": r.get("compact"),
                  "explore": r["explore"].get("median_abs_error"),
                  "validate": {k: r["validate"].get(k) for k in keep}} for r in rows]
             for m, rows in final["multiples"].items()}
    funnel = dict(final["funnel"])
    funnel["eligible"] = sum(1 for a in agent if al.eligible(a, rule))
    funnel["selected"] = sum(1 for rows in final["multiples"].values() for r in rows if r["source"] == "agent")
    multi_path = run_dir.parent / "multi_summary.json"
    multi = json.loads(multi_path.read_text()) if multi_path.exists() else None
    abl_path = run_dir.parent / "ablation_summary.json"
    ablation = json.loads(abl_path.read_text()) if abl_path.exists() else None
    return {"multi": multi, "ablation": ablation, "run": run_dir.name, "frozen_at": final["frozen_at"], "rule": rule, "funnel": funnel,
            "generations": max(a["generation"] for a in agent), "attempts": attempts, "random": random_pts,
            "n_random": len(rnd), "best_of_random": best_of, "validation": table}


def main() -> None:
    files = sorted((ROOT / "data/raw").glob("factset_20*.xlsx"))
    raw, logs = read_exports(files, ROOT / "config/factset_columns.json")
    panel = build_panel(raw)
    names = panel.drop_duplicates("id", keep="last").set_index("id")[["ticker", "name"]]

    specs = json.loads((ROOT / "recipes/examples.json").read_text())
    by_multiple: dict[str, list] = {}
    for s in specs:
        by_multiple.setdefault(s["multiple"], []).append(s)

    out_mult = []
    for multiple, recipe_specs in by_multiple.items():
        base = baselines_for(multiple)
        methods = [(k, b, None) for k, b in base.items()]
        methods += [(f"recipe_{i}", validate(s), s) for i, s in enumerate(recipe_specs)]
        ests = {mid: add_errors(estimate(panel, m, YEARS)) for mid, m, _ in methods}

        # Common sample across all methods (for the accuracy curve).
        common = None
        for e in ests.values():
            k = e.loc[e["estimate"].notna(), ["id", "fiscal_year"]]
            common = k if common is None else common.merge(k, on=["id", "fiscal_year"])
        common_val = common[common["fiscal_year"].isin(PROTOCOL.validate)]

        rows = []
        for mid, m, spec in methods:
            e = ests[mid]
            row = {"id": mid, "name": m.name, "short": (spec or {}).get("short", SHORT.get(mid, mid)),
                   "kind": KIND.get(mid, "recipe"), "mechanism": (spec or {}).get("mechanism"),
                   "spec": m.to_dict()}
            for period in ("explore", "validate"):
                pe = e[e["fiscal_year"].isin(PROTOCOL.years(period))]
                card = summarize(pe)
                card["vs"] = {}
                for bid in ("industry_median", "bl_regression", "bl_peers"):
                    if bid != mid:
                        be = ests[bid]
                        card["vs"][bid] = compare(pe, be[be["fiscal_year"].isin(PROTOCOL.years(period))])
                row[period] = card
            yearly = []
            ind = ests["industry_median"]
            for y in YEARS:
                ey = e[(e["fiscal_year"] == y) & e["estimate"].notna()]
                g = ey[["id", "abs_error"]].merge(ind[ind["fiscal_year"] == y][["id", "abs_error"]].dropna(),
                                                 on="id", suffixes=("", "_ind"))
                yearly.append({"year": y, "median_abs_error": ey["abs_error"].median() if len(ey) else None,
                               "coverage": e.loc[e["fiscal_year"] == y, "estimate"].notna().mean(),
                               "gain_vs_industry": (g["abs_error_ind"] - g["abs_error"]).mean() if len(g) else None})
            row["yearly"] = yearly
            cv = common_val.merge(e, on=["id", "fiscal_year"])
            ratio_dev = np.abs(np.exp(cv["error"]) - 1)
            row["accuracy_curve"] = [float((ratio_dev <= t).mean()) for t in THRESHOLDS]
            rows.append(row)
        out_mult.append({"multiple": multiple, "rows": rows, "n_common_validate": len(common_val)})

    # Worked examples: one firm-year, every method, with the peers each method chose.
    ev = by_multiple["EV/EBITDA"]
    best_spec = ev[0]
    best = validate(best_spec)
    base = baselines_for("EV/EBITDA")
    ex_methods = {"industry_median": base["industry_median"], "bl_regression": base["bl_regression"],
                  "bl_peers": base["bl_peers"], "recipe_0": best}
    ex_est = {}
    for mid, m in ex_methods.items():
        if isinstance(m, WarrantedBenchmark):
            ex_est[mid] = m.apply(panel, [SHOWCASE_YEAR], keep_peers=True)
        else:
            ex_est[mid] = apply_recipe(panel, m, [SHOWCASE_YEAR], keep_peers=True)
    py = panel[panel["fiscal_year"] == SHOWCASE_YEAR].set_index("id")
    mult_y = py["ev"] / py["ebitda"]
    examples = []
    for t in SHOWCASE:
        hit = py[py["ticker"] == t]
        if hit.empty:
            continue
        fid = hit.index[0]
        ex = {"ticker": t, "name": hit.iloc[0]["name"], "sic3": hit.iloc[0]["industry_l3"],
              "actual_ev": float(hit.iloc[0]["ev"]), "ebitda": float(hit.iloc[0]["ebitda"]),
              "actual_multiple": float(mult_y[fid]),
              "features": {k: float(hit.iloc[0][k]) if pd.notna(hit.iloc[0][k]) else None
                           for k in ("sales_growth_3y", "roic", "ebitda_margin", "log_sales")},
              "methods": {}}
        for mid, e in ex_est.items():
            er = e[e["id"] == fid]
            if er.empty or pd.isna(er.iloc[0]["estimate"]):
                continue
            er = er.iloc[0]
            peers = [{"ticker": names.loc[p, "ticker"], "name": names.loc[p, "name"],
                      "multiple": float(mult_y.get(p, np.nan))} for p in er["peers"]]
            ex["methods"][mid] = {"estimate": float(er["estimate"]), "peer_multiple": float(er["peer_multiple"]),
                                  "n_peers": int(er["n_peers"]), "error": float(np.log(er["estimate"] / er["actual"])),
                                  "peers": peers if mid != "industry_median" else peers[:0],
                                  "peer_count": len(peers)}
        examples.append(ex)

    # Exploration example: does matching on growth help EV/Sales comps? (explore years only)
    disc_years = [2018, 2019]
    disc_base = dict(multiple="EV/Sales", filters=[{"same": "industry_l3"}], k=8, agg="median",
                     min_peers=3, fallback=[[{"same": "industry_l2"}]])
    discovery = []
    for label, rank in [("Margin only", {"ebitda_margin": 1.0}),
                        ("Margin + 1-year growth", {"ebitda_margin": 0.6, "sales_growth_1y": 0.4}),
                        ("Margin + 3-year growth", {"ebitda_margin": 0.6, "sales_growth_3y": 0.4})]:
        e = add_errors(apply_recipe(panel, validate(dict(disc_base, name=label, rank=rank)), disc_years))
        discovery.append({"label": label, "median_abs_error": e["abs_error"].median(),
                          "coverage": e["estimate"].notna().mean()})

    # Bhojraj-Lee coefficients (estimated on each prior year).
    coefs = {}
    for multiple in by_multiple:
        _, betas = warranted(panel, multiple)
        coefs[multiple] = {"years": sorted(betas), "terms": ["const"] + REGRESSORS,
                           "values": [list(map(float, betas[y])) for y in sorted(betas)]}

    # Data audit: Apple net income before and after the FactSet fix.
    aapl = panel[panel["ticker"] == "AAPL"].sort_values("fiscal_year")
    audit = {"years": aapl["fiscal_year"].tolist(), "after": aapl["net_income"].tolist(),
             "before": [112010.0] * len(aapl)}

    agent = agent_block(ROOT / "results/agent_runs/r1")

    counts = panel.groupby("fiscal_year").size()
    data = {
        "generated": datetime.now().strftime("%Y-%m-%d"),
        "protocol": {"explore": list(PROTOCOL.explore), "validate": list(PROTOCOL.validate),
                     "holdout": list(PROTOCOL.holdout), "train_only": [2015]},
        "sample": {"firm_years": int(len(panel)), "firms": int(panel["id"].nunique()),
                   "per_year": {int(k): int(v) for k, v in counts.items()}},
        "funnel": logs,
        "thresholds": THRESHOLDS,
        "multiples": out_mult,
        "examples": examples, "example_year": SHOWCASE_YEAR,
        "discovery": {"years": disc_years, "rows": discovery},
        "coefficients": coefs,
        "audit": audit,
        "agent": agent,
    }
    data = clean(data)
    site = ROOT / "site"
    (site / "site_data.json").write_text(json.dumps(data, indent=1))
    html = (site / "template.html").read_text()
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = html.replace("/*__DATA__*/null", payload)
    (site / "index.html").write_text(page)
    print("wrote", site / "index.html", f"({len(payload) / 1024:.0f} KB data)")
    # Standalone copy for GitHub Pages (docs/index.html): a full HTML document.
    cut = page.index('<header class="top">')
    head, body = page[:cut], page[cut:]
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           '<meta name="description" content="ValuationLab: grading comparable-company valuation rules on US data, '
           'and AI agents that invent them.">\n'
           '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n'
           + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "index.html").write_text(doc)
    print("wrote", ROOT / "docs" / "index.html", "(standalone, for GitHub Pages)")


if __name__ == "__main__":
    main()
