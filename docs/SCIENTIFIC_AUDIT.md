# TerraSharp: Comprehensive Scientific & Engineering Audit

**Document Version**: 1.0.0  
**Audit Date**: 2026-09-17  
**Auditor Role**: Lead Geospatial ML Scientist, Remote-Sensing Engineer, Hydrologist & Backend Architect  
**Status**: ACTIVE BASELINE AUDIT  

---

## Executive Summary & Guiding Principle

> **Core Mandate**: *"Do not make TerraSharp look like a real disaster-warning system. Make it actually be one. When evidence is weak, report uncertainty—not a better-looking number. When data is unavailable, expose it—never fake it. When ML is unjustified, do not pretend."*

This document provides a systematic, line-by-line scientific audit of the TerraSharp (SH-304) repository. It maps every claim against executable evidence in code, benchmarks datasets against physical realities, exposes synthetic fallbacks and data leakage risks, and charts the engineering remediation roadmap required for near-production deployment.

---

## 1. Claim vs. Code vs. Data vs. Evaluation Matrix

| Domain / Claim | Repository Implementation | Provenance Truth | Scientific / Engineering Assessment | Audit Finding & Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **High-Res DEM Elevation** | `srtm_dem.tif`, `live_point_fetcher.py` querying Open-Elevation / Open-Meteo | `DERIVED` / `OBSERVED` (SRTM GL1 30m / Copernicus) | Real 30m stencils used for Wayanad/Idukki; dynamic points sample Open-Elevation API. In offline test mode, a synthetic 9-point elevation kernel was previously generated. | **RULE ENFORCED**: All synthetic DEM fallbacks must be explicitly tagged `SIMULATED (TEST-ONLY)`. Never claim SRTM attribution for synthetic tiles. |
| **Slope & Terrain Derivatives** | Horn's 1981 8-neighbor gradient algorithm in `terrain.py` | `DERIVED` | Mathematically sound 2nd-order finite difference slope computation on metric projected CRS (EPSG:32643). | **VALID**: Retain Horn slope and D8 hydrological routing; add planar/profile curvature & Topographic Wetness Index (TWI). |
| **Precipitation Ingestion** | Open-Meteo Forecast & Archive APIs + NASA GPM IMERG | `OBSERVED` / `ESTIMATED` | Real-time weather queries hourly rainfall and 14-day antecedent totals. Offline demo previously relied on point-interpolated precipitation. | **ACTION REQUIRED**: Fully transition spatial grids from point interpolation to true gridded NASA GPM IMERG calibrated satellite rasters (`GPM_3IMERGDF`). |
| **Antecedent Soil Moisture** | 14-day antecedent precipitation sum ($API_{14} = \sum_{t=1}^{14} P_t \cdot k^t$) | `PROXY` (Rainfall-derived) | Falsely called "Soil Moisture" in legacy UI; actually an Antecedent Precipitation Index ($k=0.88$). | **CORRECTED**: Must be strictly labeled `Antecedent Wetness Proxy (API14)`. Cannot be treated as independent soil moisture without in-situ/SMAP sensors. |
| **Historical Landslide Events** | `glc_events.json`, NASA Global Landslide Catalog | `OBSERVED` & `CURATED` | Contains genuine Wayanad July 30, 2024 disaster coordinates (Chooralmala, Mundakkai) and historic Western Ghats records. | **ACTION REQUIRED**: Audit each event coordinate against GSI (Geological Survey of India) field reports; strictly eliminate unverified synthetic points. |
| **Factor of Safety ($FoS$) Model** | Infinite Slope Stability Equation in `infinite_slope.py` | `MODELLED` (Physics-based) | Valid Coulomb-Terzaghi limit equilibrium: $FoS = \frac{c' + (\gamma z - u)\cos^2\beta \tan\phi'}{\gamma z \sin\beta \cos\beta}$. | **VALID**: Retain deterministic geotechnical baseline; expose parameter sensitivity ($c', \phi', z$). |
| **Lead-Time Formulation** | $T_{\text{fail}} = \frac{FoS - 1.0}{\alpha}$ where $\alpha = \frac{dI}{dt}$ | `ESTIMATED` | Physical approximation of time-to-failure based on rainfall intensification rate. | **REMEDIATION**: Distinguish between forecast horizon (hours), emergency response time, and verified hindcast lead time. Mark as `NOT_ESTIMABLE` if $\alpha \le 0$. |
| **Early Warning Alerts** | Threshold-based classification (`GREEN`, `YELLOW`, `ORANGE`, `RED`) | `MODELLED` | Triggers alert levels based on $FoS$ and rainfall. Lacked full stateful hysteresis (bounce prevention). | **ACTION REQUIRED**: Implement full state machine (`NORMAL -> WATCH -> WARNING -> CRITICAL -> RECOVERY`) with persistence, cooldown, and audit trail. |
| **ML / Super-Resolution** | PyTorch Sentinel-2 SRNet ($2\times$ Bicubic/TTA ensemble) | `MODELLED` (Deep Learning) | Actual CNN weights loaded for spatial optical enhancement; TTA uncertainty estimation implemented. | **VALID**: Model runs locally on CPU/CUDA. Clearly delineate between physical geotechnical $FoS$ and optical super-resolution. |

