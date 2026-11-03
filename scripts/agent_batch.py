"""Advance several agent runs by one step each (used to run independent searches in parallel).

    python3 scripts/agent_batch.py --runs r2 r3 r4 r5

For each run: if the subagent's reply for the current stage exists, process it
(submit proposals -> write critic brief, or grade verdicts -> write next proposer brief).
Prints the brief each run now waits on. Stops issuing proposer briefs after --generations.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuationlab import agentloop as al  # noqa: E402
from valuationlab.data import load_panel  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--runs", nargs="+", required=True)
ap.add_argument("--generations", type=int, default=5)
a = ap.parse_args()
panel = load_panel(ROOT)

def step(name: str) -> bool:
    """Advance one run by one stage if its input is ready. Returns True if it moved."""
    run = al.Run(ROOT, name)
    st, g, cfg = run.state, run.state["generation"], run.config
    gd = run.gen_dir(g) if g else None
    if st["stage"] == "awaiting_proposals" and (gd / "proposals.txt").exists():
        reply = al.parse_json_reply((gd / "proposals.txt").read_text())
        pending = al.register_proposals(run, panel, reply, g, "claude-code-subagent")
        if cfg.get("critic", True):
            (gd / "critic_prompt.md").write_text(al.critic_prompt(run, panel, pending))
            run.save_state({"generation": g, "stage": "awaiting_verdicts"})
            print(f"{name} gen{g}: {len(pending)} proposals to critic -> CRITIC {gd / 'critic_prompt.md'}")
            return True
        run.save_state({"generation": g, "stage": "awaiting_verdicts"})
        return grade(run, name, g, None)
    if st["stage"] == "awaiting_verdicts" and cfg.get("critic", True) and (gd / "verdicts.txt").exists():
        return grade(run, name, g, al.parse_json_reply((gd / "verdicts.txt").read_text()))
    return False


def grade(run, name, g, reply) -> bool:
    recs = al.apply_verdicts(run, panel, reply, g)
    run.save_state({"generation": g, "stage": "graded"})
    best = [r["explore"]["median_abs_error"] for r in recs if r.get("explore")]
    print(f"  {name} gen{g}: graded {len(best)}/{len(recs)}" + (f", best {min(best):.3f}" if best else ""))
    if g < a.generations:
        g2 = g + 1
        p = run.gen_dir(g2) / "proposer_prompt.md"
        p.write_text(al.proposer_prompt(run, panel, g2))
        run.save_state({"generation": g2, "stage": "awaiting_proposals"})
        print(f"{name} -> PROPOSER {p}")
    else:
        print(f"{name}: search complete ({al.funnel(run.archive('agent'))})")
    return True


moved = True
while moved:
    moved = any([step(n) for n in a.runs])
for n in a.runs:
    print(n, al.Run(ROOT, n).state)
