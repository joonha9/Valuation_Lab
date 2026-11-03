"""Agent search loop for comps recipes (Stage 2), following the SignalLab design.

Roles
  - Proposer (an LLM agent): writes new recipes, each with a mechanism and a
    falsifiable prediction. It sees the DSL, baseline scores and the archive of
    earlier attempts with their EXPLORATION scores only.
  - Critic (a separate LLM agent): approves or rejects each proposal BEFORE it is
    graded, on economic logic, novelty and leakage. It never sees any score.
  - Grader (this module, deterministic): validates, de-duplicates, grades approved
    recipes on exploration years only, and appends every attempt to the archive.
  - Selection (this module): a rule fixed in config.json when the run is created
    picks the finalists from the archive; only they are graded on validation years,
    once. Holdout years are never touched.

Every attempt is logged, including invalid, duplicate and rejected ones, so the
search denominator is always known. The agents run as Claude Code subagents: this
module writes their prompts to files and reads their JSON answers back.
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .baselines import baselines_for
from .grader import Protocol, add_errors, compare, estimate, summarize
from .panel import FEATURES
from .recipe import AGGREGATORS, RecipeError, validate

MULTIPLES_IN_SCOPE = ["EV/EBITDA", "EV/Sales"]
GROUPS_IN_DATA = ["industry_l2", "industry_l3", "industry_l4"]
DEFAULT_CONFIG = {
    "protocol": {"explore": [2016, 2017, 2018, 2019], "validate": [2020, 2021, 2022, 2023],
                 "holdout": [2024, 2025]},
    "multiples": MULTIPLES_IN_SCOPE,
    "proposals_per_generation": 6,
    "selection_rule": {
        "description": ("Among graded recipes with exploration coverage >= 95% that beat the industry "
                        "median in at least 3 of 4 exploration years, pick the one with the lowest "
                        "exploration median |error| for each multiple."),
        "min_coverage": 0.95, "min_years_beating_industry": 3, "top_n_per_multiple": 1,
    },
    "critic_sees_scores": False,
    "proposer_sees_validation": False,
    # Ablation switches (the causal design). "full" = proposer sees the archive and a critic filters.
    "condition": "full",
    "critic": True,
    "archive_to_proposer": True,
}
CONDITIONS = {
    "full": {"critic": True, "archive_to_proposer": True},
    "no_critic": {"critic": False, "archive_to_proposer": True},
    "no_archive": {"critic": True, "archive_to_proposer": False},
    "neither": {"critic": False, "archive_to_proposer": False},
}

FEATURE_NOTES = {
    "log_sales": "log of sales (size)",
    "log_assets": "log of total assets (size)",
    "sales_growth_1y": "1-year sales growth",
    "sales_growth_3y": "3-year annualized sales growth (missing for FY2016-2017: not enough history)",
    "gross_margin": "gross profit / sales",
    "ebitda_margin": "EBITDA / sales",
    "ebit_margin": "EBIT / sales",
    "net_margin": "net income / sales",
    "roic": "EBIT x (1 - 25%) / (equity + debt - cash)",
    "roe": "net income / book equity",
    "asset_turnover": "sales / total assets",
    "net_debt_to_ebitda": "(debt - cash) / EBITDA",
    "debt_to_assets": "total debt / total assets",
    "rnd_intensity": "R&D / sales",
    "capex_intensity": "capital expenditure / sales",
}


# ---------------------------------------------------------------- utilities

def spec_hash(recipe) -> str:
    """Identity of a recipe's behaviour (name excluded)."""
    d = recipe.to_dict()
    d.pop("name")
    return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:10]


def compact(recipe) -> str:
    d = recipe.to_dict()
    parts = [d["multiple"]]
    if d["filters"]:
        parts.append("screen " + ", ".join(_f(f) for f in d["filters"]))
    if d["rank"]:
        parts.append("rank " + ", ".join(f"{k} {v:g}" for k, v in d["rank"].items()))
    parts.append(f"k={d['k']}, {d['agg']}, min_peers={d['min_peers']}")
    if d["fallback"]:
        parts.append("fallback " + " -> ".join("[" + ", ".join(_f(f) for f in fs) + "]" for fs in d["fallback"]))
    return " | ".join(parts)


