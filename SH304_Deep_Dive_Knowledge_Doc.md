**SH-304 Deep-Dive Knowledge Document** _Hyper-Local Landslide & Flash-Flood Warning System_ Convergence 2026 — Slide-by-Slide Preparation Document 

### **How to use this document** 

- Mapped 1:1 onto the 7 slides of the sample PPT (Title, Team, Problem, Solution, Technical, Impact, References). 

- Gives context, reasoning and defence for every slide — not ready-to-paste slide bullets. 

- Tags mark the confidence level of every claim: [PS CONFIRMED] · [PROJECT GUIDE] · [RESEARCH] · [PROPOSED] · [ASSUMPTION]. 

- Each slide section ends with a concrete Visual Approach — what the slide should look like, not just what it should say. 

# **Slide 1 — Title Slide ("SOFTWARE")** 

## **What it's proving** 

Nothing technical — it's orientation: track (Software), theme, and team identity. 

## **Visual approach** 

Keep this close to the template: track name, hackathon name/logo, PSID (SH-304), problem title ("Hyper-Local Landslide & Flash-Flood Warning System"), team name, centered, high contrast. No content decisions needed here — don't over-design it. 

# **Slide 2 — Team Details** 

## **What it's proving** 

Nothing technical — credibility of who's presenting. 

## **Content needed** 

- Team name, Domain — should read Disaster Management / Geospatial AI / Climate-Tech, not a vague "Software". 

- PSID = SH-304. 

- Table: Team Lead + 3 members — Name, Phone Number, Roll Number. 

## **Visual approach** 

Keep the template table. Optionally add a one-line role specialization under each name (e.g. "Data/Backend," "Geospatial/Modeling," "Frontend/Viz," "Research/Docs") — judges like seeing a clear division of labour, and it quietly tells them who to direct which question to. 

# **Slide 3 — Problem Statement & Understanding** 

## **What this section must prove to judges** 

That you understand the real-world mechanism of the disaster (not just paraphrased the PS), that you know why it's hard, and that you can name concretely who suffers and what "hyper-local" means as opposed to the national-scale maps that already exist. 

## **Full background and context** 

- PS number & title **[PS CONFIRMED]** — SH-304, "Hyper-Local Landslide and Flash-Flood Warning System." The ask: combine rainfall, terrain slope, soil saturation, and historical hazard data to identify landslide/flash-flood risk in vulnerable hilly regions, and produce (a) village-level risk maps, (b) lead-time estimates, and (c) evacuation alerts. 

- Why this is a real, hard problem **[PS CONFIRMED / PROJECT GUIDE]** — a landslide is a mass of rock/soil/debris moving downslope once gravity beats the ground's resisting strength. A flash flood is a sudden, fast-rising flood from intense short-duration rainfall in steep terrain that concentrates runoff quickly into valleys. India's Geological Survey (GSI) has already mapped ~4.3 lakh sq. km as landslide-prone with tens of thousands of historical events recorded — so the risk factors are well studied. What's missing is turning them into a live, location-specific ("hyper-local") early warning — that's the actual engineering gap. 

- Why no single dataset solves it — rainfall stations don't measure slope, satellites don't measure soil-water everywhere, and historical catalogs are incomplete. So this is fundamentally a data-fusion problem: combine several imperfect, partially-available sources into one honest, explainable risk score. This framing tells judges you're not claiming to invent a perfect predictor — you're responsibly fusing imperfect signals, which is intellectually honest and defensible. 

- Who experiences this — villages/hamlets in Himalayan states, North-Eastern hills, and the Western Ghats during monsoon, typically served by low-resource local disaster-response teams who currently rely on generalized national/state susceptibility maps that are not granular or not live. 

