"""
Alert System Endpoints.
Provides simulated tiered alerts (NORMAL, WATCH, WARNING, CRITICAL) for disaster response.
"""
from typing import List
from fastapi import APIRouter
from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.schemas import AlertItem

router = APIRouter(prefix="/alerts", tags=["Alert Engine"])


@router.get("", response_model=List[AlertItem])
def list_active_alerts():
    """
    Returns active alerts for all settlements within the current AOI.
    Alerts are strictly simulated early-warning advisories.
    """
    if not pipeline_state.alerts:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.alerts
