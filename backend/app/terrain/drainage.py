"""
Drainage and Flow Accumulation Module using D8 Routing.
Computes hydrological flow accumulation to distinguish flash-flood prone valley funnels
from steep landslide slip zones.
"""
from typing import Dict, Any, Tuple
import numpy as np

from backend.app.models.domain import ProvenanceTag


def compute_d8_flow_accumulation(
    elevation: np.ndarray,
    dx_meters: float,
    dy_meters: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Computes D8 flow direction and upstream contributing flow accumulation.

    Returns:
      flow_accumulation: 2D array of upstream contributing cells (>= 1)
      flow_accum_norm: 2D array log-normalized to [0, 1]
      valley_bottom_norm: 2D array representing valley/channel concentration
      metadata: summary statistics
    """
    rows, cols = elevation.shape

    # 8 neighbor offsets: (dr, dc)
    # 0: E, 1: SE, 2: S, 3: SW, 4: W, 5: NW, 6: N, 7: NE
    neighbors = [
        (0, 1, dx_meters),
        (1, 1, np.hypot(dx_meters, dy_meters)),
        (1, 0, dy_meters),
        (1, -1, np.hypot(dx_meters, dy_meters)),
        (0, -1, dx_meters),
        (-1, -1, np.hypot(dx_meters, dy_meters)),
        (-1, 0, dy_meters),
        (-1, 1, np.hypot(dx_meters, dy_meters)),
    ]

    # Flow direction matrix: holds index of downstream target (target_r, target_c)
    # -1 indicates sink or boundary
    downstream_r = np.full((rows, cols), -1, dtype=np.int32)
    downstream_c = np.full((rows, cols), -1, dtype=np.int32)

    for r in range(rows):
        for c in range(cols):
            curr_z = elevation[r, c]
            max_slope = 0.0
            best_r, best_c = -1, -1

            for dr, dc, dist in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    drop = curr_z - elevation[nr, nc]
                    slope = drop / dist
                    if slope > max_slope:
                        max_slope = slope
                        best_r, best_c = nr, nc

            downstream_r[r, c] = best_r
            downstream_c[r, c] = best_c

    # Flow accumulation: Sort cells by descending elevation
    flat_indices = np.argsort(-elevation.ravel())
    sorted_coords = np.unravel_index(flat_indices, (rows, cols))

    # Every cell starts with 1 unit of runoff (itself)
    flow_accum = np.ones((rows, cols), dtype=np.float32)

    for r, c in zip(sorted_coords[0], sorted_coords[1]):
        tgt_r = downstream_r[r, c]
        tgt_c = downstream_c[r, c]
        if tgt_r != -1 and tgt_c != -1:
            flow_accum[tgt_r, tgt_c] += flow_accum[r, c]

    # Log-transform for normalization since accumulation spans orders of magnitude
    log_accum = np.log10(flow_accum)
    max_log = np.max(log_accum)
    min_log = np.min(log_accum)

    if max_log > min_log:
        flow_accum_norm = (log_accum - min_log) / (max_log - min_log)
    else:
        flow_accum_norm = np.zeros_like(flow_accum, dtype=np.float32)

    flow_accum_norm = np.clip(flow_accum_norm, 0.0, 1.0).astype(np.float32)

    metadata = {
        "max_accumulation_cells": int(np.max(flow_accum)),
        "mean_accumulation_cells": round(float(np.mean(flow_accum)), 2),
        "major_drainage_cells_pct": round(float(np.sum(flow_accum > 50) / flow_accum.size * 100), 2),
        "provenance": ProvenanceTag.DERIVED.value,
        "algorithm": "D8 hydrological flow routing (O'Callaghan & Mark 1984)",
    }

    return flow_accum, flow_accum_norm, metadata
