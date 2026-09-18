"""
Central Pipeline Orchestrator for SH-304.
Executes data fusion end-to-end: AOI -> Ingestion -> Alignment -> Features -> Scoring -> Alerts -> Villages.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import numpy as np

from backend.app.config import settings, AOIConfig
from backend.app.preprocessing.grid import AnalysisGrid
from backend.app.preprocessing.raster_ops import resample_raster_to_grid, write_grid_raster
from backend.app.ingestion.dem_ingest import DEMIngestionClient
from backend.app.ingestion.nasa_gpm import IMERGIngestionClient
from backend.app.ingestion.glc_ingest import GLCIngestionClient
from backend.app.ingestion.boundaries import BoundaryIngestionClient
from backend.app.terrain.slope import compute_slope_and_aspect
from backend.app.terrain.drainage import compute_d8_flow_accumulation
from backend.app.rainfall.imerg_processor import RainfallProcessor
from backend.app.soil.proxy import compute_soil_saturation_proxy
from backend.app.history.density import compute_historical_landslide_density
from backend.app.scoring.weighted_index import LandslideRiskScorer
from backend.app.scoring.flash_flood import FlashFloodRiskScorer
from backend.app.leadtime.caine_threshold import evaluate_caine_lead_time
from backend.app.alerts.engine import AlertEngine
from backend.app.aggregation.village import aggregate_grid_to_villages
from backend.app.backtest.evaluator import BacktestEvaluator
from backend.app.models.domain import ProvenanceTag, RiskLevel
from backend.app.models.schemas import (
    GridCellRisk,
    RiskRasterSummary,
    LeadTimeEvaluation,
    AlertItem,
    VillageRiskSummary,
    BacktestComparisonResponse,
)

logger = logging.getLogger(__name__)


class PipelineState:
    """Holds in-memory cache of the latest pipeline execution results."""
    def __init__(self):
        self.current_aoi: str = "wayanad"
        self.last_processed: Optional[datetime] = None
        self.grid: Optional[AnalysisGrid] = None
        self.dem_data: Optional[Dict[str, Any]] = None
        self.rainfall_data: Optional[Dict[str, Any]] = None
        self.glc_data: Optional[Dict[str, Any]] = None
        self.villages_data: Optional[Dict[str, Any]] = None

        # 2D Arrays
        self.elevation: Optional[np.ndarray] = None
        self.slope_deg: Optional[np.ndarray] = None
        self.slope_norm: Optional[np.ndarray] = None
        self.flow_accum: Optional[np.ndarray] = None
        self.flow_accum_norm: Optional[np.ndarray] = None
        self.rainfall_24h: Optional[np.ndarray] = None
        self.rainfall_3d: Optional[np.ndarray] = None
        self.rainfall_15d: Optional[np.ndarray] = None
        self.rainfall_score: Optional[np.ndarray] = None
        self.soil_proxy: Optional[np.ndarray] = None
        self.glc_density_norm: Optional[np.ndarray] = None
        self.landslide_risk: Optional[np.ndarray] = None
        self.flash_flood_risk: Optional[np.ndarray] = None

        # Aggregates
        self.village_summaries: List[VillageRiskSummary] = []
        self.enriched_villages_geojson: Optional[Dict[str, Any]] = None
        self.alerts: List[AlertItem] = []
        self.lead_time: Optional[LeadTimeEvaluation] = None
        self.backtest_results: Optional[BacktestComparisonResponse] = None


# Global pipeline state singleton
pipeline_state = PipelineState()


class PipelineOrchestrator:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.mode
        self.dem_client = DEMIngestionClient(self.mode)
        self.imerg_client = IMERGIngestionClient(self.mode)
        self.glc_client = GLCIngestionClient(self.mode)
        self.boundary_client = BoundaryIngestionClient(self.mode)
        self.landslide_scorer = LandslideRiskScorer(settings.risk_weights)
        self.flash_flood_scorer = FlashFloodRiskScorer(settings.risk_weights)
        self.alert_engine = AlertEngine()

    def run(self, aoi_key: str = "wayanad") -> Dict[str, Any]:
        """
        Executes complete spatial fusion pipeline for the chosen AOI.
        """
        logger.info(f"Starting pipeline execution for AOI: {aoi_key} (Mode: {self.mode})")
        aoi_cfg = settings.get_aoi_config(aoi_key)

        # 1. Common Analysis Grid
        grid = AnalysisGrid(
            bbox=aoi_cfg.bbox,
            resolution_deg=settings.grid_res_deg,
            utm_epsg=aoi_cfg.utm_epsg,
        )

        # 2. Data Ingestion
        dem_info = self.dem_client.get_dem_for_aoi(aoi_key)
        rf_info = self.imerg_client.fetch_rainfall_series(aoi_key)
        glc_info = self.glc_client.get_historical_landslides(aoi_key)
        villages_info = self.boundary_client.get_villages_for_aoi(aoi_key)
        villages_gdf = self.boundary_client.load_geodataframe(aoi_key)

        # 3. Resample DEM to Analysis Grid
        elevation_grid = resample_raster_to_grid(dem_info["dem_file_path"], grid, nodata_fill=500.0)

        # 4. Terrain Features: Slope and Flow Accumulation
        slope_deg, aspect_deg, slope_norm, terrain_meta = compute_slope_and_aspect(
            elevation_grid, grid.dx_meters, grid.dy_meters
        )
        flow_accum, flow_accum_norm, drainage_meta = compute_d8_flow_accumulation(
            elevation_grid, grid.dx_meters, grid.dy_meters
        )

        # 5. Rainfall Features
        rf_processor = RainfallProcessor(grid)
        rf_features = rf_processor.process_rainfall_series(rf_info)
        rainfall_score = rf_features["rainfall_score"]
        rainfall_24h_norm = rf_features["r24_norm"]

        # 6. Historical Landslide Density
        glc_density_raw, glc_density_norm, history_meta = compute_historical_landslide_density(
            glc_info, grid
        )

        # 7. Soil-Saturation Proxy
        soil_proxy, soil_meta = compute_soil_saturation_proxy(
            rf_features["rainfall_3d"], rf_features["rainfall_15d"]
        )

        # 8. Weighted Landslide Risk Index
        ls_risk_grid, ls_classes_grid, ls_meta = self.landslide_scorer.compute_risk_grid(
            rainfall_score, slope_norm, soil_proxy, glc_density_norm
        )

        # 9. Flash-Flood Risk Index
        ff_risk_grid, ff_classes_grid, ff_meta = self.flash_flood_scorer.compute_flash_flood_grid(
            rainfall_24h_norm, flow_accum_norm, slope_norm
        )

        # 10. Lead-Time Evaluation (Caine 1980)
        curr_intensity = float(rf_features["metadata"]["mean_intensity_mm_hr"])
        trend_alpha = float(rf_features["metadata"]["trend_alpha_mm_hr2"])
        lead_time = evaluate_caine_lead_time(
            current_intensity_mm_hr=curr_intensity,
            duration_hours=24.0,
            trend_alpha_mm_hr2=trend_alpha,
            location=aoi_cfg.center,
        )

        # 11. Village Aggregation
        village_summaries, enriched_villages_geojson = aggregate_grid_to_villages(
            villages_gdf=villages_gdf,
            grid=grid,
            landslide_risk_grid=ls_risk_grid,
            flash_flood_risk_grid=ff_risk_grid,
            rainfall_score_grid=rainfall_score,
            slope_norm_grid=slope_norm,
            soil_proxy_grid=soil_proxy,
            history_norm_grid=glc_density_norm,
        )

        # 12. Alert Generation
        alerts: List[AlertItem] = []
        for v_sum in village_summaries:
            # Generate explainable factor breakdown for village center
            v_c = v_sum.coordinates_center
            c_col = int(np.clip((v_c["lon"] - grid.min_lon) / grid.resolution_deg, 0, grid.cols - 1))
            c_row = int(np.clip((grid.max_lat - v_c["lat"]) / grid.resolution_deg, 0, grid.rows - 1))

            factors = self.landslide_scorer.explain_point_risk(
                rainfall_val=float(rainfall_score[c_row, c_col]),
                slope_val=float(slope_norm[c_row, c_col]),
                soil_val=float(soil_proxy[c_row, c_col]),
                history_val=float(glc_density_norm[c_row, c_col]),
            )

            # Generate alert item with stateful hysteresis and persistence
            alert = self.alert_engine.evaluate_village(
                village_id=v_sum.village_id,
                village_name=v_sum.name,
                coordinates=v_c,
                landslide_risk=v_sum.max_landslide_risk,
                flash_flood_risk=v_sum.max_flash_flood_risk,
                factors=factors,
                lead_time_hours=lead_time.estimated_lead_time_hours,
                data_completeness=1.0,
                data_freshness="FRESH",
            )
            alerts.append(alert)

        # 13. Back-Testing & Rainfall-Only Baseline Evaluation
        backtest_evaluator = BacktestEvaluator(grid)
        backtest_res = backtest_evaluator.run_backtest(
            aoi_key=aoi_key,
            glc_data=glc_info,
            rainfall_score_grid=rainfall_score,
            landslide_risk_grid=ls_risk_grid,
            slope_norm_grid=slope_norm,
        )

        # Save to in-memory state
        pipeline_state.current_aoi = aoi_key
        pipeline_state.last_processed = datetime.now(timezone.utc)
        pipeline_state.grid = grid
        pipeline_state.dem_data = dem_info
        pipeline_state.rainfall_data = rf_info
        pipeline_state.glc_data = glc_info
        pipeline_state.villages_data = villages_info
        pipeline_state.elevation = elevation_grid
        pipeline_state.slope_deg = slope_deg
        pipeline_state.slope_norm = slope_norm
        pipeline_state.flow_accum = flow_accum
        pipeline_state.flow_accum_norm = flow_accum_norm
        pipeline_state.rainfall_24h = rf_features["rainfall_24h"]
        pipeline_state.rainfall_3d = rf_features["rainfall_3d"]
        pipeline_state.rainfall_15d = rf_features["rainfall_15d"]
        pipeline_state.rainfall_score = rainfall_score
        pipeline_state.soil_proxy = soil_proxy
        pipeline_state.glc_density_norm = glc_density_norm
        pipeline_state.landslide_risk = ls_risk_grid
        pipeline_state.flash_flood_risk = ff_risk_grid
        pipeline_state.village_summaries = village_summaries
        pipeline_state.enriched_villages_geojson = enriched_villages_geojson
        pipeline_state.alerts = alerts
        pipeline_state.lead_time = lead_time
        pipeline_state.backtest_results = backtest_res

        # Write output GeoTIFF rasters to data/processed/
        out_dir = settings.data_processed_dir / f"aoi_{aoi_key}"
        out_dir.mkdir(parents=True, exist_ok=True)
        write_grid_raster(ls_risk_grid, grid, str(out_dir / "landslide_risk.tif"), tags={"title": "Landslide Risk"})
        write_grid_raster(ff_risk_grid, grid, str(out_dir / "flash_flood_risk.tif"), tags={"title": "Flash Flood Risk"})
        write_grid_raster(soil_proxy, grid, str(out_dir / "soil_saturation_proxy.tif"), tags={"title": "Soil Proxy"})

        logger.info(f"Pipeline execution completed successfully for {aoi_key}.")

        return {
            "status": "SUCCESS",
            "aoi": aoi_key,
            "processed_at": pipeline_state.last_processed.isoformat(),
            "grid_info": grid.get_info(),
            "villages_analyzed": len(village_summaries),
            "alerts_generated": len(alerts),
            "critical_alerts_count": sum(1 for a in alerts if a.alert_state == "CRITICAL"),
            "warning_alerts_count": sum(1 for a in alerts if a.alert_state == "WARNING"),
            "lead_time_status": lead_time.status,
            "estimated_lead_time_hours": lead_time.estimated_lead_time_hours,
            "backtest_full_auc": backtest_res.full_weighted_index.roc_auc,
            "backtest_rain_auc": backtest_res.rain_only_baseline.roc_auc,
        }
