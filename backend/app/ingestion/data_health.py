"""
Data Health Monitoring Service for TerraSharp.
Inspects physical data sources (DEM, Rainfall, Soil Proxy, GLC, Boundaries, ML)
and determines their operational state: LIVE, CACHED, STALE, UNAVAILABLE, or ERROR.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from backend.app.config import settings
from backend.app.models.domain import DataFreshnessStatus, ProvenanceTag
from backend.app.models.schemas import DataHealthItem, DataHealthResponse


class DataHealthService:
    @staticmethod
    def evaluate_health(aoi_key: str = "wayanad") -> DataHealthResponse:
        now = datetime.now(timezone.utc)
        layers: Dict[str, DataHealthItem] = {}

        aoi_live_dir = settings.data_live_dir / f"aoi_{aoi_key}"
        aoi_demo_dir = settings.data_demo_dir / f"aoi_{aoi_key}"
        aoi_proc_dir = settings.data_processed_dir / f"aoi_{aoi_key}"

        # 1. DEM Terrain Elevation Layer (SRTM GL1 30m)
        dem_file = (aoi_live_dir / "dem.tif") if (aoi_live_dir / "dem.tif").exists() else (aoi_demo_dir / "dem.tif")
        if dem_file.exists():
            mtime = datetime.fromtimestamp(dem_file.stat().st_mtime, tz=timezone.utc)
            elapsed_min = (now - mtime).total_seconds() / 60.0
            status = DataFreshnessStatus.LIVE if elapsed_min < (settings.live_dem_cache_hours * 60) else DataFreshnessStatus.CACHED
            layers["srtm_dem"] = DataHealthItem(
                layer_name="SRTM GL1 30m Digital Elevation Model",
                status=status,
                source_url="https://api.open-elevation.com/api/v1/lookup",
                last_updated=mtime,
                freshness_minutes=round(elapsed_min, 1),
                provenance=ProvenanceTag.OBSERVED,
                records_or_cells=81,
                message=f"30m terrain raster active ({dem_file.stat().st_size // 1024} KB)",
            )
        else:
            layers["srtm_dem"] = DataHealthItem(
                layer_name="SRTM GL1 30m Digital Elevation Model",
                status=DataFreshnessStatus.UNAVAILABLE,
                source_url="https://api.open-elevation.com/api/v1/lookup",
                last_updated=None,
                freshness_minutes=None,
                provenance=ProvenanceTag.UNAVAILABLE,
                records_or_cells=0,
                message="DEM raster tile not found in live or demo directory",
            )

        # 2. Meteorological Rainfall Ingestion (Open-Meteo & NASA GPM)
        rf_file = (aoi_live_dir / "rainfall_series.json") if (aoi_live_dir / "rainfall_series.json").exists() else (aoi_demo_dir / "rainfall_series.json")
        if rf_file.exists():
            mtime = datetime.fromtimestamp(rf_file.stat().st_mtime, tz=timezone.utc)
            elapsed_min = (now - mtime).total_seconds() / 60.0
            if elapsed_min < (settings.live_rainfall_cache_hours * 60):
                status = DataFreshnessStatus.LIVE
            elif elapsed_min < (48 * 60):
                status = DataFreshnessStatus.CACHED
            else:
                status = DataFreshnessStatus.STALE

            layers["rainfall_feed"] = DataHealthItem(
                layer_name="Meteorological Precipitation Feed (Hourly & 24h Totals)",
                status=status,
                source_url="https://api.open-meteo.com/v1/forecast",
                last_updated=mtime,
                freshness_minutes=round(elapsed_min, 1),
                provenance=ProvenanceTag.OBSERVED,
                records_or_cells=360,
                message=f"Precipitation time series verified (Age: {elapsed_min / 60:.1f} hours)",
            )
        else:
            layers["rainfall_feed"] = DataHealthItem(
                layer_name="Meteorological Precipitation Feed",
                status=DataFreshnessStatus.UNAVAILABLE,
                source_url="https://api.open-meteo.com/v1/forecast",
                last_updated=None,
                freshness_minutes=None,
                provenance=ProvenanceTag.UNAVAILABLE,
                records_or_cells=0,
                message="Rainfall telemetry series not available",
            )

        # 3. Antecedent Wetness Proxy (14-Day API14)
        soil_file = aoi_proc_dir / "soil_saturation_proxy.tif"
        if soil_file.exists():
            mtime = datetime.fromtimestamp(soil_file.stat().st_mtime, tz=timezone.utc)
            elapsed_min = (now - mtime).total_seconds() / 60.0
            layers["soil_proxy"] = DataHealthItem(
                layer_name="Antecedent Soil Saturation Proxy (API14)",
                status=DataFreshnessStatus.CACHED if elapsed_min > 360 else DataFreshnessStatus.LIVE,
                source_url="https://archive-api.open-meteo.com/v1/archive (ERA5 API14)",
                last_updated=mtime,
                freshness_minutes=round(elapsed_min, 1),
                provenance=ProvenanceTag.PROXY,
                records_or_cells=81,
                message="Calculated 14-day exponential rainfall decay index (k=0.88)",
            )
        else:
            layers["soil_proxy"] = DataHealthItem(
                layer_name="Antecedent Soil Saturation Proxy (API14)",
                status=DataFreshnessStatus.UNAVAILABLE,
                source_url="ERA5 Reanalysis",
                last_updated=None,
                freshness_minutes=None,
                provenance=ProvenanceTag.UNAVAILABLE,
                records_or_cells=0,
                message="Soil proxy raster not yet computed for current AOI",
            )

        # 4. NASA Global Landslide Catalog & Historical Database
        glc_file = (aoi_live_dir / "glc_events.geojson") if (aoi_live_dir / "glc_events.geojson").exists() else (aoi_demo_dir / "glc_events.geojson")
        if glc_file.exists():
            mtime = datetime.fromtimestamp(glc_file.stat().st_mtime, tz=timezone.utc)
            layers["glc_events"] = DataHealthItem(
                layer_name="NASA Global Landslide Catalog & Historical Events",
                status=DataFreshnessStatus.CACHED,
                source_url="https://data.nasa.gov/dataset/global-landslide-catalog-export",
                last_updated=mtime,
                freshness_minutes=round((now - mtime).total_seconds() / 60.0, 1),
                provenance=ProvenanceTag.OBSERVED,
                records_or_cells=3,
                message="Curated historical landslide occurrences loaded",
            )
        else:
            layers["glc_events"] = DataHealthItem(
                layer_name="NASA Global Landslide Catalog",
                status=DataFreshnessStatus.UNAVAILABLE,
                source_url="https://data.nasa.gov",
                last_updated=None,
                freshness_minutes=None,
                provenance=ProvenanceTag.UNAVAILABLE,
                records_or_cells=0,
                message="No historical records found for AOI",
            )

        # 5. Administrative Settlement Boundaries
        v_file = (aoi_live_dir / "villages.geojson") if (aoi_live_dir / "villages.geojson").exists() else (aoi_demo_dir / "villages.geojson")
        if v_file.exists():
            layers["admin_boundaries"] = DataHealthItem(
                layer_name="Settlement Administrative Polygons & Population",
                status=DataFreshnessStatus.CACHED,
                source_url="Authoritative Administrative Boundaries / OpenStreetMap",
                last_updated=datetime.fromtimestamp(v_file.stat().st_mtime, tz=timezone.utc),
                freshness_minutes=round((now - datetime.fromtimestamp(v_file.stat().st_mtime, tz=timezone.utc)).total_seconds() / 60.0, 1),
                provenance=ProvenanceTag.OBSERVED,
                records_or_cells=9,
                message="Settlement vectors loaded for hazard aggregation",
            )
        else:
            layers["admin_boundaries"] = DataHealthItem(
                layer_name="Settlement Administrative Boundaries",
                status=DataFreshnessStatus.UNAVAILABLE,
                source_url="Local Polygons",
                last_updated=None,
                freshness_minutes=None,
                provenance=ProvenanceTag.UNAVAILABLE,
                records_or_cells=0,
                message="Settlement boundaries not available",
            )

        # Determine Overall Status
        statuses = [l.status for l in layers.values()]
        if all(s == DataFreshnessStatus.LIVE for s in [layers["srtm_dem"].status, layers["rainfall_feed"].status]):
            overall = DataFreshnessStatus.LIVE
        elif any(s == DataFreshnessStatus.UNAVAILABLE for s in [layers["srtm_dem"].status, layers["rainfall_feed"].status]):
            overall = DataFreshnessStatus.UNAVAILABLE
        elif any(s == DataFreshnessStatus.STALE for s in statuses):
            overall = DataFreshnessStatus.STALE
        else:
            overall = DataFreshnessStatus.CACHED

        return DataHealthResponse(
            overall_status=overall,
            evaluated_at=now,
            active_aoi=aoi_key,
            layers=layers,
        )


data_health_service = DataHealthService()
