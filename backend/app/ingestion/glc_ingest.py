"""
NASA Global Landslide Catalog (GLC) Ingestion Module.
Ingests historical landslide occurrences, dates, trigger conditions,
and Indian validation cross-references (ISRO/NRSC, GSI Bhusanket).
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import geopandas as gpd

from backend.app.config import settings
from backend.app.models.domain import ProvenanceTag

logger = logging.getLogger(__name__)


class GLCIngestionClient:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.mode

    def get_historical_landslides(self, aoi_key: str) -> Dict[str, Any]:
        """
        Retrieves historical landslide events within the AOI.
        """
        live_file = settings.data_live_dir / f"aoi_{aoi_key}" / "glc_events.geojson"
        demo_file = settings.data_demo_dir / f"aoi_{aoi_key}" / "glc_events.geojson"
        glc_file = live_file if live_file.exists() else demo_file

        if not glc_file.exists():
            raise FileNotFoundError(f"GLC events file not found at {glc_file}")

        gdf = gpd.read_file(glc_file)

        events: List[Dict[str, Any]] = []
        has_simulated = False
        for _, row in gdf.iterrows():
            geom = row.geometry
            row_prov = row.get("provenance", "")
            if row_prov == "SIMULATED":
                has_simulated = True
            events.append({
                "event_id": row.get("event_id", "UNKNOWN"),
                "date": str(row.get("date", "")),
                "location": row.get("location", ""),
                "trigger": row.get("trigger", ""),
                "landslide_category": row.get("landslide_category", "Landslide"),
                "landslide_size": row.get("landslide_size", "Unknown"),
                "fatalities": int(row.get("fatalities", 0)),
                "confidence": row.get("confidence", "MEDIUM"),
                "source": row.get("source", "NASA Global Landslide Catalog"),
                "provenance": row_prov or (ProvenanceTag.OBSERVED.value if self.mode != "demo" else ProvenanceTag.DEMO.value),
                "coordinates": [geom.x, geom.y] if geom else [0.0, 0.0],
            })

        overall_prov = ProvenanceTag.SIMULATED.value if has_simulated else (
            ProvenanceTag.OBSERVED.value if self.mode != "demo" else ProvenanceTag.DEMO.value
        )

        return {
            "aoi": aoi_key,
            "count": len(events),
            "events": events,
            "file_path": str(glc_file),
            "provenance": overall_prov,
            "data_source_url": "https://data.nasa.gov/dataset/global-landslide-catalog-export" if not has_simulated else "Local Test Fixture",
            "validation_references": [
                "ISRO/NRSC Landslide Atlas of India (https://isro.gov.in/Landslide_Atlas_India.html)",
                "GSI Bhusanket / National Landslide Forecasting Centre (https://bhusanket.gsi.gov.in/)",
            ] if not has_simulated else ["Synthetic Test Calibration"],
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