---

## 2. Detailed Technical Audit Findings

### 2.1 Provenance Classification System
All data artifacts ingested or served by the TerraSharp backend must adhere to the immutable 8-state provenance taxonomy:
1. `OBSERVED`: Raw direct measurements from satellites, radar, or certified weather stations (e.g., GPM IMERG, AWS rainfall).
2. `DERIVED`: Deterministic mathematical transforms from observed data (e.g., Horn slope from SRTM DEM, flow accumulation).
3. `INTERPOLATED`: Spatial or temporal re-gridding across unmeasured locations (e.g., IDW/kriging interpolation).
4. `ESTIMATED`: Empirical or proxy approximations (e.g., $API_{14}$ antecedent wetness proxy).
5. `SIMULATED`: Synthetic generation for test/offline harnesses only. **MUST NEVER be labeled as live or observed.**
6. `CACHED`: Freshness-validated local store with source checksum and acquisition timestamp.
7. `UNAVAILABLE`: Explicit upstream network or sensor outage state.
8. `ERROR`: Pipeline execution failure or invalid numerical boundary.

### 2.2 Leakage-Free Evaluation Protocol
- **Temporal Holdout**: The test split must strictly post-date the training and calibration split (e.g., train on 2018–2023 events, hold out 2024 Wayanad/Meppadi disaster).
- **Target Event Exclusion**: When evaluating a disaster at time $T$, historical event density features must strictly filter $t < T$. The target event cannot contribute to its own spatial hazard prior.
- **Unbiased Negative Controls**: Negative non-landslide controls must be sampled across identical slope and rainfall distributions to prevent trivial feature separation.
- **No Hardcoded Metrics**: All ROC-AUC, PR-AUC, Brier score, and F1 metrics must be calculated dynamically via `evaluation/metrics.py` across executable test splits.

---

## 3. Engineering Remediation & Execution Roadmap

```
[Phase 1: Provenance & Data Integrity]
  ├── Implement Strict Provenance Metadata Schema across all models
  ├── Audit and verify all GLC and GSI historical landslide records
  └── Eliminate hidden fallbacks; expose explicit UNAVAILABLE states

[Phase 2: Geotechnical & Hydrological Pipeline]
  ├── Validate Horn slope, D8 flow accumulation, and TWI
  ├── Calibrate Infinite Slope geotechnical parameters (cohesion, friction angle)
  └── Standardize 30m grid alignment across CRS UTM Zone 43N (EPSG:32643)

[Phase 3: Stateful Alert Engine & Lead Time]
  ├── Implement 5-state hysteresis machine (NORMAL, WATCH, WARNING, CRITICAL, RECOVERY)
  ├── Enforce cooldown windows and false-alarm mitigation gates
  └── Reconcile physical lead time against measured radar/gauge timeline

[Phase 4: Unified Location Coordinator (COMPLETED)]
  ├── 3-way synchronization: Map Pin (draggable) ↔ Direct Lat/Lon ↔ Place Search
  ├── Reverse geocoding via Photon/Nominatim with in-memory caching
  └── Single source of truth for dynamic AOI and real-time point risk
```
