"""
Administrative Boundaries Ingestion Module.
Loads authoritative village polygons, properties, and coordinates for spatial aggregation.
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import geopandas as gpd

from backend.app.config import settings
from backend.app.models.domain import ProvenanceTag

logger = logging.getLogger(__name__)


class BoundaryIngestionClient:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.mode

    def get_villages_for_aoi(self, aoi_key: str) -> Dict[str, Any]:
        """
        Retrieves village boundaries as a GeoDataFrame and metadata.
        """
        live_file = settings.data_live_dir / f"aoi_{aoi_key}" / "villages.geojson"
        demo_file = settings.data_demo_dir / f"aoi_{aoi_key}" / "villages.geojson"
        villages_file = live_file if live_file.exists() else demo_file

        if not villages_file.exists():
            raise FileNotFoundError(f"Village boundaries GeoJSON not found at {villages_file}")

        gdf = gpd.read_file(villages_file)

        villages_list: List[Dict[str, Any]] = []
        has_simulated = False
        for _, row in gdf.iterrows():
            geom = row.geometry
            centroid = geom.centroid
            row_prov = row.get("provenance", "")
            if row_prov == "SIMULATED":
                has_simulated = True
            villages_list.append({
                "village_id": row.get("village_id", f"V_{_}"),
                "village_name": row.get("village_name", f"Village {_}"),
                "district": row.get("district", ""),
                "state": row.get("state", ""),
                "population": int(row.get("population", 0)),
                "bounds": [geom.bounds[0], geom.bounds[1], geom.bounds[2], geom.bounds[3]],
                "center": {"lon": float(centroid.x), "lat": float(centroid.y)},
                "source": row.get("source", "Administrative Boundaries"),
                "provenance": row_prov or ProvenanceTag.OBSERVED.value,
            })

        overall_prov = ProvenanceTag.SIMULATED.value if has_simulated else ProvenanceTag.OBSERVED.value

        return {
            "aoi": aoi_key,
            "count": len(villages_list),
            "villages": villages_list,
            "geojson_path": str(villages_file),
            "provenance": overall_prov,
            "data_source_url": "Authoritative Open Administrative Boundaries / OSM" if not has_simulated else "Synthetic Analysis Zones",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }

    def load_geodataframe(self, aoi_key: str) -> gpd.GeoDataFrame:
        live_file = settings.data_live_dir / f"aoi_{aoi_key}" / "villages.geojson"
        demo_file = settings.data_demo_dir / f"aoi_{aoi_key}" / "villages.geojson"
        villages_file = live_file if live_file.exists() else demo_file
        return gpd.read_file(villages_file)
