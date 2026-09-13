"""
Pydantic schemas for API inputs and outputs.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.models.domain import RiskLevel, AlertState, HazardType, ProvenanceTag


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    mode: str  # "demo" or "live"
    timestamp: datetime
    data_status: Dict[str, Any]


class AOIInfo(BaseModel):
    id: str
    name: str
    description: str
    bbox: Dict[str, float]
    center: Dict[str, float]
    default_zoom: int
    elevation_range: List[float]


class CustomAOIRequest(BaseModel):
    name: str
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class IngestStatusResponse(BaseModel):
    layer: str
    status: str
    provenance: ProvenanceTag
    records_or_cells: int
    source_url: str
    timestamp: datetime
    message: str


class ContributingFactors(BaseModel):
    rainfall_score: float
    slope_score: float
    soil_proxy_score: float
    history_score: float
    weights_used: Dict[str, float]
    dominant_factor: str
    explanation: str


class GridCellRisk(BaseModel):
    lat: float
    lon: float
    landslide_risk: float
    landslide_class: RiskLevel
    flash_flood_risk: float
    flash_flood_class: RiskLevel
    elevation_m: float
    slope_deg: float
    rainfall_24h_mm: float
    rainfall_3d_mm: float
    rainfall_15d_mm: float
    soil_saturation_proxy: float
    flow_accumulation: float
    historical_density: float
    factors: ContributingFactors
    provenance: Dict[str, ProvenanceTag]


class RiskRasterSummary(BaseModel):
    aoi_id: str
    timestamp: datetime
    grid_rows: int
    grid_cols: int
    cell_size_deg: float
    bounds: List[float]
    max_landslide_risk: float
    mean_landslide_risk: float
    high_risk_cells_count: int
    provenance_summary: Dict[str, str]


class LeadTimeEvaluation(BaseModel):
    location: Optional[Dict[str, float]] = None
    current_intensity_mm_hr: float
    duration_hours: float
    caine_threshold_intensity_mm_hr: float
    rainfall_trend_alpha_mm_hr2: float
    estimated_lead_time_hours: Optional[float] = None
    uncertainty_range_hours: Optional[List[float]] = None
    status: str  # "THRESHOLD_BREACHED", "APPROACHING_THRESHOLD", "STABLE_BELOW_THRESHOLD"
    scientific_disclaimer: str
    formula: str


class AlertItem(BaseModel):
    alert_id: str
    location_name: str
    coordinates: Dict[str, float]
    hazard_type: HazardType
    alert_state: AlertState
    risk_score: float
    risk_class: RiskLevel
    estimated_lead_time_hours: Optional[float]
    confidence_score: float  # 0.0 - 1.0 based on data completeness
    contributing_factors: ContributingFactors
    recommended_action: str
    simulated: bool = True  # strictly simulated in MVP
    timestamp: datetime
    data_provenance: Dict[str, ProvenanceTag]


class VillageRiskSummary(BaseModel):
    village_id: str
    name: str
    area_sqkm: float
    mean_landslide_risk: float
    max_landslide_risk: float
    mean_flash_flood_risk: float
    max_flash_flood_risk: float
    risk_class: RiskLevel
    alert_state: AlertState
    critical_area_pct: float
    dominant_factor: str
    recommended_action: str
    coordinates_center: Dict[str, float]


class ModelPerformanceMetrics(BaseModel):
    model_name: str
    precision: float
    recall: float
    f1_score: float
    false_alarm_rate: float
    roc_auc: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


class BacktestComparisonResponse(BaseModel):
    aoi_id: str
    evaluation_date: datetime
    sample_events_count: int
    non_event_controls_count: int
    rain_only_baseline: ModelPerformanceMetrics
    full_weighted_index: ModelPerformanceMetrics
    comparison_summary: str
    scientific_note: str


class SystemHealthDataStatus(BaseModel):
    dem_loaded: bool
    imerg_loaded: bool
    glc_loaded: bool
    villages_loaded: bool
    mode: str
