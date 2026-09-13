"""
Terrain Slope & Aspect Computation using Horn's Finite-Difference Method.
Converts DEM elevation into terrain gradient in degrees and normalized hazard scores.
"""
from typing import Dict, Any, Tuple
import numpy as np
from scipy.ndimage import convolve

from backend.app.models.domain import ProvenanceTag


def compute_slope_and_aspect(
    elevation_grid: np.ndarray,
    dx_meters: float,
    dy_meters: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Computes slope (in degrees) and aspect (in degrees from North) from a 2D elevation grid.
    Uses Horn's (1981) 3x3 finite-difference algorithm.

    Returns:
      slope_deg: 2D array of slope in degrees [0, 90]
      aspect_deg: 2D array of aspect in degrees [0, 360)
      slope_norm: 2D array of normalized slope score [0, 1] (clipped at 60 deg)
      metadata: dictionary with terrain summary statistics
    """
    # Horn kernels for partial derivatives
    # dz/dx kernel:
    # [-1, 0, 1]
    # [-2, 0, 2]
    # [-1, 0, 1]
    kx = np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]], dtype=np.float32) / (8.0 * dx_meters)

    # dz/dy kernel (note y increases southwards in image coords, so negate for north-up):
    # [ 1,  2,  1]
    # [ 0,  0,  0]
    # [-1, -2, -1]
    ky = np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]], dtype=np.float32) / (8.0 * dy_meters)

    dz_dx = convolve(elevation_grid.astype(np.float32), kx, mode="nearest")
    dz_dy = convolve(elevation_grid.astype(np.float32), ky, mode="nearest")

    gradient_mag = np.sqrt(dz_dx**2 + dz_dy**2)
    slope_rad = np.arctan(gradient_mag)
    slope_deg = np.degrees(slope_rad)

    # Aspect: direction of steepest downslope
    # 0 = North, 90 = East, 180 = South, 270 = West
    aspect_rad = np.arctan2(-dz_dy, -dz_dx)
    aspect_deg = (450.0 - np.degrees(aspect_rad)) % 360.0

    # Normalization: slopes >= 55-60 deg reach maximum landslide hazard saturation
    max_hazard_slope = 55.0
    slope_norm = np.clip(slope_deg / max_hazard_slope, 0.0, 1.0).astype(np.float32)

    metadata = {
        "mean_slope_deg": round(float(np.mean(slope_deg)), 2),
        "max_slope_deg": round(float(np.max(slope_deg)), 2),
        "min_slope_deg": round(float(np.min(slope_deg)), 2),
        "steep_cells_pct": round(float(np.sum(slope_deg > 30.0) / slope_deg.size * 100), 2),
        "provenance": ProvenanceTag.DERIVED.value,
        "algorithm": "Horn (1981) 3x3 finite-difference",
    }

    return slope_deg, aspect_deg, slope_norm, metadata