def _f(f: dict) -> str:
    (kind, arg), = f.items()
    return f"same {arg}" if kind == "same" else f"band {arg['var']}±{arg['width']:g}"


class Run:
    """A search run stored under results/agent_runs/<name>/."""

    def __init__(self, root: Path, name: str):
        self.dir = root / "results" / "agent_runs" / name
        self.name = name

    # -- files
    @property
    def config(self) -> dict:
        return json.loads((self.dir / "config.json").read_text())

    @property
    def state(self) -> dict:
        return json.loads((self.dir / "state.json").read_text())

    def save_state(self, s: dict) -> None:
        (self.dir / "state.json").write_text(json.dumps(s, indent=2))

    def archive(self, kind: str = "agent") -> list[dict]:
        p = self.dir / f"archive_{kind}.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

    def append(self, rec: dict, kind: str = "agent") -> None:
        with open(self.dir / f"archive_{kind}.jsonl", "a") as fh:
            fh.write(json.dumps(rec, default=float) + "\n")

    def gen_dir(self, g: int) -> Path:
        d = self.dir / f"gen{g:02d}"
        d.mkdir(exist_ok=True)
        return d

    def protocol(self) -> Protocol:
        p = self.config["protocol"]
        return Protocol(tuple(p["explore"]), tuple(p["validate"]), tuple(p["holdout"]))

    @classmethod
    def create(cls, root: Path, name: str, overrides: dict | None = None) -> "Run":
        run = cls(root, name)
        if run.dir.exists():
            raise FileExistsError(f"run '{name}' already exists")
        run.dir.mkdir(parents=True)
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        cfg.update(overrides or {})
        cfg.update({"run": name, "created": datetime.now().isoformat(timespec="seconds")})
        (run.dir / "config.json").write_text(json.dumps(cfg, indent=2))
        run.save_state({"generation": 0, "stage": "ready"})
        return run


# ---------------------------------------------------------------- grading

def baseline_scores(panel: pd.DataFrame, protocol: Protocol) -> dict:
    out = {}
    years = protocol.years("explore")
    for m in MULTIPLES_IN_SCOPE:
        for bid, b in baselines_for(m).items():
            if bid == "market_median":
                continue
            s = summarize(estimate(panel, b, years))
            out.setdefault(m, {})[bid] = {"name": b.name, "median_abs_error": s["median_abs_error"],
                                          "mean_abs_error": s["mean_abs_error"], "coverage": s["coverage"]}
    return out


def grade_period(panel: pd.DataFrame, recipe, years: list[int]) -> dict:
    est = add_errors(estimate(panel, recipe, years))
    card = summarize(est)
    base = baselines_for(recipe.multiple)
    for bid in ("industry_median", "bl_regression", "bl_peers"):
        c = compare(est, estimate(panel, base[bid], years))
        card[f"gain_vs_{bid}"] = c["mean_gain"]
        card[f"years_beating_{bid}"] = int(round(c["share_years_better"] * c["n_years"])) if c["n_years"] else 0
    card["yearly_median_abs_error"] = {int(y): float(v) for y, v in
                                       est.dropna(subset=["estimate"]).groupby("fiscal_year")["abs_error"].median().items()}
    return card


# ---------------------------------------------------------------- prompts

