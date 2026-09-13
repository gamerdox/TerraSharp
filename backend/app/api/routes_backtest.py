"""
Historical Back-Testing & Model Comparison Endpoints.
Mandatory comparison: Rain-Only Baseline vs Full Weighted Risk Index.
"""
from fastapi import APIRouter
from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.schemas import BacktestComparisonResponse

router = APIRouter(prefix="/backtest", tags=["Back-Testing & Validation"])


@router.get("", response_model=BacktestComparisonResponse)
def get_backtest_results():
    """
    Returns empirical back-testing results using NASA GLC historical landslide records.
    Provides rigorous comparison of Full Weighted Index against Rainfall-Only baseline.
    """
    if pipeline_state.backtest_results is None:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.backtest_results
