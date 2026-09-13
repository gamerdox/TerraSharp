# SH-304 Environmental Data Sources & Inventory

This document details every environmental dataset, satellite instrument, access protocol, credential requirement, and processing transformation utilized within the **SH-304 Early Warning System**.

---

## 1. NASA GPM IMERG Final Daily Precipitation

| Attribute | Specification |
|---|---|
| **Product Identifier** | `GPM_3IMERGDF` v07 (IMERG Final Run Daily Precipitation) |
| **Provider** | NASA Goddard Earth Sciences Data and Information Services Center (GES DISC) |
| **Official Catalog URL** | https://earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07 |
| **Spatial Resolution** | 0.1° $\times$ 0.1° (~10 km $\times$ 10 km at the equator) |
| **Temporal Coverage** | June 2000 – Present; Daily accumulations |
| **Access Mechanism** | NASA Earthdata Login via `earthaccess` Python SDK |
| **Authentication** | Free NASA Earthdata account required for live access (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`) |
| **Demo Offline Fallback** | Deterministic 15-day monsoon precipitation time series calibrated against historical deluge events |
| **Processing Pipeline** | Resampled to 0.01° analysis grid via conservative area-weighted interpolation; decomposed into 24h intensity, 3-day rolling sum, and 15-day antecedent rainfall |
| **Known Limitations** | 0.1° native cell size smoothes extreme localized micro-scale convective rainfall peaks; satellite passive microwave retrieval can experience radar attenuation in heavy cloudbursts. |

---

## 2. SRTM GL1 30m Global Digital Elevation Model

| Attribute | Specification |
|---|---|
| **Product Identifier** | Shuttle Radar Topography Mission Global 1 Arc-Second (`SRTMGL1` v003) |
| **Provider** | NASA Jet Propulsion Laboratory (JPL) / USGS LP DAAC / OpenTopography |
| **Official Catalog URL** | https://lpdaac.usgs.gov/products/srtmgl1v003/ / https://opentopography.org/ |
| **Spatial Resolution** | 1 arc-second (~30 meters at the equator) |
| **Vertical Accuracy** | $\le 16\text{ m}$ absolute vertical error |
| **Projection / Datum** | WGS84 Geographic (EPSG:4326), EGM96 Geoid vertical datum |
| **Access Mechanism** | OpenTopography Global DEM API or local GeoTIFF clips |
| **Authentication** | OpenTopography API key (optional for live queries; offline clips provided) |
| **Demo Offline Fallback** | Georeferenced, realistic 30m DEM GeoTIFF clips for Wayanad (Western Ghats) and Chamoli (Himalayas) |
| **Processing Pipeline** | Reprojected to local UTM zone (`EPSG:32643` / `EPSG:32644`) to compute Horn 3x3 finite-difference slope gradient (degrees) and D8 topological flow accumulation |
| **Known Limitations** | C-band radar can reflect off dense forest canopy top rather than bare earth in thick tropical jungles; steep mountain shadow voids are present in raw data (mitigated by void filling). |

---

## 3. NASA Global Landslide Catalog (GLC)

| Attribute | Specification |
|---|---|
| **Product Identifier** | NASA Global Landslide Catalog Export |
| **Provider** | NASA Goddard Space Flight Center Landslide Team |
| **Official Catalog URL** | https://data.nasa.gov/dataset/global-landslide-catalog-export / https://landslides.nasa.gov/ |
| **Spatial Resolution** | Coordinate points (latitude, longitude) of reported mass movements |
| **Temporal Coverage** | 2007 – Present |
| **Access Mechanism** | Open CSV / GeoJSON export |
| **Authentication** | None required (Public Domain / NASA Open Data) |
| **Demo Offline Fallback** | Georeferenced catalog records for Wayanad (including Puthumala, Mundakkai, Chooralmala) and Chamoli |
| **Processing Pipeline** | Spatial density derived via Gaussian Kernel Density Estimation (sigma = 3 cells ~ 3 km); neutral AOI-median imputation applied to unrecorded cells |
| **Known Limitations** | Inventory is report-based (news, road maintenance, disaster reports). Urban and populated road corridors are over-represented while uninhabited wilderness is under-represented. Absence of records must never be interpreted as absence of physical hazard. |

---

## 4. Indian Validation & Cross-Reference Sources

| Authority | Portal & Product | Role in SH-304 |
|---|---|---|
| **ISRO / NRSC** | [Landslide Atlas of India](https://isro.gov.in/Landslide_Atlas_India.html) | Macro-susceptibility zones and spatial validation benchmark |
| **GSI Bhusanket** | [National Landslide Forecasting Centre](https://bhusanket.gsi.gov.in/) | Regional rainfall threshold calibration reference and bulletin validation |

---

## 5. Administrative Village Boundaries

| Attribute | Specification |
|---|---|
| **Source** | Authoritative Open Administrative Boundaries / Survey of India / OSM Reference |
| **Format** | GeoJSON Polygon FeatureCollection |
| **Attributes** | `village_id`, `village_name`, `district`, `state`, `population`, `bounds` |
| **Processing Pipeline** | Spatial intersection (`gpd.sjoin`) with raster grid cells to calculate settlement-level mean risk, peak risk, and % critical hazard footprint |
| **Known Limitations** | Administrative village boundaries reflect governance areas rather than physical watershed divides. |

---

## 6. Soil-Saturation Indicator (Explicitly Labeled PROXY)

| Attribute | Specification |
|---|---|
| **Indicator Name** | Antecedent Moisture Index (AMI) Proxy |
| **Formula** | $\text{AMI} = \frac{0.60 \cdot R_{3d} + 0.40 \cdot R_{15d} \cdot e^{-0.08 \times 12}}{S_{\text{max}}}$ |
| **Provenance Tag** | `PROXY` |
| **Scientific Rationale** | True direct in-situ soil moisture sensor networks or high-resolution radar soil moisture products (e.g. SMAP / SMOS L-band) are often inaccessible or obstructed by dense canopy cover during active storm events. An antecedent rainfall decay index acts as a transparent, empirical hydrologic proxy. |
| **Caveat** | Strictly an empirical estimator; does not replace calibrated field tensiometers or piezometer groundwater measurements. |
