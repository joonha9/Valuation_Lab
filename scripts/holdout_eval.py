"""One-time holdout evaluation (FY2024-2025), following docs/holdout_protocol.md.

    python3 scripts/holdout_eval.py manifest   # freeze the recipe list and the protocol's hash
    python3 scripts/holdout_eval.py dry-run    # whole pipeline without the holdout: FY2022-2023 stand in
    python3 scripts/holdout_eval.py open       # the one real evaluation (refuses to run twice)

Steps of `open`:
  1. The manifest must match the current final.json files and the protocol's SHA-256.
  2. The panel is rebuilt with data/holdout/ included.
  3. Integrity gate: every manifest recipe is re-scored on the validation years and must equal
     its stored validation score. On any mismatch the script stops before scoring the holdout.
  4. Every recipe is scored on the holdout years once; the pre-registered analyses are computed.
Outputs go to results/holdout/ (dry runs to results/holdout/dry_run/).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuationlab import agentloop as al  # noqa: E402
from valuationlab.baselines import baselines_for  # noqa: E402
from valuationlab.data import load_panel  # noqa: E402
from valuationlab.grader import Protocol, add_errors, by_year, compare, estimate, summarize  # noqa: E402
from valuationlab.recipe import validate  # noqa: E402

OUT = ROOT / "results/holdout"
PROTOCOL_DOC = ROOT / "docs/holdout_protocol.md"
RUNS = {"full": [f"r{i}" for i in range(1, 6)], "no_critic": [f"nc{i}" for i in range(1, 6)],
        "no_archive": [f"na{i}" for i in range(1, 6)], "neither": [f"nn{i}" for i in range(1, 6)]}
RANDOM_RUN = "r1"
HAND_FOR_H4 = {"EV/EBITDA": "Growth and ROIC peers", "EV/Sales": "Margin-matched sales peers"}
BENCHMARKS = ["industry_median", "bl_regression", "bl_peers", "market_median"]
SIMS, SEED = 20000, 2026
TOL = 1e-9
CHECKED = ("median_abs_error", "mean_abs_error", "coverage")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec_key(multiple: str, spec: dict) -> str:
    d = dict(spec)
    d.pop("name", None)
    return multiple + ":" + hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]


def sign_p(k: int, n: int) -> float:
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def perm_p(a: list[float], b: list[float]) -> float:
    """One-sided exact permutation p-value that mean(a) < mean(b)."""
    pooled, n, obs = np.array(a + b), len(a), np.mean(a) - np.mean(b)
    diffs = [pooled[list(i)].mean() - np.delete(pooled, list(i)).mean() for i in combinations(range(len(pooled)), n)]
    return float(np.mean(np.array(diffs) <= obs + 1e-12))


# ---------------------------------------------------------------- manifest

def build_manifest() -> dict:
    units: dict[str, dict] = {}   # unit key -> definition and stored validation score
    entries: list[dict] = []      # every role a unit plays

    def add_unit(key: str, unit: dict) -> None:
        if key in units and units[key]["validate"] != unit["validate"]:
            for c in CHECKED:  # same definition must have the same stored score
                if abs(units[key]["validate"][c] - unit["validate"][c]) > TOL:
                    raise ValueError(f"{key}: two stored validation scores disagree on {c}")
        units.setdefault(key, unit)

    for cond, runs in RUNS.items():
        for name in runs:
            run = al.Run(ROOT, name)
            final = json.loads((run.dir / "final.json").read_text())
            graded = [a for a in run.archive("agent") if a["status"] == "graded"]
            for m in al.MULTIPLES_IN_SCOPE:
                for row in final["multiples"][m]:
                    if row["source"] == "baseline":
                        key = f"{m}:baseline:{row['id']}"
                        unit = {"kind": "baseline", "multiple": m, "id": row["id"]}
                    else:
                        key = spec_key(m, row["spec"])
                        unit = {"kind": "recipe", "multiple": m, "spec": row["spec"]}
                    add_unit(key, {**unit, "validate": {c: row["validate"][c] for c in CHECKED}})
                    if row["source"] == "agent":
                        entries.append({"role": "agent", "condition": cond, "run": name, "multiple": m,
                                        "id": row["id"], "name": row["name"], "unit": key,
                                        "n_graded": sum(1 for a in graded if a["multiple"] == m)})
                    elif name == RANDOM_RUN:
                        entries.append({"role": row["source"], "multiple": m, "id": row["id"], "name": row["name"], "unit": key})

    rrun = al.Run(ROOT, RANDOM_RUN)
    rval = {json.loads(l)["id"]: json.loads(l)["validate"]
            for l in (rrun.dir / "random_validate.jsonl").read_text().splitlines() if l.strip()}
    rule = rrun.config["selection_rule"]
    for r in rrun.archive("random"):
        key = spec_key(r["multiple"], r["spec"])
        add_unit(key, {"kind": "recipe", "multiple": r["multiple"], "spec": r["spec"],
                       "validate": {c: rval[r["id"]][c] for c in CHECKED}})
        entries.append({"role": "random_pool", "multiple": r["multiple"], "id": r["id"], "unit": key,
                        "explore_median_abs_error": r["explore"]["median_abs_error"], "eligible": al.eligible(r, rule)})

    return {"protocol_file": str(PROTOCOL_DOC.relative_to(ROOT)), "protocol_sha256": sha256(PROTOCOL_DOC),
            "selection_rule": rule, "validate_years": [2020, 2021, 2022, 2023], "holdout_years": [2024, 2025],
            "n_units": len(units), "units": units, "entries": entries}


# ---------------------------------------------------------------- scoring

def score(panel, unit: dict, years: list[int]) -> dict:
    m = unit["multiple"]
    if unit["kind"] == "baseline":
        est = add_errors(estimate(panel, baselines_for(m)[unit["id"]], years))
        card = summarize(est)
        card["yearly_median_abs_error"] = {int(r.fiscal_year): float(r.median_abs_error) for r in by_year(est).itertuples()}
        return card
    recipe = validate(unit["spec"], set(panel.columns))
    card = al.grade_period(panel, recipe, years)
    ind = compare(estimate(panel, recipe, years), estimate(panel, baselines_for(m)["industry_median"], years))
    card["firm_level_vs_industry_median"] = {"n_common": ind["n_common"], "share_firms_better": ind["share_firms_better"],
                                             "mean_gain": ind["mean_gain"]}
    return card


def integrity_gate(panel, manifest: dict) -> list[dict]:
    years = manifest["validate_years"]
    bad = []
    for i, (key, unit) in enumerate(manifest["units"].items(), 1):
        s = summarize(estimate(panel, baselines_for(unit["multiple"])[unit["id"]] if unit["kind"] == "baseline"
                               else validate(unit["spec"], set(panel.columns)), years))
        for c in CHECKED:
            if not abs(s[c] - unit["validate"][c]) <= TOL:
                bad.append({"unit": key, "field": c, "stored": unit["validate"][c], "recomputed": s[c]})
        if i % 50 == 0:
            print(f"  integrity: {i}/{manifest['n_units']} units checked", flush=True)
    return bad


# ---------------------------------------------------------------- analyses

def analyses(manifest: dict, scores: dict, label: str) -> dict:
    E = manifest["entries"]
    val = lambda key: manifest["units"][key]["validate"]["median_abs_error"]  # noqa: E731
    hold = lambda key: scores[key]["median_abs_error"]  # noqa: E731
    rng = np.random.default_rng(SEED)
    out = {"period": label, "multiples": {}, "ablation": {}}

    def bench_key(m: str, bid: str) -> str:
        return f"{m}:baseline:{bid}"

    for m in al.MULTIPLES_IN_SCOPE:
        agents = [e for e in E if e["role"] == "agent" and e["condition"] == "full" and e["multiple"] == m]
        v = [hold(e["unit"]) for e in agents]
        hand = {e["name"]: e["unit"] for e in E if e["role"] == "hand" and e["multiple"] == m}
        rand_fin = next(e for e in E if e["role"] == "random" and e["multiple"] == m)
        fixed = {bid: bench_key(m, bid) for bid in BENCHMARKS}
        fixed.update({f"hand: {n}": k for n, k in hand.items()})
        fixed["random-search finalist"] = rand_fin["unit"]
        tests = {}
        for bid, key in fixed.items():
            k = sum(x < hold(key) for x in v)
            tests[bid] = {"holdout": hold(key), "validate": val(key), "runs_better": k, "of": len(v), "sign_p": sign_p(k, len(v))}

        pool = [e for e in E if e["role"] == "random_pool" and e["multiple"] == m]
        pe = np.array([e["explore_median_abs_error"] for e in pool])
        ok = np.array([e["eligible"] for e in pool])
        ph = np.array([hold(e["unit"]) for e in pool])
        sims = []
        for e in agents:
            idx = rng.integers(0, len(pool), size=(SIMS, e["n_graded"]))
            ex = np.where(ok[idx], pe[idx], np.inf)
            s = ph[idx[np.arange(SIMS), ex.argmin(axis=1)]].astype(float)
            s[~np.isfinite(ex.min(axis=1))] = np.nan
            sims.append(s)
        null = np.nanmean(np.column_stack(sims), axis=1)
        agent_mean = float(np.mean(v))
        p_random = float(np.nanmean(null <= agent_mean))

        h = {"H1_vs_industry_median": tests["industry_median"]["sign_p"] < 0.05,
             "H2_vs_bl_regression": tests["bl_regression"]["sign_p"] < 0.05,
             "H3_vs_random_search": p_random < 0.05}
        direction = (agent_mean < hold(fixed["industry_median"]) and agent_mean < hold(fixed["bl_regression"])
                     and agent_mean < float(np.nanmedian(null)))
        verdict = "replicated" if all(h.values()) else ("partly replicated" if direction else "not replicated")
        h4 = tests[f"hand: {HAND_FOR_H4[m]}"]
        ind = hold(fixed["industry_median"])
        out["multiples"][m] = {
            "agents": [{"run": e["run"], "id": e["id"], "name": e["name"], "validate": val(e["unit"]),
                        "holdout": hold(e["unit"]), "yearly": scores[e["unit"]]["yearly_median_abs_error"],
                        "coverage": scores[e["unit"]]["coverage"], "within_15pct": scores[e["unit"]]["within_15pct"],
                        "years_beating_industry_median": scores[e["unit"]]["years_beating_industry_median"],
                        "years_beating_bl_regression": scores[e["unit"]]["years_beating_bl_regression"],
                        "firm_level_vs_industry_median": scores[e["unit"]]["firm_level_vs_industry_median"],
                        "rel_improvement_vs_industry": (ind - hold(e["unit"])) / ind} for e in agents],
            "agent_mean_holdout": agent_mean,
            "agent_mean_validate": float(np.mean([val(e["unit"]) for e in agents])),
            "benchmarks": tests,
            "benchmark_yearly": {bid: scores[k]["yearly_median_abs_error"] for bid, k in fixed.items()},
            "random_search": {"p_value": p_random, "null_median": float(np.nanmedian(null)),
                              "null_p05": float(np.nanquantile(null, 0.05)), "null_p95": float(np.nanquantile(null, 0.95))},
            "hypotheses": {**h, "H4_vs_hand": h4["sign_p"] < 0.05, "H4_runs_better": h4["runs_better"]},
            "verdict_H1_H3": verdict,
            "decay": {"agent_rel_improvement_validate": float(np.mean([(val(fixed["industry_median"]) - val(e["unit"])) / val(fixed["industry_median"]) for e in agents])),
                      "agent_rel_improvement_holdout": float(np.mean([(ind - hold(e["unit"])) / ind for e in agents])),
                      "change_in_error": {bid: hold(k) - val(k) for bid, k in fixed.items()},
                      "agent_mean_change_in_error": agent_mean - float(np.mean([val(e["unit"]) for e in agents]))},
        }

    # S1 ablation, same summary metric as scripts/ablation_analysis.py
    per_run: dict[str, list[float]] = {}
    for cond, runs in RUNS.items():
        rows = []
        for name in runs:
            rel, ms = [], {}
            for m in al.MULTIPLES_IN_SCOPE:
                e = next((x for x in E if x["role"] == "agent" and x["run"] == name and x["multiple"] == m), None)
                if e is None:
                    continue
                ind = hold(bench_key(m, "industry_median"))
                rel.append((ind - hold(e["unit"])) / ind)
                ms[m] = hold(e["unit"])
            rows.append({"run": name, "holdout": ms, "rel_improvement": float(np.mean(rel)) if len(rel) == 2 else None})
        per_run[cond] = [r["rel_improvement"] for r in rows if r["rel_improvement"] is not None]
        out["ablation"][cond] = {"runs": rows, "mean_rel_improvement": float(np.mean(per_run[cond]))}
    out["ablation_tests"] = {
        f"full_vs_{c}": {"diff": float(np.mean(per_run["full"]) - np.mean(per_run[c])),
                         "p_full_better": perm_p([-x for x in per_run["full"]], [-x for x in per_run[c]]),
                         "p_condition_better": perm_p([-x for x in per_run[c]], [-x for x in per_run["full"]])}
        for c in ("no_critic", "no_archive", "neither")}
    return out


def print_summary(res: dict) -> None:
    for m, d in res["multiples"].items():
        print(f"\n{m} ({res['period']}): agents mean {d['agent_mean_holdout']:.3f} (validation {d['agent_mean_validate']:.3f}) "
              f"| random search p = {d['random_search']['p_value']:.4f} | {d['verdict_H1_H3']}")
        for a in d["agents"]:
            print(f"  {a['run']} {a['id']:7s} validate {a['validate']:.3f} -> test {a['holdout']:.3f}")
        for bid, t in d["benchmarks"].items():
            print(f"  vs {bid:34s} {t['validate']:.3f} -> {t['holdout']:.3f}: {t['runs_better']}/{t['of']} runs better (p={t['sign_p']:.3f})")
    for c, a in res["ablation"].items():
        print(f"ablation {c:10s} rel. improvement vs industry {a['mean_rel_improvement']:+.1%}")


# ---------------------------------------------------------------- main

def run(mode: str) -> int:
    mpath = OUT / "manifest.json"
    if mode == "manifest":
        if mpath.exists():
            print("manifest already exists; delete it only before the holdout is opened")
            return 1
        OUT.mkdir(parents=True, exist_ok=True)
        man = build_manifest()
        mpath.write_text(json.dumps(man, indent=1, default=float))
        print(f"wrote {mpath} ({man['n_units']} units, {len(man['entries'])} entries, protocol {man['protocol_sha256'][:12]})")
        return 0

    manifest = json.loads(mpath.read_text())
    fresh = build_manifest()
    if fresh["units"] != manifest["units"] or fresh["entries"] != manifest["entries"]:
        print("STOP: recipes in the run folders no longer match the frozen manifest")
        return 1
    if fresh["protocol_sha256"] != manifest["protocol_sha256"]:
        print("STOP: docs/holdout_protocol.md changed after the manifest was frozen")
        return 1

    if mode == "open":
        target = OUT / "holdout_results.json"
        if target.exists():
            print(f"STOP: {target} exists; the holdout is evaluated once")
            return 1
        panel = load_panel(ROOT, include_holdout=True)
        years = Protocol((2016, 2017, 2018, 2019), (2020, 2021, 2022, 2023), (2024, 2025)).years("holdout", allow_holdout=True)
        if not set(years) <= set(panel["fiscal_year"].unique()):
            print("STOP: holdout years missing from the panel")
            return 1
    else:
        target = OUT / "dry_run" / "dry_run_results.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        panel = load_panel(ROOT)  # never reads data/holdout/
        years = [2022, 2023]
        if panel["fiscal_year"].max() > 2023:
            print("STOP: dry-run panel contains holdout years")
            return 1

    started = datetime.now().isoformat(timespec="seconds")
    print(f"{mode}: integrity gate on validation years ({manifest['n_units']} units)", flush=True)
    bad = integrity_gate(panel, manifest)
    if bad:
        (target.parent / f"integrity_failure_{mode}.json").write_text(json.dumps(bad, indent=1, default=float))
        print(f"STOP: {len(bad)} validation scores differ; nothing was scored on {years}")
        return 1
    print(f"  integrity gate passed: all {manifest['n_units']} validation scores reproduced", flush=True)

    scores = {}
    for i, (key, unit) in enumerate(manifest["units"].items(), 1):
        scores[key] = score(panel, unit, years)
        if i % 50 == 0:
            print(f"  scored {i}/{manifest['n_units']} on FY{years[0]}-{years[-1]}", flush=True)
    res = analyses(manifest, scores, f"FY{years[0]}-{years[-1]}" + (" (dry run)" if mode != "open" else ""))
    res.update({"mode": mode, "years": years, "started": started, "finished": datetime.now().isoformat(timespec="seconds"),
                "protocol_sha256": manifest["protocol_sha256"], "manifest_sha256": sha256(mpath),
                "integrity_gate": "passed", "scores": scores})
    target.write_text(json.dumps(res, indent=1, default=float))
    print_summary(res)
    print("\nwrote", target)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["manifest", "dry-run", "open"])
    sys.exit(run(ap.parse_args().mode))
