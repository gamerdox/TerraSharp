"""
Rainfall Ingestion Module.
Supports live retrieval via Open-Meteo forecast API (free, global, keyless),
with fallback to NASA GPM IMERG via earthaccess, and deterministic demo datasets.
"""
import json
import logging
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import rasterio

from backend.app.config import settings
from backend.app.models.domain import ProvenanceTag

logger = logging.getLogger(__name__)


class IMERGIngestionClient:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.mode
        self.username = settings.earthdata_username
        self.password = settings.earthdata_password

    def fetch_rainfall_series(
        self,
        aoi_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves rainfall raster series for the given AOI.
        Priority: Live Open-Meteo → NASA Earthdata → Demo data
        """
        # 1. Try live Open-Meteo (free, keyless, global)
        if self.mode == "live":
            try:
                return self._fetch_openmeteo_live(aoi_key)
            except Exception as e:
                logger.warning(f"Live Open-Meteo rainfall failed: {e}. Trying alternatives...")

        # 2. Check for cached live data
        live_series = settings.data_live_dir / f"aoi_{aoi_key}" / "rainfall_series.json"
        if live_series.exists():
            return self._load_series_json(live_series, aoi_key, is_live=True)

        # 3. Try NASA Earthdata (if credentials available)
        if self.mode == "live" and self.username and self.password:
            try:
                return self._fetch_earthdata_live(aoi_key, start_date, end_date)
            except Exception as e:
                logger.warning(f"NASA Earthdata ingestion failed: {e}. Falling back to demo data.")

        # 4. Final fallback: demo data
        return self._fetch_demo_data(aoi_key)

    def _fetch_openmeteo_live(self, aoi_key: str) -> Dict[str, Any]:
        """Fetches real rainfall grid from Open-Meteo forecast API."""
        from backend.app.ingestion.live_grid_fetcher import generate_live_rainfall

        aoi_cfg = settings.get_aoi_config(aoi_key)
        output_dir = settings.data_live_dir / f"aoi_{aoi_key}"

        series_file = generate_live_rainfall(
            aoi_key=aoi_key,
            name=aoi_cfg.name,
            min_lon=aoi_cfg.bbox.min_lon,
            min_lat=aoi_cfg.bbox.min_lat,
            max_lon=aoi_cfg.bbox.max_lon,
            max_lat=aoi_cfg.bbox.max_lat,
            output_dir=output_dir,
            cache_hours=settings.live_rainfall_cache_hours,
        )

        return self._load_series_json(series_file, aoi_key, is_live=True)

    def _load_series_json(self, series_file: Path, aoi_key: str, is_live: bool = False) -> Dict[str, Any]:
        """Loads a rainfall_series.json file and resolves raster paths."""
        with open(series_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        parent_dir = series_file.parent
        for item in data.get("daily_series", []):
            item["raster_path"] = str(parent_dir / item["raster_file"])

        if is_live:
            data["provenance"] = ProvenanceTag.OBSERVED.value
            data["data_source_url"] = "https://open-meteo.com/ (ERA5/ECMWF Real-Time Precipitation)"
        else:
            data.setdefault("provenance", ProvenanceTag.DEMO.value)

        data["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return data

    def _fetch_demo_data(self, aoi_key: str) -> Dict[str, Any]:
        demo_dir = settings.data_demo_dir / f"aoi_{aoi_key}"
        series_file = demo_dir / "rainfall_series.json"

        if not series_file.exists():
            raise FileNotFoundError(f"Demo rainfall series not found at {series_file}")

        return self._load_series_json(series_file, aoi_key, is_live=False)

    def _fetch_earthdata_live(
        self,
        aoi_key: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> Dict[str, Any]:
        """
        Live Earthdata retrieval using earthaccess (NASA GPM IMERG).
        """
        import earthaccess

        aoi_cfg = settings.get_aoi_config(aoi_key)
        auth = earthaccess.login(strategy="environment")
        if not auth.authenticated:
            auth = earthaccess.login(strategy="interactive", persist=False)

        bbox = (
            aoi_cfg.bbox.min_lon,
            aoi_cfg.bbox.min_lat,
            aoi_cfg.bbox.max_lon,
            aoi_cfg.bbox.max_lat,
        )

        results = earthaccess.search_data(
            short_name="GPM_3IMERGDF",
            version="07",
            bounding_box=bbox,
            temporal=(start_date or "2024-07-01", end_date or "2024-07-30"),
            count=15,
        )

        downloaded_files = earthaccess.download(results, str(settings.data_raw_dir / "imerg"))

        daily_series = []
        for file in downloaded_files:
            file_path = Path(file)
            with rasterio.open(file_path) as src:
                arr = src.read(1)
                daily_series.append({
                    "date": file_path.stem.split(".")[4][:8] if len(file_path.stem.split(".")) > 4 else "unknown",
                    "mean_mm": float(np.mean(arr[arr >= 0])),
                    "max_mm": float(np.max(arr[arr >= 0])),
                    "raster_path": str(file_path),
                })

        return {
            "aoi": aoi_key,
            "description": "Live NASA GPM IMERG Final Daily v07 data via earthaccess",
            "provenance": ProvenanceTag.OBSERVED.value,
            "data_source_url": "https://earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07",
            "daily_series": daily_series,
            "current_intensity_mm_hr": daily_series[-1]["max_mm"] / 24.0 if daily_series else 0.0,
            "trend_alpha_mm_hr2": 0.5,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
