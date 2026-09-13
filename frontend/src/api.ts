/**
 * API Client service for SH-304 Early Warning System Backend.
 */
import {
  AOIInfo,
  GridCell,
  PointRiskDetail,
  LeadTimeEvaluation,
  AlertItem,
  VillageRiskSummary,
  BacktestComparison,
  SystemHealth,
  PinPointLiveResult,
} from "./types";

const API_BASE = "http://127.0.0.1:8000";

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchAOIs(): Promise<AOIInfo[]> {
  const res = await fetch(`${API_BASE}/aoi`);
  if (!res.ok) throw new Error(`Failed to fetch AOIs: ${res.statusText}`);
  return res.json();
}

export async function switchAOI(aoiId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/aoi/select/${aoiId}`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to switch AOI: ${res.statusText}`);
}

export async function triggerPipeline(aoiId?: string): Promise<any> {
  const url = aoiId ? `${API_BASE}/process?aoi=${aoiId}` : `${API_BASE}/process`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to process pipeline: ${res.statusText}`);
  return res.json();
}

export async function fetchRiskGrid(): Promise<{
  aoi: string;
  summary: any;
  grid_meta: any;
  cells: GridCell[];
}> {
  const res = await fetch(`${API_BASE}/risk`);
  if (!res.ok) throw new Error(`Failed to fetch risk grid: ${res.statusText}`);
  return res.json();
}

export async function fetchPointRisk(lat: number, lon: number): Promise<PointRiskDetail> {
  const res = await fetch(`${API_BASE}/risk/point?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`Failed to query point risk: ${res.statusText}`);
  return res.json();
}

export async function fetchLeadTime(): Promise<LeadTimeEvaluation> {
  const res = await fetch(`${API_BASE}/leadtime`);
  if (!res.ok) throw new Error(`Failed to fetch lead-time: ${res.statusText}`);
  return res.json();
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error(`Failed to fetch alerts: ${res.statusText}`);
  return res.json();
}

export async function fetchVillages(): Promise<VillageRiskSummary[]> {
  const res = await fetch(`${API_BASE}/villages`);
  if (!res.ok) throw new Error(`Failed to fetch villages: ${res.statusText}`);
  return res.json();
}

export async function fetchVillagesGeoJSON(): Promise<any> {
  const res = await fetch(`${API_BASE}/villages/geojson`);
  if (!res.ok) throw new Error(`Failed to fetch villages GeoJSON: ${res.statusText}`);
  return res.json();
}

export async function fetchBacktest(): Promise<BacktestComparison> {
  const res = await fetch(`${API_BASE}/backtest`);
  if (!res.ok) throw new Error(`Failed to fetch backtest results: ${res.statusText}`);
  return res.json();
}

export async function fetchSituationReport(): Promise<any> {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error(`Failed to fetch situation report: ${res.statusText}`);
  return res.json();
}

export async function fetchLivePinpoint(lat: number, lon: number): Promise<PinPointLiveResult> {
  const res = await fetch(`${API_BASE}/risk/point/live?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`Failed to fetch live pinpoint prediction: ${res.statusText}`);
  return res.json();
}

export async function createAoiFromPin(lat: number, lon: number, name?: string): Promise<any> {
  const query = name ? `lat=${lat}&lon=${lon}&name=${encodeURIComponent(name)}` : `lat=${lat}&lon=${lon}`;
  const res = await fetch(`${API_BASE}/aoi/create_from_pin?${query}`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to generate AOI grid: ${res.statusText}`);
  return res.json();
}