def dsl_text(panel_cols: set[str]) -> str:
    feats = "\n".join(f"  - {f}: {FEATURE_NOTES.get(f, '')}" for f in FEATURES if f in panel_cols)
    return f"""RECIPE LANGUAGE
A recipe is one firm-agnostic peer-selection rule. For every target firm in every year the
engine (1) takes all other firms in the same fiscal year with a positive multiple (the target
itself is always excluded), (2) applies the hard screens in "filters", (3) if fewer than
"min_peers" survive, tries each "fallback" screen set in order, (4) ranks survivors by a
weighted distance on within-year z-scores of the "rank" features and keeps the "k" nearest,
(5) aggregates the peers' multiples with "agg" and multiplies by the target's own driver.

Fields
  multiple:   one of {MULTIPLES_IN_SCOPE}  (EV/EBITDA uses firms with positive EBITDA)
  filters:    list of screens, each either {{"same": GROUP}} or {{"band": {{"var": FEATURE, "width": number}}}}
              GROUP is one of {GROUPS_IN_DATA}  (2-, 3- and 4-digit SIC codes)
              a band keeps candidates whose feature is within ±width of the target's (raw units)
  rank:       {{FEATURE: positive weight, ...}}  (empty = no ranking; then k must be "all")
  k:          "all" or an integer 3-30
  agg:        one of {sorted(AGGREGATORS)}
  min_peers:  positive integer (default 3)
  fallback:   list of filter lists tried in order when too few peers survive

FEATURES (accounting only; ratio features are winsorized 1%/99% each year)
{feats}

HARD RULES
  - No market-based inputs (price, market cap, EV) for the target: they are the answer.
  - Missing feature values: a target missing ALL rank features gets no estimate; candidates
    missing a used rank feature are dropped. Low coverage is penalized by the selection rule.
"""


def memoryless_prompt(panel: pd.DataFrame, protocol: Protocol, k: int = 6) -> str:
    """Proposer brief without any archive or feedback (no-archive conditions).

    Identical for every generation and run, so independent draws from it can be shared
    between the 'no_archive' and 'neither' conditions (a paired design for the critic).
    """
    base = baseline_scores(panel, protocol)
    btxt = "\n".join(f"  {m}: " + "; ".join(f"{v['name']} median {v['median_abs_error']:.3f}, mean {v['mean_abs_error']:.3f}"
                                            for v in d.values()) for m, d in base.items())
    return f"""You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly {k} recipes. Accuracy is the median of |ln(V_est / V)| across firm-years, where V
is the firm's actual enterprise value on June 30 after its fiscal year. Lower is better. Recipes
are scored on exploration years FY{protocol.explore[0]}-{protocol.explore[-1]}; the best ones will later be tested ONCE on
later years you will never see, so prefer rules with a clear economic reason over fragile tweaks.
Cover both multiples across your proposals.

{dsl_text(set(panel.columns))}
BASELINES (exploration years)
{btxt}

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{{"proposals": [{{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {{"multiple": "...", "filters": [...], "rank": {{...}}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}}}]}}
"""


def proposer_prompt(run: Run, panel: pd.DataFrame, generation: int) -> str:
    cfg, proto = run.config, run.protocol()
    if not cfg.get("archive_to_proposer", True):
        return memoryless_prompt(panel, proto, cfg["proposals_per_generation"])
    k = cfg["proposals_per_generation"]
    base = baseline_scores(panel, proto)
    btxt = "\n".join(f"  {m}: " + "; ".join(f"{v['name']} median {v['median_abs_error']:.3f}, mean {v['mean_abs_error']:.3f}"
                                           for v in d.values()) for m, d in base.items())
    arch = run.archive("agent")
    graded = [a for a in arch if a["status"] == "graded"]
    graded.sort(key=lambda a: (a["multiple"], a["explore"]["median_abs_error"]))
    lines = []
    for a in graded:
        e = a["explore"]
        lines.append(f"  [{a['id']}] {a['multiple']} median {e['median_abs_error']:.3f} | mean {e['mean_abs_error']:.3f} | "
                     f"coverage {e['coverage']:.1%} | beats industry {e['years_beating_industry_median']}/4 yrs | "
                     f"gain vs industry {e['gain_vs_industry_median']:+.3f}\n      {a['compact']}\n      mechanism: {a['mechanism']}")
    failed = [a for a in arch if a["status"] != "graded"]
    flines = [f"  [{a['id']}] {a['status']}: {a.get('reason', '')[:200]}" for a in failed[-15:]]
    return f"""You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly {k} NEW recipes (generation {generation}). Accuracy is the median of |ln(V_est / V)|
across firm-years, where V is the firm's actual enterprise value on June 30 after its fiscal year.
Lower is better. Recipes are scored only on exploration years FY{proto.explore[0]}-{proto.explore[-1]}; the
best ones will later be tested ONCE on later years you will never see, so prefer rules with a
clear economic reason over fragile tweaks. Cover both multiples across your proposals.

{dsl_text(set(panel.columns))}
BASELINES (exploration years)
{btxt}

ARCHIVE: your earlier graded attempts, exploration scores only ({len(graded)} graded)
{chr(10).join(lines) if lines else "  (none yet)"}

FAILED OR REJECTED ATTEMPTS (most recent)
{chr(10).join(flines) if flines else "  (none)"}

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
{"A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by" + chr(10) + "an independent referee, who sees your mechanism but no scores." + chr(10) if cfg.get("critic", True) else ""}
Reply with ONLY this JSON, no other text:
{{"proposals": [{{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {{"multiple": "...", "filters": [...], "rank": {{...}}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}}}]}}
"""


