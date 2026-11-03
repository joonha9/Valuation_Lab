"""Grade every random-control recipe on the validation years (control group only).

The random pool is never selected from on these scores; they are used only to build the
luck distribution: how good a random-search finalist would have been in validation.

    python3 scripts/random_validate.py --run r1
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
from valuationlab.recipe import validate  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run", default="r1")
a = ap.parse_args()
run = al.Run(ROOT, a.run)
panel = load_panel(ROOT)
out = run.dir / "random_validate.jsonl"
done = {json.loads(l)["id"] for l in out.read_text().splitlines()} if out.exists() else set()
years = run.protocol().years("validate")
with open(out, "a") as fh:
    for r in run.archive("random"):
        if r["id"] in done:
            continue
        rec = validate(r["spec"], set(panel.columns))
        fh.write(json.dumps({"id": r["id"], "multiple": r["multiple"],
                             "validate": al.grade_period(panel, rec, years)}, default=float) + "\n")
print("graded", len(run.archive("random")), "random recipes on validation years")
