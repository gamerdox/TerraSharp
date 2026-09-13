# **PixelForge Disaster Intelligence Platform** 

Complete Implementation Blueprint — Build-Ready Specification SIH26142 (PS142) — Team VIJAYAASTRA — Grand Finale 

##### **Legend:** 

**[IMPLEMENTED]** verified present in your uploaded code/docs/PPT/Excel **[TO BUILD]** required for the 36-hour MVP, not yet built **[PLANNED]** post-Finale roadmap, architecture only 

1 

## 0. Source-of-Truth & Method Note 

This blueprint is built from direct inspection of PROJECT_SYSTEM_DOCUMENTATION.docx, PixelForge.pptx (8 slides, SIH26142), and Sentinel2SRNet_Benchmark_Comparison.xlsx, plus your original attached specification document (treated as target architecture) and the prior integrity audit (backend serving FSRCNN/ESPCN instead of Sentinel2SRNet; EDSR silently falling back to bicubic). Every dataset/license/access-method claim below was checked against live sources on 11 Sep 2026; anything not independently verifiable is explicitly marked UNVERIFIED — do not repeat those claims to a jury without checking the primary source yourself first. 

Nothing in this document claims a model, dataset, or pipeline is trained/running unless it is tagged IMPLEMENTED. Everything else is a specification for another engineer/agent to execute — not a claim of existing functionality. 

## 1. Gap Analysis 

|**Component**|**Documented/Claimed**|**Actually Implemented**|**Status**|**Required Action**|
|---|---|---|---|---|
|Sentinel2SRNet<br>architecture|193.6K params, YCrCb chroma-<br>lock, Sobel-edge + zero-mean-<br>drift loss, 8-way D4 TTA, 2.5m<br>GSD cascade|Architecture documented in spec;<br>prior audit found live backend<br>serving OpenCV<br>FSRCNN/ESPCN instead of this<br>checkpoint|GAP —<br>CRITICAL|Load and serve the<br>real .pth checkpoint;<br>remove OpenCV<br>model substitution|
|EDSR baseline|Listed as comparison baseline in<br>benchmark sheet|Silently falls back to bicubic<br>interpolation when invoked|GAP —<br>CRITICAL|Either load true<br>EDSR weights or<br>relabel the row<br>'Bicubic (mislabeled<br>EDSR)' until fixed|
|Benchmark metrics|Deck narrative implies SR<br>superiority|Excel shows Sentinel2SRNet<br>behind<br>Bicubic/ESPCN/FSRCNN/EDSR<br>on<br>PSNR/SSIM/MAE/SAM/ERGA<br>S; wins only on params (~200x<br>smaller than EDSR), speed, and<br>TTA uncertainty|Data accurate,<br>narrative not<br>yet aligned|Rewrite deck claims<br>to match workbook<br>exactly|
|TTA variant|8-way dihedral TTA for<br>uncertainty mapping|Currently produces a smoothing<br>effect (negative edge gain)<br>instead of sharpening|GAP|Fix aggregation<br>(median/trimmed-<br>mean instead of<br>plain mean) or<br>clearly narrate it as<br>an uncertainty tool,<br>not a sharpening tool|
|Disaster response|1 bullet on slide 7: damage<br>detection, road/building<br>disruption mapping|No code — no change detection,<br>no damage model, no GIS, no<br>infrastructure intersection|NET-NEW|This entire<br>document specifies<br>the build|
|Backend framework|FastAPI in tech stack|SR-serving endpoints only|PARTIAL|Extend with<br>ingestion/change/pri<br>ority/report<br>endpoints (Section<br>6)|
|Frontend|Not detailed in supplied docs|Unknown — not present in files<br>reviewed|UNKNOWN|Inspect separately if<br>it exists; else build<br>per Section 7|
|GIS layer|Leaflet named once in stack list|No map, no AOI, no overlays|NET-NEW|Build per Section 9|



2 

|**Component**|**Documented/Claimed**|**Actually Implemented**|**Status**|**Required Action**|
|---|---|---|---|---|
|Datasets beyond<br>SEN2VENµS|Not present|Not present|NET-NEW|Section 3|



## 2. Final System Architecture (text diagram) 

### 2.1 Layered view 

<mark>┌─────────────────────────────────────────────────────────────────┐ │ FRONTEND (React + Leafet)                          [TO BUILD]   │ │  Map Console  AOI Draw  Before/After Swipe  Evidence Panel     │ │ │ │ │  Priority Dashboard  Report Viewer  (SOS/Incidents — stretch)   │ │ │ └───────────────┬─────────────────────────────────────────────────┘ REST/JSON + GeoJSON  (Section 6)│ ┌───────────────▼─────────────────────────────────────────────────┐ │ API GATEWAY — FastAPI (async)                                    │ │  /aoi /imagery /sr /change /infrastructure /priority /report      │ │  Auth stub, request validation, job dispatch                      │ └───────────────┬─────────────────────────────────────────────────┘ │ ┌───────────┼──────────────┬───────────────┬─────────────────┐ ▼ ▼ ▼ ▼ ▼ ┌─────────┐┌───────────┐┌───────────┐┌───────────────┐┌─────────────┐ │INGESTION SR ENGINE   CHANGE       INFRASTRUCTURE   PRIORITY     ││ ││ ││ ││ │ │SERVICE   Sentinel2   DETECTION    INTERSECTION     ENGINE       ││ ││ ││ ││ │ │[TO BUILD] SRNet+TTA   NDWI/NDVI/   OSM Overpass     Transparent  ││ ││ ││ ││ │ │Copernicus [FIX+SERVE] NBR dif││ ││ GHSL pop         scoring      ││ ││ │ │OData API              [TO BUILD]   [TO BUILD]       [TO BUILD]   ││ ││ ││ ││ │ └────┬────┘└─────┬─────┘└─────┬─────┘└───────┬────────┘└──────┬──────┘ │ │ │ │ │</mark> 

<mark>└────────────┴──────┬──────┴────────────────┴─────────────────┘</mark> 

<mark>▼</mark> 

<mark>┌──────────────────────────────┐</mark> 

<mark>DB (PostGIS) + OBJECT STORE     [TO BUILD]│ │ metadata, geometries, tiles   │ │ └──────────────┬────────────────┘ ▼ ┌──────────────────────────────┐ REPORT GENERATOR (PDF/GeoJSON) [TO BUILD]│ │ └──────────────────────────────┘</mark> 

