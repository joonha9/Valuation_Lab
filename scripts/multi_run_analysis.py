"""Skill or luck? Compare the finalists of several independent agent runs with random search.

    python3 scripts/multi_run_analysis.py --runs r1 r2 r3 r4 r5

For each multiple:
  - each run's finalist (picked by the frozen rule on exploration years) and its
    validation-year error;
  - a luck distribution: simulate a random-search run with the same number of graded
    recipes as the agent run (drawn with replacement from the 100 random recipes of
    that multiple), apply the same selection rule, and record the random finalist's
    validation error; repeat many times;
  - per-run percentile: share of simulated random runs that did at least as well;
  - combined test: the mean validation error of the K agent finalists against the
    distribution of the mean of K simulated random finalists (one-sided p-value);
  - sign tests: in how many runs the finalist beat each fixed benchmark.
Writes results/agent_runs/multi_summary.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuationlab import agentloop as al  # noqa: E402

SIMS = 20000


def sign_p(k: int, n: int) -> float:
    """P(X >= k) for X ~ Binomial(n, 0.5)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--random-run", default="r1")
    a = ap.parse_args()

    rrun = al.Run(ROOT, a.random_run)
    rule = rrun.config["selection_rule"]
    rnd = {r["id"]: r for r in rrun.archive("random")}
    rval = {json.loads(l)["id"]: json.loads(l)["validate"]
            for l in (rrun.dir / "random_validate.jsonl").read_text().splitlines() if l.strip()}
    rng = np.random.default_rng(2026)
    out = {"runs": a.runs, "sims": SIMS, "rule": rule, "multiples": {}}

    for m in al.MULTIPLES_IN_SCOPE:
        pool = [r for r in rnd.values() if r["multiple"] == m]
        p_exp = np.array([r["explore"]["median_abs_error"] for r in pool])
        p_ok = np.array([al.eligible(r, rule) for r in pool])
        p_val = np.array([rval[r["id"]]["median_abs_error"] for r in pool])

        def sim_random_finalists(n: int, size: int) -> np.ndarray:
            idx = rng.integers(0, len(pool), size=(size, n))
            e = np.where(p_ok[idx], p_exp[idx], np.inf)
            best = idx[np.arange(size), e.argmin(axis=1)]
            v = p_val[best].astype(float)
            v[~np.isfinite(e.min(axis=1))] = np.nan  # no eligible recipe drawn
            return v

        runs, sims_by_run = [], []
        bench = None
        for name in a.runs:
            run = al.Run(ROOT, name)
            final = json.loads((run.dir / "final.json").read_text())
            rows = final["multiples"][m]
            fin = next((r for r in rows if r["source"] == "agent"), None)
            n = sum(1 for x in run.archive("agent") if x.get("multiple") == m and x["status"] == "graded")
            sims = sim_random_finalists(n, SIMS)
            sims_by_run.append(sims)
            if bench is None:
                bench = {r["id"]: r["validate"]["median_abs_error"] for r in rows if r["source"] in ("baseline", "hand")}
            if fin is None:
                runs.append({"run": name, "n_graded": n, "finalist": None})
                continue
            v = fin["validate"]["median_abs_error"]
            runs.append({"run": name, "n_graded": n, "id": fin["id"], "name": fin["name"], "compact": fin["compact"],
                         "explore": fin["explore"]["median_abs_error"], "validate": v,
                         "validate_mean": fin["validate"]["mean_abs_error"],
                         "years_beating_industry": fin["validate"].get("years_beating_industry_median"),
                         "years_beating_bl_regression": fin["validate"].get("years_beating_bl_regression"),
                         "pct_random_as_good": float(np.nanmean(sims <= v)),
                         "random_finalist_median": float(np.nanmedian(sims))})
        got = [r for r in runs if r.get("validate") is not None]
        agent_mean = float(np.mean([r["validate"] for r in got]))
        S = np.column_stack([sims_by_run[i] for i, r in enumerate(runs) if r.get("validate") is not None])
        null_mean = np.nanmean(S, axis=1)
        tests = {}
        for bid, bv in bench.items():
            k = sum(r["validate"] < bv for r in got)
            tests[bid] = {"value": bv, "runs_better": k, "of": len(got), "sign_p": sign_p(k, len(got))}
        out["multiples"][m] = {
            "runs": runs, "agent_mean_validate": agent_mean,
            "random_mean_of_k": {"median": float(np.nanmedian(null_mean)), "p05": float(np.nanquantile(null_mean, 0.05)),
                                 "p95": float(np.nanquantile(null_mean, 0.95))},
            "p_value_vs_random": float(np.nanmean(null_mean <= agent_mean)),
            "benchmarks": tests,
            "random_single_run": {q: float(np.nanquantile(S.ravel(), v)) for q, v in
                                  (("p05", .05), ("p25", .25), ("p50", .5), ("p75", .75), ("p95", .95))},
        }

    path = ROOT / "results/agent_runs/multi_summary.json"
    path.write_text(json.dumps(out, indent=1))
    for m, d in out["multiples"].items():
        print(f"\n{m}: agent mean validation error {d['agent_mean_validate']:.3f} | random-search mean of {len(d['runs'])}: "
              f"median {d['random_mean_of_k']['median']:.3f} (5-95%: {d['random_mean_of_k']['p05']:.3f}-{d['random_mean_of_k']['p95']:.3f}) "
              f"| p = {d['p_value_vs_random']:.4f}")
        for r in d["runs"]:
            if r.get("validate") is None:
                print(f"  {r['run']}: no eligible finalist")
                continue
            print(f"  {r['run']} {r['id']} explore {r['explore']:.3f} validate {r['validate']:.3f} mean {r['validate_mean']:.3f} "
                  f"beats-ind {r['years_beating_industry']}/4 | random as good: {r['pct_random_as_good']:.1%}  {r['name']}")
        for bid, t in d["benchmarks"].items():
            print(f"  vs {bid:28s} {t['value']:.3f}: {t['runs_better']}/{t['of']} runs better (sign p={t['sign_p']:.3f})")
    print("\nwrote", path)


if __name__ == "__main__":
    main()
