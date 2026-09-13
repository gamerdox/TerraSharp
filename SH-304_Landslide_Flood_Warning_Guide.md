**Problem Statement SH-304** 

# **Hyper-Local Landslide and Flash Flood Warning System** 

_Complete Beginner-to-Working-Project Implementation Guide_ 

This document takes you from zero technical background to a working, demonstrable hazard-prediction prototype: problem understanding, solution design, tech stack, core concepts, architecture, datasets, model choice, preprocessing, exact implementation steps, project structure, setup/run commands, evaluation, expected outputs, and a full execution checklist. 

Assumes no prior knowledge of remote sensing, GIS, or machine learning. Every technical term is explained the first time it is used. 

## **1. Problem Understanding** 

### **1.1 The problem statement, in plain language** 

Problem Statement Number: SH-304 — “Hyper-Local Landslide and Flash Flood Warning System.” The ask: build a system that combines rainfall, terrain slope, soil saturation, and historical hazard data to identify landslide and flash-flood risk in vulnerable hilly regions, then (a) generate village-level risk maps, (b) estimate the lead time available before a slope failure or flood, and (c) trigger timely evacuation alerts. 

Broken into plain requirements, the system must take four kinds of input and produce three kinds of output: 

#### **Inputs required by the problem statement** 

- Rainfall — how much rain has fallen and is falling, in a specific hilly area. 

- Terrain slope — how steep the ground is at each location (steeper slopes fail more easily). 

- Soil saturation — how ‘full of water’ the ground already is (saturated soil fails at lower rainfall). 

- Historical hazard data — where landslides/floods have happened before, used as evidence of which locations are already known to be fragile. 

#### **Outputs required by the problem statement** 

- Village-level risk maps — a map where each village/area is colour-coded by how risky it currently is. 

- Lead time — an estimate, in hours, of how much warning time is left before failure/flooding is likely. 

- Evacuation alerts — a clear, timely trigger (alert level + message) so local disaster-response teams can act. 

### **1.2 Why this is a hard, real problem (not a toy exercise)** 

Landslides and flash floods in Indian hill states (e.g. the Himalayan belt, North-Eastern hills, Western Ghats) are triggered mainly by intense or prolonged monsoon rainfall acting on already-unstable slopes. A landslide is a mass of rock, soil, or debris moving down a slope once gravity overcomes the resisting strength of the ground; a flash flood is a sudden, fast-rising flood usually caused by intense rainfall over a short time in steep terrain that concentrates runoff quickly into valleys and streams. National mapping by the Geological Survey of India (GSI) already shows about 4.3 lakh sq. km of the country is landslideprone, with tens of thousands of historical landslides recorded — so the risk factors are well studied, but turning them into a live, location-specific (‘hyper-local’) early warning is the actual engineering challenge. 

Because no single dataset gives a ready-made answer (rainfall stations don't measure slope, satellites don't measure soil water content everywhere, and historical catalogs are incomplete), this project's real job is to combine several imperfect, partially-available data sources into one honest, explainable risk score — not to invent a perfect predictor. 

## **2. Proposed Solution** 

Build a grid-based (village/1–5 km cell) hazard-scoring pipeline that ingests rainfall, terrain slope, a soilsaturation proxy, and historical landslide/flood records for a chosen hilly Area of Interest (AOI) in India, combines them into a transparent Risk Score (0–100) per cell, classifies each cell into Low / Moderate / High / Severe, estimates lead time using a published rainfall intensity–duration threshold, and renders the result as a colour-coded map plus an alert table — with a simulated (not live-SMS) evacuation notification step. 

#### **2.1 MVP scope (what we will actually build first)** 

- A fixed, small AOI (one district or a ~50×50 km hilly region you choose, e.g. part of Uttarakhand, Himachal Pradesh, or the Western Ghats). 

- A rule-based, fully explainable Weighted Risk Index — no GPU, no model training required to get a working demo. 

- A daily-refresh batch pipeline (not true real-time streaming) — realistic for a beginner project and for the actual latency of the free data sources used (see Section 6). 

- An interactive map (via a Jupyter notebook or a small Streamlit/FastAPI app) showing per-village/per-grid-cell risk and a table of lead-time estimates and alert levels. 

#### **2.2 Why rule-based first, not deep learning first** 