### 2.2 What is real today vs what this document specifies 

- **[IMPLEMENTED]** Sentinel2SRNet architecture + training methodology (documented, needs checkpoint wired into serving path) 

- **[IMPLEMENTED]** Benchmark comparison data (Excel) against ESPCN/FSRCNN/EDSR/Bicubic 

- **[TO BUILD]** Everything inside the dashed boxes above except the SR engine core math 

3 

- **[PLANNED]** Sentinel-1 SAR fusion, SOS/incident workflow, RBAC/auth, offline sync — specified in later sections as architecture only 

4 

## 3. Complete Dataset Matrix 

Verification status as of 11 Sep 2026. UNVERIFIED items must be re-checked by your team before citing exact license text to a jury — licenses and access mechanisms on third-party portals change. 

### 3.1 Datasets for the FLOOD MVP (36-hour scope) 

|**Dataset**|**Source / URL**|**Resolution &**<br>**Bands**|**Labels**|**License**|**Access**<br>**Method**|**Intended**<br>**Module**|**Verify**|
|---|---|---|---|---|---|---|---|
|Sentinel-2<br>L2A|Copernicus Data<br>Space Ecosystem<br>dataspace.copernic<br>us.eu|10m/20m/60m, 13<br>bands (B2-B4, B8<br>= RGB+NIR at<br>10m)|None (raw<br>imagery)|Free, open,<br>ESA<br>Copernicus<br>terms|OData API /<br>Copernicus<br>Browser /<br>sentinelhub-py|Ingestion,<br>SR input,<br>spectral<br>indices|VERIFI<br>ED|
|SEN2VENµS|CNES/ESA<br>research release|Sentinel-2 10m<br>paired with<br>VENµS 5m|Paired LR/HR<br>reflectance|Research use<br>(non-<br>commercial)|Direct<br>download from<br>project page|<br>SR training<br>(already in<br>use)|VERIFI<br>ED —<br>already<br>in your<br>pipeline|
|Sen1Floods11|Cloud to Street;<br>github.com/cloudt<br>ostreet/Sen1Floods<br>11|Sentinel-1 SAR<br>(VV/VH, 10m) +<br>Sentinel-2 (13<br>bands); 4,831<br>chips, 446 hand-<br>labeled high-<br>quality|Pixel-wise<br>water/permanen<br>t-water/flood<br>labels,<br>generated via<br>NDVI+MNDWI<br>thresholding<br>then hand-<br>corrected|<br>Open access<br>research<br>dataset<br>(attribution<br>required —<br>confirm exact<br>SPDX before<br>commercial<br>claims)|Google Cloud<br>Storage bucket<br>gs://sen1floods<br>11 via gsutil,<br>or<br>HuggingFace<br>mirror|Flood<br>segmentatio<br>n model<br>training/vali<br>dation<br>(SHOULD-<br>tier)|PARTIA<br>LLY<br>VERIFI<br>ED —<br>confirm<br>license<br>text<br>directly|
|OpenStreetMa<br>p (buildings,<br>roads)|OpenStreetMap.or<br>g via Overpass<br>API|Vector, not<br>imagery|Building<br>footprints, road<br>centerlines/class<br>es, POIs<br>(hospitals,<br>shelters)|ODbL<br>(attribution +<br>share-alike<br>for derived<br>databases)|Overpass API /<br>osmnx<br>(Python)|<br>Infrastructur<br>e<br>intersection<br>— no model<br>needed|<br>VERIFI<br>ED|
|GHSL (GHS-<br>BUILT-C,<br>GHS-POP)|human-<br>settlement.emerge<br>ncy.copernicus.eu<br>(EC Joint<br>Research Centre)|GHS-BUILT-C:<br>10m (derived from<br>Sentinel-2 2018<br>composite); GHS-<br>POP: 100m grid|Built-up<br>classification /<br>population<br>count per cell|CC BY 4.0,<br>free, no<br>registration|Direct<br>download from<br>JRC portal or<br>Google Earth<br>Engine catalog|<br>Population/<br>settlement<br>exposure<br>estimate|VERIFI<br>ED|
|Copernicus<br>DEM GLO-30|Copernicus Data<br>Space Ecosystem /<br>OpenTopography /<br>AWS Open Data<br>(s3://copernicus-<br>dem-30m)|30m global DSM|Elevation only|Free for<br>general<br>public under<br>Copernicus<br>DEM license<br>(attribution<br>required)|AWS S3<br>direct,<br>OpenTopograp<br>hy API (free<br>key), or CDSE|Slope/<br>terrain<br>context for<br>landslide-<br>adjacent<br>talking<br>points, flood<br>flow<br>direction|<br>VERIFI<br>ED|
|Copernicus<br>EMS Rapid<br>Mapping|emergency.coperni<br>cus.eu|Varies by<br>activation (often<br>sub-metre to a few<br>m, event-specific)|Authoritative<br>flood/damage<br>extent polygons<br>for actual<br>declared<br>disasters|Free and open<br>Copernicus<br>data policy|<br>Direct<br>download per<br>activation, no<br>API for<br>arbitrary AOI|Ground-<br>truth<br>validation<br>for a<br>specific<br>historical<br>demo event<br>only|VERIFI<br>ED —<br>activatio<br>n-based,<br>not for<br>arbitrary<br>AOI|



5 

3.2 Datasets evaluated but NOT recommended for the flood MVP (domain mismatch — explain if asked) 

|**Dataset**|**Resolution/Sensor**|**Why it doesn't fit the MVP**|**Where it DOES fit**|**License**|
|---|---|---|---|---|
|xBD / xView2|~0.3–0.5m Maxar<br>optical (DigitalGlobe<br>Open Data)|Order-of-magnitude finer resolution<br>than Sentinel-2 (10m). Training a<br>Sentinel-2-scale model on 0.5m<br>labels without resolution-matched<br>downsampling will silently<br>mismatch label granularity to pixel<br>footprint — a jury-catchable error|Building damage<br>classification IF you later<br>fuse a high-res commercial<br>or UAV source; or as a<br>pretraining prior with<br>heavy domain-gap caveats|CC BY-NC-SA<br>(registration required at<br>xview2.org) —<br>UNVERIFIED exact<br>version (3.0 vs 4.0 cited<br>inconsistently across<br>mirrors)|
|FloodNet /<br>RescueNet|UAV imagery,<br>~1.5cm GSD|UAV, not satellite — completely<br>different sensor geometry and<br>altitude; cannot be mixed into a<br>Sentinel-2 pipeline without a<br>separate model|Field-verification<br>companion tool if NDRF<br>ever supplies drone<br>footage — PLANNED,<br>not MVP|Community Data License<br>Agreement (permissive) for<br>FloodNet|
|SpaceNet<br>(building/road)|~0.3–0.5m<br>WorldView optical;<br>SpaceNet 6 adds<br>Sentinel-1 SAR|Same resolution mismatch as xBD<br>for the optical tiers; SpaceNet 6<br>SAR component is the only sub-<br>collection resolution-compatible<br>with a Sentinel-1 fusion path|Road/building extraction<br>backbone IF you add<br>Sentinel-1 fusion in a later<br>phase|CC BY-SA 4.0 —<br>UNVERIFIED, confirm<br>per-collection terms on<br>registry.opendata.aws/space<br>net|
|WorldPop|100m / 1km gridded<br>population|Redundant with GHS-POP for<br>MVP purposes; GHSL already<br>selected for consistency with GHS-<br>BUILT-C|Alternate/cross-check<br>population source|CC BY 4.0 —<br>UNVERIFIED, confirm on<br>worldpop.org before citing|



Explain-if-asked line for the jury: "We evaluated xBD/xView2, FloodNet, and SpaceNet for building-damage training data. All three operate at sub-metre to centimetre resolution — 20 to 300 times finer than Sentinel-2's 10m native GSD. Training or validating a Sentinel-2-scale model against those labels would silently misrepresent detection confidence, so for the Sentinel-2 MVP we use direct OSM footprint intersection instead of a learned damage classifier, and flag learned building-damage segmentation as a Phase-2 item requiring either SAR fusion (SpaceNet 6) or a resolution-matched high-res source." 

### 3.3 Disaster-specific dataset additions (PLANNED, beyond flood MVP) 

|**Disaster**|**Additional dataset**|**Purpose**|**Verify status**|
|---|---|---|---|
|Earthquake|xBD (earthquake subset) + Copernicus<br>DEM|Building/road change candidates, terrain<br>context|License UNVERIFIED per<br>§3.2|
|Cyclone|GHSL + OSM + Sentinel-2 NDVI time<br>series|Vegetation loss, settlement exposure,<br>road disruption|VERIFIED (already listed<br>above)|
|Wildfire|Sentinel-2 (NBR/dNBR bands B8/B12) +<br>Copernicus EMS burn perimeter (where<br>activated)|Burn severity classification|VERIFIED|
|Landslide|Copernicus DEM (slope/aspect) +<br>Sentinel-1 SAR coherence|Terrain-risk candidate zones, not<br>confirmed slides|VERIFIED (DEM); SAR<br>coherence pipeline<br>PLANNED|



6 

## 4. Complete Model / Training Matrix 

### 4.1 Sentinel2SRNet — fix and serve (MUST, fixes existing gap) 

|**Field**|**Value**|
|---|---|
|Task|Single-image super-resolution, 10m → 2.5m (2x then cascaded 2x = 4x)|
|Architecture|Deep residual CNN, 48-channel residual body, PixelShuffle sub-pixel upsampling, YCrCb luminance-only<br>processing, zero-mean residual projection (documented in your spec — IMPLEMENTED as architecture)|
|Params / checkpoint|193,601 trainable params, 765.5KB checkpoint (per your benchmark sheet — IMPLEMENTED)|
|Loss|L_total = L1 + α·L_Sobel_edge (α=2.5) + β·L_mean_drift (β=5.0) — documented, IMPLEMENTED|
|Training data|SEN2VENµS paired LR(10m)/HR(5m/2.5m) tiles|
|Status|TO BUILD: locate/retrain the checkpoint and wire it into the FastAPI /sr endpoint, replacing the OpenCV<br>FSRCNN/ESPCN substitution found in the prior audit. This is the single highest-priority fix.|
|Inference|~25–38ms/tile on CPU (per your deck claim — verify on the actual serving hardware before repeating this<br>number to a jury; re-benchmark after the checkpoint swap)|
|TTA fix|8-way D4 TTA currently smooths rather than sharpens (negative edge gain). Likely cause: simple mean<br>aggregation across the 8 transformed predictions washes out high-frequency detail. TO BUILD: switch<br>aggregation to per-pixel median or a learned confidence-weighted average; re-measure edge gain (Sobel<br>energy ratio, SR vs bicubic) before/after the fix.|
|Evaluation|PSNR, SSIM, MAE, SAM, ERGAS, VARI-index MAE vs Bicubic/ESPCN/FSRCNN/EDSR — all<br>IMPLEMENTED in your Excel workbook. Honest framing: currently behind all baselines on fidelity<br>metrics; wins on parameter count (~200x smaller than EDSR), latency, and TTA-derived uncertainty.|



### 4.2 Flood change detection — NDWI/MNDWI differencing (MUST, no training required) 

|**Field**|**Value**|
|---|---|
|Task|Pre/post water-extent change → flood polygon|
|Method|Rule-based spectral index, not a trained model: MNDWI = (Green−SWIR)/(Green+SWIR) using<br>Sentinel-2 B3 (Green) and B11 (SWIR); threshold MNDWI > 0 as water. Compute for pre- and post-<br>disaster scenes, difference the water masks, keep newly-water pixels as flood candidates.|
|Preprocessing|Cloud/shadow mask via Sentinel-2 Scene Classification Layer (SCL band); co-register pre/post scenes<br>(same UTM tile, resample to common grid); apply after SR upsampling so index is computed at 2.5m|
|Confidence|Per-pixel confidence = f(TTA variance at that pixel, cloud-mask distance, index margin from threshold) —<br>simple weighted combination, documented not black-box|
|Output|GeoJSON polygon(s) of flood extent + area in km² + confidence band|
|Validation method|Cross-check against Copernicus EMS Rapid Mapping flood polygon for the SAME historical event used<br>in the demo (only works for a past declared emergency — pick one, e.g. a known flood event with EMS<br>activation, as your demo AOI)|
|Metrics|IoU / F1 / precision / recall vs EMS polygon for the demo event|
|Compute|CPU-only, no GPU required, runs in well under a second per tile|



### 4.3 Flood segmentation model — SHOULD tier, only if time remains 

|**Field**|**Value**|
|---|---|
|Task|Learned water segmentation to complement/cross-check the NDWI rule|



7 

|**Field**|**Value**|
|---|---|
|Dataset|Sen1Floods11 (446 hand-labeled chips, 512x512, 10m) — see §3.1 for access|
|Split|Use the dataset's own published train/valid/test CSV splits (do not re-split — preserves comparability to<br>published baselines)|
|Preprocessing|Normalize Sentinel-1 VV/VH to dB scale (10·log10); Sentinel-2 to top-of-atmosphere reflectance [0,1];<br>resize/crop to 256x256 patches|
|Augmentation|Random flip (H/V), 90° rotations only — avoid arbitrary-angle rotation/color jitter, which would corrupt<br>radiometric meaning|
|Model|Lightweight U-Net (ResNet-18 or MobileNetV3 encoder) — NOT a full ResNet-50/DeepLab, to keep this<br>CPU/low-GPU trainable in hackathon time|
|Loss|Combined Dice + BCE (standard for imbalanced water/non-water segmentation)|
|Hyperparameters|batch=8, lr=1e-3 with cosine decay, AdamW, weight_decay=1e-4, epochs=30–50 with early stopping on<br>val IoU|
|Hardware|Single mid-range GPU (e.g. T4/RTX3060) can finish in 1–2 hours on the 446-chip hand-labeled set; CPU-<br>only training is possible but slow (avoid under 36-hour pressure)|
|Checkpointing|Save best-val-IoU checkpoint only; log every epoch to a CSV for the evidence panel|
|Metrics|IoU, Dice/F1, precision, recall on held-out split|
|Status|TO BUILD only if Section 4.2's rule-based approach is validated first and time remains — do not attempt<br>this before the rule-based pipeline works end-to-end|



### 4.4 Model-to-module mapping 

|**Module**|**Model/Method**|**Tier**|**API endpoint**|**Frontend consumer**|
|---|---|---|---|---|
|Super-resolution|Sentinel2SRNet (fixed checkpoint) +<br>TTA|MUST|POST /sr/{scene_id}|Map layer toggle:<br>Original/Bicubic/SR/TTA|
|Flood extent|NDWI/MNDWI differencing (rule-<br>based)|MUST|GET /change/{aoi_id}|Flood overlay layer, area stat<br>panel|
|Flood extent (cross-<br>check)|U-Net on Sen1Floods11|SHOULD|GET /change/{aoi_id}?<br>method=learned|Toggle: rule-based vs learned<br>overlay|
|Infrastructure<br>exposure|OSM Overpass intersection (no<br>model)|MUST|GET<br>/infrastructure/{aoi_id}|Building/road count badges<br>on map|
|Population exposure|GHS-POP raster zonal sum within<br>flood polygon|SHOULD|GET /population/{aoi_id}|Exposure stat panel|
|Priority scoring|Weighted transparent formula<br>(Section 8.4)|MUST|GET /priority/{aoi_id}|P1–P4 map zones + factor<br>breakdown card|
|Building damage<br>(learned)|xBD-pretrained segmentation, heavy<br>domain-gap caveat|PLANNE<br>D|n/a|n/a — not in MVP|
|Sentinel-1 fusion|SAR coherence change for cloud-<br>blocked scenes|PLANNE<br>D|n/a|n/a — architecture only,<br>Section 8.5|



8 

## 5. Database Schema (PostgreSQL + PostGIS) — TO BUILD 

PostGIS chosen over plain PostgreSQL because every core entity (AOI, flood polygon, priority zone, building/road footprint) is a geometry that needs spatial indexing and intersection queries (ST_Intersects) — implementing that in application code instead would be slower and more error-prone under time pressure. 

<mark>-- aoi: user-drawn or preset areas of interest CREATE TABLE aoi ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name TEXT, geom GEOMETRY(Polygon, 4326) NOT NULL, disaster_type TEXT CHECK (disaster_type IN ('food','earthquake','cyclone','wildfre','landslide')), created_at TIMESTAMPTZ DEFAULT now(), created_by UUID REFERENCES users(id) ); -- scenes: raw + SR imagery metadata (fles live in object storage, not DB) CREATE TABLE scenes ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), aoi_id UUID REFERENCES aoi(id), role TEXT CHECK (role IN ('pre','post')), acquisition_date DATE NOT NULL, cloud_cover_pct NUMERIC, source TEXT DEFAULT 'Copernicus Data Space Ecosystem', raw_object_key TEXT NOT NULL,       -- path in object store scl_mask_key TEXT,                  -- cloud/shadow mask bands JSONB,                        -- which bands captured created_at TIMESTAMPTZ DEFAULT now() ); -- sr_results: one row per SR run on a scene CREATE TABLE sr_results ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), scene_id UUID REFERENCES scenes(id), model_version TEXT NOT NULL,        -- e.g. 'sentinel2srnet-v1.2' tta_enabled BOOLEAN DEFAULT false, sr_object_key TEXT NOT NULL, bicubic_object_key TEXT NOT NULL,   -- always kept alongside uncertainty_object_key TEXT,        -- TTA variance map, null if tta_enabled=false psnr NUMERIC, ssim NUMERIC, mae NUMERIC, sam NUMERIC, ergas NUMERIC, latency_ms NUMERIC, created_at TIMESTAMPTZ DEFAULT now() );</mark> 

