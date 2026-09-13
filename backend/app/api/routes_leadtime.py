"""
Lead-Time Query Endpoints.
Caine (1980) Empirical Intensity-Duration Threshold and Trend Projection.
"""
from fastapi import APIRouter
from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.schemas import LeadTimeEvaluation

router = APIRouter(prefix="/leadtime", tags=["Lead-Time Estimation"])


@router.get("", response_model=LeadTimeEvaluation)
def get_lead_time():
    """
    Returns estimated time toward Caine (1980) critical threshold under current rainfall trend.
    Includes explicit scientific limitations and non-guarantee disclosures.
    """
    if pipeline_state.lead_time is None:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.lead_time
