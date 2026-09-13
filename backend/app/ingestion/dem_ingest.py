"""
DEM Ingestion Module for SRTM GL1 30m / Copernicus GLO-30.
Supports live fetching via Open-Meteo elevation API or cached demo datasets.
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
        In live mode, fetches real elevation data from Open-Meteo API.
        In demo mode, falls back to pre-generated GeoTIFFs.
        """
        # Try live data first (if mode is live or if live cache exists)
        if self.mode == "live":
            try:
                return self._get_live_dem(aoi_key)
            except Exception as e:
                logger.warning(f"Live DEM fetch failed for {aoi_key}: {e}. Falling back to demo data.")

        # Fallback: check live cache even in demo mode
        live_dem = settings.data_live_dir / f"aoi_{aoi_key}" / "dem.tif"
        if live_dem.exists():
            return self._read_dem_metadata(live_dem, aoi_key, ProvenanceTag.OBSERVED)

        # Final fallback: demo data
        demo_dem = settings.data_demo_dir / f"aoi_{aoi_key}" / "dem.tif"
        if demo_dem.exists():
            return self._read_dem_metadata(demo_dem, aoi_key, ProvenanceTag.DEMO)

        raise FileNotFoundError(f"No DEM data found for AOI '{aoi_key}'. Run pipeline first.")

    def _get_live_dem(self, aoi_key: str) -> Dict[str, Any]:
        """Fetches real DEM from Open-Meteo elevation API and caches as GeoTIFF."""
        from backend.app.ingestion.live_grid_fetcher import generate_live_dem

        aoi_cfg = settings.get_aoi_config(aoi_key)
        output_dir = settings.data_live_dir / f"aoi_{aoi_key}"

        dem_path = generate_live_dem(
            aoi_key=aoi_key,
            min_lon=aoi_cfg.bbox.min_lon,
            min_lat=aoi_cfg.bbox.min_lat,
            max_lon=aoi_cfg.bbox.max_lon,
            max_lat=aoi_cfg.bbox.max_lat,
            output_dir=output_dir,
            cache_hours=settings.live_dem_cache_hours,
        )

        return self._read_dem_metadata(dem_path, aoi_key, ProvenanceTag.OBSERVED)

    def _read_dem_metadata(self, dem_file: Path, aoi_key: str, provenance: ProvenanceTag) -> Dict[str, Any]:
        """Reads metadata from a DEM GeoTIFF file."""
        with rasterio.open(dem_file) as src:
            bounds = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
            crs = str(src.crs)
            width = src.width
            height = src.height
            tags = src.tags()

        source_tag = tags.get("source", "SRTM GL1 30m DEM")
        is_live = tags.get("tag", "") == "LIVE_API_DATA"

        return {
            "aoi": aoi_key,
            "dem_file_path": str(dem_file),
            "crs": crs,
            "bounds": bounds,
            "width": width,
            "height": height,
            "resolution_m": 30.0,
            "provenance": provenance.value,
            "source": source_tag if is_live else "SRTM GL1 30m DEM (OpenTopography / NASA JPL)",
            "data_source_url": "https://api.open-meteo.com/v1/elevation" if is_live else "https://opentopography.org/",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