Section 3.2.1 of the original SR-mapping-style guides you may be used to jumps straight to a pretrained neural network. This problem is different: there is no ready-made pretrained ‘landslide risk’ model, and building a trustworthy machine-learning classifier needs a properly labelled dataset (real landslide points + carefully chosen non-landslide points), which takes real effort to assemble correctly. A transparent weighted-overlay index is the standard first step used in real landslide-susceptibility studies (frequency-ratio and weighted-overlay methods are long-established in GSI/NRSC-style susceptibility mapping) and is easy to defend in a demo: you can always explain exactly why a village got a high score. Section 8 covers the optional machine-learning upgrade once the rule-based MVP works. 

## **3. Required Tech Stack** 

|**Layer**|**Tool / Library**|**Purpose**|
|---|---|---|
|Language & env|Python 3.10/3.11, venv|Core language; isolated environment|
|Editor|VS Code + Python extension|Writng/running code, previewing<br>images|
|Data access|earthaccess|Ofcial NASA library to search/download<br>Earthdata (GPM IMERG)|
|Data access|requests|Downloading NASA GLC/COOLR CSV and<br>OpenTopography DEM|
|Geospatal core|rasterio, numpy|Reading GeoTIFFs (DEM, rainfall grids),<br>array math|
|Geospatal vector|geopandas, shapely|Village/AOI boundaries, points, polygons|
|Terrain analysis|richdem (or numpy.gradient fallback)|Computng slope/aspect and fow|



|**Layer**|**Tool / Library**|**Purpose**|
|---|---|---|
|||accumulaton from the DEM|
|Tabular / ML|pandas, scikit-learn|Feature tables; optonal Random Forest<br>susceptbility model (Sec. 8)|
|Visualizaton|matplotlib, folium|Statc charts and interactve Leafet-style<br>risk maps|
|Demo app (optonal)|streamlit or FastAPI + Jinja/Leafet|Clickable village-level dashboard for the<br>live demo|
|Packaging|pip, requirements.txt|Reproducible installs|



_All of this runs on a normal laptop CPU — no GPU is required for the MVP._ 

## **4. Core Concepts — Explained From Zero** 

Read this once before touching any code. Every term used later in this document is defined here. 

|**Term**|**Plain-language meaning**|
|---|---|
|Remote sensing|Measuring the Earth using sensors that aren't physically touching it — usually<br>satellites.|
|DEM (Digital Elevaton<br>Model)|A grid of numbers where each cell stores the ground's height above sea level. Used<br>to compute slope.|
|Slope|How steep the ground is at a point, usually in degrees (0° = fat, 90° = vertcal).<br>Computed from a DEM by comparing each cell's height to its neighbours.|
|Aspect|The compass directon a slope faces — sometmes relevant because sun/rain<br>exposure difers by aspect; optonal refnement.|
|Rainfall intensity vs.<br>accumulaton|Intensity = how hard it's raining right now (mm/hour). Accumulaton = total rainfall<br>added up over a period (e.g. mm over the last 3 days). Landslides usually respond<br>to a mix of both.|
|Soil saturaton|How much of the soil's pore space already holds water. Fully saturated soil has<br>almost no spare capacity, so new rain runs of or triggers failure faster. This project<br>approximates it (Secton 6) because no ready dataset for it was supplied.|
|Antecedent rainfall|Rainfall that already fell in the recent past (e.g. previous 5 or 15 days), used here as<br>a practcal stand-in (proxy) for soil saturaton — weter recent history roughly<br>means weter soil.|
|Landslide/food inventory|A historical record (points on a map with dates) of where landslides or foods have<br>actually happened.|
|Susceptbility vs. hazard<br>vs. risk|Susceptbility = how prone an area is to failure based on its physical propertes<br>(slope, history). Hazard = susceptbility combined with a triggering event (rainfall<br>happening now). Risk = hazard combined with what/who could be afected<br>(people, property). This project mainly computes hazard, labelled as ‘Risk Score’<br>for simplicity, as the problem statement requests.|



|**Term**|**Plain-language meaning**|
|---|---|
|Lead tme|How many hours of warning exist before a rainfall trigger threshold is likely to be<br>crossed — the whole point of an early-warning system.|
|Rainfall intensity–duraton<br>(ID) threshold|A published curve/formula statng: ‘at duraton D hours, rainfall intensity above I<br>mm/hr has historically triggered landslides.’ Comparing current rainfall against this<br>curve is a standard early-warning technique (Secton 8.3).|
|GeoTIFF (.tf)|An image fle format that also stores exact real-world locaton — used for the DEM<br>and rainfall grids.|
|Shapefle / GeoJSON|Common fle formats for storing points, lines, or polygons (e.g. village boundaries)<br>with their locatons.|
|CRS (Coordinate Reference<br>System)|The system used to translate row/column positons in a grid into real<br>lattude/longitude on Earth. All layers must share one CRS before combining them.|
|Grid cell / AOI|AOI (Area of Interest) is the region you're studying. It's divided into a grid of small<br>cells (e.g. 1–5 km) or matched to real village boundaries — the unit every output is<br>reported at.|
|Flow accumulaton|For each DEM cell, how much upstream area drains through it — high values mark<br>valleys/streams, which is where fash foods concentrate. Optonal refnement for<br>the food side.|



