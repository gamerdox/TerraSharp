# Implementation Plan - SH-304: Hyper-Local Landslide & Flash-Flood Warning System

## Goal Description
Build a complete MVP and near-production prototype from scratch for **SH-304: Hyper-Local Landslide & Flash-Flood Early Warning System**. 
The system ingests and fuses NASA GPM IMERG rainfall, SRTM GL1 30m DEM terrain, NASA Global Landslide Catalog (GLC) historical records, and village administrative boundaries. It derives terrain slopes and flow accumulations, computes 3-day and 15-day soil-saturation proxies, evaluates transparent weighted risk indices for landslides and flash floods, projects lead time via the Caine (1980) empirical intensity-duration threshold ($I = 14.82 \times D^{-0.39}$), generates tiered alerts (NORMAL, WATCH, WARNING, CRITICAL), aggregates grid-level risk to village polygons, runs historical back-testing comparing RAINFALL-ONLY vs FULL WEIGHTED models, and presents the results via a FastAPI backend and interactive React + Leaflet dashboard.

---

## User Review Required

> [!IMPORTANT]
> **Project Directory**: The system will be created in `C:\Users\Vanaparthi\.gemini\antigravity\scratch\sh304-landslide-warning`. Once created, you may set this directory as your active workspace.

> [!IMPORTANT]
> **Scientific Honesty & Proxy Disclaimers**:
> - **Soil Saturation**: Strictly labeled as `PROXY` computed from 3-day and 15-day antecedent rainfall.
> - **Lead Time**: Evaluated via the Caine (1980) global reference threshold ($I = 14.82 \times D^{-0.39}$) under current rainfall rate of increase; strictly labeled as "Estimated time to threshold under current rainfall trend" (never a guaranteed event time).
> - **Missing Historical Data**: Documented neutral AOI-median imputation strategy is used (never assumed to be zero hazard).
> - **Evacuation Alerts**: Clearly labeled as `SIMULATED` early-warning actions (no real SMS/WhatsApp dispatch).
> - **Data Provenance**: Every output tag explicitly marks inputs as `OBSERVED`, `DERIVED`, `PROXY`, `MODELLED`, `ESTIMATED`, or `DEMO`.

---

## Proposed Architecture & File Structure