<mark>-- change_results: pre/post comparison for one AOI CREATE TABLE change_results ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), aoi_id UUID REFERENCES aoi(id), method TEXT CHECK (method IN ('ndwi_dif','learned_unet')),</mark> 

9 

<mark>food_geom GEOMETRY(MultiPolygon, 4326), area_km2 NUMERIC, confdence NUMERIC,                 -- 0-1 model_version TEXT, created_at TIMESTAMPTZ DEFAULT now() );</mark> 

<mark>-- infrastructure_exposure: OSM intersection results CREATE TABLE infrastructure_exposure ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), change_result_id UUID REFERENCES change_results(id), feature_type TEXT CHECK (feature_type IN ('building','road','hospital','shelter')), osm_id BIGINT, geom GEOMETRY(Geometry, 4326), intersects_food BOOLEAN, created_at TIMESTAMPTZ DEFAULT now() );</mark> 

<mark>-- priority_zones: transparent scoring output CREATE TABLE priority_zones ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), change_result_id UUID REFERENCES change_results(id), geom GEOMETRY(Polygon, 4326), priority TEXT CHECK (priority IN ('P1','P2','P3','P4')), score NUMERIC, factors JSONB,                      -- {damage_extent, buildings_afected, roads_cut, pop_exposed, confdence} created_at TIMESTAMPTZ DEFAULT now() );</mark> 