## **5. Datasets, APIs, and Tools** 

The problem statement's four required inputs map to five real, checked data sources below. Terrain slope has no ready dataset of its own — it must be derived from a Digital Elevation Model (DEM), so one standard free DEM source is added; this is the only source not explicitly given in the brief, and it exists purely to compute the slope input the brief itself asks for. 

### **5.1 Rainfall — GPM IMERG Final Daily Precipitation (GPM_3IMERGDF, Version 07)** 

- What it is: a NASA–JAXA Global Precipitation Measurement (GPM) product. IMERG combines many satellites into one global rainfall estimate at 0.1° (~10 km) resolution, produced every half-hour and available since 2000. 

- This specific product: the Final Run daily total, in millimetres per day, per 0.1°×0.1° grid cell. 

- Latency caveat (important, state this honestly in any demo): the Final Run used here has roughly a 3.5-month processing delay, so it's excellent for building/testing the pipeline and for historical backtesting (Section 13), but a real deployment would swap in the Early Run (~4-hour latency) or Late Run (~14-hour latency) IMERG products for live alerts. The MVP explicitly uses Final Run data and documents this limitation. 

- Access: NASA Earthdata — requires a free Earthdata Login account (urs.earthdata.nasa.gov), then Python via the official earthaccess library. 

- Catalog page: earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07 

### **5.2 Historical landslide records — GSI Bhusanket Web Portal** 

- What it is: the Geological Survey of India's (GSI) National Landslide Forecasting Centre portal (with the companion Bhooskhalan mobile app), which shows landslide susceptibility zones and is intended to eventually issue short/medium-range landslide forecast bulletins nationwide. 