def critic_prompt(run: Run, panel: pd.DataFrame, pending: list[dict]) -> str:
    arch = run.archive("agent")
    tried = "\n".join(f"  [{a['id']}] {a['compact']}" for a in arch if a["status"] in ("graded", "rejected")) or "  (none)"
    props = "\n\n".join(f"  ({i}) {p['name']}\n      recipe: {p['compact']}\n      mechanism: {p['mechanism']}\n      prediction: {p['prediction']}"
                        for i, p in enumerate(pending))
    return f"""You are an independent referee for a valuation research project. A proposer has submitted
comps recipes. You decide which may be tested. You do NOT see any results, and you must not try
to find any: judge only the logic.

{dsl_text(set(panel.columns))}
Approve a proposal only if ALL hold:
  1. The mechanism is a specific, economically sensible reason why the selected peers should
     trade at a similar multiple to the target.
  2. The recipe actually implements that mechanism (the screens and rank features match it).
  3. It is not a trivial variant of a recipe already tried (listed below): changing only k by a
     few, one weight slightly, or the aggregator alone is trivial; a new feature, screen or
     economic idea is not.
  4. The prediction is falsifiable.
Reject otherwise, with a one-sentence reason the proposer can learn from.

RECIPES ALREADY TRIED (no scores shown)
{tried}

PROPOSALS
{props}

Reply with ONLY this JSON, no other text:
{{"verdicts": [{{"index": 0, "verdict": "approve" or "reject", "reason": "..."}}]}}
"""


# ---------------------------------------------------------------- loop steps

def parse_json_reply(text: str) -> dict:
    """Accept a raw JSON reply, tolerating code fences or stray text around it."""
    s = text.strip()
    if "```" in s:
        s = s.split("```")[1]
        s = s[4:] if s.startswith("json") else s
    i, j = s.find("{"), s.rfind("}")
    return json.loads(s[i:j + 1])


def register_proposals(run: Run, panel: pd.DataFrame, reply: dict, generation: int, proposer: str) -> list[dict]:
    """Validate and de-duplicate proposals; invalid/duplicate ones are archived immediately."""
    known = {a["hash"] for a in run.archive("agent") if a.get("hash")}
    n0 = len(run.archive("agent"))
    pending, cols = [], set(panel.columns)
    for i, p in enumerate(reply.get("proposals", [])):
        rid = f"g{generation:02d}-{i + 1:02d}"
        rec = {"id": rid, "generation": generation, "proposer": proposer,
               "time": datetime.now().isoformat(timespec="seconds"),
               "name": p.get("name", ""), "mechanism": p.get("mechanism", ""), "prediction": p.get("prediction", ""),
               "raw": p.get("recipe")}
        try:
            spec = dict(p.get("recipe") or {})
            spec["name"] = p.get("name") or rid
            r = validate(spec, cols)
            if r.multiple not in MULTIPLES_IN_SCOPE:
                raise RecipeError(f"multiple must be one of {MULTIPLES_IN_SCOPE}")
        except (RecipeError, TypeError, ValueError, AttributeError) as e:
            run.append({**rec, "status": "invalid", "reason": str(e)})
            continue
        h = spec_hash(r)
        rec.update(hash=h, multiple=r.multiple, spec=r.to_dict(), compact=compact(r))
        if h in known:
            run.append({**rec, "status": "duplicate", "reason": "identical to an archived recipe"})
            continue
        known.add(h)
        pending.append(rec)
    (run.gen_dir(generation) / "pending.json").write_text(json.dumps(pending, indent=1))
    return pending


