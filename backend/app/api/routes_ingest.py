"""
Data Ingestion Endpoints.
Trigger or reload individual data layers with clear provenance transparency.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException
from backend.app.config import settings
from backend.app.models.schemas import IngestStatusResponse
from backend.app.models.domain import ProvenanceTag
from backend.app.pipeline import pipeline_state
from backend.app.ingestion.nasa_gpm import IMERGIngestionClient
from backend.app.ingestion.dem_ingest import DEMIngestionClient
from backend.app.ingestion.glc_ingest import GLCIngestionClient

router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])


@router.post("/rainfall", response_model=IngestStatusResponse)
def ingest_rainfall(aoi: str = Query(None)):
    aoi_key = aoi or pipeline_state.current_aoi
    client = IMERGIngestionClient()
    try:
        data = client.fetch_rainfall_series(aoi_key)
        pipeline_state.rainfall_data = data
        return IngestStatusResponse(
            layer="rainfall_imerg_v07",
            status="SUCCESS",
            provenance=ProvenanceTag(data.get("provenance", "DEMO")),
            records_or_cells=len(data.get("daily_series", [])),
            source_url=data.get("data_source_url", "https://earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07"),
            timestamp=datetime.now(timezone.utc),
            message=f"Ingested {len(data.get('daily_series', []))} daily IMERG precipitation rasters for {aoi_key}.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dem", response_model=IngestStatusResponse)
def ingest_dem(aoi: str = Query(None)):
    aoi_key = aoi or pipeline_state.current_aoi
    client = DEMIngestionClient()
    try:
        data = client.get_dem_for_aoi(aoi_key)
        pipeline_state.dem_data = data
        return IngestStatusResponse(
            layer="srtm_gl1_30m_dem",
            status="SUCCESS",
            provenance=ProvenanceTag(data.get("provenance", "DEMO")),
            records_or_cells=data.get("width", 0) * data.get("height", 0),
            source_url=data.get("data_source_url", "https://opentopography.org/"),
            timestamp=datetime.now(timezone.utc),
            message=f"Ingested SRTM GL1 30m DEM ({data.get('width')}x{data.get('height')}) for {aoi_key}.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history", response_model=IngestStatusResponse)
def ingest_history(aoi: str = Query(None)):
    aoi_key = aoi or pipeline_state.current_aoi
    client = GLCIngestionClient()
    try:
        data = client.get_historical_landslides(aoi_key)
        pipeline_state.glc_data = data
        return IngestStatusResponse(
            layer="nasa_glc_catalog",
            status="SUCCESS",
            provenance=ProvenanceTag(data.get("provenance", "DEMO")),
            records_or_cells=data.get("count", 0),
            source_url=data.get("data_source_url", "https://data.nasa.gov/dataset/global-landslide-catalog-export"),
            timestamp=datetime.now(timezone.utc),
            message=f"Ingested {data.get('count', 0)} NASA Global Landslide Catalog records for {aoi_key}.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
