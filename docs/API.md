# SH-304 REST API Documentation

Base URL: `http://127.0.0.1:8000`  
Interactive OpenAPI Documentation: `http://127.0.0.1:8000/docs`  
Alternative ReDoc: `http://127.0.0.1:8000/redoc`

---

## 1. System & Health Endpoints

### `GET /health`
Returns system operational status, dataset loading flags, and active configuration.

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "app_name": "SH-304 Hyper-Local Landslide & Flash-Flood Early Warning System",
  "version": "1.0.0",
  "mode": "demo",
  "timestamp": "2026-09-13T04:00:00.000Z",
  "data_status": {
    "dem_loaded": true,
    "imerg_loaded": true,
    "glc_loaded": true,
    "villages_loaded": true,
    "active_aoi": "wayanad",
    "last_processed": "2026-09-13T03:50:16.339Z"
  }
}
```

---

## 2. Area of Interest (AOI) Endpoints

### `GET /aoi`
Lists all available pre-configured AOIs.

### `GET /aoi/current`
Returns active AOI details, bounding box, and center coordinate.

### `POST /aoi/select/{aoi_key}`
Switches the active AOI (e.g. `wayanad` or `chamoli`).

---

## 3. Data Ingestion Endpoints

### `POST /ingest/rainfall?aoi={aoi_key}`
Triggers IMERG precipitation ingestion (via Earthdata or offline demo).

### `POST /ingest/dem?aoi={aoi_key}`
Triggers SRTM GL1 30m DEM ingestion.

### `POST /ingest/history?aoi={aoi_key}`
Triggers NASA GLC historical inventory ingestion.

---

## 4. Pipeline Execution Endpoint

### `POST /process?aoi={aoi_key}`
Executes the full data-fusion pipeline end-to-end for the specified AOI.

**Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "aoi": "wayanad",
  "processed_at": "2026-09-13T03:50:16.339Z",
  "grid_info": {
    "crs": "EPSG:4326",
    "utm_epsg": 32643,
    "rows": 50,
    "cols": 55,
    "resolution_deg": 0.01,
    "approx_dx_meters": 1085.71,
    "approx_dy_meters": 1110.11,
    "approx_cell_area_sqkm": 1.2053
  },
  "villages_analyzed": 10,
  "alerts_generated": 10,
  "critical_alerts_count": 8,
  "warning_alerts_count": 2,
  "lead_time_status": "THRESHOLD_BREACHED",
  "estimated_lead_time_hours": 0.0,
  "backtest_full_auc": 0.972,
  "backtest_rain_auc": 0.583
}
```

---

## 5. Risk & Explainability Endpoints

### `GET /risk`
Returns all analysis grid cells with multi-hazard scores for map heatmaps.

### `GET /risk/point?lat={float}&lon={float}`
Returns an exact, explainable factor breakdown for a specific coordinate.

**Response (200 OK):**
```json
{
  "lat": 11.50,
  "lon": 76.15,
  "landslide_risk": 0.812,
  "landslide_class": "VERY_HIGH",
  "flash_flood_risk": 0.624,
  "flash_flood_class": "HIGH",
  "elevation_m": 1280.5,
  "slope_deg": 38.4,
  "rainfall_24h_mm": 245.0,
  "rainfall_3d_mm": 410.0,
  "rainfall_15d_mm": 950.0,
  "soil_saturation_proxy": 0.885,
  "flow_accumulation": 142.0,
  "historical_density": 0.720,
  "factors": {
    "rainfall_score": 0.92,
    "slope_score": 0.70,
    "soil_proxy_score": 0.88,
    "history_score": 0.72,
    "weights_used": {
      "w_rainfall": 0.35,
      "w_slope": 0.30,
      "w_soil": 0.20,
      "w_history": 0.15
    },
    "dominant_factor": "Heavy Rainfall",
    "explanation": "Evaluated as VERY_HIGH risk (0.81). The primary hazard driver is Heavy Rainfall..."
  },
  "provenance": {
    "elevation": "DEMO",
    "slope": "DERIVED",
    "rainfall": "DEMO",
    "soil_proxy": "PROXY",
    "historical_density": "DEMO",
    "landslide_risk": "MODELLED",
    "flash_flood_risk": "MODELLED"
  }
}
```

---

## 6. Lead-Time Endpoints

### `GET /leadtime`
Returns Caine (1980) empirical threshold and trend projection.

---

## 7. Alerts & Village Boundaries Endpoints

### `GET /alerts`
Returns active settlement alerts with simulated evacuation guidance.

### `GET /villages`
Returns village metrics (mean risk, max risk, % critical area, dominant trigger).

### `GET /villages/geojson`
Returns enriched GeoJSON FeatureCollection for direct Leaflet rendering.

---

## 8. Back-Testing Endpoints

### `GET /backtest`
Returns empirical comparison metrics: Rain-Only Baseline vs Full Weighted Index.

---

## 9. Reports & Export Endpoints

### `GET /reports`
Generates comprehensive situation assessment report in JSON.

### `GET /reports/markdown`
Downloads the formatted Situation Assessment Report as a Markdown document.