def apply_verdicts(run: Run, panel: pd.DataFrame, reply: dict, generation: int) -> list[dict]:
    """Archive rejected proposals and grade approved ones on exploration years."""
    pending = json.loads((run.gen_dir(generation) / "pending.json").read_text())
    if reply is None:  # no-critic conditions: every valid proposal is graded
        reply = {"verdicts": [{"index": i, "verdict": "approve", "reason": "(no critic in this condition)"} for i in range(len(pending))]}
    verdicts = {int(v["index"]): v for v in reply.get("verdicts", [])}
    years = run.protocol().years("explore")
    out = []
    for i, rec in enumerate(pending):
        v = verdicts.get(i, {"verdict": "reject", "reason": "no verdict returned"})
        rec = {**rec, "critic": v.get("verdict"), "critic_reason": v.get("reason", "")}
        if str(v.get("verdict", "")).lower() != "approve":
            rec.update(status="rejected", reason="critic: " + v.get("reason", ""))
        else:
            r = validate(rec["spec"], set(panel.columns))
            rec.update(status="graded", explore=grade_period(panel, r, years))
        run.append(rec)
        out.append(rec)
    return out


# ---------------------------------------------------------------- random-search control

def random_recipe(rng: random.Random, multiple: str) -> dict:
    """A valid recipe drawn at random from the same language (the luck benchmark)."""
    screens = [[], [{"same": "industry_l2"}], [{"same": "industry_l3"}], [{"same": "industry_l4"}]]
    filters = list(rng.choice(screens))
    feats = rng.sample(FEATURES, rng.choice([1, 2, 2, 3]))
    w = [rng.random() + 0.1 for _ in feats]
    rank = {f: round(x / sum(w), 2) for f, x in zip(feats, w)}
    if rng.random() < 0.2:
        bvar = rng.choice(["ebitda_margin", "sales_growth_1y", "log_sales", "roic", "debt_to_assets"])
        filters.append({"band": {"var": bvar, "width": {"log_sales": 1.0}.get(bvar, 0.1)}})
    fallback = []
    if filters:
        fallback = [[{"same": "industry_l2"}]] if {"same": "industry_l2"} not in filters else [[]]
    return {"name": "random", "multiple": multiple, "filters": filters, "rank": rank,
            "k": rng.randint(3, 20), "agg": rng.choice(sorted(AGGREGATORS)), "min_peers": 3, "fallback": fallback}


def run_random(run: Run, panel: pd.DataFrame, n: int, seed: int = 7) -> None:
    rng, years = random.Random(seed), run.protocol().years("explore")
    have = len(run.archive("random"))
    for i in range(have, n):
        m = MULTIPLES_IN_SCOPE[i % 2]
        spec = random_recipe(rng, m)
        spec["name"] = f"random-{i + 1:03d}"
        r = validate(spec, set(panel.columns))
        run.append({"id": spec["name"], "status": "graded", "multiple": m, "hash": spec_hash(r),
                    "spec": r.to_dict(), "compact": compact(r), "explore": grade_period(panel, r, years)}, "random")


# ---------------------------------------------------------------- selection and validation

