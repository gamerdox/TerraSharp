"""
NASA GPM IMERG Ingestion Module.
Supports live retrieval via earthaccess for GPM_3IMERGDF v07 (Final Daily),
with clean, transparent fallback to deterministic demo datasets.
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
        If live mode is requested and credentials are valid, queries Earthdata.
        Otherwise loads deterministic demo datasets with explicit DEMO provenance tag.
        """
        if self.mode == "live" and self.username and self.password:
            try:
                return self._fetch_earthdata_live(aoi_key, start_date, end_date)
            except Exception as e:
                logger.warning(f"Live Earthdata ingestion failed: {e}. Falling back to demo data.")

        return self._fetch_demo_data(aoi_key)

    def _fetch_demo_data(self, aoi_key: str) -> Dict[str, Any]:
        demo_dir = settings.data_demo_dir / f"aoi_{aoi_key}"
        series_file = demo_dir / "rainfall_series.json"

        if not series_file.exists():
            raise FileNotFoundError(f"Demo rainfall series not found at {series_file}")

        with open(series_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Resolve full raster filepaths
        for item in data.get("daily_series", []):
            item["raster_path"] = str(demo_dir / item["raster_file"])

        data["provenance"] = ProvenanceTag.DEMO.value
        data["data_source_url"] = "https://earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07 (Demo Fallback)"
        data["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return data

    def _fetch_earthdata_live(
        self,
        aoi_key: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> Dict[str, Any]:
        """
        Live Earthdata retrieval using earthaccess.
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
