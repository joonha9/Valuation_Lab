"""Causal design: which part of the agent matters? Compares four conditions, five runs each.

    python3 scripts/ablation_analysis.py

  full        proposer sees the archive + critic filters      (r1-r5)
  no_critic   proposer sees the archive, no critic            (nc1-nc5)
  no_archive  memoryless proposer + critic                    (na1-na5)
  neither     memoryless proposer, no critic                  (nn1-nn5)

no_archive and neither share the same proposer draws (paired design for the critic).
For each run the finalist is picked by the same frozen rule and graded once on the
validation years. Summary metric per run: validation error relative to the industry
median, averaged over the two multiples. Condition differences are tested with exact
permutation tests (5 vs 5 runs); each condition is also compared with random search.
Writes results/agent_runs/ablation_summary.json.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuationlab import agentloop as al  # noqa: E402

CONDITIONS = {"full": ["r1", "r2", "r3", "r4", "r5"], "no_critic": [f"nc{i}" for i in range(1, 6)],
              "no_archive": [f"na{i}" for i in range(1, 6)], "neither": [f"nn{i}" for i in range(1, 6)]}
SIMS = 20000


def perm_p(a: list[float], b: list[float]) -> float:
    """One-sided exact permutation p-value that mean(a) < mean(b) (lower error is better)."""
    pooled, n, obs = np.array(a + b), len(a), np.mean(a) - np.mean(b)
    diffs = [pooled[list(i)].mean() - np.delete(pooled, list(i)).mean() for i in combinations(range(len(pooled)), n)]
    return float(np.mean(np.array(diffs) <= obs + 1e-12))


def main() -> None:
    rrun = al.Run(ROOT, "r1")
    rule = rrun.config["selection_rule"]
    rnd = rrun.archive("random")
    rval = {json.loads(l)["id"]: json.loads(l)["validate"]["median_abs_error"]
            for l in (rrun.dir / "random_validate.jsonl").read_text().splitlines() if l.strip()}
    rng = np.random.default_rng(7)
    out = {"conditions": {}, "tests": {}}
    per_run_score: dict[str, list[float]] = {}

    for cond, runs in CONDITIONS.items():
        rows = []
        for name in runs:
            run = al.Run(ROOT, name)
            final = json.loads((run.dir / "final.json").read_text())
            arch = run.archive("agent")
            graded = [a for a in arch if a["status"] == "graded"]
            ideas = {(a["multiple"], tuple(sorted(a["spec"]["rank"])), tuple(sorted(str(f) for f in a["spec"]["filters"]))) for a in graded}
            rec = {"run": name, "funnel": final["funnel"], "eligible": sum(al.eligible(a, rule) for a in arch),
                   "distinct_ideas": len(ideas), "multiples": {}}
            rel = []
            for m in al.MULTIPLES_IN_SCOPE:
                rs = final["multiples"][m]
                fin = next((r for r in rs if r["source"] == "agent"), None)
                ind = next(r for r in rs if r["id"] == "industry_median")["validate"]["median_abs_error"]
                bestx = min((a["explore"]["median_abs_error"] for a in graded if a["multiple"] == m), default=None)
                if fin is None:
                    rec["multiples"][m] = {"finalist": None, "best_explore_any": bestx}
                    continue
                v = fin["validate"]["median_abs_error"]
                rel.append((ind - v) / ind)
                rec["multiples"][m] = {"id": fin["id"], "name": fin["name"], "explore": fin["explore"]["median_abs_error"],
                                       "validate": v, "best_explore_any": bestx, "n_graded": sum(1 for a in graded if a["multiple"] == m)}
            rec["rel_improvement"] = float(np.mean(rel)) if len(rel) == 2 else None
            rows.append(rec)
        per_run_score[cond] = [r["rel_improvement"] for r in rows if r["rel_improvement"] is not None]
        summ = {"runs": rows, "mean_rel_improvement": float(np.mean(per_run_score[cond])), "multiples": {}}
        for m in al.MULTIPLES_IN_SCOPE:
            vals = [r["multiples"][m]["validate"] for r in rows if r["multiples"][m].get("validate") is not None]
            pool = [r for r in rnd if r["multiple"] == m]
            pe = np.array([r["explore"]["median_abs_error"] for r in pool])
            ok = np.array([al.eligible(r, rule) for r in pool])
            pv = np.array([rval[r["id"]] for r in pool])
            sims = []
            for r in rows:
                n = r["multiples"][m].get("n_graded") or 25
                idx = rng.integers(0, len(pool), size=(SIMS, n))
                e = np.where(ok[idx], pe[idx], np.inf)
                sims.append(pv[idx[np.arange(SIMS), e.argmin(axis=1)]])
            null = np.mean(np.column_stack(sims), axis=1)
            summ["multiples"][m] = {"mean_validate": float(np.mean(vals)), "sd_validate": float(np.std(vals, ddof=1)),
                                    "values": vals, "p_vs_random": float(np.mean(null <= np.mean(vals)))}
        f = [r["funnel"] for r in rows]
        summ["funnel_mean"] = {k: float(np.mean([x[k] for x in f])) for k in f[0]}
        summ["eligible_mean"] = float(np.mean([r["eligible"] for r in rows]))
        summ["distinct_ideas_mean"] = float(np.mean([r["distinct_ideas"] for r in rows]))
        out["conditions"][cond] = summ

    for cond in ("no_critic", "no_archive", "neither"):
        t = {"rel_improvement_diff": float(np.mean(per_run_score["full"]) - np.mean(per_run_score[cond])),
             "p_full_better": perm_p([-x for x in per_run_score["full"]], [-x for x in per_run_score[cond]]),
             "p_condition_better": perm_p([-x for x in per_run_score[cond]], [-x for x in per_run_score["full"]])}
        for m in al.MULTIPLES_IN_SCOPE:
            a = out["conditions"]["full"]["multiples"][m]["values"]; b = out["conditions"][cond]["multiples"][m]["values"]
            t[m] = {"diff": float(np.mean(b) - np.mean(a)), "p_full_better": perm_p(a, b)}
        out["tests"][f"full_vs_{cond}"] = t
    # critic effect without archive (paired: same proposals)
    a = per_run_score["no_archive"]; b = per_run_score["neither"]
    out["tests"]["critic_effect_without_archive"] = {"rel_improvement_diff": float(np.mean(a) - np.mean(b)),
                                                     "p": perm_p([-x for x in a], [-x for x in b])}
    path = ROOT / "results/agent_runs/ablation_summary.json"
    path.write_text(json.dumps(out, indent=1))
    for cond, s in out["conditions"].items():
        print(f"{cond:11s} rel.improv vs industry {s['mean_rel_improvement']:+.3%} | "
              + " | ".join(f"{m} {d['mean_validate']:.3f}±{d['sd_validate']:.3f} (p vs random {d['p_vs_random']:.4f})" for m, d in s["multiples"].items())
              + f" | graded {s['funnel_mean']['graded']:.1f} rejected {s['funnel_mean']['rejected_by_critic']:.1f} dup {s['funnel_mean']['duplicate']:.1f} eligible {s['eligible_mean']:.1f} ideas {s['distinct_ideas_mean']:.1f}")
    for k, t in out["tests"].items():
        print(k, json.dumps(t))
    print("wrote", path)


if __name__ == "__main__":
    main()
