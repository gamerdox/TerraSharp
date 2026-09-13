"""
Soil-Saturation Proxy Module.
IMPORTANT: Strictly labeled as PROXY derived from 3-day and 15-day antecedent precipitation.
Does NOT claim direct in-situ or direct satellite microwave radiometer observation.
"""
from typing import Dict, Any, Tuple
import numpy as np

from backend.app.models.domain import ProvenanceTag


def compute_soil_saturation_proxy(
    rainfall_3d: np.ndarray,
    rainfall_15d: np.ndarray,
    saturation_capacity_mm: float = 380.0,
    decay_constant: float = 0.08,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Computes Antecedent Moisture Index (AMI) proxy for soil saturation.

    Formula:
      AMI = (0.60 * R_3d + 0.40 * R_15d * exp(-decay * 12)) / saturation_capacity_mm

    Returns:
      soil_saturation_proxy: 2D array normalized to [0.0, 1.0]
      metadata: transparent proxy provenance and scientific caveats
    """
    decay_factor = np.exp(-decay_constant * 12.0)
    raw_ami = 0.60 * rainfall_3d + 0.40 * (rainfall_15d * decay_factor)

    # Normalize to [0, 1] relative to saturation capacity
    soil_proxy = np.clip(raw_ami / saturation_capacity_mm, 0.0, 1.0).astype(np.float32)

    metadata = {
        "provenance": ProvenanceTag.PROXY.value,
        "indicator_name": "ANTECEDENT_SOIL_SATURATION_PROXY",
        "saturation_capacity_threshold_mm": saturation_capacity_mm,
        "decay_constant": decay_constant,
        "mean_saturation_proxy": round(float(np.mean(soil_proxy)), 3),
        "max_saturation_proxy": round(float(np.max(soil_proxy)), 3),
        "high_saturation_cells_pct": round(float(np.sum(soil_proxy > 0.70) / soil_proxy.size * 100), 2),
        "scientific_honesty_disclaimer": (
            "CRITICAL: This layer is an Antecedent Moisture Proxy derived mathematically "
            "from 3-day and 15-day GPM IMERG rainfall accumulation with exponential drainage decay. "
            "It is NOT a direct in-situ soil moisture sensor reading or SMAP/SMOS satellite radiometer measurement."
        ),
    }

    return soil_proxy, metadata