<mark>-- reports: exported artifacts CREATE TABLE reports ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), aoi_id UUID REFERENCES aoi(id), format TEXT CHECK (format IN ('pdf','geojson','csv')), object_key TEXT NOT NULL, generated_at TIMESTAMPTZ DEFAULT now() ); -- users: minimal auth (PLANNED full RBAC — see Section 13) CREATE TABLE users ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), email TEXT UNIQUE NOT NULL, role TEXT DEFAULT 'viewer' CHECK (role IN ('admin','responder','viewer')), created_at TIMESTAMPTZ DEFAULT now() );</mark> 

<mark>-- incidents: SOS module (CAN tier, mock adapter only) CREATE TABLE incidents ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(),</mark> 

10 

<mark>aoi_id UUID REFERENCES aoi(id), location GEOMETRY(Point, 4326), incident_type TEXT, severity TEXT, description TEXT, status TEXT DEFAULT 'NEW' CHECK (status IN ('NEW','VERIFIED','ASSIGNED','RESPONDING','RESOLVED')), reported_at TIMESTAMPTZ DEFAULT now() ); CREATE INDEX idx_aoi_geom ON aoi USING GIST (geom); CREATE INDEX idx_change_geom ON change_results USING GIST (food_geom); CREATE INDEX idx_infra_geom ON infrastructure_exposure USING GIST (geom); CREATE INDEX idx_priority_geom ON priority_zones USING GIST (geom);</mark> 

