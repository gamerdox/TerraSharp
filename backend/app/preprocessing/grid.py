"""
Analysis Grid Generator and CRS Normalization.
Establishes a uniform spatial analysis grid (~1km default or configurable)
across all data layers for a chosen AOI.
"""
from typing import Dict, Any, Tuple
import numpy as np
from affine import Affine
from shapely.geometry import box, Polygon
import pyproj

from backend.app.config import settings, BoundingBox


class AnalysisGrid:
    def __init__(
        self,
        bbox: BoundingBox,
        resolution_deg: float = 0.01,
        target_crs: str = "EPSG:4326",
        utm_epsg: int = 32643,
    ):
        self.bbox = bbox
        self.resolution_deg = resolution_deg
        self.target_crs = target_crs
        self.utm_epsg = utm_epsg

        # Calculate grid shape
        self.min_lon = bbox.min_lon
        self.min_lat = bbox.min_lat
        self.max_lon = bbox.max_lon
        self.max_lat = bbox.max_lat

        self.cols = int(np.ceil((self.max_lon - self.min_lon) / self.resolution_deg))
        self.rows = int(np.ceil((self.max_lat - self.min_lat) / self.resolution_deg))

        # Adjust max_lon / min_lat to fit exact integer cell count
        self.adjusted_max_lon = self.min_lon + self.cols * self.resolution_deg
        self.adjusted_min_lat = self.max_lat - self.rows * self.resolution_deg

        # Affine transform: maps pixel (col, row) to (lon, lat)
        self.transform = Affine(
            self.resolution_deg,
            0.0,
            self.min_lon,
            0.0,
            -self.resolution_deg,
            self.max_lat,
        )

        # 1D coordinate vectors (cell center coordinates)
        self.lons = self.min_lon + (np.arange(self.cols) + 0.5) * self.resolution_deg
        self.lats = self.max_lat - (np.arange(self.rows) + 0.5) * self.resolution_deg

        # 2D Meshgrids
        self.lon_grid, self.lat_grid = np.meshgrid(self.lons, self.lats)

        # Compute cell dimensions in meters using UTM projection
        self._compute_metric_cell_size()

    def _compute_metric_cell_size(self):
        proj_wgs84 = pyproj.CRS("EPSG:4326")
        proj_utm = pyproj.CRS(f"EPSG:{self.utm_epsg}")
        transformer = pyproj.Transformer.from_crs(proj_wgs84, proj_utm, always_xy=True)

        center_lon = (self.min_lon + self.max_lon) / 2.0
        center_lat = (self.min_lat + self.max_lat) / 2.0

        x0, y0 = transformer.transform(center_lon, center_lat)
        x1, y1 = transformer.transform(center_lon + self.resolution_deg, center_lat + self.resolution_deg)

        self.dx_meters = abs(x1 - x0)
        self.dy_meters = abs(y1 - y0)
        self.cell_area_sqkm = (self.dx_meters * self.dy_meters) / 1e6

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Returns (min_lon, min_lat, max_lon, max_lat)."""
        return (self.min_lon, self.adjusted_min_lat, self.adjusted_max_lon, self.max_lat)

    @property
    def geometry(self) -> Polygon:
        return box(*self.bounds)

    def get_info(self) -> Dict[str, Any]:
        return {
            "crs": self.target_crs,
            "utm_epsg": self.utm_epsg,
            "rows": self.rows,
            "cols": self.cols,
            "resolution_deg": self.resolution_deg,
            "approx_dx_meters": round(self.dx_meters, 2),
            "approx_dy_meters": round(self.dy_meters, 2),
            "approx_cell_area_sqkm": round(self.cell_area_sqkm, 4),
            "bounds": list(self.bounds),
        }
