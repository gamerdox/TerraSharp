"""
Main FastAPI Application Entry Point for SH-304.
Hyper-Local Landslide & Flash-Flood Early Warning System.
"""
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.models.schemas import HealthResponse
from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.api.routes_aoi import router as aoi_router
from backend.app.api.routes_ingest import router as ingest_router
from backend.app.api.routes_process import router as process_router
from backend.app.api.routes_risk import router as risk_router
from backend.app.api.routes_leadtime import router as leadtime_router
from backend.app.api.routes_alerts import router as alerts_router
from backend.app.api.routes_villages import router as villages_router
from backend.app.api.routes_backtest import router as backtest_router
from backend.app.api.routes_reports import router as reports_router

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sh304")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prime pipeline state upon startup with default AOI in demo mode
    logger.info(f"Initializing SH-304 Early Warning System in {settings.mode.upper()} mode...")
    try:
        orchestrator = PipelineOrchestrator()
        orchestrator.run(settings.default_aoi)
        logger.info(f"Default AOI '{settings.default_aoi}' primed successfully.")
    except Exception as e:
        logger.warning(f"Startup priming warning: {e}")
    yield
    logger.info("Shutting down SH-304 Early Warning System.")


app = FastAPI(
    title="SH-304 Hyper-Local Landslide & Flash-Flood Early Warning System",
    description=(
        "Data-fusion early warning prototype combining NASA GPM IMERG precipitation, "
        "SRTM GL1 30m DEM terrain, antecedent soil-saturation proxy, and NASA Global Landslide Catalog."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React / Leaflet frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(aoi_router)
app.include_router(ingest_router)
app.include_router(process_router)
app.include_router(risk_router)
app.include_router(leadtime_router)
app.include_router(alerts_router)
app.include_router(villages_router)
app.include_router(backtest_router)
app.include_router(reports_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """System health check and environmental dataset load status."""
    return HealthResponse(
        status="HEALTHY",
        app_name=settings.app_name,
        version=settings.model_version,
        mode=settings.mode,
        timestamp=datetime.now(timezone.utc),
        data_status={
            "dem_loaded": pipeline_state.elevation is not None,
            "imerg_loaded": pipeline_state.rainfall_24h is not None,
            "glc_loaded": pipeline_state.glc_density_norm is not None,
            "villages_loaded": len(pipeline_state.village_summaries) > 0,
            "active_aoi": pipeline_state.current_aoi,
            "last_processed": pipeline_state.last_processed.isoformat() if pipeline_state.last_processed else None,
        },
    )


@app.get("/", tags=["System"])
def root():
    return {
        "system": "SH-304 Hyper-Local Landslide & Flash-Flood Warning System",
        "docs_url": "/docs",
        "health_url": "/health",
        "mode": settings.mode.upper(),
        "active_aoi": pipeline_state.current_aoi,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