11 

## 6. API Specification — TO BUILD 

#### POST /aoi 

**[TO BUILD]** Register an AOI polygon and disaster type. 

##### **Request:** 

<mark>{ "name": "Kosi Basin Test AOI", "geometry": { "type": "Polygon", "coordinates": [...] }, "disaster_type": "food" }</mark> 

##### **Response:** 

<mark>{ "aoi_id": "uuid", "created_at": "..." }</mark> 

#### POST /imagery/{aoi_id} 

**[TO BUILD]** Async job: query Copernicus OData API for best pre/post Sentinel-2 scenes (lowest cloud cover, closest to requested dates), download, cache in object storage. 

##### **Request:** 

<mark>{ "pre_date_range": ["2024-06-01","2024-06-10"], "post_date_range": ["2024-07-15","2024-07-25"], "max_cloud_pct": 20 }</mark> 

##### **Response:** 

<mark>{ "job_id": "uuid", "status": "queued" }</mark> 

<mark>-- poll GET /jobs/{job_id} for completion, then --</mark> 

<mark>{ "pre_scene_id": "uuid", "post_scene_id": "uuid" }</mark> 

_Background job via FastAPI BackgroundTasks or a Celery/RQ worker — imagery download is slow (tens of MB to GB) and must not block the request thread._ 

#### POST /sr/{scene_id} 

**[TO BUILD (fix)]** Run Sentinel2SRNet on a cached scene. This is the endpoint that currently serves OpenCV FSRCNN/ESPCN instead of the real model — highest-priority fix. 

##### **Request:** 

<mark>{ "tta": true }</mark> 

##### **Response:** 

<mark>{ "sr_result_id": "uuid", "sr_url": "...", "bicubic_url": "...", "uncertainty_url": "...", "model_version": "sentinel2srnet-v1.2", "latency_ms": 34.2 }</mark> 

#### GET /change/{aoi_id} 

**[TO BUILD]** Compute NDWI/MNDWI difference between pre/post SR scenes; return flood polygon. 

##### **Response:** 

<mark>{ "food_geojson": {...}, "area_km2": 12.4, "confdence": 0.78, "method": "ndwi_dif", "model_version": "rule-v1" }</mark> 

12 

#### GET /infrastructure/{aoi_id} 

**[TO BUILD]** Intersect the flood polygon with OSM buildings/roads and GHSL population raster. 

##### **Response:** 

<mark>{ "buildings_afected": 214, "roads_afected_km": 6.3,</mark> 

<mark>"population_estimate": 3400, "population_source": "GHS-POP 2023, 100m", "hospitals_at_risk": 1 }</mark> 

_population_estimate is always returned with its dataset date — never presented as ground-truth census._ 

#### GET /priority/{aoi_id} 

**[TO BUILD]** Return transparent priority zones with visible scoring factors. 

##### **Response:** 

<mark>{ "zones": [</mark> 

<mark>{ "zone_id":"uuid","priority":"P1","score":0.86, "factors": {"damage_extent":0.9,"buildings_afected":80, "roads_cut":2,"pop_exposed":1200,"confdence":0.75} }</mark> 

<mark>] }</mark> 

#### GET /report/{aoi_id} 

**[TO BUILD]** Generate and return a PDF + GeoJSON export bundle. 

##### **Response:** 

<mark>{ "pdf_url": "...", "geojson_url": "...", "csv_url": "..." }</mark> 

#### GET /health 

**[TO BUILD]** Liveness/readiness probe reporting model_version loaded, so a jury can verify the real checkpoint is live, not a stub. 

##### **Response:** 

<mark>{ "status": "ok", "sr_model_version": "sentinel2srnet-v1.2",</mark> 

<mark>"gpu_available": false }</mark> 

13 

## 7. Frontend Pages / Components — TO BUILD 

|**Page**|**Key components**|**Data source**|**Priority**|
|---|---|---|---|
|Command Dashboard|AOI list, active disaster event card, quick stats|GET /aoi, GET /priority/{aoi_id}|MUST|
|Map Intelligence (core<br>screen)|Leaflet map, AOI draw tool, layer control<br>(Original/Bicubic/SR/TTA/Flood/Priority), before/after<br>swipe slider, legend, scale, coordinate readout|GET /imagery, GET /sr, GET<br>/change, GET /priority|MUST|
|Evidence Panel|Side drawer: acquisition dates, bands used, model<br>version, confidence, 'AI-assisted — requires field<br>verification' badge|GET /sr, GET /change (metadata<br>fields)|MUST|
|Priority/Risk View|P1–P4 zone list with factor breakdown (bar chart of<br>damage/pop/roads/confidence)|GET /priority/{aoi_id}|SHOULD|
|Report Viewer/Export|PDF preview, GeoJSON/CSV download buttons|GET /report/{aoi_id}|SHOULD|
|Infrastructure Panel|Building/road/hospital counts affected, small table|GET /infrastructure/{aoi_id}|SHOULD|
|SOS/Incidents (stretch)|Simple form + status badge list; mock adapter, clearly<br>labeled 'demo only, not connected to NDRF'|POST/GET /incidents|CAN|
|Timeline (stretch)|T1→T2 slider if more than 2 dates are loaded|GET /imagery history|CAN|