```
sh304-landslide-warning/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entry point & CORS
│   │   ├── config.py                # Pydantic BaseSettings, weights, thresholds
│   │   ├── models/
│   │   │   ├── schemas.py           # Request/response Pydantic models
│   │   │   └── domain.py            # Domain types (RiskLevel, AlertState, ProvenanceTag)
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── nasa_gpm.py          # NASA Earthdata earthaccess IMERG client + deterministic fallback
│   │   │   ├── dem_ingest.py        # SRTM GL1 30m DEM fetcher + deterministic fallback
│   │   │   ├── glc_ingest.py        # NASA Global Landslide Catalog parser + demo events
│   │   │   └── boundaries.py        # Village & admin boundary loader (GeoJSON/Shapefile)
│   │   ├── preprocessing/
│   │   │   ├── __init__.py
│   │   │   ├── grid.py              # Common analysis grid builder (~1km default or configurable)
│   │   │   ├── raster_ops.py        # Resampling, reprojection (EPSG:4326/UTM), clipping
│   │   │   └── normalization.py     # Min-max scaling [0, 1], clipping, neutral missing imputation
│   │   ├── terrain/
│   │   │   ├── __init__.py
│   │   │   ├── slope.py             # Finite-difference Horn / Zevenbergen-Thorne slope & aspect
│   │   │   └── drainage.py          # D8 flow direction & flow accumulation for valley identification
│   │   ├── rainfall/
│   │   │   ├── __init__.py
│   │   │   ├── imerg_processor.py   # Daily rainfall, intensity, 3-day & 15-day accumulations
│   │   │   └── trend.py             # Rainfall rate of increase (dI/dt)
│   │   ├── soil/
│   │   │   ├── __init__.py
│   │   │   └── proxy.py             # Antecedent Soil Moisture Proxy: f(R_3d, R_15d) with decay
│   │   ├── history/
│   │   │   ├── __init__.py
│   │   │   └── density.py           # Kernel density / grid spatial density of NASA GLC landslides
│   │   ├── scoring/
│   │   │   ├── __init__.py
│   │   │   ├── weighted_index.py    # Transparent weighted risk formula + factor breakdown
│   │   │   ├── flash_flood.py       # Flash-flood index: rainfall accumulation + drainage/slope concavity
│   │   │   └── classifier.py        # LOW, MODERATE, HIGH, VERY HIGH categorization
│   │   ├── leadtime/
│   │   │   ├── __init__.py
│   │   │   └── caine_threshold.py   # Caine (1980) I = 14.82 * D^-0.39 threshold & trend projection
│   │   ├── alerts/
│   │   │   ├── __init__.py
│   │   │   └── engine.py            # NORMAL, WATCH, WARNING, CRITICAL alert generation & action protocols
│   │   ├── aggregation/
│   │   │   ├── __init__.py
│   │   │   └── village.py           # Grid-to-village spatial aggregation (mean, max, % critical area)
│   │   ├── backtest/
│   │   │   ├── __init__.py
│   │   │   └── evaluator.py         # NASA GLC validation: Confusion matrix, Precision, Recall, ROC-AUC, Rain-Only vs Full Index
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── routes_aoi.py        # /aoi endpoints
│   │       ├── routes_ingest.py     # Ingestion triggers (/ingest/rainfall, /ingest/dem, /ingest/history)
│   │       ├── routes_process.py    # End-to-end pipeline trigger (/process)
│   │       ├── routes_risk.py       # Grid & location risk queries (/risk, /risk/{location})
│   │       ├── routes_leadtime.py   # Lead-time query (/leadtime)
│   │       ├── routes_alerts.py     # Active alerts (/alerts)
│   │       ├── routes_villages.py   # Village-level risk & polygon GeoJSON (/villages)
│   │       ├── routes_backtest.py   # Back-testing results & model comparison (/backtest)
│   │       └── routes_reports.py    # Summary reports & GeoJSON/CSV export (/reports)
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── types/api.ts
│       ├── services/apiClient.ts
│       └── components/
│           ├── Header.tsx           # Title, Live vs Demo badge, mode toggle, system status
│           ├── MapView.tsx          # Leaflet map with GeoJSON village overlays, raster grid heatmaps, GLC markers
│           ├── LayerControls.tsx    # Toggle Landslide Risk, Flash-Flood Risk, Slope, Rainfall, Villages, GLC
│           ├── AOISelector.tsx      # Pre-loaded high-hazard AOIs (e.g. Wayanad Kerala, Chamoli Uttarakhand) + custom bbox
│           ├── RiskFactorCard.tsx   # Explainable factor breakdown (Rainfall, Slope, Soil Proxy, History)
│           ├── LeadTimeGauge.tsx    # Caine (1980) threshold curve, current operating point, estimated time to threshold
│           ├── AlertsPanel.tsx      # Filterable list of simulated alerts with action recommendations
│           ├── VillageDetailModal.tsx # Inspection of specific village: population, mean/max risk, dominant factor
│           ├── BacktestView.tsx     # Confusion matrix, Precision/Recall, Rain-only vs Full Index comparison charts
│           ├── ProvenanceModal.tsx  # Transparent dataset lineage (source URLs, resolutions, status tags)
│           └── ExportModal.tsx      # Export report in JSON, GeoJSON, or Markdown
├── data/
│   ├── raw/                         # Downloaded original GeoTIFFs, GLC CSVs, GeoJSONs
│   ├── processed/                   # Normalized aligned grids
│   ├── cache/                       # Cached Earthdata queries
│   └── demo/                        # Pre-packaged deterministic offline datasets
│       ├── aoi_wayanad/             # High-risk Western Ghats region (Kerala)
│       │   ├── dem.tif              # SRTM GL1 30m DEM clip
│       │   ├── rainfall_series.json # IMERG daily rainfall series (recent 15 days + storm event)
│       │   ├── glc_events.geojson   # Historical NASA GLC landslide events in AOI
│       │   └── villages.geojson     # Village administrative boundaries
│       └── aoi_chamoli/             # Himalayan high-risk region (Uttarakhand)
│           ├── dem.tif
│           ├── rainfall_series.json
│           ├── glc_events.geojson
│           └── villages.geojson
├── configs/
│   ├── default_config.yaml          # Default AOI, grid resolution (0.01 deg ~ 1.1 km), thresholds
│   └── risk_weights.yaml            # Configurable weights (w_rainfall=0.35, w_slope=0.30, w_soil=0.20, w_history=0.15)
├── scripts/
│   ├── run_pipeline_cli.py          # Standalone CLI to execute the pipeline end-to-end
│   └── seed_demo_data.py            # Generates realistic, georeferenced synthetic DEM, IMERG, GLC demo data
├── tests/
│   ├── test_grid.py                 # Common grid coordinate alignment tests
│   ├── test_terrain.py              # Slope and flow accumulation correctness
│   ├── test_rainfall.py             # 3-day, 15-day rolling windows, intensity
│   ├── test_soil_proxy.py           # Antecedent soil moisture decay logic
│   ├── test_scoring.py              # Weighted risk index bounds [0, 1] & factor weights
│   ├── test_leadtime.py             # Caine formula evaluation & trend extrapolation
│   ├── test_alerts.py               # Alert state transitions & confidence scoring
│   ├── test_village_agg.py          # Spatial join and grid-to-village aggregation
│   ├── test_backtest.py             # Model evaluation: Rain-only vs Full Index
│   └── test_api.py                  # FastAPI route responses & Pydantic validation
├── docs/
│   ├── README.md                    # Project overview, quickstart, system features
│   ├── ARCHITECTURE.md              # Technical pipeline diagrams & dataflow
│   ├── DATA_SOURCES.md              # GPM IMERG, SRTM, GLC, ISRO/NRSC, GSI metadata & licenses
│   ├── METHODOLOGY.md               # Mathematical equations, Caine 1980, flow accumulation, weights
│   ├── API.md                       # Complete REST API reference with payload examples
│   ├── LIMITATIONS.md               # Explicit scientific boundaries, proxy caveats, false alarm rates
│   ├── DEPLOYMENT.md                # Docker containerization, environment setup
│   └── DEMO_GUIDE.md                # Step-by-step walkthrough of deterministic demo scenarios
├── IMPLEMENTATION_STATUS.md         # Continuously updated feature status tracking
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Detailed Methodological & Scientific Specifications

### 1. Analysis Grid & Alignment
- **CRS**: Standardized on `EPSG:4326` (WGS84) with projection to appropriate UTM zone (e.g. `EPSG:32643` for Western Ghats, `EPSG:32644` for Uttarakhand) during spatial metric calculations (slope in degrees, flow accumulation in meters).
- **Resolution**: Grid cells of $0.01^\circ \times 0.01^\circ$ (approx. $1.1\text{ km} \times 1.1\text{ km}$), matching GPM IMERG native grid scale or resampled higher where DEM demands.
- **Resampling**: Bilinear interpolation for continuous DEM elevation; nearest-neighbor for categorical; conservative area-weighted aggregation for rainfall.

### 2. Terrain Metrics
- **Slope ($S$)**: Horn's finite-difference method:
  $$\text{Slope} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180}{\pi}$$
  Normalized: $S_{\text{norm}} = \text{clip}\left(\frac{S}{60^\circ}, 0, 1\right)$ (slopes above $60^\circ$ saturate hazard).
- **Drainage & Flow Accumulation ($A$)**:
  - D8 flow direction algorithm to route steepest downhill flow.
  - Flow accumulation raster tracks upslope contributing cell count.
  - Flash-flood topographic concavity: High flow accumulation + lower slope valleys = peak flash flood hazard.

### 3. Rainfall Features (NASA GPM IMERG v07)
- $R_{24h}$: Recent 24-hour rainfall (mm).
- $I_{recent}$: Recent rainfall intensity ($\text{mm/hr}$).
- $R_{3d}$: 3-day cumulative rainfall ($\text{mm}$).
- $R_{15d}$: 15-day cumulative antecedent rainfall ($\text{mm}$).
- Trend: $\frac{dR}{dt}$ (rate of increase in $\text{mm/hr}^2$).

### 4. Soil-Saturation Proxy (Explicitly labeled `PROXY`)
- Soil moisture is approximated by the Antecedent Moisture Index ($AMI$):
  $$AMI = R_{3d} \cdot 0.6 + R_{15d} \cdot 0.4 \cdot e^{-15 / k_\tau}$$
  Normalized to $[0, 1]$ via AOI historical wet-season 95th percentile clipping.

### 5. Historical Landslide Density (NASA GLC)
- Kernel Density Estimation (Gaussian kernel, radius $5\text{ km}$) of historical landslide occurrences from NASA GLC.
- Imputation for zero/unreported cells: Uses median AOI baseline to avoid treating lack of records as absence of hazard.

### 6. Explainable Weighted Risk Index
$$R_{\text{landslide}} = w_{\text{rain}} \cdot S_{\text{rain}} + w_{\text{slope}} \cdot S_{\text{slope}} + w_{\text{soil}} \cdot S_{\text{soil}} + w_{\text{history}} \cdot S_{\text{history}}$$
Default weights (versioned in `configs/risk_weights.yaml` v1.0.0):
- $w_{\text{rain}} = 0.35$
- $w_{\text{slope}} = 0.30$
- $w_{\text{soil}} = 0.20$
- $w_{\text{history}} = 0.15$
*(Sum = 1.00)*

Flash-Flood Index:
$$R_{\text{flash\_flood}} = 0.50 \cdot S_{\text{rain\_24h}} + 0.35 \cdot S_{\text{flow\_accum}} + 0.15 \cdot (1 - S_{\text{slope}})$$
*(Flat valley bottoms with massive upstream drainage and torrential rain receive the highest flash-flood risk)*.

**Risk Classification**:
- $[0.00, 0.25) \rightarrow$ **LOW** (Green)
- $[0.25, 0.50) \rightarrow$ **MODERATE** (Yellow)
- $[0.50, 0.75) \rightarrow$ **HIGH** (Orange)
- $[0.75, 1.00] \rightarrow$ **VERY HIGH / CRITICAL** (Red)

### 7. Lead-Time Estimation (Caine 1980 Threshold)
- Reference threshold:
  $$I_{\text{crit}} = 14.82 \times D^{-0.39}$$
  where $I_{\text{crit}}$ is critical mean intensity ($\text{mm/hr}$) over duration $D$ (hours).
- Under current rainfall trend $I(t) = I_0 + \alpha t$, lead time to breach:
  $$T_{\text{lead}} = \frac{I_{\text{crit}}(D) - I_0}{\alpha} \quad (\text{if } \alpha > 0 \text{ and } I_0 < I_{\text{crit}})$$
- Output clearly formatted: *"Estimated lead time to threshold under current rainfall trend: ~X.X hours (Uncertainty: ±30%, Reference: Caine 1980 Global Model)"*.

### 8. Back-Testing & Baseline Comparison
- Tests historical NASA GLC events within the AOI against non-event control days/points.
- Calculates Confusion Matrix, Precision, Recall, F1-Score, False Alarm Rate (FAR), and ROC-AUC.
- **Mandatory Comparison Table**:
  | Metric | Rain-Only Baseline | Full Weighted Risk Index | $\Delta$ Improvement |
  |---|---|---|---|
  | Precision | ... | ... | ... |
  | Recall | ... | ... | ... |
  | False Alarm Rate | ... | ... | ... |
  | ROC-AUC | ... | ... | ... |

---

## Verification Plan

### Automated Tests
1. Unit tests:
   ```bash
   python -m pytest tests/ -v
   ```
   - Grid CRS reprojection & cell dimension assertions.
   - Horn slope computation against known analytical planar slopes.
   - D8 flow direction routing & accumulation conservation.
   - Rolling rainfall window aggregations (3-day, 15-day).
   - Soil saturation proxy decay calculation.
   - Caine (1980) threshold inversion & trend extrapolation.
   - Alert state machine transitions (NORMAL $\rightarrow$ WATCH $\rightarrow$ WARNING $\rightarrow$ CRITICAL).
   - Spatial join & village boundary aggregation.
   - Full weighted model vs Rain-only model backtest evaluation.
2. API endpoint integration tests:
   ```bash
   python -m pytest tests/test_api.py -v
   ```
   - `/health`, `/aoi`, `/ingest/*`, `/process`, `/risk`, `/leadtime`, `/alerts`, `/villages`, `/backtest`, `/reports`.

### Manual & Interactive Verification
1. Standalone Pipeline Run:
   ```bash
   python scripts/run_pipeline_cli.py --aoi wayanad --mode demo
   ```
   Verifies end-to-end grid generation, GeoTIFF creation, village scoring, and alert generation.
2. Dashboard Verification:
   - Run FastAPI backend on port 8000.
   - Run Vite + React frontend on port 5173.
   - Switch between Wayanad and Chamoli AOIs.
   - Toggle between Landslide Risk, Flash Flood Risk, Slope, Rainfall, and Soil Proxy layers.
   - Click on individual villages and grid cells to inspect explainable contributing factors.
   - Review Alert Table with simulated evacuation guidelines.
   - View Backtest modal comparing Rain-only vs Full Weighted model.
   - Export summary reports in GeoJSON and JSON formats.
