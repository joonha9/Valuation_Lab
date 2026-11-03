"""Comps recipe schema and deterministic validator.

A recipe is a firm-agnostic peer-selection rule. The same recipe is applied to
every target firm-year by the engine. Example:

    {
      "name": "growth-stage peers",
      "multiple": "EV/EBITDA",
      "filters": [{"same": "industry_l3"},
                  {"band": {"var": "sales_growth_3y", "width": 0.05}}],
      "rank": {"ebitda_margin": 0.5, "roic": 0.3, "log_sales": 0.2},
      "k": 8,
      "agg": "median",
      "min_peers": 3,
      "fallback": [[{"same": "industry_l3"}], [{"same": "industry_l2"}]]
    }

Fields
- multiple: which multiple to apply (see panel.MULTIPLES).
- filters: hard screens. `same` keeps candidates in the target's group;
  `band` keeps candidates whose feature is within +/- width of the target's.
- rank: weighted nearest-neighbour distance on standardized features. Empty
  means no ranking: every screened candidate is a peer.
- k: number of nearest peers, or "all". A fixed k requires a rank.
- agg: how peer multiples are combined.
- min_peers: if fewer peers survive the filters, try each fallback filter set
  in order. If all fail, the target gets no estimate (counts against coverage).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .panel import FEATURES, MARKET_COLUMNS, MULTIPLES

GROUP_COLUMNS = {
    "industry_l1", "industry_l2", "industry_l3", "industry_l4",
    "industry_l5", "industry_l6",
    "gics_sector", "gics_industry", "sic2", "sic3", "sic4",
}
AGGREGATORS = {"median", "harmonic_mean", "mean", "trimmed_mean"}
K_RANGE = (3, 30)


class RecipeError(ValueError):
    """Raised when a recipe violates the schema. Message lists every problem."""


@dataclass(frozen=True)
class Recipe:
    name: str
    multiple: str
    filters: tuple[dict, ...] = ()
    rank: dict[str, float] = field(default_factory=dict)
    k: int | str = "all"
    agg: str = "median"
    min_peers: int = 3
    fallback: tuple[tuple[dict, ...], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "multiple": self.multiple,
            "filters": list(self.filters), "rank": dict(self.rank),
            "k": self.k, "agg": self.agg, "min_peers": self.min_peers,
            "fallback": [list(f) for f in self.fallback],
        }


def _check_filters(filters: Any, where: str, problems: list[str], panel_cols: set[str] | None) -> None:
    if not isinstance(filters, list):
        problems.append(f"{where}: must be a list")
        return
    for i, f in enumerate(filters):
        tag = f"{where}[{i}]"
        if not isinstance(f, dict) or len(f) != 1:
            problems.append(f"{tag}: each filter is a one-key object ('same' or 'band')")
            continue
        (kind, arg), = f.items()
        if kind == "same":
            if arg not in GROUP_COLUMNS:
                problems.append(f"{tag}: 'same' must be one of {sorted(GROUP_COLUMNS)}")
            elif panel_cols is not None and arg not in panel_cols:
                problems.append(f"{tag}: classification '{arg}' is not in the data")
        elif kind == "band":
            if not isinstance(arg, dict) or set(arg) != {"var", "width"}:
                problems.append(f"{tag}: 'band' needs exactly {{'var', 'width'}}")
                continue
            _check_feature(arg["var"], tag, problems)
            if not isinstance(arg["width"], (int, float)) or arg["width"] <= 0:
                problems.append(f"{tag}: band width must be a positive number")
        else:
            problems.append(f"{tag}: unknown filter '{kind}'")


def _check_feature(var: Any, where: str, problems: list[str]) -> None:
    if var in MARKET_COLUMNS:
        problems.append(f"{where}: '{var}' is market-based; a target's own market value cannot be an input")
    elif var not in FEATURES:
        problems.append(f"{where}: unknown feature '{var}'")


def validate(spec: dict[str, Any], panel_cols: set[str] | None = None) -> Recipe:
    """Return a Recipe or raise RecipeError listing every violation."""
    problems: list[str] = []
    allowed_keys = {"name", "multiple", "filters", "rank", "k", "agg", "min_peers", "fallback",
                    "mechanism", "prediction", "rationale", "task", "short"}
    extra = set(spec) - allowed_keys
    if extra:
        problems.append(f"unknown keys: {sorted(extra)}")

    name = spec.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append("name: required non-empty string")

    multiple = spec.get("multiple")
    if multiple not in MULTIPLES:
        problems.append(f"multiple: must be one of {sorted(MULTIPLES)}")
    elif panel_cols is not None and MULTIPLES[multiple][1] not in panel_cols:
        problems.append(f"multiple: driver '{MULTIPLES[multiple][1]}' is not in the data")

    filters = spec.get("filters", [])
    _check_filters(filters, "filters", problems, panel_cols)

    rank = spec.get("rank", {})
    if not isinstance(rank, dict):
        problems.append("rank: must be an object of {feature: weight}")
        rank = {}
    for var, w in rank.items():
        _check_feature(var, f"rank.{var}", problems)
        if not isinstance(w, (int, float)) or w <= 0:
            problems.append(f"rank.{var}: weight must be a positive number")

    k = spec.get("k", "all")
    if k != "all" and not (isinstance(k, int) and K_RANGE[0] <= k <= K_RANGE[1]):
        problems.append(f"k: must be 'all' or an integer in {K_RANGE}")
    if k != "all" and not rank:
        problems.append("k: a fixed k needs a 'rank' to decide which peers are nearest")

    agg = spec.get("agg", "median")
    if agg not in AGGREGATORS:
        problems.append(f"agg: must be one of {sorted(AGGREGATORS)}")

    min_peers = spec.get("min_peers", 3)
    if not isinstance(min_peers, int) or min_peers < 1:
        problems.append("min_peers: must be a positive integer")

    fallback = spec.get("fallback", [])
    if not isinstance(fallback, list):
        problems.append("fallback: must be a list of filter lists")
        fallback = []
    for i, fset in enumerate(fallback):
        _check_filters(fset, f"fallback[{i}]", problems, panel_cols)

    if problems:
        raise RecipeError("; ".join(problems))

    return Recipe(
        name=name.strip(), multiple=multiple,
        filters=tuple(filters), rank=dict(rank), k=k, agg=agg, min_peers=min_peers,
        fallback=tuple(tuple(f) for f in fallback),
    )
