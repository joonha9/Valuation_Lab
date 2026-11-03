"""Deterministic comps engine.

For each target firm-year the engine
  1. builds the candidate pool: same fiscal year, valid positive multiple,
     target itself excluded (otherwise the estimate would contain the answer);
  2. applies the recipe's filters (then each fallback set if too few peers);
  3. keeps the k nearest candidates on the recipe's weighted, standardized
     features;
  4. aggregates the peer multiples and multiplies by the target's driver.

The engine never reads a target's own market value except to compute the
error afterwards, in grader.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .panel import MULTIPLES
from .recipe import Recipe


def _aggregate(values: np.ndarray, how: str) -> float:
    if how == "median":
        return float(np.median(values))
    if how == "mean":
        return float(np.mean(values))
    if how == "harmonic_mean":
        return float(len(values) / np.sum(1.0 / values))
    if how == "trimmed_mean":
        v = np.sort(values)
        cut = int(len(v) * 0.10)
        return float(np.mean(v[cut: len(v) - cut] if len(v) - 2 * cut > 0 else v))
    raise ValueError(how)


def _filter_mask(year: pd.DataFrame, cols: dict[str, np.ndarray], i: int, filters: tuple[dict, ...]) -> np.ndarray:
    mask = np.ones(len(year), dtype=bool)
    for f in filters:
        (kind, arg), = f.items()
        if kind == "same":
            col = cols[arg]
            target = col[i]
            if pd.isna(target):
                return np.zeros(len(year), dtype=bool)
            mask &= col == target
        else:  # band
            x = cols[arg["var"]]
            if np.isnan(x[i]):
                return np.zeros(len(year), dtype=bool)
            mask &= np.abs(x - x[i]) <= arg["width"]  # NaN candidates drop out
    return mask


def apply_recipe(panel: pd.DataFrame, recipe: Recipe, years: list[int] | None = None,
                 keep_peers: bool = False) -> pd.DataFrame:
    """Return one row per eligible target firm-year with the recipe's estimate.

    Columns: id, fiscal_year, actual, estimate, peer_multiple, n_peers,
    fallback_level (0 = primary filters, -1 = no estimate), and peers (list of
    peer ids) when keep_peers is True.
    """
    value_col, driver_col = MULTIPLES[recipe.multiple]
    data = panel if years is None else panel[panel["fiscal_year"].isin(years)]
    data = data[(data[value_col] > 0) & (data[driver_col] > 0)].copy()
    data["multiple"] = data[value_col] / data[driver_col]
    data = data[np.isfinite(data["multiple"])]

    filter_sets = (recipe.filters,) + recipe.fallback
    group_cols = {f["same"] for fs in filter_sets for f in fs if "same" in f}
    band_cols = {f["band"]["var"] for fs in filter_sets for f in fs if "band" in f}
    rank_vars = list(recipe.rank)
    weights = np.array([recipe.rank[v] for v in rank_vars], dtype=float)

    out = []
    for fy, year in data.groupby("fiscal_year", sort=True):
        year = year.sort_values("id").reset_index(drop=True)  # stable tie-breaking
        n = len(year)
        cols = {c: year[c].to_numpy() for c in group_cols}
        cols.update({c: year[c].to_numpy(dtype=float) for c in band_cols})
        mult = year["multiple"].to_numpy(dtype=float)
        driver = year[driver_col].to_numpy(dtype=float)
        ids = year["id"].to_numpy()

        # Standardize rank features within the year (z-scores).
        if rank_vars:
            z = np.column_stack([
                ((year[v] - year[v].mean()) / year[v].std(ddof=0)).to_numpy(dtype=float)
                for v in rank_vars
            ])

        for i in range(n):
            peers_idx = None
            level = -1
            for lvl, fs in enumerate(filter_sets):
                mask = _filter_mask(year, cols, i, fs)
                mask[i] = False
                if rank_vars:
                    use = ~np.isnan(z[i])
                    if not use.any():
                        break  # target lacks every ranking feature: no estimate
                    zc = z[:, use]
                    mask &= ~np.isnan(zc).any(axis=1)
                if mask.sum() < recipe.min_peers:
                    continue
                cand = np.flatnonzero(mask)
                if rank_vars and recipe.k != "all":
                    d = np.sqrt(((zc[cand] - zc[i]) ** 2 * weights[use]).sum(axis=1))
                    cand = cand[np.argsort(d, kind="stable")[: recipe.k]]
                peers_idx, level = cand, lvl
                break

            row = {"id": ids[i], "fiscal_year": fy, "actual": year.at[i, value_col],
                   "fallback_level": level}
            if peers_idx is None:
                row.update(estimate=np.nan, peer_multiple=np.nan, n_peers=0)
            else:
                pm = _aggregate(mult[peers_idx], recipe.agg)
                row.update(estimate=pm * driver[i], peer_multiple=pm, n_peers=len(peers_idx))
            if keep_peers:
                row["peers"] = [] if peers_idx is None else ids[peers_idx].tolist()
            out.append(row)

    return pd.DataFrame(out)
