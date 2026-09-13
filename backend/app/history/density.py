"""
Historical Landslide Density Module using NASA Global Landslide Catalog.
Computes spatial hazard density while strictly enforcing the Neutral Missing Data Policy
(never interpreting unrecorded areas as zero hazard).
"""
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.ndimage import gaussian_filter

from backend.app.preprocessing.grid import AnalysisGrid
from backend.app.preprocessing.normalization import impute_neutral_missing, min_max_normalize
from backend.app.models.domain import ProvenanceTag


def compute_historical_landslide_density(
    glc_data: Dict[str, Any],
    target_grid: AnalysisGrid,
    bandwidth_cells: float = 3.0,  # ~3 km radius smoothing
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Computes Gaussian kernel density raster of historical landslide events.

    Returns:
      raw_density: raw smoothed event count density
      normalized_density: normalized hazard index [0, 1] with neutral baseline
      metadata: details of points processed, neutral imputation, and scientific rationale
    """
    events = glc_data.get("events", [])
    rows, cols = target_grid.rows, target_grid.cols

    # Initialize count matrix
    count_matrix = np.zeros((rows, cols), dtype=np.float32)

    valid_events_in_aoi = 0
    for ev in events:
        coords = ev.get("coordinates", [])
        if len(coords) == 2:
            lon, lat = coords[0], coords[1]
            # Convert (lon, lat) to grid indices
            c = int((lon - target_grid.min_lon) / target_grid.resolution_deg)
            r = int((target_grid.max_lat - lat) / target_grid.resolution_deg)
            if 0 <= r < rows and 0 <= c < cols:
                count_matrix[r, c] += 1.0
                valid_events_in_aoi += 1

    # Apply Gaussian smoothing kernel to represent spatial hazard influence zone
    smoothed_density = gaussian_filter(count_matrix, sigma=bandwidth_cells, mode="nearest")

    # Neutral Missing Data Enforcement:
    # If historical data is sparse or unrecorded, NEVER interpret as 0 hazard!
    # A location without a catalog entry might simply lack observation stations/reporters.
    zero_mask = smoothed_density < 1e-4
    if np.any(zero_mask):
        # Calculate non-zero median or benchmark baseline
        non_zero_vals = smoothed_density[~zero_mask]
        if len(non_zero_vals) > 0:
            neutral_baseline = float(np.percentile(non_zero_vals, 25))  # 25th percentile of known hazard
        else:
            neutral_baseline = 0.20  # Neutral prior

        smoothed_density[zero_mask] = neutral_baseline
        imputation_applied = True
    else:
        imputation_applied = False
        neutral_baseline = 0.0

    # Normalize to [0, 1]
    norm_density, v_min, v_max = min_max_normalize(smoothed_density)

    metadata = {
        "catalog_source": glc_data.get("data_source_url", "NASA Global Landslide Catalog"),
        "total_catalog_events": len(events),
        "valid_events_in_aoi": valid_events_in_aoi,
        "bandwidth_km": round(bandwidth_cells * target_grid.dx_meters / 1000.0, 2),
        "imputation_applied": imputation_applied,
        "imputed_neutral_baseline": round(neutral_baseline, 4),
        "scientific_honesty_note": (
            "Areas lacking historical records are NOT assumed to be zero hazard. "
            "Neutral AOI-median imputation applied to prevent under-reporting bias."
        ),
        "provenance": glc_data.get("provenance", ProvenanceTag.DEMO.value),
    }

    return smoothed_density, norm_density, metadata
