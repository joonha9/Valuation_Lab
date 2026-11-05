"""Load the FactSet panel with a local cache (rebuilt when any raw export changes).

By default only data/raw/ is read and the sealed holdout folder is never touched.
`include_holdout=True` also reads data/holdout/ (FY2024-2025); only the one-time
holdout evaluation (scripts/holdout_eval.py --open) passes it, and it uses a
separate cache file so the everyday panel never contains holdout rows.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .factset import read_exports
from .panel import build_panel


def _exports(folder: Path) -> list[Path]:
    return [f for f in sorted(folder.glob("factset_20*.xlsx")) if not f.name.startswith("~$")]


def load_panel(root: Path, include_holdout: bool = False) -> pd.DataFrame:
    files = _exports(root / "data/raw")
    if include_holdout:
        files += _exports(root / "data/holdout")
    sig = json.dumps([[f.name, f.stat().st_mtime, f.stat().st_size] for f in files])
    cache = root / "data/cache"
    cache.mkdir(parents=True, exist_ok=True)
    stem = "panel_with_holdout" if include_holdout else "panel"
    pkl, meta = cache / f"{stem}.pkl", cache / f"{stem}.sig"
    if pkl.exists() and meta.exists() and meta.read_text() == sig:
        return pd.read_pickle(pkl)
    raw, _ = read_exports(files, root / "config/factset_columns.json")
    panel = build_panel(raw)
    panel.to_pickle(pkl)
    meta.write_text(sig)
    return panel
