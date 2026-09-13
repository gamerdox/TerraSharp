export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "VERY_HIGH";
export type AlertState = "NORMAL" | "WATCH" | "WARNING" | "CRITICAL";
export type HazardType = "LANDSLIDE" | "FLASH_FLOOD" | "MULTI_HAZARD";
export type ProvenanceTag = "OBSERVED" | "DERIVED" | "PROXY" | "MODELLED" | "ESTIMATED" | "DEMO";

export interface AOIInfo {
  id: string;
  name: string;
  description: string;
  bbox: {
    min_lon: number;
    min_lat: number;
    max_lon: number;
    max_lat: number;
  };
  center: {
    lat: number;
    lon: number;
  };
  default_zoom: number;
  elevation_range: number[];
}

export interface ContributingFactors {
  rainfall_score: number;
  slope_score: number;
  soil_proxy_score: number;
  history_score: number;
  weights_used: Record<string, number>;
  dominant_factor: string;
  explanation: string;
}

export interface GridCell {
  lat: number;
  lon: number;
  landslide_risk: number;
  landslide_class: RiskLevel;
  flash_flood_risk: number;
  flash_flood_class: RiskLevel;
  elevation_m: number;
  slope_deg: number;
  rainfall_24h_mm: number;
  soil_proxy: number;
}

export interface PointRiskDetail {
  lat: number;
  lon: number;
  landslide_risk: number;
  landslide_class: RiskLevel;
  flash_flood_risk: number;
  flash_flood_class: RiskLevel;
  elevation_m: number;
  slope_deg: number;
  rainfall_24h_mm: number;
  rainfall_3d_mm: number;
  rainfall_15d_mm: number;
  soil_saturation_proxy: number;
  flow_accumulation: number;
  historical_density: number;
  factors: ContributingFactors;
  provenance: Record<string, ProvenanceTag>;
}

export interface LeadTimeEvaluation {
  location?: { lat: number; lon: number };
  current_intensity_mm_hr: number;
  duration_hours: number;
  caine_threshold_intensity_mm_hr: number;
  rainfall_trend_alpha_mm_hr2: number;
  estimated_lead_time_hours: number | null;
  uncertainty_range_hours: number[] | null;
  status: "THRESHOLD_BREACHED" | "APPROACHING_THRESHOLD" | "STABLE_BELOW_THRESHOLD";
  scientific_disclaimer: string;
  formula: string;
}

export interface AlertItem {
  alert_id: string;
  location_name: string;
  coordinates: { lat: number; lon: number };
  hazard_type: HazardType;
  alert_state: AlertState;
  risk_score: number;
  risk_class: RiskLevel;
  estimated_lead_time_hours: number | null;
  confidence_score: number;
  contributing_factors: ContributingFactors;
  recommended_action: string;
  simulated: boolean;
  timestamp: string;
  data_provenance: Record<string, ProvenanceTag>;
}

export interface VillageRiskSummary {
  village_id: string;
  name: string;
  area_sqkm: number;
  mean_landslide_risk: number;
  max_landslide_risk: number;
  mean_flash_flood_risk: number;
  max_flash_flood_risk: number;
  risk_class: RiskLevel;
  alert_state: AlertState;
  critical_area_pct: number;
  dominant_factor: string;
  recommended_action: string;
  coordinates_center: { lat: number; lon: number };
}

export interface ModelPerformanceMetrics {
  model_name: string;
  precision: number;
  recall: number;
  f1_score: number;
  false_alarm_rate: number;
  roc_auc: number;
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
}

export interface BacktestComparison {
  aoi_id: string;
  evaluation_date: string;
  sample_events_count: number;
  non_event_controls_count: number;
  rain_only_baseline: ModelPerformanceMetrics;
  full_weighted_index: ModelPerformanceMetrics;
  comparison_summary: string;
  scientific_note: string;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  mode: string;
  timestamp: string;
  data_status: {
    dem_loaded: boolean;
    imerg_loaded: boolean;
    glc_loaded: boolean;
    villages_loaded: boolean;
    active_aoi: string;
    last_processed: string | null;
  };
}

export interface FalseAlarmMitigation {
  suppressed: boolean;
  status_message: string;
  confidence_score_pct: number;
  false_alarm_risk_pct: number;
}

export interface CaineThresholdInfo {
  critical_intensity_mm_hr: number;
  intensity_ratio: number;
  status: string;
  estimated_lead_time_hours: number;
}

export interface PinPointLiveResult {
  latitude: number;
  longitude: number;
  elevation_m: number;
  slope_deg: number;
  aspect_deg: number;
  rainfall_24h_mm: number;
  rainfall_3d_mm: number;
  rainfall_15d_mm: number;
  current_intensity_mm_hr: number;
  soil_saturation_proxy: number;
  soil_saturation_pct: number;
  landslide_risk: number;
  flash_flood_risk: number;
  risk_class: RiskLevel;
  alert_state: AlertState;
  caine_threshold: CaineThresholdInfo;
  false_alarm_mitigation: FalseAlarmMitigation;
  dominant_factor: string;
  data_provenance: {
    terrain: string;
    rainfall: string;
    terrain_source: string;
    rainfall_source: string;
    fetched_at: string;
  };
}
