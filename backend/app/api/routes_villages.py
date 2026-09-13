"""
Village-Level Aggregated Risk Endpoints.
Provides both structured village metrics and enriched GeoJSON polygons for Leaflet rendering.
"""
from typing import List, Dict, Any
from fastapi import APIRouter
from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.schemas import VillageRiskSummary

router = APIRouter(prefix="/villages", tags=["Village Aggregation"])


@router.get("", response_model=List[VillageRiskSummary])
def list_village_risks():
    """Returns aggregated risk metrics for all villages in active AOI."""
    if not pipeline_state.village_summaries:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.village_summaries


@router.get("/geojson")
def get_villages_geojson():
    """Returns enriched GeoJSON FeatureCollection with attached risk properties."""
    if pipeline_state.enriched_villages_geojson is None:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.enriched_villages_geojson