Stack: React + Leaflet (or MapLibre) for the map, Tailwind for styling, react-query for data fetching/caching against the FastAPI backend. Keep the map screen as the single source of truth — every other page is a view/filter over the same AOI, not a separate workflow, so an operator never re-enters context. 

14 

## 8. ML Pipelines 

### 8.1 FLOOD (36-hour MVP — build this first and only this, end to end) 

###### <mark>1. AOI polygon submitted → /aoi</mark> 

<mark>2. /imagery: Copernicus OData query, pre + post Sentinel-2 L2A scenes, cloud_cover < 20%, SCL mask fetched</mark> 

<mark>3. Co-register: reproject both scenes to same UTM CRS, resample to matching pixel grid</mark> 

<mark>4. Original imagery archived to object storage (both dates) — never overwritten</mark> 

<mark>5. /sr on each scene: Sentinel2SRNet (fxed checkpoint) 10m -> 2.5m, TTA on -> uncertainty map</mark> 

<mark>6. Compute MNDWI on both SR outputs (Green=B3, SWIR=B11, both resampled to 2.5m)</mark> 

<mark>7. Threshold MNDWI>0 -> water mask per date; dif(post_water, pre_water) -> food candidate pixels</mark> 

<mark>8. Vectorize food candidate raster -> polygon(s); compute area_km2</mark> 

<mark>9. Confdence = weighted(TTA variance at food pixels, cloud-mask proximity, MNDWI margin from 0) 10. /infrastructure: Overpass query for buildings/roads/hospitals inside food polygon bbox, ST_Intersects</mark> 11. /priority: score = w1*area_norm + w2*buildings_norm + w3*roads_cut_norm + w4*pop_norm, weights shown in evidence panel, thresholds map score -> P1-P4 

<mark>12. Frontend renders: original/SR toggle, food overlay, priority zones, evidence panel, export button 13. /report: assemble PDF (map screenshot + stats + evidence) + GeoJSON of food + priority polygons</mark> 

### 8.2 EARTHQUAKE — PLANNED (architecture only, not built for MVP) 

- Input: pre/post optical Sentinel-2, SR-enhanced 

- Change signal: structural/rubble spectral signature is weak at 10m/2.5m GSD — Sentinel-2 alone is a poor sensor for earthquake building damage (this is a real physical limitation, not a build gap; disclose it directly if asked) 

- Recommended real approach: fuse with a high-res source (xBD-style, if a partner can supply one) or SAR coherence loss from Sentinel-1; Sentinel-2-only should be scoped as 'road network disruption + large-scale visible change' only, not building-level damage 

### 8.3 CYCLONE — PLANNED 

- Combine flood pipeline (8.1) + NDVI difference for vegetation/crop loss + OSM road intersection — largely a reuse of the flood MVP components, achievable relatively quickly after flood MVP is solid 

### 8.4 WILDFIRE — PLANNED 

- NBR = (NIR−SWIR)/(NIR+SWIR) using B8/B12; dNBR = NBR_pre − NBR_post; USGS burn-severity thresholds (unburned/low/moderate/high) are published and can be applied directly — rule-based, same complexity class as the flood MNDWI approach 

### 8.5 LANDSLIDE — PLANNED 

- Copernicus DEM slope/aspect + optical change + (optional) Sentinel-1 coherence drop as a landslide-risk proxy — this is architecture-stage; do not claim a trained landslide detector without one 

### 8.6 Transparent priority scoring formula (used across all disaster types) 

<mark>score = w1 * normalize(damage_extent_km2)</mark> 

<mark>+ w2 * normalize(buildings_afected)</mark> 

- <mark>+ w3 * normalize(roads_cut_count)</mark> 

<mark>+ w4 * normalize(population_exposed)</mark> 

15 

<mark>- w5 * (1 - confdence)          # low-confdence fndings are down-weighted, not hidden</mark> 

<mark>P1 (Immediate): score >= 0.75 P2 (High):      0.5 <= score < 0.75 P3 (Monitor):   0.25 <= score < 0.5 P4 (Low):       score < 0.25</mark> 

<mark>Default weights (documented, adjustable): w1=0.3, w2=0.25, w3=0.2, w4=0.2, w5=0.15</mark> 

Every zone's factor breakdown is returned by the API and shown in the UI — this is what makes the score defensible under jury cross-examination; a bare number is not. 

16 

## 9. GIS Architecture — TO BUILD 

|**Layer**|**Format**|**Source**|**Rendering**|
|---|---|---|---|
|Basemap|XYZ tiles|OpenStreetMap or CartoDB Positron|Leaflet TileLayer|
|Original Sentinel-2|Cloud-optimized<br>GeoTIFF (COG)|Ingestion service output|Leaflet.TileLayer via a COG tile server<br>(titiler) or pre-tiled PNG|
|SR output|COG, 2.5m|SR engine output|Same tiling pipeline as above|
|TTA uncertainty|COG, single-band,<br>colormapped|SR engine output|titiler with a viridis-style colormap|
|Flood polygon|GeoJSON|/change endpoint|Leaflet GeoJSON layer, semi-transparent<br>blue fill|
|Priority zones|GeoJSON|/priority endpoint|Leaflet GeoJSON, colored by P1-P4|
|Buildings/roads|GeoJSON (subset within<br>AOI only — do not load<br>unbounded OSM)|/infrastructure endpoint|Leaflet GeoJSON, filtered to intersecting<br>features|
|AOI boundary|GeoJSON|User-drawn via Leaflet.Draw|Editable polygon layer|



Serve raster layers as Cloud-Optimized GeoTIFFs through a lightweight tile server (titiler, FastAPI-based) rather than pre-rendering every zoom level — this avoids a large precompute step under time pressure and lets the map request only the tiles it needs. 

17 

## 10. Exact Integration / Connections — TO BUILD 

<mark>Copernicus Data Space Ecosystem (OData API)</mark> 

<mark>HTTPS, OAuth2 client-credentials token│ ▼</mark> 