- Why existing approaches are insufficient — national-scale susceptibility maps (like GSI's) tell you a zone is prone, historically. They are static and coarse. They don't tell a village official today, in real time, "your specific village has elevated risk right now with roughly X hours before likely failure." That gap — static/coarse vs. dynamic/hyper-local — is the actual bottleneck this project targets. 

## **Reasoning behind how to frame this slide** 

Don't just restate the PS bullet-for-bullet. Structure it as: mechanism → scale of the problem → why current maps don't solve it → who is affected → what "solved" would look like. This shows genuine understanding rather than PS regurgitation. 

## **What's confirmed vs proposed here** 

Everything on this slide should be [PS CONFIRMED] or [PROJECT GUIDE]-backed. There should be zero [PROPOSED] content on this slide — it's understanding, not solutioning. 

## **What judges may challenge** 

- "Isn't this already solved by GSI's Bhusanket portal?" → GSI's portal gives susceptibility zones (static, historicallyderived), not a live, per-village risk score with rainfall-driven lead time. You use GSI as a validation reference, not as your source of truth. 

- "Why hyper-local — what resolution exactly?" → State your grid cell size (1–5 km, or matched to actual village polygons) and defend why. 

- "What makes this different from a rainfall alert app?" → Rainfall alone doesn't tell you if a specific slope is primed to fail; you need slope + antecedent wetness + history, not just "it's raining hard." 

## **Must be able to explain verbally** 

The exact difference between susceptibility, hazard, and risk (see Slide 5 concepts) — susceptibility is static/physical, hazard = susceptibility + a triggering event (rain happening now), risk = hazard + who/what is exposed. This project computes hazard but calls it "Risk Score" for PS-alignment simplicity — be ready to admit and explain this terminology simplification if asked. 

## **Visual approach** 

Two- or three-panel layout, not a wall of text: 

- Left/top panel — "The Mechanism": a simple side-profile diagram of a hillslope with an arrow showing rainfall → soil saturation rising → slope failure/runoff, annotated with the 4 required inputs (rainfall, slope, soil saturation, history) as labeled inputs feeding into the slope. 

- Right/bottom panel — "The Gap": a simple before/after contrast — "Existing (GSI static, state-level, historical)" vs "Needed (live, village-level, hours-of-lead-time)." Add a small stat callout: "~4.3 lakh sq km landslide-prone (GSI)" for scale and credibility. 

- Keep text sparse — numbers and a diagram carry more credibility than paragraphs. One sentence per box, maximum. 

# **Slide 4 — Proposed Solution & Innovation** 

## **What this section must prove** 

That your solution actually closes the specific gap named in Slide 3 (not a generic "we use AI" claim), and that you can honestly separate what's genuinely new/clever from what's just implementation work. 

## **The proposed solution, in full** 

- **[PROJECT GUIDE / PROPOSED]** Build a grid-based (village/1–5 km cell) hazard-scoring pipeline for a chosen hilly Area of Interest (AOI) in India that: 

   - Ingests rainfall, terrain slope, a soil-saturation proxy, and historical landslide/flood records. 

   - Combines them into a transparent Weighted Risk Index → Risk Score (0–100) per grid cell. 

   - Classifies each cell: Low (0–24) / Moderate (25–49) / High (50–74) / Severe (75–100). 

   - Estimates lead time (hours of warning left) using a published rainfall intensity–duration threshold. 

   - Renders a colour-coded map + alert table, with a simulated (not live-SMS) evacuation notification step. 

## **Why rule-based, not deep learning — the core defensible decision** 

This is the single most important reasoning chain to internalize, because judges will ask "why not ML/deep learning?" 

- There is no pretrained "landslide risk" neural network available off-the-shelf (unlike image super-resolution, where pretrained SR models exist). 

- A trustworthy ML classifier needs a properly labelled dataset — real landslide points + carefully chosen nonlandslide ("pseudo-absence") points — which takes real curation effort most hackathon teams underestimate. 

- A transparent weighted-overlay index is the established first step in real susceptibility mapping — frequency-ratio and weighted-overlay methods are long-used in GSI/NRSC-style mapping. 

- It is fully explainable: for any village, you can point to exactly which factor (slope? recent rain? history?) pushed the score up — a major viva/judge-Q&A advantage over a black-box model. 

- This is a technically appropriate choice, not a "ran out of time" simplification — say this explicitly, because judges often assume rule-based = lazy. 

## **What is genuinely innovative vs. what is "just implementation"** 

- **NOT innovative (just implementation):** downloading rainfall/DEM data, computing slope, building a weighted sum. These are standard GIS/geoscience operations. 

- **Genuinely innovative/differentiating:** fusing 4 independently-sourced, heterogeneous datasets (satellite rainfall, DEM-derived slope, a derived soil-saturation proxy, and historical point data) into one coherent per-village decision artifact (score + class + lead time + alert) — most citizen-facing tools show one of these layers in isolation, not fused. 

   - The explicit lead-time estimate via the rainfall intensity–duration (ID) threshold, converting a scientific curve into an actionable "hours remaining" number — most susceptibility maps are static and don't give an operational countdown. 

- Being honest about data latency and building the pipeline to be swappable for near-real-time sources later — an engineering-maturity point, genuinely a differentiator vs. many hackathon prototypes that quietly ignore latency. 

## **Alternatives considered and why not chosen** 

- Deep learning / CNN on satellite imagery — rejected for MVP (no pretrained model, needs a large labelled imagery corpus, GPU dependency, harder to explain to judges/officials). Deferred as background context only. 

- Random Forest ML classifier — not rejected, but deferred to the optional stretch goal; requires enough labelled historical points in the AOI to be meaningful, which needs checking before committing to it as the primary model. 

- Real-time streaming pipeline — rejected for MVP in favour of a daily-refresh batch pipeline, because it matches the actual latency of the free data sources used; building "fake real-time" on top of daily-updating data would be dishonest. 

## **What's confirmed vs proposed vs optional** 

- **[PROJECT GUIDE]** Weighted Risk Index formula, MVP scope, AOI choice, rule-based-first reasoning. 

- **[PROPOSED]** Your team's design choices — specific AOI, final tuned weights, UI framework (Streamlit vs FastAPI+Leaflet), exact alert message wording. 

- **[OPTIONAL / STRETCH]** Random Forest upgrade, flow-accumulation-based flood refinement, live SMS/webhook alerts, FastAPI backend. 

## **What judges may challenge** 

- "Why should we trust a manually-weighted formula over a trained model?" → Because the weights mirror the same weighted-overlay method used in real GSI/NRSC-style mapping, and you can show the exact contribution of each factor per village — full auditability, which matters for a life-safety system. 

- "How is this different from an existing app?" → Emphasize fusion + explicit lead-time + explainability, not a generic claim of "we use satellite data." 

- "What's actually novel here versus just gluing together public datasets?" → Be honest: the novelty is in the fusion logic, the lead-time translation, and the transparency — not in inventing new data or new science. Own this rather than oversell. 

## **Visual approach** 

- Top strip: one-line solution statement — "A transparent, explainable Risk Score (0–100) per village, refreshed daily, with an hours-of-lead-time estimate." 

- Center: a simple horizontal pipeline diagram — 4 input icons (rain cloud, mountain/slope, water-droplet/soil, history-clock) → funnel/plus-sign icon → single gauge icon labeled "Risk Score 0–100" → branching into 2 output icons (a small map icon and an alert-bell icon). This one diagram is your solution in a glance — let icons + 4–6 word labels do the work, not paragraphs. 

- Bottom: a small "Why rule-based, not ML" callout box with a one-line justification, so the innovation defence is visible rather than saved only for Q&A. 

- Avoid generic AI/ML iconography (brains, robots) since your MVP is explicitly not deep learning — using that imagery would contradict your own technical honesty. 

# **Slide 5 — Technical Implementation** 

_This is the deepest slide — go component by component._ 

## **What this section must prove** 

That the system is real, buildable on a laptop, and that every design decision (dataset choice, model choice, preprocessing step) has a stated reason — not just a stack of buzzwords. 

## **System input → output, in sequence** 

Data Ingestion  →  Preprocessing  →  Feature Engineering  →  Risk Scoring Engine →  Lead-Time Estimator  →  Alert Generator  →  Visualization / API 

## **Component-by-component** 

## **1. Data Ingestion** 

- **What:** pulls raw rainfall, DEM, and historical hazard points for the chosen AOI. Why: the 4 PS-required inputs come from 3 independent external sources — nothing is bundled together upstream. 

- **Rainfall:** GPM IMERG Final Daily Precipitation (GPM_3IMERGDF v07), NASA–JAXA satellite product, 0.1° (~10 km) grid, mm/day. Latency caveat (state honestly): ~3.5-month processing delay on the Final Run — great for pipeline building & historical back-testing, but real deployment would swap to IMERG Early Run (~4 hr) or Late Run (~14 hr). Access via NASA Earthdata Login + the earthaccess Python library. 

- **Terrain slope:** no ready dataset exists for slope directly — it's derived from a DEM. Recommended: OpenTopography's SRTM GL1 (30 m) or Copernicus GLO-30, via a free OpenTopography API key. Delivered as GeoTIFF. 

- **Historical hazard data:** primary machine-readable source = NASA Global Landslide Catalog (GLC/COOLR) — CSV/JSON/XML export with event date + lat/long + trigger category, direct bulk download. Cross-validated visually (not bulk API) against GSI Bhusanket portal and the ISRO/NRSC Landslide Atlas of India (~80,000 landslides, 1998–2022, delivered as a PDF atlas, not an API) — used to sanity-check district-level exposure, not as a primary programmatic input. 

- Tech: earthaccess, requests. Where it runs: local laptop CPU, no GPU needed. 

## **2. Preprocessing** 

- What enters: raw DEM GeoTIFF, raw IMERG NetCDF/HDF5, raw GLC CSV — all in different resolutions and possibly different coordinate systems. 

   - Reprojection — convert everything to one common CRS (EPSG:4326 lat/long, or local UTM for accurate distance). 

   - Clipping — crop every layer to the AOI boundary/bounding box. 

   - Resampling — DEM (30 m) and IMERG (~10 km) are wildly different resolutions; both are resampled onto one common analysis grid (e.g. 1 km cells) — bilinear interpolation for continuous values, nearest-neighbour where appropriate. 

   - Slope computation — standard 3×3 neighbourhood gradient method on the resampled DEM (richdem, or numpy.gradient as manual fallback). 

   - Missing-data handling — a cell with zero historical points is not automatically "safe": missing historical density is treated as the AOI median (neutral), not zero, to avoid under-scoring genuinely risky but underreported villages. (Good "we thought about failure modes" point for judges.) 

- Tech: rasterio, numpy, geopandas, shapely, richdem. Where: local CPU. 

## **3. Feature Engineering** 

- What enters: the cleaned, aligned layers. Inside: assembles one feature table — one row per grid cell/village, columns = normalised slope, today's rainfall, 3-day rainfall sum, 15-day rainfall sum (soil-saturation proxy), historical density, elevation. Every factor is normalised to 0–1 so no single factor's raw units dominate the combined score. 

- **Soil saturation caveat (important honesty point):** there is no direct soil-saturation dataset supplied by the PS, so this project approximates it using antecedent rainfall (3-day and 15-day rolling sums) as a proxy — wetter recent history roughly implies wetter soil. State this plainly; don't imply a real soil-moisture sensor/dataset unless separately sourced. 

## **4. Risk Scoring Engine — the algorithmic core** 

The Weighted Risk Index formula: 

RiskScore = 100 × ( w1·slope_norm + w2·rain_today_norm + w3·rain_3day_norm + w4·rain_15day_norm + w5·historical_density_norm ) Suggested starting weights (sum to 1, tune per region): w1 (slope) = 0.30    w2 (today's rain) = 0.20    w3 (3-day) = 0.15 w4 (15-day) = 0.15    w5 (history) = 0.20 

- Classification thresholds: Low 0–24 / Moderate 25–49 / High 50–74 / Severe 75–100 (adjust after seeing real AOI scores). 

- Flash-flood variant: same formula, but re-weight toward low-slope, high-flow-accumulation valley cells instead of steep cells, since flash floods concentrate in drainage lines, not on the steepest slope points. 

## **Model choice comparison (for judge Q&A)** 

|**Approach**|**Verdict**|**Why**|
|---|---|---|
|Weighted Risk Index (rule-based)|Chosen for MVP|No GPU/training data needed; fully<br>explainable; matches established GSI/NRSC<br>weighted-overlay methodology|
|Random Forest classifier|Optional stretch (8.2)|Needs labelled positive + pseudo-absence<br>points; feasible on CPU in seconds; only<br>viable if AOI has enough historical points|
|Deep learning / CNN|Rejected for MVP|No pretrained "landslide risk" network exists;<br>small, sparse, tabular data doesn't suit deep<br>nets; needs GPU + large labelled imagery<br>corpus|



Tech: pure numpy/pandas for the weighted index; scikit-learn RandomForestClassifier for the optional upgrade. Where: CPU, laptop-grade. 

## **5. Lead-Time Estimator** 

- What enters: per-cell recent rainfall trend (intensity + running duration). 

- Inside: compares it against a published rainfall intensity–duration (ID) threshold — a globally-cited reference (Caine, 1980): I = 14.82 × D^(-0.39) (I = intensity mm/hr, D = duration hours). Combinations above the curve have historically been associated with triggered landslides. 

- Out: estimated hours remaining until the trend would cross the threshold at the current rate. 

- **Explicit limitation to state out loud:** this is a global reference curve, not locally calibrated to your AOI — GSI's India-specific Regional Landslide Forecasting System thresholds are the "right" long-term replacement once available. Stating this yourself pre-empts a judge catching you overclaiming. 

## **6. Alert Generator** 

What enters: Risk class + lead time per cell/village. Inside: converts (Risk class, lead time) → an alert record (village, risk class, lead time, recommended action) and simulates dispatch — console/log/webhook print, explicitly no real SMS/telecom integration in the MVP (that would need a telecom/notification API not provided by the PS). 

## **7. Visualization / API** 

Inside: colour-coded interactive map via folium (Leaflet-style) + an alert table. Optional: FastAPI backend serving Risk GeoJSON + alert table, Streamlit or Leaflet frontend for a clickable live demo. 

## **Evaluation metrics** 

|**Metric**|**Meaning**|**How computed**|
|---|---|---|
|Precision|Of cells flagged High/Severe, fraction that had a<br>nearby recorded event|TP/(TP+FP) on back-test|
|Recall (Detection Rate)|Of actual historical events, fraction flagged<br>High/Severe in advance|TP/(TP+FN) on back-test|
|False Alarm Rate|How often it cries wolf with no recorded event|FP/(FP+TN)|
|AUC / Success-Rate curve|Overall ranking quality of Risk Score vs known<br>events|sklearn.metrics.roc_auc_score|
|Lead-time back-test|Median hours between alert crossing High/Severe<br>and recorded event date|Compare alert timestamp vs<br>GLC event date|
|Baseline comparison|Does the full index beat rainfall alone?|Re-run back-test using only<br>the rainfall factor and<br>compare — your single most<br>convincing evidence|



## **Tech stack summary** 

|**Layer**|**Tool**|
|---|---|
|Language / env|Python 3.10/3.11, venv|
|Data access|earthaccess, requests|
|Geospatial core|rasterio, numpy|
|Geospatial vector|geopandas, shapely|
|Terrain analysis|richdem|
|Tabular / ML|pandas, scikit-learn|
|Visualization|matplotlib, folium|
|Demo app|streamlit or FastAPI + Leaflet|



## **What judges may challenge on this slide** 

- "What's your actual grid/village resolution and why?" — pick and justify a number (e.g. 1 km, matched to your resampling choice). 

- "Why weighted sum weights of 0.30/0.20/0.15/0.15/0.20 specifically?" — be honest these are suggested starting weights, meant to be tuned per region; not yet locally calibrated — a legitimate limitation to state, not hide. 

- "Is your rainfall data real-time?" — No: Final Run IMERG has ~3.5-month latency; MVP is a daily-refresh batch pipeline, not streaming; production would switch data products. 

- "How do you validate against ground truth?" — via the back-test against NASA GLC historical events plus visual cross-check against GSI Bhusanket / ISRO Atlas zones. 

## **Visual approach** 

This slide needs the most structure. Recommended layout: one big horizontal architecture diagram spanning the slide width, 7 boxes left to right (Ingestion → Preprocessing → Feature Engineering → Risk Scoring → Lead-Time → Alerts → Visualization), each box with a 1-line tech label underneath and a small icon (satellite, funnel, gauge, clock, bell, map). 

Below/beside the diagram, give the Weighted Risk Index formula its own visually distinct callout (monospace/formula styling) — it's your single most important piece of intellectual content and deserves visual prominence, not burial in a bullet list. 

If your deck allows a second slide here, put the model-choice comparison table (Weighted Index vs Random Forest vs Deep Learning) on it — it directly answers the "why not ML" question before it's asked. 

# **Slide 6 — Impact & Feasibility** 

## **What this section must prove** 

That the system, if built as scoped, is realistically usable by real people, on real hardware, at real cost — and that you know its limits rather than overselling it. 

## **Beneficiaries & real-world use cases** 

- Primary beneficiaries: village-level disaster-response teams and local administration in landslide/flash-flood-prone hill districts (Himalayan belt, North-East hills, Western Ghats). 

- Use case: a district disaster-management officer opens the daily-refreshed risk map, sees which villages are High/Severe today, checks the estimated lead time, and dispatches a (currently simulated) evacuation notice/advisory. 

- Secondary beneficiary: researchers/GSI-adjacent bodies could use the transparent scoring as a cross-check reference alongside their own susceptibility zoning. 

## **Practical benefits** 

Converts scattered public/satellite datasets that no single agency currently fuses at the village level into one actionable daily artifact (map + table + alert log) — fully auditable, since every score is explainable by factor contribution, which matters for institutional trust in a life-safety tool. 

## **Technical feasibility** 

- Runs entirely on a normal laptop CPU — no GPU required for the MVP (rule-based scoring + optional Random Forest both train/run in seconds on CPU). 

- All core datasets are free: NASA Earthdata (free login), OpenTopography (free API key), NASA GLC (free CSV download). 

- Software stack is all open-source Python (rasterio, geopandas, scikit-learn, folium, etc.) — no licensing cost. 

## **Cost / resource considerations** 

- Zero data acquisition cost (all sources are free/public). 

- Compute cost ≈ a laptop; no cloud GPU spend needed for MVP. 

- Main resource cost is engineering time to correctly reproject/resample/align the different-resolution datasets (DEM 30 m vs. rainfall ~10 km) — worth naming explicitly, since it shows technical maturity. 

## **Scalability** 

- The pipeline is designed per-AOI (bounding box in, results out) — scaling to new districts/states means re-running with a new bounding box, not re-architecting. 

- Scaling to true near-real-time nationwide coverage would require switching to IMERG Early/Late Run, automating the batch refresh (e.g. a daily cron job), and a proper backend (the optional FastAPI layer) rather than notebookdriven runs. 

## **Deployment practicality** 

MVP deployment = a saved HTML map (folium) + a CSV/table, or a Streamlit app for a live clickable demo — realistic within a hackathon's time window. Full deployment (real SMS/WhatsApp alert dispatch) explicitly requires a telecom/notification API integration not provided by the problem statement — flag this as future work, don't imply it's built. 

## **Limitations (state these proactively — it builds credibility)** 

- Rainfall data (Final Run IMERG) has ~3.5-month latency — not usable for live alerting as-is, only for pipeline development and historical back-testing. 

- Soil saturation is a proxy (antecedent rainfall), not a directly measured quantity. 

- The lead-time threshold curve (Caine, 1980) is a global reference, not locally calibrated to the AOI. 

- Historical data (NASA GLC) is incomplete — media/database-compiled, not an exhaustive record — so recall against it is a lower bound on real performance, not an absolute number. 

## **Risks** 

- False alarms (rule-based thresholds mis-tuned) eroding local trust in the system over time. 

- Under-reporting bias in historical data making some genuinely risky villages look "clean" by the historical-density factor (mitigated by the neutral-median handling described in preprocessing). 

## **Future extensions** 

- Random Forest / ML susceptibility layer once enough labelled points exist for the AOI. 

- DEM-derived flow accumulation for a sharper, valley-focused flash-flood signal. 

- Real soil-moisture satellite data replacing the antecedent-rainfall proxy, if access is separately arranged. 

- Real SMS/WhatsApp/webhook-based alert dispatch (needs an external telecom API). 

- Swap to IMERG Early/Late Run once near-real-time alerting is the goal. 

## **What can realistically be demoed at a hackathon** 

A working pipeline for one chosen AOI and one historical date range, showing: the risk map (color-coded, per grid cell/village), the alert table with lead times, a simulated alert log for High/Severe cells, and — most convincingly — the baseline comparison chart (rainfall-only vs. full Weighted Risk Index) proving the fused approach adds real value over the naive one. 

## **Visual approach** 

- A "who benefits" strip at the top: 2–3 icon+caption pairs (village disaster officer, resident, planner) rather than paragraphs. 

- A feasibility checklist/badge row: "No GPU needed," "Free data sources," "Runs on laptop," "Open-source stack" — small pill/badge shapes, very scannable, reassures judges on practicality in seconds. 

- A small, honest limitations box (present but not the visual focus) — 3–4 short lines, so the slide doesn't read as oversold. 

- If you have a real back-test result by demo day, a small before/after bar chart (rainfall-only vs. full-model recall/precision) is the single most persuasive visual you can put anywhere in the deck — prioritize building this over more diagrams elsewhere if time is short. 

# **Slide 7 — References & Research** 

## **What it's proving** 

Rigor, and that your data sources are real, traceable, and legitimate — not invented. 

## **The actual reference list** 

- GPM IMERG Final Daily Precipitation (GPM_3IMERGDF v07) — earthdata.nasa.gov 

- earthaccess Python library — earthaccess.readthedocs.io 

- GSI Bhusanket Web Portal / National Landslide Forecasting Centre — bhusanket.gsi.gov.in 

- ISRO/NRSC Landslide Atlas of India — isro.gov.in/Landslide_Atlas_India.html 

- NASA Global Landslide Catalog (GLC) export — data.nasa.gov 

- NASA COOLR (Cooperative Open Online Landslide Repository) — landslides.nasa.gov 

- OpenTopography (SRTM GL1 / Copernicus GLO-30 DEM) — opentopography.org 

- Caine, N. (1980). The rainfall intensity–duration control of shallow landslides and debris flows. Geografiska Annaler, 62A(1–2), 23–27 — source of the lead-time formula. 

## **Visual approach** 

A clean two-column list (Data sources | Scientific reference), small official logos/icons where you have rights to use them (NASA, ISRO, GSI), with the Caine (1980) citation set visually apart since it's the one academic citation underpinning your lead-time formula — research-background judges will specifically look for this to confirm the formula isn't invented. 

# **A. Complete System Mental Model** 

Every day, the pipeline looks at one chosen hilly patch of India (your AOI). It downloads: how much it rained there recently (satellite rainfall data), how steep the ground is there (from elevation data), and where landslides/floods have happened there before (a historical events list). Since nobody directly measures "how soggy is the soil," it estimates that using recent rainfall totals as a stand-in. It lines all of this up on the same map grid, turns each factor into a 0–1 number, and combines them with fixed, human-chosen weights into a single 0–100 Risk Score per village-sized cell. That score is bucketed into Low/Moderate/High/Severe. Separately, it checks today's rainfall trend against a known scientific rule about how much rain over how many hours has historically triggered landslides, to estimate how many hours of warning are left. Finally, it draws a color-coded map, produces a table of villages with their risk level and hours-remaining, and prints/logs a simulated evacuation alert for anything High or Severe. Nothing here is a trained AI model in the MVP — it's a transparent formula, which is a deliberate, defensible choice given the data and time constraints. 

# **B. Technical Architecture Summary** 

Seven layers in sequence: Ingestion (earthaccess / OpenTopography / GLC CSV) → Preprocessing (reproject / clip / resample / slope / handle missing data) → Feature Engineering (normalised feature table per cell) → Risk Scoring (Weighted Risk Index formula, optionally Random Forest later) → Lead-Time Estimator (Caine 1980 ID-threshold comparison) → Alert Generator (simulated dispatch) → Visualization (folium map + table, optional FastAPI/Streamlit). Everything runs CPU-only on a laptop. 

# **C. Judge Question Bank** 

- **"Why not deep learning?" →** No pretrained landslide-risk network exists; ML needs curated labelled points, a real data-engineering task; tabular/sparse data suits simple interpretable models better; weighted-overlay is the established real-world first step. 

- **"How do you know your weights are right?" →** They're published starting weights from the guide's methodology, explicitly meant to be tuned per-region using back-test results; not yet locally calibrated — state as a known limitation. 

- **"Your rainfall data is 3.5 months old — how is this an early-warning system?" →** It isn't, yet, for live deployment; the Final Run product is deliberately used for pipeline-building and historical back-testing; production would swap to Early/Late Run IMERG (4–14 hr latency). 

- **"What is 'soil saturation' actually measured from?" →** It's not measured — it's a proxy built from 3-day and 15-day antecedent rainfall sums, explicitly acknowledged as an approximation. 

- **"How is 'lead time' calculated — is it a guess?" →** Derived from comparing current rainfall trend against a peerreviewed global threshold curve (Caine, 1980); scientifically grounded but based on a global, not India-locallycalibrated, curve. 

- **"How do you validate this actually works?" →** Back-testing against real historical NASA GLC events: check whether the pipeline, run with only data available up to that date, would have flagged the event location as High/Severe, comparing against a rainfall-only baseline. 

- **"What happens to villages with no historical landslide records — marked 'safe'?" →** No — missing historical density is treated as the AOI median (neutral), specifically to avoid under-scoring genuinely risky but underreported villages. 

- **"Is this scalable beyond your one AOI?" →** Yes architecturally (bounding-box parameterized pipeline), but each new AOI needs its own data pull and possibly re-tuned weights; not literally a flip-a-switch nationwide system yet. 

- **"What's actually novel vs. just plumbing together public data?" →** The honest answer: fusing 4 heterogeneous sources into one explainable, per-village decision artifact with an operational lead-time number — not a new algorithm or new dataset. 

- **"Are the evacuation alerts real?" →** No — simulated (console/log output) in the MVP; real SMS/WhatsApp dispatch needs a telecom/notification API not provided by the problem statement. 

# **D. What We Must Actually Build** 

## **MVP (must-have, required)** 

- Fixed AOI (one district or ~50×50 km hilly region). 

- Data ingestion for rainfall (IMERG), DEM (OpenTopography/SRTM), and historical points (NASA GLC). 

- Preprocessing: reprojection, clipping, resampling, slope computation, historical density rasterization. 

- Weighted Risk Index scoring engine + classification. 

- Lead-time estimator (Caine ID-threshold). 

- Simulated alert generator. 

- Static or lightly-interactive map (folium) + alert table. 

- Basic back-test evaluation (precision/recall/false-alarm-rate) + rainfall-only baseline comparison. 

## **Optional / stretch (build only if MVP is fully working)** 

- Random Forest susceptibility classifier (needs sufficient labelled points — verify first). 

- DEM-derived flow accumulation for sharper flash-flood (valley) detection. 

- FastAPI backend + Streamlit/Leaflet live dashboard. 

- Real soil-moisture data replacing the rainfall proxy. 

- Real SMS/WhatsApp/webhook alert dispatch. 

- IMERG Early/Late Run for near-real-time capability. 

# **E. Knowledge Gaps — Resolve Before/While Implementing** 

- **[ASSUMPTION]** Which specific AOI (district/state) your team will use is not yet decided — needs picking before any data can be pulled (guide suggests Uttarakhand, Himachal Pradesh, or Western Ghats as examples). 

- **[ASSUMPTION]** Whether your AOI has enough NASA GLC historical points to make the optional Random Forest upgrade meaningful is unverified — check before committing to it as a stretch goal. 

- **[ASSUMPTION]** Final weight values (currently just "suggested starting weights") are untuned for your specific AOI — real tuning needs back-test data you don't have yet. 

- **[ASSUMPTION]** Access to ISRO Atlas shapefiles / GSI NLSM shapefiles (better than the CSV-only NASA GLC) depends on institutional access your team may or may not have — the guide treats NASA GLC CSV as the fallback machine-readable source. 

- **[RESEARCH NEEDED]** The Caine (1980) ID-threshold is a global reference; whether a more locally-calibrated Indian threshold (referenced only as "GSI's Regional Landslide Forecasting System work") is publicly obtainable is unconfirmed — worth a quick search before claiming any locally-tuned threshold. 

- **[ASSUMPTION]** Exact grid-cell size (the guide suggests 1–5 km / matching village boundaries) is a team decision not yet locked in — affects both DEM/rainfall resampling and how results map to real villages. 

