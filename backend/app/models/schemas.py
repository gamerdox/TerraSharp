"""
Pydantic schemas for API inputs and outputs.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.models.domain import (
    RiskLevel,
    AlertState,
    HazardType,
    ProvenanceTag,
    EmailStatus,
    DataFreshnessStatus,
)


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
    simulated: bool = False
    timestamp: datetime
    data_provenance: Dict[str, ProvenanceTag]
    email_status: Optional[EmailStatus] = None
    trigger_reason: Optional[str] = None
    persistence_count: Optional[int] = 1
    data_freshness: Optional[str] = "FRESH"


class AlertTransitionItem(BaseModel):
    transition_id: str
    village_id: str
    location_name: str
    from_state: AlertState
    to_state: AlertState
    risk_score: float
    hazard_type: HazardType
    trigger_reason: str
    timestamp: datetime
    email_status: EmailStatus
    recipients_count: int
    data_freshness: str


class EmailDispatchRecord(BaseModel):
    dispatch_id: str
    alert_id: str
    village_name: str
    severity: AlertState
    hazard_type: HazardType
    recipient: str
    subject: str
    status: EmailStatus
    timestamp: datetime
    error_message: Optional[str] = None
    retry_count: int = 0
    simulated: bool = False


class TestEmailRequest(BaseModel):
    recipient_email: Optional[str] = None
    severity: AlertState = AlertState.WARNING
    village_name: str = "Wayanad Sector 4"


class TestEmailResponse(BaseModel):
    status: EmailStatus
    message: str
    dispatch_record: Optional[EmailDispatchRecord] = None


class DataHealthItem(BaseModel):
    layer_name: str
    status: DataFreshnessStatus
    source_url: str
    last_updated: Optional[datetime] = None
    freshness_minutes: Optional[float] = None
    provenance: ProvenanceTag
    records_or_cells: int = 0
    message: str


class DataHealthResponse(BaseModel):
    overall_status: DataFreshnessStatus
    evaluated_at: datetime
    active_aoi: str
    layers: Dict[str, DataHealthItem]



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


class FalseAlarmMitigation(BaseModel):
    suppressed: bool
    status_message: str
    confidence_score_pct: float
    false_alarm_risk_pct: float


class CaineThresholdInfo(BaseModel):
    critical_intensity_mm_hr: float
    intensity_ratio: float
    status: str
    estimated_lead_time_hours: float


class PinPointLiveResponse(BaseModel):
    latitude: float
    longitude: float
    elevation_m: float
    slope_deg: float
    slope_pct: Optional[float] = None
    slope_norm: Optional[float] = None
    aspect_deg: float
    rainfall_24h_mm: float
    rainfall_3d_mm: float
    rainfall_15d_mm: float
    current_intensity_mm_hr: float
    soil_saturation_proxy: float
    soil_saturation_pct: float
    landslide_risk: float
    flash_flood_risk: float
    risk_class: RiskLevel
    alert_state: AlertState
    caine_threshold: CaineThresholdInfo
    false_alarm_mitigation: FalseAlarmMitigation
    dominant_factor: str
    data_provenance: Dict[str, Any]