<mark>Ingestion Service (FastAPI background task / RQ worker) writes raw + SCL mask to Object Storage (S3-compatible / MinIO for local dev)│ writes scene metadata row to Postgres `scenes` table│ ▼</mark> 

<mark>Preprocessing (co-register, cloud mask apply, band select) reads/writes Object Storage; updates `scenes` row│ ▼</mark> 

<mark>SR Engine (Sentinel2SRNet, PyTorch, served via a dedicated /sr FastAPI route</mark> 

<mark>or a separate inference microservice behind an internal HTTP call) writes SR + bicubic + uncertainty COGs to Object Storage│ writes row to `sr_results`│</mark> 

<mark>▼</mark> 

<mark>Change Detection Service (NDWI/MNDWI, pure Python/numpy/rasterio, no GPU) writes f│ ood polygon to `change_results.food_geom` (PostGIS geometry) ▼ Infrastructure Service (osmnx/Overpass query, PostGIS ST_Intersects) writes rows to `infrastructure_exposure`│ ▼</mark> 

<mark>Priority Engine (pure Python scoring function, Section 8.6) writes rows to `priority_zones`│ ▼ FastAPI Gateway  ── serves all of the above via REST/GeoJSON ──▶  React/Leafet Frontend │ ▼</mark> 

<mark>Report Generator (weasyprint/reportlab for PDF, geojson dump for vector export) writes to Object Storage, row to `reports`│</mark> 

Asynchronous jobs required for: imagery download (slow, network-bound), SR inference (CPU/GPU-bound, seconds), report PDF generation (assembly + rendering). Use FastAPI BackgroundTasks for the hackathon scope; a Redis+RQ or Celery queue is the PLANNED production upgrade if load increases. 

## 11. Training / Inference Setup 

|**Item**|**Requirement**|
|---|---|
|SR inference|IMPLEMENTED (fix required): CPU is sufficient per your existing claim (~25-38ms/tile)<br>— re-verify after checkpoint fix|
|SR training (if retraining needed)|Single GPU (e.g. T4 or better), PyTorch >=2.0, ~193K params trains fast — hours not days<br>on SEN2VENµS-scale data|
|Flood NDWI pipeline|CPU only, numpy/rasterio, no training required|
|Optional U-Net flood segmentation (§4.3)|Single GPU, 1-2 hrs on the 446-chip hand-labeled Sen1Floods11 split|
|OSM/GHSL intersection|CPU only, PostGIS spatial query|
|Report generation|CPU only|



18 

## 12. Deployment Setup — TO BUILD 

<mark>docker-compose.yml services: frontend        (React build, served via nginx)</mark> 

<mark>api             (FastAPI + uvicorn) worker          (background jobs: ingestion, SR inference, report gen) db              (postgres + postgis extension) object-storage  (minio, S3-compatible, for local/dev; swap for real S3 in prod) tile-server     (titiler, serves COGs to Leafet)</mark> 

<mark>Local dev: docker-compose up — single command bring-up for the demo laptop</mark> Env vars: COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET, DATABASE_URL, S3_ENDPOINT, MODEL_CHECKPOINT_PATH 

## 13. Security & Uncertainty/Provenance Safeguards 

### 13.1 Security — MVP-realistic subset 

- **[TO BUILD]** Basic API key or JWT auth on write endpoints (POST /aoi, POST /imagery) 

- **[TO BUILD]** Input validation on AOI polygon size (reject absurdly large areas that would blow the imagery budget) 

- **[TO BUILD]** File size limits on any uploaded imagery fallback path 

- **[PLANNED]** Full RBAC (admin/responder/viewer), audit logs, encrypted transport in production deployment, secrets management — state these as architecture in the deck, do not claim implemented 

### 13.2 Uncertainty / provenance — cheap, non-negotiable, build these regardless of time pressure 

- Every map layer tagged OBSERVED / AI-ENHANCED / DERIVED / UNCONFIRMED in its legend entry 

- TTA uncertainty layer always available alongside SR output, never hidden by default 

- Priority score never rendered without its factor breakdown 

- Every exported report footer: "AI-assisted analysis — requires field verification. Not an authoritative emergency response system." 

- Population/infrastructure figures always shown with dataset name + date (e.g. "GHS-POP 2023, 100m grid") 

19 

## 14. 36-Hour Implementation Sequence 

|**Hours**|**Work**|**Exit criterion**|
|---|---|---|
|0-4|Fix Sentinel2SRNet backend: locate/retrain checkpoint, wire into /sr,<br>remove OpenCV FSRCNN/ESPCN fallback, fix EDSR fallback<br>labeling|/health reports real model_version; SR output<br>visibly differs from bicubic on a test tile|
|4-6|Fix TTA aggregation (median instead of mean); re-measure edge gain|TTA output has positive Sobel edge-energy gain<br>vs bicubic, documented before/after|
|6-10|Ingestion service: Copernicus OData auth + scene query + download +<br>SCL cloud mask + object storage write|Given an AOI + date range, pre/post scenes land<br>in storage with metadata in DB|
|10-14|Co-registration + NDWI/MNDWI change detection + polygon<br>vectorization|Given two SR scenes, a flood GeoJSON<br>polygon + area_km2 is produced|
|14-17|OSM Overpass integration (buildings/roads) + PostGIS intersection|Given a flood polygon, affected building/road<br>counts are returned|
|17-19|GHSL population zonal stat + priority scoring engine|Given infra counts, a P1-P4 zone set with factor<br>breakdown is returned|
|19-26|Frontend: Leaflet map, AOI draw, layer toggles, before/after swipe,<br>evidence panel|Operator can draw an AOI and see the full flood<br>workflow rendered on the map|
|26-29|Report generator: PDF + GeoJSON export|Given an AOI with completed analysis, a<br>downloadable PDF+GeoJSON bundle is<br>produced|
|29-32|End-to-end rehearsal on the chosen demo AOI/event; fix breakages|Full flow runs without manual intervention,<br>twice in a row|
|32-34|Update deck slide 7 + benchmark narrative to match actual results;<br>prepare evidence panel screenshots for slides|Deck claims match live demo exactly|
|34-36|Jury Q&A rehearsal (Section 18), buffer for the inevitable last-minute<br>bug|Team can answer all 18 questions below without<br>hesitation|



20 

## 15. Exact Folder / File Structure — TO BUILD 

<mark>pixelforge/</mark> 

