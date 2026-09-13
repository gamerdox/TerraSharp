"""
IMERG Rainfall Feature Extraction Module.
Computes 24h rainfall, 3-day and 15-day rolling accumulations, intensity, and rate of change.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

from backend.app.preprocessing.grid import AnalysisGrid
from backend.app.preprocessing.raster_ops import resample_raster_to_grid
from backend.app.preprocessing.normalization import min_max_normalize
from backend.app.models.domain import ProvenanceTag


class RainfallProcessor:
    def __init__(self, target_grid: AnalysisGrid):
        self.grid = target_grid

    def process_rainfall_series(
        self,
        rainfall_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Processes rainfall time-series rasters into standardized hazard feature grids.

        Returns:
          rainfall_24h: 2D array of most recent 24h precipitation (mm)
          rainfall_3d: 2D array of 3-day accumulated precipitation (mm)
          rainfall_15d: 2D array of 15-day accumulated precipitation (mm)
          intensity_mm_hr: 2D array of current rainfall intensity (mm/hr)
          trend_alpha: estimated rate of increase dI/dt (mm/hr^2)
          normalized feature grids [0, 1]
          metadata
        """
        series = rainfall_data.get("daily_series", [])
        if not series:
            raise ValueError("No daily rainfall records provided in rainfall series.")

        # Resample all daily rasters to target grid
        daily_grids = []
        for entry in series:
            raster_path = entry.get("raster_path")
            if not raster_path or not Path(raster_path).exists():
                raise FileNotFoundError(f"Rainfall raster not found: {raster_path}")
            grid_arr = resample_raster_to_grid(raster_path, self.grid, nodata_fill=0.0)
            daily_grids.append(grid_arr)

        daily_stack = np.stack(daily_grids, axis=0)  # Shape: (T, Rows, Cols)
        num_days = daily_stack.shape[0]

        # 1. Recent 24h rainfall
        rainfall_24h = daily_stack[-1].copy()

        # 2. 3-day accumulation (last 3 days)
        window_3d = min(3, num_days)
        rainfall_3d = np.sum(daily_stack[-window_3d:], axis=0)

        # 3. 15-day accumulation (up to 15 days)
        window_15d = min(15, num_days)
        rainfall_15d = np.sum(daily_stack[-window_15d:], axis=0)

        # 4. Current intensity (mm/hr): either provided or derived from peak 24h / 24
        intensity_mm_hr = np.maximum(rainfall_24h / 24.0, 0.0)

        # 5. Trend (dI/dt): change in intensity between recent days (e.g. Day T vs Day T-2)
        if num_days >= 3:
            prev_intensity = daily_stack[-3] / 24.0
            dt_hours = 48.0
            trend_grid = (intensity_mm_hr - prev_intensity) / dt_hours
            trend_alpha = float(np.mean(trend_grid[trend_grid > 0])) if np.any(trend_grid > 0) else 0.0
        else:
            trend_alpha = rainfall_data.get("trend_alpha_mm_hr2", 0.5)

        # 6. Feature Normalization [0, 1]
        # Benchmark scale for extreme rainfall (e.g. Western Ghats / Himalayan cloudbursts):
        # 24h: 300 mm = 1.0 (extreme downpour)
        # 3d: 500 mm = 1.0
        # 15d: 1200 mm = 1.0
        r24_norm = np.clip(rainfall_24h / 250.0, 0.0, 1.0).astype(np.float32)
        r3d_norm = np.clip(rainfall_3d / 450.0, 0.0, 1.0).astype(np.float32)
        r15d_norm = np.clip(rainfall_15d / 1000.0, 0.0, 1.0).astype(np.float32)

        # Dynamic rainfall score: combination of peak 24h and short-term 3d
        rainfall_score = (0.60 * r24_norm + 0.40 * r3d_norm).astype(np.float32)

        provenance = rainfall_data.get("provenance", ProvenanceTag.DEMO.value)

        metadata = {
            "num_days_analyzed": num_days,
            "max_24h_mm": round(float(np.max(rainfall_24h)), 2),
            "mean_24h_mm": round(float(np.mean(rainfall_24h)), 2),
            "max_3d_mm": round(float(np.max(rainfall_3d)), 2),
            "max_15d_mm": round(float(np.max(rainfall_15d)), 2),
            "mean_intensity_mm_hr": round(float(np.mean(intensity_mm_hr)), 2),
            "trend_alpha_mm_hr2": round(float(trend_alpha), 4),
            "provenance": provenance,
            "data_source_url": rainfall_data.get("data_source_url", ""),
        }

        return {
            "rainfall_24h": rainfall_24h,
            "rainfall_3d": rainfall_3d,
            "rainfall_15d": rainfall_15d,
            "intensity_mm_hr": intensity_mm_hr,
            "trend_alpha": trend_alpha,
            "r24_norm": r24_norm,
            "r3d_norm": r3d_norm,
            "r15d_norm": r15d_norm,
            "rainfall_score": rainfall_score,
            "metadata": metadata,
        }
