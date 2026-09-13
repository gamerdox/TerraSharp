"""
AOI Selection and Query Endpoints.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from backend.app.config import settings
from backend.app.models.schemas import AOIInfo, CustomAOIRequest
from backend.app.pipeline import pipeline_state

router = APIRouter(prefix="/aoi", tags=["Area of Interest"])


@router.get("", response_model=List[AOIInfo])
def list_available_aois():
    """Returns pre-configured high-hazard AOIs (Wayanad, Chamoli)."""
    aois = settings.default_config.get("aois", {})
    res = []
    for k, v in aois.items():
        res.append(
            AOIInfo(
                id=k,
                name=v["name"],
                description=v["description"],
                bbox=v["bbox"],
                center=v["center"],
                default_zoom=v["default_zoom"],
                elevation_range=v["elevation_range"],
            )
        )
    return res


@router.get("/current")
def get_current_aoi():
    """Returns the currently active AOI and bounding information."""
    aoi_key = pipeline_state.current_aoi
    aoi_cfg = settings.get_aoi_config(aoi_key)
    return {
        "active_aoi": aoi_key,
        "name": aoi_cfg.name,
        "description": aoi_cfg.description,
        "bbox": aoi_cfg.bbox.model_dump(),
        "center": aoi_cfg.center,
        "last_processed": pipeline_state.last_processed.isoformat() if pipeline_state.last_processed else None,
    }


@router.post("/select/{aoi_key}")
def select_aoi(aoi_key: str):
    """Switches the active AOI to a pre-configured region."""
    aois = settings.default_config.get("aois", {})
    if aoi_key not in aois:
        raise HTTPException(status_code=404, detail=f"AOI '{aoi_key}' not recognized. Available: {list(aois.keys())}")
    pipeline_state.current_aoi = aoi_key
    return {"status": "SUCCESS", "active_aoi": aoi_key, "message": f"Active AOI set to {aois[aoi_key]['name']}"}


@router.post("/create_from_pin")
def create_aoi_from_pin(lat: float, lon: float, name: str = None):
    """
    Creates a new custom AOI centered on any given (lat, lon) with a complete georeferenced raster grid,
    runs the data-fusion pipeline, and switches the active AOI to it.
    """
    from backend.app.ingestion.dynamic_aoi_generator import create_custom_aoi_from_point
    from backend.app.pipeline import PipelineOrchestrator

    res = create_custom_aoi_from_point(lat, lon, name)
    aoi_key = res["aoi_key"]
    pipeline_state.current_aoi = aoi_key

    # Execute complete pipeline for the newly generated AOI
    orchestrator = PipelineOrchestrator()
    pipeline_result = orchestrator.run(aoi_key)

    return {
        "status": "SUCCESS",
        "active_aoi": aoi_key,
        "name": res["config"]["name"],
        "bbox": res["config"]["bbox"],
        "center": res["config"]["center"],
        "pipeline_result": pipeline_result,
    }
