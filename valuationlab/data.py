"""Load the FactSet panel with a local cache (rebuilt when any raw export changes).

Only data/raw/ is read; the sealed holdout folder is never touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .factset import read_exports
from .panel import build_panel


def load_panel(root: Path) -> pd.DataFrame:
    files = sorted((root / "data/raw").glob("factset_20*.xlsx"))
    files = [f for f in files if not f.name.startswith("~$")]
    sig = json.dumps([[f.name, f.stat().st_mtime, f.stat().st_size] for f in files])
    cache = root / "data/cache"
    cache.mkdir(parents=True, exist_ok=True)
    pkl, meta = cache / "panel.pkl", cache / "panel.sig"
    if pkl.exists() and meta.exists() and meta.read_text() == sig:
        return pd.read_pickle(pkl)
    raw, _ = read_exports(files, root / "config/factset_columns.json")
    panel = build_panel(raw)
    panel.to_pickle(pkl)
    meta.write_text(sig)
    return panel
