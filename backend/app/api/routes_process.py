"""
Pipeline Execution Trigger Endpoint.
"""
from fastapi import APIRouter, Query, HTTPException
from backend.app.pipeline import PipelineOrchestrator, pipeline_state

router = APIRouter(prefix="/process", tags=["Processing Pipeline"])


@router.post("")
@router.post("/run")
def execute_pipeline(aoi: str = Query(None)):
    """Executes the full spatial data-fusion pipeline for the requested or current AOI."""
    aoi_key = aoi or pipeline_state.current_aoi
    orchestrator = PipelineOrchestrator()
    try:
        result = orchestrator.run(aoi_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
