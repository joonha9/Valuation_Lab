"""Standard comps baselines every recipe is compared against."""

from __future__ import annotations

from .recipe import Recipe, validate
from .warranted import WarrantedBenchmark


def baselines_for(multiple: str) -> dict:
    """Practitioner defaults (market and industry median) and the academic
    warranted-multiple benchmarks of Bhojraj & Lee (2002)."""
    return {
        "market_median": validate({
            "name": "Market-wide median",
            "multiple": multiple,
            "filters": [],
            "k": "all",
            "agg": "median",
        }),
        "industry_median": validate({
            "name": "Industry median (L3, fallback L2)",
            "multiple": multiple,
            "filters": [{"same": "industry_l3"}],
            "k": "all",
            "agg": "median",
            "min_peers": 3,
            "fallback": [[{"same": "industry_l2"}]],
        }),
        "bl_regression": WarrantedBenchmark("Warranted multiple (Bhojraj-Lee regression)", multiple, "regression"),
        "bl_peers": WarrantedBenchmark("Warranted-multiple peers (Bhojraj-Lee, k=8)", multiple, "peers", 8),
    }
