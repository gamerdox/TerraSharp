# TerraSharp (SH-304) REST API Reference

**Base URL:** `http://127.0.0.1:8000`  
**Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc UI:** `http://127.0.0.1:8000/redoc`

---

## 1. System Health

### `GET /health`
Returns system status, active AOI, and data loading flags.

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "app_name": "SH-304 Hyper-Local Landslide & Flash-Flood Early Warning System",
  "version": "1.0.0",
  "mode": "live",
  "timestamp": "2026-09-13T20:34:00.416Z",
  "data_status": {
    "dem_loaded": true,
    "imerg_loaded": true,
    "glc_loaded": true,
    "villages_loaded": true,
    "active_aoi": "wayanad",
    "last_processed": "2026-09-13T20:34:00.416Z"
  }
}
```

---

## 2. Area of Interest (AOI) Management

### `GET /aoi`
Lists all available pre-configured and dynamically generated AOIs.

**Response (200 OK):**
```json
[
  {
    "id": "wayanad",
    "name": "Wayanad District, Kerala, India",
    "description": "High-hazard Western Ghats terrain prone to monsoon debris flows",
    "bbox": { "min_lon": 75.9, "min_lat": 11.45, "max_lon": 76.35, "max_lat": 11.95 },
    "center": { "lat": 11.7, "lon": 76.08 },
    "default_zoom": 11,
    "elevation_range": [600.0, 2100.0]
  }
]
```

### `GET /aoi/current`
Returns active AOI configuration, bounding box, and last processing timestamp.

### `POST /aoi/select/{aoi_key}`
Switches the active AOI to a registered region.

### `POST /aoi/create_from_pin`
Dynamically creates a new custom AOI centered on any given coordinate, generates georeferenced DEM and rainfall rasters in < 2s, executes the full data-fusion pipeline, and switches the active AOI to it.

**Query Parameters:**
- `lat` (float, required): Latitude of pinned center
- `lon` (float, required): Longitude of pinned center
- `name` (string, optional): Custom display name

**Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "active_aoi": "custom_1155_7615",
  "name": "Custom Region (11.55°, 76.15°)",
  "bbox": {
    "min_lon": 75.9,
    "min_lat": 11.3,
    "max_lon": 76.4,
    "max_lat": 11.8
  },
  "center": {
    "lat": 11.55,
    "lon": 76.15
  },
  "pipeline_result": {
    "aoi": "custom_1155_7615",
    "status": "SUCCESS",
    "villages_analyzed": 6,
    "alerts_generated": 0
  }
}
```

---

## 3. Hazard Risk Endpoints

### `GET /risk`
Returns all 2,500 grid cells for the active AOI with physical attributes and risk scores.

**Response (200 OK):**
```json
{
  "aoi": "wayanad",
  "cells_count": 2500,
  "cells": [
    {
      "lat": 11.455,
      "lon": 75.905,
      "elevation_m": 875.0,
      "slope_deg": 24.3,
      "rainfall_24h_mm": 195.4,
      "soil_proxy": 0.82,
      "landslide_risk": 0.762,
      "landslide_class": "VERY_HIGH",
      "flash_flood_risk": 0.541,
      "flash_flood_class": "HIGH"
    }
  ]
}
```

### `GET /risk/point?lat={lat}&lon={lon}`
Returns explainable factor contributions for a specific grid cell within the active AOI.

**Response (200 OK):**
```json
{
  "lat": 11.55,
  "lon": 76.15,
  "elevation_m": 875.0,
  "slope_deg": 22.1,
  "rainfall_24h_mm": 180.0,
  "soil_proxy": 0.75,
  "landslide_risk": 0.71,
  "landslide_class": "HIGH",
  "factor_contributions": {
    "rainfall": 35.0,
    "slope": 30.0,
    "soil": 20.0,
    "history": 15.0
  }
}
```

### `GET /risk/point/live?lat={lat}&lon={lon}`
Queries live planetary APIs for real-time terrain (Horn 30m stencil), 15-day hourly rainfall, Caine lead time, and evaluates the Physical False-Alarm Mitigation Gate.

**Response (200 OK):**
```json
{
  "latitude": 11.55,
  "longitude": 76.15,
  "elevation_m": 875.0,
  "slope_deg": 18.4,
  "aspect_deg": 242.1,
  "rainfall_24h_mm": 2.8,
  "rainfall_15d_mm": 41.3,
  "current_intensity_mm_hr": 0.0,
  "soil_saturation_proxy": 0.062,
  "landslide_risk": 0.037,
  "risk_class": "LOW",
  "flash_flood_risk": 0.082,
  "caine_threshold": {
    "lead_time_status": "SAFE_MARGIN",
    "estimated_lead_time_hours": 48.0,
    "critical_intensity_mm_hr": 4.29
  },
  "false_alarm_mitigation": {
    "suppressed": false,
    "confidence_pct": 90.0,
    "reason": "Nominal multi-factor evaluation within standard physical bounds."
  }
}
```

---

## 4. Lead-Time & Alert Endpoints

### `GET /leadtime`
Returns Caine (1980) threshold status, current rainfall trend, and projected hours to critical limit.

**Response (200 OK):**
```json
{
  "status": "IMMINENT_APPROACHING",
  "lead_time_hours": 6.4,
  "uncertainty_lower_hours": 4.5,
  "uncertainty_upper_hours": 8.3,
  "current_intensity_mm_hr": 18.5,
  "critical_intensity_mm_hr": 4.29,
  "trend_alpha_mm_hr2": 0.35,
  "model": "Caine (1980) Empirical I-D Threshold"
}
```

### `GET /alerts`
Returns tiered alert items and simulated evacuation decision guidelines.

---

## 5. Settlement & Vector Endpoints

### `GET /villages`
Returns risk summaries for administrative village polygons.

### `GET /villages/geojson`
Returns village boundary polygons in standard GeoJSON format for Leaflet mapping.

---

## 6. Backtesting & Validation

### `GET /backtest`
Returns empirical comparison metrics between the Rainfall-Only Baseline and the Full Weighted Risk Index.

**Response (200 OK):**
```json
{
  "aoi": "wayanad",
  "baseline_metrics": {
    "false_alarm_rate": 0.542,
    "roc_auc": 0.68,
    "pr_auc": 0.52
  },
  "weighted_index_metrics": {
    "false_alarm_rate": 0.187,
    "roc_auc": 0.89,
    "pr_auc": 0.81
  },
  "performance_gain": {
    "far_reduction_pct": 65.5,
    "roc_auc_gain_pct": 30.9
  }
}
```

---

## 7. Reports & Situation Summaries

### `GET /reports`
Generates an operational Situation Report (SITREP) in structured JSON.