- How this project uses it: as a reference / validation layer. Open the portal for your chosen AOI and visually cross-check that the risk zones your own pipeline produces are broadly consistent with GSI's official susceptibility zoning. It is a map/app-based portal, not documented here as a bulkdownload API — if your institution has direct data access to GSI's National Landslide Susceptibility Mapping (NLSM) shapefiles (also mirrored on GSI's Bhukosh / NGDR portals), that is strictly better than the proxy in Section 6.3 and should replace it. 

- Portal: bhusanket.gsi.gov.in 

### **5.3 Historical landslide inventory — ISRO Landslide Atlas of India (NRSC)** 

- What it is: a national atlas published by ISRO's National Remote Sensing Centre (NRSC), containing a geospatial inventory of roughly 80,000 landslides mapped across 17 states and 2 union territories (Himalayas and Western Ghats) for 1998–2022, plus a district-level ranking of landslide exposure. 

- Format: delivered as a descriptive PDF report/atlas (~10.5 MB) rather than a query-ready API. 

- How this project uses it: to sanity-check which districts in your AOI are known high-exposure districts, and — if you can obtain the underlying inventory shapefile from NRSC/Bhuvan for your specific AOI — to seed the historical point layer in Section 6.3 with more (and more India-specific) points than the global catalog alone provides. 

- Page: isro.gov.in/Landslide_Atlas_India.html 

### **5.4 Historical landslide points (India + global) — NASA Global Landslide Catalog (GLC)** 

- What it is: a catalog of rainfall-triggered landslide events worldwide, compiled by NASA Goddard since 2007 from media reports, disaster databases, and scientific sources. It is the point layer behind NASA's COOLR (Cooperative Open Online Landslide Repository) viewer. 

- Format: directly downloadable as CSV, JSON, XML, or RDF — this is the one historical-hazard source in the brief with a genuine bulk-download file, so it is the primary machine-readable historical layer for the MVP. 

- Each record includes an event date, location (lat/long), and a landslide trigger category, which is exactly what's needed to build a historical-density feature and to back-test lead-time estimates (Section 13). 

- Access: data.nasa.gov/dataset/global-landslide-catalog-export (agree to the terms and download the CSV resource). 

### **5.5 Terrain slope — Digital Elevation Model (added; required to compute the brief's ‘terrain slope’ input)** 

- What it is: a global, free 30 m elevation grid — recommended: OpenTopography's SRTM GL1 (30 m) or the Copernicus GLO-30 DEM, both accessible via the OpenTopography API with a free API key. 

- How this project uses it: download the DEM tile(s) covering your AOI, then compute slope (and optionally aspect and flow accumulation) from it locally — this is standard GIS terrain analysis, not a modelling step. 

- Access: opentopography.org (free account → API key → REST download by bounding box). 

### **5.6 Summary table** 

|**Required input**|**Source used**|**Access type**|**Format**|
|---|---|---|---|
|Rainfall|GPM IMERG Final Daily<br>(GPM_3IMERGDF v07)|earthaccess<br>(Earthdata login)|NetCDF/HDF5 grid|
|Terrain slope|SRTM GL1 30 m DEM (added —<br>needed to derive slope)|OpenTopography API<br>key|GeoTIFF|
|Soil saturaton|Proxy: antecedent rainfall from GPM<br>IMERG (Secton 6.4)|Derived, not a<br>separate source|Computed array|
|Historical hazard data|NASA Global Landslide Catalog<br>(GLC/COOLR)|Direct CSV download|CSV|
|Historical hazard data<br>(validaton)|ISRO Landslide Atlas of India (NRSC)|PDF report / Bhuvan<br>(if available)|PDF / shapefle|
|Historical hazard data<br>(validaton)|GSI Bhusanket portal|Web/app viewer|Interactve map|



## **6. System Architecture and Data Flow** 

One-paragraph summary: every data source is pulled independently, reprojected onto one common AOI grid, turned into a small set of numeric ‘risk factor’ layers, combined into a single Risk Score per grid cell, checked against a rainfall threshold curve to estimate lead time, and finally rendered as a map and an alert table. 

### **6.1 Architecture layers** 

|**Layer**|**Responsibility**|
|---|---|
|1. Data Ingeston|Download raw rainfall (IMERG), DEM (OpenTopography), and historical points<br>(GLC CSV) for the chosen AOI.|
|2. Preprocessing|Reproject everything to one CRS/grid; compute slope from the DEM; clip to the<br>AOI boundary; build the antecedent-rainfall proxy; rasterize historical points to<br>a density layer.|
|3. Feature Engineering|Assemble one feature table: one row per grid cell / village, columns =<br>normalised slope, rainfall (today + 3-day + 15-day), historical density, elevaton.|
|4. Risk Scoring Engine|Weighted Risk Index (Secton 8.1) — combines the normalised factors into a<br>single 0–100 score and a Low/Moderate/High/Severe class.|
|5. Lead-Time Estmator|Compares current/recent rainfall against the published intensity–duraton<br>threshold (Secton 8.3) to estmate hours of warning remaining.|



|**Layer**|**Responsibility**|
|---|---|
|6. Alert Generator|Converts (Risk class + lead tme) into a per-village alert record; simulates<br>dispatch (console/log/webhook — no real SMS/telecom integraton in the<br>MVP).|
|7. Visualizaton / API|Colour-coded map (folium) and an alert table; optonal FastAPI/Streamlit layer<br>to serve this interactvely for a live demo.|



### **6.2 Data flow (step by step)** 

1. Define the AOI: pick one hilly district or a bounding box, and get its village/administrative boundaries (e.g. from a public shapefile such as India's Survey of India / Bhuvan admin boundaries, or approximate with a regular grid if boundaries aren't available). 

2. Pull the DEM for that bounding box from OpenTopography → compute slope (degrees) per cell. 

3. Pull daily IMERG rainfall for that bounding box and date range via earthaccess → build today's rainfall, 3-day sum, and 15-day sum per cell (the soil-saturation proxy). 

4. Download the NASA GLC CSV, filter to points inside/near the AOI, and rasterize into a historicallandslide-density layer (points per cell, or nearest-point distance). 

5. Reproject/resample all layers (DEM-derived slope, rainfall grid, historical density) onto one common grid matching the AOI. 

6. Normalise each layer to 0–1 and combine with the Weighted Risk Index formula → Risk Score per cell → map to a village by spatial join or by averaging cells inside each village polygon. 

7. Run the rainfall intensity–duration threshold check per cell to estimate lead time in hours. 

8. Generate the risk map, the alert table (village, risk class, lead time, recommended action), and log/print simulated alert dispatches for High/Severe villages. 

## **7. Components / Modules** 

|**Module (folder)**|**Responsibility**|**Key fles**|
|---|---|---|
|src/ingeston/|Download rainfall, DEM, historical points|get_rainfall.py, get_dem.py,<br>get_history.py|
|src/terrain/|Slope/aspect/fow-accumulaton from DEM|terrain_features.py|
|src/rainfall/|Antecedent rainfall proxy, rolling sums|rainfall_features.py|
|src/history/|Rasterize historical points to density grid|history_density.py|
|src/scoring/|Weighted Risk Index + optonal ML model|risk_index.py, ml_model.py|
|src/leadtme/|Intensity–duraton threshold + lead-tme calc|lead_tme.py|
|src/alerts/|Alert-level logic and simulated dispatch|alert_engine.py|
|src/viz/|Map rendering, charts, metrics table|make_map.py, plots.py|
|backend/ (optonal)|FastAPI serving risk GeoJSON + alert table|main.py|
|frontend/ (optonal)|Leafet/Streamlit map-based demo UI|app.py or index.html|



## **8. Model / Algorithm Choice and Justification** 

### **8.1 Landslide risk score — Weighted Risk Index (MVP, recommended)** 

Each grid cell's factors are normalised to a 0–1 scale and combined with fixed weights into a single score. This is the standard ‘weighted overlay’ approach long used in susceptibility mapping (the same principle behind GSI's NLSM classification into high/moderate/low zones), and it is fully explainable — useful for a viva or judge Q&A because you can point to exactly which factor pushed a village's score up. 

