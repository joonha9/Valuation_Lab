"""Command-line driver for the agent search loop (proposer -> critic -> grader -> archive).

    python3 scripts/agent_loop.py init     --run r1          # freeze config and selection rule
    python3 scripts/agent_loop.py random   --run r1 --n 200  # random-search control (no LLM)
    python3 scripts/agent_loop.py prompt   --run r1          # write the next proposer prompt
    python3 scripts/agent_loop.py submit   --run r1          # read genXX/proposals.txt, write critic prompt
    python3 scripts/agent_loop.py grade    --run r1          # read genXX/verdicts.txt, grade approved
    python3 scripts/agent_loop.py status   --run r1
    python3 scripts/agent_loop.py finalize --run r1          # select by the frozen rule, validate once

Proposer and critic are Claude Code subagents: their raw replies are saved as
genXX/proposals.txt and genXX/verdicts.txt before the next step runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuationlab import agentloop as al  # noqa: E402
from valuationlab.data import load_panel  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["init", "random", "prompt", "submit", "grade", "status", "finalize"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--proposer", default="claude-code-subagent")
    ap.add_argument("--condition", default="full", choices=list(al.CONDITIONS))
    a = ap.parse_args()

    if a.cmd == "init":
        run = al.Run.create(ROOT, a.run, {"condition": a.condition, **al.CONDITIONS[a.condition]})
        print("created", run.dir)
        print("selection rule:", run.config["selection_rule"]["description"])
        return

    run = al.Run(ROOT, a.run)
    st = run.state
    panel = load_panel(ROOT)

    if a.cmd == "random":
        al.run_random(run, panel, a.n)
        print(f"random archive: {len(run.archive('random'))} recipes")

    elif a.cmd == "prompt":
        if st["stage"] not in ("ready", "graded"):
            sys.exit(f"stage is '{st['stage']}', finish the current generation first")
        g = st["generation"] + 1
        p = run.gen_dir(g) / "proposer_prompt.md"
        p.write_text(al.proposer_prompt(run, panel, g))
        run.save_state({"generation": g, "stage": "awaiting_proposals"})
        print(p)

    elif a.cmd == "submit":
        g = st["generation"]
        reply = al.parse_json_reply((run.gen_dir(g) / "proposals.txt").read_text())
        pending = al.register_proposals(run, panel, reply, g, a.proposer)
        p = run.gen_dir(g) / "critic_prompt.md"
        p.write_text(al.critic_prompt(run, panel, pending))
        run.save_state({"generation": g, "stage": "awaiting_verdicts"})
        bad = [x for x in run.archive("agent") if x["generation"] == g and x["status"] in ("invalid", "duplicate")]
        print(f"gen {g}: {len(pending)} valid proposals sent to critic; {len(bad)} invalid/duplicate")
        for x in bad:
            print("  ", x["id"], x["status"], x["reason"][:160])
        print(p)

    elif a.cmd == "grade":
        g = st["generation"]
        reply = al.parse_json_reply((run.gen_dir(g) / "verdicts.txt").read_text())
        recs = al.apply_verdicts(run, panel, reply, g)
        run.save_state({"generation": g, "stage": "graded"})
        for r in recs:
            if r["status"] == "graded":
                e = r["explore"]
                print(f"  {r['id']} {r['multiple']:9s} median {e['median_abs_error']:.3f} mean {e['mean_abs_error']:.3f} "
                      f"cov {e['coverage']:.1%} beats-ind {e['years_beating_industry_median']}/4  {r['name']}")
            else:
                print(f"  {r['id']} rejected: {r['critic_reason'][:150]}")

    elif a.cmd == "status":
        print(json.dumps(st), al.funnel(run.archive("agent")))
        base = al.baseline_scores(panel, run.protocol())
        for m in al.MULTIPLES_IN_SCOPE:
            print(m, {k: round(v["median_abs_error"], 3) for k, v in base[m].items()})
            g = sorted((x for x in run.archive("agent") if x["status"] == "graded" and x["multiple"] == m),
                       key=lambda x: x["explore"]["median_abs_error"])[:5]
            for x in g:
                print(f"   {x['id']} {x['explore']['median_abs_error']:.3f} beats {x['explore']['years_beating_industry_median']}/4 {x['compact']}")

    elif a.cmd == "finalize":
        hand = json.loads((ROOT / "recipes/examples.json").read_text())
        res = al.finalize(run, panel, hand)
        print("frozen at", res["frozen_at"], res["funnel"])
        for m, rows in res["multiples"].items():
            print(m)
            for r in rows:
                print(f"  {r['source']:8s} {str(r['name'])[:40]:40s} explore {r['explore']['median_abs_error']:.3f}  validate {r['validate']['median_abs_error']:.3f}")


if __name__ == "__main__":
    main()