def eligible(rec: dict, rule: dict) -> bool:
    e = rec.get("explore") or {}
    return (rec.get("status") == "graded" and e.get("coverage", 0) >= rule["min_coverage"]
            and e.get("years_beating_industry_median", 0) >= rule["min_years_beating_industry"])


def select(records: list[dict], rule: dict) -> dict[str, list[dict]]:
    out = {}
    for m in MULTIPLES_IN_SCOPE:
        pool = sorted((r for r in records if r.get("multiple") == m and eligible(r, rule)),
                      key=lambda r: r["explore"]["median_abs_error"])
        out[m] = pool[: rule["top_n_per_multiple"]]
    return out


def finalize(run: Run, panel: pd.DataFrame, hand_recipes: list[dict]) -> dict:
    """Freeze finalists by the pre-set rule, then grade them on validation years once."""
    sealed = run.dir / "final.json"
    if sealed.exists():
        return json.loads(sealed.read_text())
    cfg, proto = run.config, run.protocol()
    rule = cfg["selection_rule"]
    agent, rnd = run.archive("agent"), run.archive("random")
    chosen = {"agent": select(agent, rule), "random": select(rnd, rule)}
    frozen_at = datetime.now().isoformat(timespec="seconds")
    vyears = proto.years("validate")
    res = {"frozen_at": frozen_at, "rule": rule, "multiples": {}}
    for m in MULTIPLES_IN_SCOPE:
        rows = []
        for src in ("agent", "random"):
            for rec in chosen[src][m]:
                r = validate(rec["spec"], set(panel.columns))
                rows.append({"source": src, "id": rec["id"], "name": rec.get("name") or rec["id"],
                             "mechanism": rec.get("mechanism"), "compact": rec["compact"], "spec": rec["spec"],
                             "explore": rec["explore"], "validate": grade_period(panel, r, vyears)})
        for s in hand_recipes:
            if s["multiple"] != m:
                continue
            r = validate(s, set(panel.columns))
            rows.append({"source": "hand", "id": s["name"], "name": s["name"], "mechanism": s.get("mechanism"),
                         "compact": compact(r), "spec": r.to_dict(),
                         "explore": grade_period(panel, r, proto.years("explore")),
                         "validate": grade_period(panel, r, vyears)})
        for bid, b in baselines_for(m).items():
            rows.append({"source": "baseline", "id": bid, "name": b.name,
                         "explore": {k: v for k, v in summarize(estimate(panel, b, proto.years("explore"))).items()},
                         "validate": {k: v for k, v in summarize(estimate(panel, b, vyears)).items()}})
        res["multiples"][m] = rows
    res["funnel"] = funnel(agent)
    res["random_pool"] = {"n": len(rnd), "n_eligible": sum(eligible(r, rule) for r in rnd)}
    sealed.write_text(json.dumps(res, indent=1, default=float))
    return res


def funnel(arch: list[dict]) -> dict:
    n = len(arch)
    count = lambda s: sum(a["status"] == s for a in arch)  # noqa: E731
    return {"proposed": n, "invalid": count("invalid"), "duplicate": count("duplicate"),
            "rejected_by_critic": count("rejected"), "graded": count("graded")}


def best_of_random(rnd: list[dict], multiple: str, n: int, rule: dict, draws: int = 2000, seed: int = 11) -> dict:
    """Distribution of the best exploration error when picking from n random recipes."""
    pool = [r for r in rnd if r["multiple"] == multiple]
    if not pool or n <= 0:
        return {}
    rng = np.random.default_rng(seed)
    errs = np.array([r["explore"]["median_abs_error"] if eligible(r, rule) else np.inf for r in pool])
    best = []
    for _ in range(draws):
        s = errs[rng.integers(0, len(errs), n)]
        best.append(s.min())
    best = np.array(best)
    best = best[np.isfinite(best)]
    return {"n": n, "median": float(np.median(best)), "p05": float(np.quantile(best, 0.05)),
            "p95": float(np.quantile(best, 0.95))} if len(best) else {}
