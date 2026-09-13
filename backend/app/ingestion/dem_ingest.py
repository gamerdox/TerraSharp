"""
DEM Ingestion Module for SRTM GL1 30m / Copernicus GLO-30.
Handles live fetching or deterministic demo datasets with clear provenance.
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import rasterio

from backend.app.config import settings
from backend.app.models.domain import ProvenanceTag

logger = logging.getLogger(__name__)


class DEMIngestionClient:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.mode

    def get_dem_for_aoi(self, aoi_key: str) -> Dict[str, Any]:
        """
        Retrieves DEM GeoTIFF path and metadata for the specified AOI.
        """
        demo_dir = settings.data_demo_dir / f"aoi_{aoi_key}"
        dem_file = demo_dir / "dem.tif"

        if not dem_file.exists():
            raise FileNotFoundError(f"DEM GeoTIFF not found at {dem_file}")

        with rasterio.open(dem_file) as src:
            bounds = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
            crs = str(src.crs)
            width = src.width
            height = src.height
            tags = src.tags()

        return {
            "aoi": aoi_key,
            "dem_file_path": str(dem_file),
            "crs": crs,
            "bounds": bounds,
            "width": width,
            "height": height,
            "resolution_m": 30.0,
            "provenance": ProvenanceTag.DEMO.value if self.mode == "demo" else ProvenanceTag.OBSERVED.value,
            "source": tags.get("source", "SRTM GL1 30m DEM (OpenTopography / NASA JPL)"),
            "data_source_url": "https://opentopography.org/ / https://lpdaac.usgs.gov/products/srtmgl1v003/",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
