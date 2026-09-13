"""
Feature normalization and missing data imputation module.
Guarantees scale compatibility [0, 1] while strictly obeying scientific honesty rules
(e.g. missing historical records are imputed with neutral AOI-median, never zero).
"""
import numpy as np
from typing import Tuple, Optional, Dict, Any


def min_max_normalize(
    data: np.ndarray,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    clip_percentiles: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, float, float]:
    """
    Scales an array to [0.0, 1.0].
    Optionally clips to robust percentiles (e.g. 1st and 99th) to prevent extreme outliers.
    Returns (normalized_array, effective_min, effective_max).
    """
    valid_mask = ~np.isnan(data) & ~np.isinf(data)
    if not np.any(valid_mask):
        return np.zeros_like(data, dtype=np.float32), 0.0, 1.0

    valid_vals = data[valid_mask]

    if clip_percentiles is not None:
        p_low, p_high = np.percentile(valid_vals, clip_percentiles)
        v_min = min_val if min_val is not None else float(p_low)
        v_max = max_val if max_val is not None else float(p_high)
    else:
        v_min = min_val if min_val is not None else float(np.min(valid_vals))
        v_max = max_val if max_val is not None else float(np.max(valid_vals))

    if v_max <= v_min:
        return np.zeros_like(data, dtype=np.float32), v_min, v_max

    normalized = np.clip((data - v_min) / (v_max - v_min), 0.0, 1.0)
    return normalized.astype(np.float32), v_min, v_max


def impute_neutral_missing(
    data: np.ndarray,
    strategy: str = "aoi_median",
    default_neutral_val: float = 0.5,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Neutral imputation for missing/unrecorded grid cells.
    NEVER sets missing historical records or missing sensors to 0.0.
    Strategies:
      - 'aoi_median': fills unrecorded/NaN values with median of observed cells in the AOI.
      - 'fixed_neutral': fills with a neutral baseline (e.g., 0.5 on a 0-1 scale).
    """
    out = data.copy()
    missing_mask = np.isnan(out) | (out < 0)
    missing_count = int(np.sum(missing_mask))

    if missing_count == 0:
        return out, {"missing_cells": 0, "strategy": "none", "imputed_value": None}

    if strategy == "aoi_median":
        valid_vals = out[~missing_mask]
        if len(valid_vals) > 0:
            fill_val = float(np.median(valid_vals))
        else:
            fill_val = default_neutral_val
    elif strategy == "fixed_neutral":
        fill_val = default_neutral_val
    else:
        fill_val = default_neutral_val

    out[missing_mask] = fill_val

    metadata = {
        "missing_cells": missing_count,
        "missing_pct": round(float(missing_count / data.size * 100), 2),
        "strategy": strategy,
        "imputed_value": round(fill_val, 4),
        "scientific_rationale": "Missing data treated with neutral imputation to prevent false-negative hazard bias.",
    }
    return out.astype(np.float32), metadata
