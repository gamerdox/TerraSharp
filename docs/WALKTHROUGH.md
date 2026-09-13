# Walkthrough: SH-304 Hyper-Local Landslide & Flash-Flood Warning System

The **SH-304 Hyper-Local Landslide & Flash-Flood Early Warning System** has been built completely from scratch in:
`C:\Users\Vanaparthi\.gemini\antigravity\scratch\sh304-landslide-warning`

---

## 1. Accomplishments & Delivered Components

### 1.1 Core Geospatial Data-Fusion Pipeline
- **Analysis Grid & Reprojection:** Uniform common analysis grid (`0.01°` ~ `1.1 km`) matching GPM IMERG scale with localized UTM projections (`EPSG:32643` for Wayanad, `EPSG:32644` for Chamoli).
- **DEM Terrain Derivations:** 30m SRTM DEM finite-difference Horn (1981) slope gradient ($0^\circ$–$90^\circ$, aspect) and D8 topological flow accumulation to identify upstream contributing catchments.
- **Precipitation Engine (NASA GPM IMERG v07):** 24h storm volume, peak intensity ($I$ mm/hr), 3-day short-term trigger sum, 15-day antecedent buildup, and rate of intensification ($\frac{dI}{dt}$).
- **Soil-Saturation Proxy (Explicitly Labeled `PROXY`):** Antecedent Moisture Index (AMI) decay formula:
  $$\text{AMI} = \frac{0.60 \cdot R_{3d} + 0.40 \cdot R_{15d} \cdot e^{-0.08 \times 12}}{380\text{ mm}}$$
- **NASA Global Landslide Catalog (GLC) Susceptibility:** Gaussian kernel spatial density with neutral AOI-median imputation for unrecorded zones (never assuming 0 hazard).
- **Explainable Weighted Risk Index:**
  $$\text{Risk}_{\text{landslide}} = 0.35 \cdot S_{\text{rain}} + 0.30 \cdot S_{\text{slope}} + 0.20 \cdot S_{\text{soil}} + 0.15 \cdot S_{\text{hist}}$$
- **Flash-Flood Risk Index:**
  $$\text{Risk}_{\text{flash\_flood}} = 0.50 \cdot S_{R24h} + 0.35 \cdot S_{\text{flow\_accum}} + 0.15 \cdot (1.0 - S_{\text{slope}})$$
- **Caine (1980) Empirical Lead-Time Estimator:** Projects time to breach critical threshold ($I = 14.82 \times D^{-0.39}$) under dynamic trend, with $\pm 30\%$ uncertainty bounds and strict scientific limitation disclosures.
- **Village Polygon Aggregation & Alert Engine:** Spatially aggregates grid cells to cadastral village polygons, generating tiered alerts (`NORMAL`, `WATCH`, `WARNING`, `CRITICAL`) and simulated evacuation guidance.

---

## 2. Automated Test Verification

All 19 unit and integration tests passed cleanly:

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Vanaparthi\.gemini\antigravity\scratch\sh304-landslide-warning
plugins: anyio-4.12.1
collected 19 items

tests/test_api.py::test_health_endpoint PASSED                           [  5%]
tests/test_api.py::test_aoi_endpoints PASSED                             [ 10%]
tests/test_api.py::test_process_pipeline PASSED                          [ 15%]
tests/test_api.py::test_risk_endpoints PASSED                            [ 21%]
tests/test_api.py::test_leadtime_endpoint PASSED                         [ 26%]
tests/test_api.py::test_alerts_endpoint PASSED                           [ 31%]
tests/test_api.py::test_villages_and_geojson_endpoints PASSED            [ 36%]
tests/test_api.py::test_backtest_endpoint PASSED                         [ 42%]
tests/test_api.py::test_reports_endpoint PASSED                          [ 47%]
tests/test_grid.py::test_analysis_grid_creation PASSED                   [ 52%]
tests/test_leadtime.py::test_caine_threshold_evaluation PASSED           [ 57%]
tests/test_leadtime.py::test_alert_engine_transitions PASSED             [ 63%]
tests/test_scoring.py::test_classifier_thresholds PASSED                 [ 68%]
tests/test_scoring.py::test_weighted_index_bounds_and_weights PASSED     [ 73%]
tests/test_scoring.py::test_explain_point_risk PASSED                    [ 78%]
tests/test_soil_proxy.py::test_soil_saturation_proxy_bounds_and_decay PASSED [ 84%]
tests/test_terrain.py::test_horn_slope_flat_plane PASSED                 [ 89%]
tests/test_terrain.py::test_horn_slope_known_gradient PASSED             [ 94%]
tests/test_terrain.py::test_d8_flow_accumulation PASSED                  [100%]

============================= 19 passed in 2.79s ==============================
```

---

## 3. Mandatory Model Benchmark: Rain-Only vs Full Weighted Index

Tested against historical ground truth landslide events from the NASA Global Landslide Catalog (GLC):

| Metric | Rain-Only Baseline | Full Weighted Risk Index | Delta Improvement (Δ) |
|---|:---:|:---:|:---:|
| **ROC-AUC** | 0.583 | **0.972** | **+0.389** |
| **Precision** | 33.3% | **85.7%** | **+52.4%** |
| **Recall** | 100.0% | **100.0%** | **0.0%** (Preserved) |
| **False Alarm Rate (FAR)** | 66.7% | **14.3%** | **-52.4%** (Significant Reduction) |
| **F1-Score** | 0.500 | **0.923** | **+0.423** |

*Scientific Finding:* Rain-Only triggers massive false alarms in flat plains where torrential rain falls on $0^\circ$ slopes without causing landslides. Fusing 30m DEM slope, antecedent soil moisture proxy, and historical susceptibility cuts false alarms by $52.4\%$ while identifying all critical slope failures (e.g. Mundakkai, Chooralmala, Meppadi).

---

## 4. Frontend Production Build Verification

The React 18 + Leaflet + TypeScript frontend was built for production via Vite:
```
✓ 1601 modules transformed.
dist/index.html                   1.35 kB │ gzip:   0.74 kB
dist/assets/index-C7kkYQcN.css    2.29 kB │ gzip:   0.87 kB
dist/assets/index-Zi13Sypx.js   352.02 kB │ gzip: 103.67 kB
✓ built in 9.94s
```

---

## 5. Documentation Delivered

1. **[`README.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/README.md):** Master documentation and quickstart.
2. **[`ARCHITECTURE.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/ARCHITECTURE.md):** Complete architectural data flow diagrams.
3. **[`DATA_SOURCES.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/DATA_SOURCES.md):** Inventory of satellite datasets, URLs, resolutions, and access methods.
4. **[`METHODOLOGY.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/METHODOLOGY.md):** Full mathematical equations, Horn slope, D8 drainage, and Caine formula.
5. **[`API.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/API.md):** Complete REST API endpoints and JSON payloads.
6. **[`LIMITATIONS.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/LIMITATIONS.md):** Explicit scientific disclaimers and operational boundaries.
7. **[`DEPLOYMENT.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/DEPLOYMENT.md):** Setup commands, Dockerfile, and docker-compose.
8. **[`DEMO_GUIDE.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/docs/DEMO_GUIDE.md):** Interactive walkthrough of Wayanad and Chamoli scenarios.
9. **[`IMPLEMENTATION_STATUS.md`](file:///C:/Users/Vanaparthi/.gemini/antigravity/scratch/sh304-landslide-warning/IMPLEMENTATION_STATUS.md):** Phase-by-phase status tracking log.
