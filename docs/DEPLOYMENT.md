# SH-304 Deployment & Setup Guide

## 1. Prerequisites

- **Python:** 3.10+ (Tested on Python 3.14 on Windows & Linux)
- **Node.js:** 18.0+ (Tested on Node 24 with npm 11)
- **Docker & Docker Compose:** (Optional, for containerized deployment)

---

## 2. Local Environment Setup

### 2.1 Backend Setup
```bash
# 1. Navigate to project root
cd C:\Users\Vanaparthi\.gemini\antigravity\scratch\sh304-landslide-warning

# 2. Install required Python packages
python -m pip install -r requirements.txt
# (or: pip install rasterio geopandas shapely earthaccess pyyaml pytest httpx fastapi uvicorn scipy scikit-learn)

# 3. Seed deterministic demo data (if not already seeded)
python scripts/seed_demo_data.py

# 4. Run automated test suite
python -m pytest tests/ -v

# 5. Start FastAPI Backend Server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend will be available at `http://127.0.0.1:8000`. OpenAPI docs at `http://127.0.0.1:8000/docs`.

### 2.2 Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```
The React + Leaflet dashboard will be available at `http://localhost:5173`.

---

## 3. Standalone CLI Execution

The data-fusion pipeline can also be executed entirely from the command line:
```bash
python scripts/run_pipeline_cli.py --aoi wayanad --mode demo --export-json
python scripts/run_pipeline_cli.py --aoi chamoli --mode demo --export-json
```

---

## 4. Docker & Containerized Deployment

### 4.1 Running via Docker Compose
```bash
# Build and launch both Backend and Frontend containers
docker-compose up --build
```
- Dashboard: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 5. Environment Variables Reference

| Variable | Default | Purpose |
|---|---|---|
| `MODE` | `demo` | `demo` (offline deterministic data) or `live` (NASA Earthdata APIs) |
| `EARTHDATA_USERNAME` | `""` | NASA Earthdata username (required only for live IMERG downloads) |
| `EARTHDATA_PASSWORD` | `""` | NASA Earthdata password |
| `DEFAULT_AOI` | `wayanad` | Initial district selected on startup (`wayanad` or `chamoli`) |
| `PORT` | `8000` | FastAPI server listening port |
| `ANALYSIS_GRID_RESOLUTION_DEG` | `0.01` | Spatial resolution of analysis grid (~1.1 km) |