RiskScore = 100 * ( w1*slope_norm + w2*rain_today_norm + w3*rain_3day_norm + w4*rain_15day_norm + w5*historical_density_norm ) 

Suggested starting weights (must sum to 1; tune per region): w1 (slope)              = 0.30 w2 (today's rainfall)   = 0.20 w3 (3-day rainfall)     = 0.15 w4 (15-day rainfall, soil-saturation proxy) = 0.15 w5 (historical density) = 0.20 

- Classification: Low (0–24), Moderate (25–49), High (50–74), Severe (75–100) — adjust thresholds after looking at real scores for your AOI. 

- Flash-flood variant: use the same formula but weight low-slope/high-flow-accumulation valley cells (rather than steep cells) more heavily, since flash floods concentrate in drainage lines, not on the steepest slopes themselves. 

### **8.2 Optional upgrade — Random Forest susceptibility classifier (stretch goal)** 

Once the MVP works, an optional improvement is a supervised classifier: label NASA GLC historical points (and, if obtained, ISRO Atlas points) as positive examples (“landslide occurred here”), randomly sample an equal number of ‘pseudo-absence’ points elsewhere in the AOI as negative examples, attach each point's slope/elevation/rainfall features, and train a scikit-learn RandomForestClassifier to output a susceptibility probability. This point-and-pseudo-absence approach (with frequency-ratio, logisticregression, or random-forest classifiers) is a well-established technique in published landslidesusceptibility literature. It needs no GPU and trains in seconds on a laptop, but requires enough historical points in your AOI to be meaningful — check this before committing to it as your primary model. 

#### **Why not deep learning / a pretrained neural network for the MVP** 

Unlike an image task such as super-resolution, there is no widely available pretrained ‘landslide risk’ network, and the tabular, small-sample, spatially-sparse nature of this data (a few hundred to a few thousand historical points per state) favours simple, interpretable models over deep learning. A Random Forest or weighted overlay is the technically appropriate choice here — not a simplification made for lack of time. 

### **8.3 Lead-time estimation — rainfall intensity–duration (ID) threshold** 

Landslide early-warning systems commonly compare current rainfall against a published empirical threshold curve relating rainfall intensity (mm/hour) to storm duration (hours): rainfall combinations above the curve have historically been associated with triggered landslides. A widely cited global reference threshold (Caine, 1980) is: 

<mark>I = 14.82 * D ^ (-0.39)        # I = intensity in mm/hr, D = duration in hours</mark> 

Lead time for a cell is estimated by tracking how its recent rainfall (intensity and running duration) is trending toward this curve, and reporting the estimated hours remaining until the trend would cross it at the current rate. Treat this global curve as a reference starting point, not a locally-calibrated guarantee — state this limitation explicitly in the demo, and mention that GSI's Regional Landslide Forecasting System work (built on India-specific rainfall thresholds) is the right long-term replacement once such thresholds are available for your AOI. 

## **9. Preprocessing** 

9. Reprojection: convert the DEM, IMERG rainfall grid, and any village boundaries to one common CRS (EPSG:4326 for lat/long, or a local UTM zone for accurate distance/area work). 

10. Clipping: crop every layer to the AOI bounding box/polygon so you're not processing data you don't need. 

11. Resampling: the DEM (30 m) and IMERG (~10 km) are at very different resolutions — resample both onto one common analysis grid (e.g. 1 km cells) using bilinear interpolation for continuous values (elevation, rainfall) and nearest-neighbour where appropriate. 

12. Slope computation: derive slope (degrees) from the resampled DEM using a standard 3×3 neighbourhood gradient method (richdem's slope function, or numpy.gradient as a manual fallback). 

13. Rainfall feature engineering: from the daily IMERG series, compute today's value, a rolling 3-day sum, and a rolling 15-day sum (the antecedent-rainfall soil-saturation proxy) per cell. 

14. Historical density: rasterize NASA GLC points (and any ISRO Atlas points obtained) onto the same grid — either a simple point-count per cell or a kernel density estimate for a smoother surface. 

15. Normalisation: scale every factor layer to 0–1 (min-max or percentile-based) before combining in the Weighted Risk Index, so no single factor's raw units dominate the score. 

16. Missing-data handling: cells with no historical points are not automatically ‘safe’ — treat missing historical density as neutral (e.g. the AOI median) rather than zero, to avoid under-scoring genuinely risky but under-reported villages. 

## **10. Implementation Steps** 

### **10.1 Step 0 — accounts and software** 

17. Create a free NASA Earthdata Login account at urs.earthdata.nasa.gov (needed for GPM IMERG via earthaccess). 

18. Create a free OpenTopography account and API key at opentopography.org (needed for the DEM). 

19. Install Python 3.10 or 3.11 from python.org/downloads (Windows: check ‘Add Python to PATH’). Verify with: python --version 

20. Install VS Code from code.visualstudio.com and its Python extension. 

### **10.2 Step 1 — open the project and create a virtual environment** 

# Create the environment (once) python -m venv .venv # Activate it (every new terminal) # Windows PowerShell:   .venv\Scripts\Activate.ps1 # Windows CMD:          .venv\Scripts\activate.bat # Mac/Linux:            source .venv/bin/activate 

### **10.3 Step 2 — install packages** 

pip install --upgrade pip pip install -r requirements.txt # requirements.txt should list: #   earthaccess rasterio geopandas shapely richdem numpy pandas #   scikit-learn matplotlib folium streamlit fastapi uvicorn requests 

### **10.4 Step 3 — authenticate and fetch data** 

python src/ingestion/get_dem.py        # pulls SRTM GL1 DEM for the AOI (OpenTopography) python src/ingestion/get_rainfall.py   # earthaccess.login() then downloads IMERG for the date range python src/ingestion/get_history.py    # downloads and filters the NASA GLC CSV to the AOI 

### **10.5 Step 4 — preprocess and build features** 

python src/terrain/terrain_features.py     # DEM -> slope grid python src/rainfall/rainfall_features.py   # IMERG -> today / 3-day / 15-day rainfall grids python src/history/history_density.py      # GLC points -> historical density grid python src/scoring/build_feature_table.py  # merges everything onto one grid/village table 

### **10.6 Step 5 — score risk and estimate lead time** 

python src/scoring/risk_index.py    # Weighted Risk Index -> Risk Score + class per cell/village python src/leadtime/lead_time.py    # ID-threshold comparison -> estimated lead time (hours) python src/alerts/alert_engine.py   # Risk class + lead time -> alert table + simulated dispatch log 

### **10.7 Step 6 — visualize and demo** 

python src/viz/make_map.py     # saves an interactive folium risk map (HTML) to results/ streamlit run frontend/app.py  # optional: clickable dashboard for the live demo 

### **10.8 Step 7 (stretch goal) — Random Forest upgrade and API** 

Only after Steps 1–6 work end-to-end: build the labelled point table and train the Random Forest classifier (src/scoring/ml_model.py), and/or wrap the pipeline in backend/main.py (FastAPI) so the frontend map can query live results. 

## **11. Project Structure** 

sh304-landslide-flood-warning/ ├── README.md ├── requirements.txt ├── data/ │├── dem/                 <- downloaded SRTM/Copernicus DEM tiles │├── rainfall/             <- downloaded IMERG files │└── history/              <- NASA GLC CSV (+ ISRO Atlas data if obtained) ├── src/ │├── ingestion/    get_dem.py, get_rainfall.py, get_history.py │├── terrain/      terrain_features.py │├── rainfall/     rainfall_features.py │├── history/      history_density.py │├── scoring/      build_feature_table.py, risk_index.py, ml_model.py │├── leadtime/     lead_time.py │├── alerts/       alert_engine.py │└── viz/          make_map.py, plots.py ├── backend/                  <- optional FastAPI app ├── frontend/                 <- optional Streamlit/Leaflet demo UI ├── results/                  <- generated maps, tables, metrics (output) └── notebooks/                <- exploration / sanity-check notebooks 

## **12. Exact Setup and Run Commands** 

# 1. Clone/open the project folder in VS Code, then open a terminal # 2. Create and activate the virtual environment python -m venv .venv source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1 # 3. Install dependencies pip install --upgrade pip pip install -r requirements.txt 

# 4. Configure credentials (one-time) 

#    - Earthdata: earthaccess.login() will prompt for your EDL username/password #      and can save them to a .netrc file for future runs #    - OpenTopography: set your API key export OPENTOPO_API_KEY=your_key_here     # Windows: set OPENTOPO_API_KEY=your_key_here # 5. Run the full pipeline for your chosen AOI and date range python src/ingestion/get_dem.py --bbox 30.0 78.0 30.5 78.5 python src/ingestion/get_rainfall.py --bbox 30.0 78.0 30.5 78.5 --start 2024-07-01 --end 2024-07-31 python src/ingestion/get_history.py --bbox 30.0 78.0 30.5 78.5 python src/terrain/terrain_features.py python src/rainfall/rainfall_features.py python src/history/history_density.py python src/scoring/build_feature_table.py 

python src/scoring/risk_index.py python src/leadtime/lead_time.py python src/alerts/alert_engine.py python src/viz/make_map.py 

# 6. Open results/risk_map.html in a browser, or: streamlit run frontend/app.py 

## **13. Testing and Evaluation Metrics** 

Because this is a classification/scoring task rather than image generation, evaluate it against the historical record itself, using a back-test: for past dates where a NASA GLC event is known to have happened in/near the AOI, check whether the pipeline (run with only the rainfall data available up to that point) would have flagged that cell as High/Severe, and how much lead time it would have given. 

|**Metric**|**What it tells you**|**How to compute**|
|---|---|---|
|Precision|Of the cells fagged High/Severe, what<br>fracton actually had a recorded historical<br>event nearby|TP / (TP + FP) over the back-test set|
|Recall (Detecton<br>Rate)|Of the actual historical events, what<br>fracton were fagged High/Severe in<br>advance|TP / (TP + FN) over the back-test set|
|False Alarm Rate|How ofen the system cries wolf on<br>days/cells with no recorded event|FP / (FP + TN)|
|AUC / Success-Rate<br>curve|Overall ranking quality of the Risk Score<br>against known event locatons (standard<br>metric in susceptbility-mapping literature)|sklearn.metrics.roc_auc_score on Risk<br>Score vs. event/no-event label|
|Lead-tme back-test|Median/average hours between the alert<br>frst crossing High/Severe and the recorded<br>event date|Compare alert tmestamp vs. GLC event<br>date for matched cases|
|Baseline comparison|Whether the Weighted Risk Index adds<br>value over rainfall alone|Run the same back-test using only the<br>rainfall factor, and compare|



_Always show the baseline-comparison result (rainfall-only vs. full Weighted Risk Index) — exactly like showing bicubic vs. model output in an image super-resolution project, this is the single most convincing evidence that combining slope, soil-saturation proxy, and history actually helps._ 

## **14. Expected Outputs** 

- A colour-coded, interactive village/grid-level risk map (Low/Moderate/High/Severe) for the chosen AOI and date. 

- An alert table: village/cell ID, Risk Score, Risk class, estimated lead time (hours), recommended action. 

- A simulated evacuation-alert log for every High/Severe entry (printed/logged — not a live SMS/telecom dispatch in the MVP). 

- A metrics report: precision, recall, false alarm rate, and the rainfall-only vs. full-model baseline comparison from Section 13. 

- A short before/after or with/without-history comparison showing how adding the historical layer changes which villages get flagged. 

## **15. MVP vs. Optional / Stretch Features** 

|**Feature**|**MVP (build frst)**|**Optonal / stretch**|
|---|---|---|
|Risk model|Weighted Risk Index (Secton 8.1)|Random Forest susceptbility classifer<br>(Secton 8.2)|
|Rainfall product|IMERG Final Run (batch/back-test friendly)|IMERG Early/Late Run for near-real-tme<br>alerts|
|Soil saturaton|Antecedent-rainfall proxy|Real soil-moisture dataset (e.g. satellite<br>soil moisture) if access is arranged<br>separately|
|Flood side|Slope-based proxy only|DEM-derived fow accumulaton to fag<br>valley/drainage cells specifcally|
|Historical data|NASA GLC CSV only|ISRO Landslide Atlas / GSI NLSM shapefles<br>if insttutonal access is obtained|
|Delivery|Statc map + table (notebook or saved<br>HTML)|FastAPI backend + Streamlit/Leafet live<br>dashboard|
|Alerts|Simulated log/console output|Real SMS/WhatsApp/webhook integraton<br>(needs a telecom/notfcaton API, not<br>provided in the brief)|



## **16. Full Execution Checklist** 

### **Phase A — Understand** 

- Can explain, in your own words: susceptibility vs. hazard vs. risk, and why slope + rainfall + soilsaturation proxy + history are combined rather than used alone. 

- Chosen a specific AOI (district or bounding box) and can justify why it's landslide/flood-prone. 

### **Phase B — Accounts and environment** 

- NASA Earthdata Login account created. 

- OpenTopography account + API key created. 

- Python, VS Code, and the Python extension installed; virtual environment created and activated. 

- pip install -r requirements.txt completes without unresolved errors. 

### **Phase C — Data** 

- DEM downloaded for the AOI and opened/visualised at least once. 

- IMERG rainfall downloaded for a test date range and opened/visualised at least once. 

- NASA GLC CSV downloaded and filtered to points inside/near the AOI. 

- GSI Bhusanket portal and ISRO Landslide Atlas checked manually for the same AOI, for crossvalidation. 

### **Phase D — Preprocessing and features** 

- Slope grid computed from the DEM and visually sanity-checked against known steep terrain. 

- Rainfall (today / 3-day / 15-day) grids computed. 

- Historical density grid computed from the GLC points. 

- All layers merged onto one common AOI grid without misalignment (spot-check a few cells). 

### **Phase E — Scoring and alerts** 

- Weighted Risk Index runs end-to-end and produces a Risk Score + class per cell/village. 

- Lead-time estimator runs and produces an hours-remaining figure per flagged cell. 

- Alert table and simulated dispatch log generated for High/Severe cells. 

### **Phase F — Evaluation** 

- Back-test run against at least a handful of historical GLC events in/near the AOI. 

- Precision, recall, false alarm rate, and AUC computed. 

- Rainfall-only baseline computed and compared against the full Weighted Risk Index. 

### **Phase G — Presentation** 

- Interactive risk map saved/screenshotted and looks visually convincing for at least one real rainfall event date. 

- Metrics table/chart prepared (full model vs. baseline). 

- One clear talking point ready on: (a) the Final-Run latency limitation, (b) the antecedent-rainfall soilsaturation proxy, and (c) how the Weighted Risk Index weights were chosen. 

### **Phase H — Stretch goals (optional)** 

- Random Forest susceptibility model trained and compared against the Weighted Risk Index. 

- FastAPI backend + Streamlit/Leaflet frontend built for a live, clickable demo. 

- DEM-based flow accumulation added to sharpen the flash-flood (valley-focused) risk layer. 

## **Data Sources and References** 

- GPM IMERG Final Daily Precipitation (GPM_3IMERGDF v07) — earthdata.nasa.gov/dashboard/datacatalog/GPM_3IMERGDF.v07 

- earthaccess Python library (official NASA Earthdata access tool) — earthaccess.readthedocs.io 

- GSI Bhusanket Web Portal / National Landslide Forecasting Centre — bhusanket.gsi.gov.in 

- ISRO / NRSC Landslide Atlas of India — isro.gov.in/Landslide_Atlas_India.html 

- NASA Global Landslide Catalog (GLC) export — data.nasa.gov/dataset/global-landslide-catalogexport 

- NASA COOLR (Cooperative Open Online Landslide Repository) — landslides.nasa.gov 

- OpenTopography (SRTM GL1 / Copernicus GLO-30 DEM access) — opentopography.org 

- Caine, N. (1980). The rainfall intensity–duration control of shallow landslides and debris flows. Geografiska Annaler, 62A(1–2), 23–27 — source of the reference ID threshold formula in Section 8.3. 