<mark>├── frontend/ │├── src/ ││├── pages/           (Dashboard, MapIntelligence, PriorityView, Reports) ││├── components/      (LayerToggle, EvidencePanel, SwipeCompare, AOIDraw) ││└── api/              (typed fetch wrappers per endpoint) │└── package.json ├── backend/ │├── api/ ││├── routes/           (aoi.py, imagery.py, sr.py, change.py, │││                            infrastructure.py, priority.py, report.py, health.py) ││└── main.py │├── ml/ ││├── sr/                (sentinel2srnet.py, tta.py, checkpoint loading) ││├── change_detection/  (ndwi.py, learned_unet.py [SHOULD]) ││└── priority/          (scoring.py) │├── ingestion/             (copernicus_client.py, cache.py) │├── preprocessing/         (coregister.py, cloud_mask.py) │├── geospatial/            (osm_client.py, ghsl_zonal.py, postgis_helpers.py) │├── reports/                (pdf_builder.py, geojson_export.py) │├── db/                    (models.py, migrations/) │├── confgs/               (settings.py, model_registry.yaml) │└── tests/ ├── models/                     (checkpoints — .pth fles, gitignored, documented in model_registry.yaml) ├── datasets/                   (download scripts per §3, not the raw data itself) ├── docs/                       (this document, API reference, dataset licenses) └── docker-compose.yml</mark> 

## 16. Build Checklist 

- **[MUST]** Sentinel2SRNet checkpoint wired into /sr, OpenCV fallback removed 

- **[MUST]** EDSR fallback fixed or relabeled honestly 

- **[MUST]** TTA aggregation fixed (positive edge gain measured) 

- **[MUST]** Copernicus ingestion working end-to-end for one AOI 

- **[MUST]** NDWI/MNDWI flood polygon pipeline working 

- **[MUST]** OSM building/road intersection working 

- **[SHOULD]** GHSL population zonal stat working 

- **[MUST]** Priority scoring with visible factors 

- **[MUST]** Leaflet map with layer toggles + before/after swipe 

- **[MUST]** Evidence panel with OBSERVED/AI-ENHANCED/DERIVED/UNCONFIRMED labels 

- **[SHOULD]** PDF + GeoJSON report export 

- **[MUST]** Deck slide 7 rewritten to match actual demo 

- **[MUST]** Benchmark narrative aligned with Excel data (no overclaiming) 

- **[MUST]** Jury Q&A rehearsed 

21 

- **[CAN]** SOS/incident mock module 

- **[CAN]** Sentinel-1 fusion architecture slide (not implementation) 

22 

## 17. Demo Workflow (rehearsed script) 

|**Step**|**On-screen action**|**What you say**|
|---|---|---|
|1|Open Map Intelligence, draw/select the pre-<br>chosen demo AOI (a real, historical flood event<br>with Copernicus EMS activation — pick this now<br>so validation data exists)|"This is [location], during [dated flood event]. We're using real Sentinel-2<br>imagery from before and after."|
|2|Toggle Original → Bicubic → Sentinel2SRNet →<br>TTA|"Our model is 200x smaller than EDSR and runs in milliseconds on CPU<br>— here's the honest benchmark, we're not claiming to beat every baseline<br>on raw fidelity, our edge is efficiency plus this uncertainty map."|
|3|Toggle flood overlay on|"This polygon comes from a spectral water index, not a black box —<br>MNDWI on the SR-enhanced bands, differenced pre/post."|
|4|Show infrastructure panel|"214 buildings and 6.3km of road intersect this flood extent, from direct<br>OpenStreetMap geometry — no hallucinated detections."|
|5|Show priority zones + factor breakdown|"Zone A is P1 because of this exact combination of factors, all visible —<br>not a hidden score."|
|6|Export report|"Every export carries acquisition dates, model version, and a field-<br>verification disclaimer."|



23 

## 18. Jury Q&A + Defensible Claims 

##### **Why is your model behind EDSR/FSRCNN/ESPCN on PSNR/SSIM?** 

Correct, and we say so directly — our benchmark data shows it. Our differentiator is 193.6K params vs EDSR's 43M (~200x smaller), CPU-deployable latency, and TTA-derived per-pixel uncertainty, none of which the baselines provide. 

##### **Is the flood polygon AI-generated?** 

No — it's a deterministic spectral index (MNDWI) differenced pre/post disaster, computed on SR-enhanced bands. It's explainable math, not a trained classifier, which is a deliberate choice for auditability. 

##### **How do you know the building count is accurate?** 

It's a direct geometric intersection with OpenStreetMap data, not a detector — subject to OSM's own completeness/currency limitations, which we disclose. 

##### **Where does your population number come from?** 

GHS-POP 2023, a 100m Copernicus/JRC grid, zonal-summed within the flood polygon. We show the dataset name and year every time the number appears. 

##### **What happens if the checkpoint fails to load?** 

The /health endpoint reports the loaded model_version; if it doesn't match the expected value, the UI would show a clear error rather than silently substituting a different model — this is the exact failure mode we found and fixed in our own audit. 

##### **Why flood and not earthquake/building damage?** 

Sentinel-2's 10m native resolution (2.5m after SR) is well-suited to water-extent detection but not to building-level structural damage, which needs sub-metre imagery. We scoped the MVP to the disaster type our sensor can honestly support. 

##### **Is this connected to NDRF/real emergency systems?** 

No. It's architected with a defined API surface that an official integration could plug into, but no such connection exists — we don't claim one. 

##### **Can this run offline?** 

Only in a limited sense for the demo (cached scenes); true field offline operation is a stated roadmap item, not built. 

##### **What's your uncertainty quantification actually measuring?** 

Per-pixel variance across the 8-way dihedral TTA ensemble — it reflects model disagreement under symmetric transforms, not ground-truth error, and we state that distinction. 

##### **Why not use xBD for building damage?** 

24 

Resolution mismatch — xBD is 0.3-0.5m Maxar imagery, 20-300x finer than Sentinel-2's native GSD. Training/validating against it at our scale would misrepresent confidence, so we use direct OSM footprint intersection instead. 

### What must NOT be claimed (recap) 

- SR output is not ground truth — never present it as measured evidence of damage 

- No NDRF/government API integration exists 

- Sentinel2SRNet does not beat baselines on fidelity metrics — only on efficiency/speed/uncertainty 

- Population/infrastructure numbers are estimates from named, dated public datasets, not real-time ground truth 

- Priority scores are never shown without their contributing factors 

25 

