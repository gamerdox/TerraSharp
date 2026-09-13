"""
Risk Query Endpoints.
Provides grid-level landslide & flash-flood risk data and explainable point-level factor breakdowns.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException
import numpy as np

from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.domain import RiskLevel, ProvenanceTag
from backend.app.models.schemas import GridCellRisk, RiskRasterSummary, ContributingFactors, PinPointLiveResponse
from backend.app.scoring.classifier import classify_risk_score
from backend.app.ingestion.live_point_fetcher import live_point_fetcher

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])


@router.get("", response_model=Dict[str, Any])
def get_risk_layers():
    """
    Returns summarized risk metrics and grid cells for map visualization.
    """
    if pipeline_state.last_processed is None:
        # Run default pipeline automatically if not yet run
        orchestrator = PipelineOrchestrator()
        orchestrator.run(pipeline_state.current_aoi)

    grid = pipeline_state.grid
    ls_risk = pipeline_state.landslide_risk
    ff_risk = pipeline_state.flash_flood_risk

    # Build downsampled/formatted grid points for rapid frontend rendering
    cells = []
    rows, cols = grid.rows, grid.cols

    for r in range(rows):
        for c in range(cols):
            lat = float(grid.lats[r])
            lon = float(grid.lons[c])
            ls_val = float(ls_risk[r, c])
            ff_val = float(ff_risk[r, c])

            cells.append({
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "landslide_risk": round(ls_val, 3),
                "landslide_class": classify_risk_score(ls_val).value,
                "flash_flood_risk": round(ff_val, 3),
                "flash_flood_class": classify_risk_score(ff_val).value,
                "elevation_m": round(float(pipeline_state.elevation[r, c]), 1),
                "slope_deg": round(float(pipeline_state.slope_deg[r, c]), 1),
                "rainfall_24h_mm": round(float(pipeline_state.rainfall_24h[r, c]), 1),
                "soil_proxy": round(float(pipeline_state.soil_proxy[r, c]), 3),
            })

    return {
        "aoi": pipeline_state.current_aoi,
        "processed_at": pipeline_state.last_processed.isoformat() if pipeline_state.last_processed else None,
        "grid_meta": grid.get_info(),
        "summary": {
            "mean_landslide_risk": round(float(np.mean(ls_risk)), 3),
            "max_landslide_risk": round(float(np.max(ls_risk)), 3),
            "mean_flash_flood_risk": round(float(np.mean(ff_risk)), 3),
            "max_flash_flood_risk": round(float(np.max(ff_risk)), 3),
            "total_cells": len(cells),
        },
        "cells": cells,
    }


@router.get("/point", response_model=GridCellRisk)
def get_point_risk(lat: float = Query(...), lon: float = Query(...)):
    """
    Returns explainable risk factors for an exact clicked latitude and longitude.
    """
    if pipeline_state.last_processed is None:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    grid = pipeline_state.grid
    from backend.app.scoring.weighted_index import LandslideRiskScorer
    from backend.app.config import settings

    if not (grid.min_lon <= lon <= grid.adjusted_max_lon and grid.adjusted_min_lat <= lat <= grid.max_lat):
        # Coordinate is outside current pre-computed grid - evaluate dynamically via live point fetcher
        live_res = live_point_fetcher.evaluate_live_pinpoint(lat, lon)
        scorer = LandslideRiskScorer(settings.risk_weights)
        factors = scorer.explain_point_risk(
            rainfall_val=min(1.0, live_res["rainfall_24h_mm"] / 200.0),
            slope_val=min(1.0, max(0.0, (live_res["slope_deg"] - 15.0) / 30.0)),
            soil_val=live_res["soil_saturation_proxy"],
            history_val=0.10,
        )
        provenance_dict = {
            "elevation": ProvenanceTag.OBSERVED,
            "slope": ProvenanceTag.DERIVED,
            "rainfall": ProvenanceTag.OBSERVED,
            "soil_proxy": ProvenanceTag.PROXY,
            "historical_density": ProvenanceTag.SYNTHETIC,
            "landslide_risk": ProvenanceTag.MODELLED,
            "flash_flood_risk": ProvenanceTag.MODELLED,
        }
        return GridCellRisk(
            lat=round(lat, 4),
            lon=round(lon, 4),
            landslide_risk=live_res["landslide_risk"],
            landslide_class=classify_risk_score(live_res["landslide_risk"]),
            flash_flood_risk=live_res["flash_flood_risk"],
            flash_flood_class=classify_risk_score(live_res["flash_flood_risk"]),
            elevation_m=live_res["elevation_m"],
            slope_deg=live_res["slope_deg"],
            rainfall_24h_mm=live_res["rainfall_24h_mm"],
            rainfall_3d_mm=live_res["rainfall_3d_mm"],
            rainfall_15d_mm=live_res["rainfall_15d_mm"],
            soil_saturation_proxy=live_res["soil_saturation_proxy"],
            flow_accumulation=0.0,
            historical_density=0.10,
            factors=factors,
            provenance=provenance_dict,
        )

    c = int(np.clip((lon - grid.min_lon) / grid.resolution_deg, 0, grid.cols - 1))
    r = int(np.clip((grid.max_lat - lat) / grid.resolution_deg, 0, grid.rows - 1))

    ls_val = float(pipeline_state.landslide_risk[r, c])
    ff_val = float(pipeline_state.flash_flood_risk[r, c])
    elev_val = float(pipeline_state.elevation[r, c])
    slope_val = float(pipeline_state.slope_deg[r, c])
    slope_norm_val = float(pipeline_state.slope_norm[r, c])
    rf24_val = float(pipeline_state.rainfall_24h[r, c])
    rf3d_val = float(pipeline_state.rainfall_3d[r, c])
    rf15d_val = float(pipeline_state.rainfall_15d[r, c])
    rf_score_val = float(pipeline_state.rainfall_score[r, c])
    soil_val = float(pipeline_state.soil_proxy[r, c])
    flow_accum_val = float(pipeline_state.flow_accum[r, c])
    glc_val = float(pipeline_state.glc_density_norm[r, c])

    scorer = LandslideRiskScorer(settings.risk_weights)
    factors = scorer.explain_point_risk(
        rainfall_val=rf_score_val,
        slope_val=slope_norm_val,
        soil_val=soil_val,
        history_val=glc_val,
    )

    provenance_dict = {
        "elevation": ProvenanceTag.DEMO if settings.mode == "demo" else ProvenanceTag.OBSERVED,
        "slope": ProvenanceTag.DERIVED,
        "rainfall": ProvenanceTag.DEMO if settings.mode == "demo" else ProvenanceTag.OBSERVED,
        "soil_proxy": ProvenanceTag.PROXY,
        "historical_density": ProvenanceTag.DEMO if settings.mode == "demo" else ProvenanceTag.OBSERVED,
        "landslide_risk": ProvenanceTag.MODELLED,
        "flash_flood_risk": ProvenanceTag.MODELLED,
    }

    return GridCellRisk(
        lat=round(lat, 4),
        lon=round(lon, 4),
        landslide_risk=round(ls_val, 3),
        landslide_class=classify_risk_score(ls_val),
        flash_flood_risk=round(ff_val, 3),
        flash_flood_class=classify_risk_score(ff_val),
        elevation_m=round(elev_val, 1),
        slope_deg=round(slope_val, 1),
        rainfall_24h_mm=round(rf24_val, 1),
        rainfall_3d_mm=round(rf3d_val, 1),
        rainfall_15d_mm=round(rf15d_val, 1),
        soil_saturation_proxy=round(soil_val, 3),
        flow_accumulation=round(flow_accum_val, 1),
        historical_density=round(glc_val, 3),
        factors=factors,
        provenance=provenance_dict,
    )


@router.get("/point/live", response_model=PinPointLiveResponse)
@router.post("/point/live", response_model=PinPointLiveResponse)
def get_live_pinpoint_prediction(lat: float = Query(...), lon: float = Query(...)):
    """
    Evaluates real-time predictions for ANY clicked or pinned location on Earth.
    Fetches real-time DEM elevation stencil, Horn slope, 15-day rainfall series,
    computes soil saturation proxy, Caine threshold, and executes the False-Alarm Mitigation Gate.
    """
    if lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0:
        raise HTTPException(status_code=400, detail="Invalid latitude/longitude coordinates.")

    try:
        return live_point_fetcher.evaluate_live_pinpoint(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live point prediction error: {str(e)}")
