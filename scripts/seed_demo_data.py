"""
Deterministic Demo Data Generator for SH-304.
Generates georeferenced DEM GeoTIFFs, daily IMERG rainfall series,
historical NASA GLC landslide points, and village administrative boundaries.
"""
import json
import math
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import Polygon, mapping, Point
import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"


def generate_wayanad_demo():
    aoi_dir = DEMO_DIR / "aoi_wayanad"
    aoi_dir.mkdir(parents=True, exist_ok=True)

    # 1. Bounding Box: [75.80, 11.45, 76.35, 11.95] (WGS84)
    min_lon, min_lat, max_lon, max_lat = 75.80, 11.45, 76.35, 11.95
    rows, cols = 300, 330
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

    # Generate synthetic realistic DEM: Ridge running north-south with steep western escarpment (Western Ghats)
    x = np.linspace(0, 1, cols)
    y = np.linspace(0, 1, rows)
    X, Y = np.meshgrid(x, y)

    # Main escarpment ridge + river valleys + high peaks (Chembra Peak ~2100m)
    ridge = np.exp(-((X - 0.45) ** 2) / 0.04) * 1200
    chembra_peak = np.exp(-((X - 0.42) ** 2 + (Y - 0.40) ** 2) / 0.015) * 800
    valleys = np.sin(X * 12.0) * np.cos(Y * 10.0) * 180 + np.sin(Y * 8.0) * 150
    dem = 650.0 + ridge + chembra_peak + valleys
    dem = np.clip(dem, 500.0, 2200.0).astype(np.float32)

    dem_path = aoi_dir / "dem.tif"
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        dst.write(dem, 1)
        dst.update_tags(
            source="SRTM GL1 30m DEM (Simulated Reference Clip)",
            resolution="30m",
            datum="WGS84",
            tag="DEMO_OFFLINE",
        )
    print(f"Generated DEM for Wayanad at {dem_path}")

    # 2. Daily Rainfall Series (Past 15 days ending with monsoon deluge)
    # Day 1-10: 10-35mm/day (monsoon background)
    # Day 11-13: 50-80mm/day (soil saturation buildup)
    # Day 14: 140mm/day
    # Day 15 (Current): 280mm/day peak storm on western slopes
    dates = [f"2024-07-{d:02d}" for d in range(16, 31)]
    base_amounts = [15.0, 22.0, 18.0, 30.0, 25.0, 28.0, 45.0, 35.0, 52.0, 60.0, 75.0, 95.0, 130.0, 185.0, 290.0]

    rainfall_data = {
        "aoi": "wayanad",
        "description": "Simulated NASA GPM IMERG v07 Final Daily calibrated against Wayanad July 2024 event",
        "dates": dates,
        "history_days": len(dates),
        "current_date": dates[-1],
        "current_intensity_mm_hr": 24.5,
        "trend_alpha_mm_hr2": 1.25,  # Rate of intensification
        "daily_series": [],
    }

    # Generate a rainfall grid for each day
    rf_rows, rf_cols = 50, 55
    rf_transform = from_bounds(min_lon, min_lat, max_lon, max_lat, rf_cols, rf_rows)
    rf_X, rf_Y = np.meshgrid(np.linspace(0, 1, rf_cols), np.linspace(0, 1, rf_rows))
    orographic_factor = 0.5 + np.exp(-((rf_X - 0.40) ** 2) / 0.08) * 1.5

    for i, (dt, base) in enumerate(zip(dates, base_amounts)):
        noise = np.sin(rf_X * 5 + i) * np.cos(rf_Y * 5) * (base * 0.15)
        rf_grid = np.clip(base * orographic_factor + noise, 0, None).astype(np.float32)

        day_file = aoi_dir / f"rainfall_{dt}.tif"
        with rasterio.open(
            day_file,
            "w",
            driver="GTiff",
            height=rf_rows,
            width=rf_cols,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=rf_transform,
            nodata=-9999.0,
        ) as dst:
            dst.write(rf_grid, 1)

        rainfall_data["daily_series"].append({
            "date": dt,
            "mean_mm": float(np.mean(rf_grid)),
            "max_mm": float(np.max(rf_grid)),
            "min_mm": float(np.min(rf_grid)),
            "raster_file": str(day_file.name),
        })

    with open(aoi_dir / "rainfall_series.json", "w", encoding="utf-8") as f:
        json.dump(rainfall_data, f, indent=2)
    print(f"Generated Rainfall series for Wayanad ({len(dates)} days)")

    # 3. NASA Global Landslide Catalog (GLC) Historical Events
    glc_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.12, 11.52]},
            "properties": {
                "event_id": "GLC_IND_WAY_001",
                "date": "2018-08-14",
                "location": "Puthumala / Meppadi, Wayanad",
                "trigger": "Continuous rain / Monsoon storm",
                "landslide_category": "Debris flow",
                "landslide_size": "Very Large",
                "fatalities": 17,
                "confidence": "HIGH",
                "source": "NASA Global Landslide Catalog / GSI Bhusanket Cross-Ref",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.14, 11.54]},
            "properties": {
                "event_id": "GLC_IND_WAY_002",
                "date": "2019-08-08",
                "location": "Puthumala Hillside, Wayanad",
                "trigger": "Heavy torrential monsoon rain",
                "landslide_category": "Mudslide / Debris flow",
                "landslide_size": "Large",
                "fatalities": 12,
                "confidence": "HIGH",
                "source": "NASA Global Landslide Catalog",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.04, 11.55]},
            "properties": {
                "event_id": "GLC_IND_WAY_003",
                "date": "2020-08-06",
                "location": "Vythiri Ghat Road",
                "trigger": "Rainfall",
                "landslide_category": "Rockfall / Slump",
                "landslide_size": "Medium",
                "fatalities": 0,
                "confidence": "MEDIUM",
                "source": "NASA Global Landslide Catalog",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.01, 11.60]},
            "properties": {
                "event_id": "GLC_IND_WAY_004",
                "date": "2021-07-23",
                "location": "Pozhuthana Western Slopes",
                "trigger": "Monsoon downpour",
                "landslide_category": "Debris slide",
                "landslide_size": "Medium",
                "fatalities": 1,
                "confidence": "MEDIUM",
                "source": "NASA Global Landslide Catalog",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.15, 11.51]},
            "properties": {
                "event_id": "GLC_IND_WAY_005",
                "date": "2022-08-04",
                "location": "Chooralmala Upper Catchment",
                "trigger": "Continuous rain",
                "landslide_category": "Complex / Debris flow",
                "landslide_size": "Medium",
                "fatalities": 0,
                "confidence": "HIGH",
                "source": "NASA Global Landslide Catalog",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [76.17, 11.50]},
            "properties": {
                "event_id": "GLC_IND_WAY_006",
                "date": "2024-07-30",
                "location": "Mundakkai - Chooralmala, Meppadi",
                "trigger": "Extreme cloudburst & orographic deluge",
                "landslide_category": "Catastrophic Debris Avalanche",
                "landslide_size": "Very Large",
                "fatalities": 350,
                "confidence": "VERY_HIGH",
                "source": "NASA Global Landslide Catalog / ISRO NRSC Validation",
            },
        },
    ]
    glc_geojson = {"type": "FeatureCollection", "features": glc_features}
    with open(aoi_dir / "glc_events.geojson", "w", encoding="utf-8") as f:
        json.dump(glc_geojson, f, indent=2)
    print(f"Generated NASA GLC events for Wayanad ({len(glc_features)} events)")

    # 4. Village Administrative Boundaries (Polygons)
    # Realistic villages in Wayanad
    villages = [
        {"id": "V_WYD_01", "name": "Meppadi", "coords": [76.10, 11.50, 76.16, 11.56], "pop": 34500},
        {"id": "V_WYD_02", "name": "Mundakkai", "coords": [76.14, 11.48, 76.19, 11.53], "pop": 6200},
        {"id": "V_WYD_03", "name": "Chooralmala", "coords": [76.12, 11.49, 76.17, 11.54], "pop": 8900},
        {"id": "V_WYD_04", "name": "Vythiri", "coords": [76.01, 11.52, 76.08, 11.58], "pop": 28400},
        {"id": "V_WYD_05", "name": "Kalpetta", "coords": [76.06, 11.59, 76.13, 11.64], "pop": 42000},
        {"id": "V_WYD_06", "name": "Pozhuthana", "coords": [75.98, 11.56, 76.05, 11.62], "pop": 19500},
        {"id": "V_WYD_07", "name": "Mananthavady", "coords": [75.96, 11.77, 76.05, 11.85], "pop": 46000},
        {"id": "V_WYD_08", "name": "Sulthan Bathery", "coords": [76.22, 11.63, 76.31, 11.71], "pop": 45000},
        {"id": "V_WYD_09", "name": "Ambalavayal", "coords": [76.18, 11.60, 76.25, 11.66], "pop": 26000},
        {"id": "V_WYD_10", "name": "Padinjarathara", "coords": [75.92, 11.64, 76.00, 11.71], "pop": 22000},
    ]

    village_features = []
    for v in villages:
        w, s, e, n = v["coords"]
        poly = Polygon([[w, s], [e, s], [e, n], [w, n], [w, s]])
        village_features.append({
            "type": "Feature",
            "geometry": mapping(poly),
            "properties": {
                "village_id": v["id"],
                "village_name": v["name"],
                "district": "Wayanad",
                "state": "Kerala",
                "population": v["pop"],
                "source": "Survey of India / OpenStreetMap Administrative Boundary (Clean Reference)",
            },
        })

    villages_geojson = {"type": "FeatureCollection", "features": village_features}
    with open(aoi_dir / "villages.geojson", "w", encoding="utf-8") as f:
        json.dump(villages_geojson, f, indent=2)
    print(f"Generated Village polygons for Wayanad ({len(villages)} villages)")


def generate_chamoli_demo():
    aoi_dir = DEMO_DIR / "aoi_chamoli"
    aoi_dir.mkdir(parents=True, exist_ok=True)

    # 1. Bounding Box: [79.15, 30.15, 79.75, 30.70]
    min_lon, min_lat, max_lon, max_lat = 79.15, 30.15, 79.75, 30.70
    rows, cols = 300, 330
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

    x = np.linspace(0, 1, cols)
    y = np.linspace(0, 1, rows)
    X, Y = np.meshgrid(x, y)

    # Steep Himalayan river gorge (Alaknanda / Dhauliganga) + High Himalayan ridge
    gorge = np.abs(X - 0.50) * 2200
    himalayan_peaks = (Y ** 1.5) * 2400
    relief = np.sin(X * 14.0) * np.cos(Y * 12.0) * 350
    dem = 1100.0 + gorge + himalayan_peaks + relief
    dem = np.clip(dem, 950.0, 5200.0).astype(np.float32)

    dem_path = aoi_dir / "dem.tif"
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        dst.write(dem, 1)
        dst.update_tags(
            source="SRTM GL1 30m DEM (Simulated Reference Clip)",
            resolution="30m",
            datum="WGS84",
            tag="DEMO_OFFLINE",
        )
    print(f"Generated DEM for Chamoli at {dem_path}")

    # 2. Daily Rainfall Series
    dates = [f"2021-02-{d:02d}" for d in range(1, 16)]
    base_amounts = [5.0, 8.0, 4.0, 12.0, 15.0, 10.0, 22.0, 35.0, 48.0, 60.0, 85.0, 110.0, 145.0, 190.0, 240.0]

    rainfall_data = {
        "aoi": "chamoli",
        "description": "Simulated NASA GPM IMERG v07 Final Daily calibrated against Chamoli flash-flood/debris-flow season",
        "dates": dates,
        "history_days": len(dates),
        "current_date": dates[-1],
        "current_intensity_mm_hr": 21.0,
        "trend_alpha_mm_hr2": 1.10,
        "daily_series": [],
    }

    rf_rows, rf_cols = 50, 55
    rf_transform = from_bounds(min_lon, min_lat, max_lon, max_lat, rf_cols, rf_rows)
    rf_X, rf_Y = np.meshgrid(np.linspace(0, 1, rf_cols), np.linspace(0, 1, rf_rows))
    orographic_factor = 0.6 + (rf_Y ** 1.2) * 1.4

    for i, (dt, base) in enumerate(zip(dates, base_amounts)):
        noise = np.sin(rf_X * 6 + i) * np.cos(rf_Y * 6) * (base * 0.12)
        rf_grid = np.clip(base * orographic_factor + noise, 0, None).astype(np.float32)

        day_file = aoi_dir / f"rainfall_{dt}.tif"
        with rasterio.open(
            day_file,
            "w",
            driver="GTiff",
            height=rf_rows,
            width=rf_cols,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=rf_transform,
            nodata=-9999.0,
        ) as dst:
            dst.write(rf_grid, 1)

        rainfall_data["daily_series"].append({
            "date": dt,
            "mean_mm": float(np.mean(rf_grid)),
            "max_mm": float(np.max(rf_grid)),
            "min_mm": float(np.min(rf_grid)),
            "raster_file": str(day_file.name),
        })

    with open(aoi_dir / "rainfall_series.json", "w", encoding="utf-8") as f:
        json.dump(rainfall_data, f, indent=2)
    print(f"Generated Rainfall series for Chamoli ({len(dates)} days)")

    # 3. GLC Events
    glc_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [79.56, 30.55]},
            "properties": {
                "event_id": "GLC_IND_CHM_001",
                "date": "2021-02-07",
                "location": "Raini / Tapovan, Chamoli",
                "trigger": "Rock/Ice avalanche + Torrential runoff",
                "landslide_category": "Catastrophic Rockslide Debris Flood",
                "landslide_size": "Very Large",
                "fatalities": 204,
                "confidence": "VERY_HIGH",
                "source": "NASA Global Landslide Catalog / GSI Bhusanket",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [79.54, 30.52]},
            "properties": {
                "event_id": "GLC_IND_CHM_002",
                "date": "2013-06-16",
                "location": "Joshimath Slopes",
                "trigger": "Extreme cloudburst",
                "landslide_category": "Debris flow",
                "landslide_size": "Large",
                "fatalities": 35,
                "confidence": "HIGH",
                "source": "NASA Global Landslide Catalog",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [79.35, 30.28]},
            "properties": {
                "event_id": "GLC_IND_CHM_003",
                "date": "2017-07-20",
                "location": "Karnaprayag Highway",
                "trigger": "Monsoon rain",
                "landslide_category": "Rotational slide",
                "landslide_size": "Medium",
                "fatalities": 2,
                "confidence": "MEDIUM",
                "source": "NASA Global Landslide Catalog",
            },
        },
    ]
    glc_geojson = {"type": "FeatureCollection", "features": glc_features}
    with open(aoi_dir / "glc_events.geojson", "w", encoding="utf-8") as f:
        json.dump(glc_geojson, f, indent=2)
    print(f"Generated NASA GLC events for Chamoli ({len(glc_features)} events)")

    # 4. Villages in Chamoli
    villages = [
        {"id": "V_CHM_01", "name": "Joshimath", "coords": [79.52, 30.52, 79.60, 30.58], "pop": 18000},
        {"id": "V_CHM_02", "name": "Raini", "coords": [79.57, 30.47, 79.64, 30.54], "pop": 1200},
        {"id": "V_CHM_03", "name": "Tapovan", "coords": [79.58, 30.49, 79.65, 30.56], "pop": 2400},
        {"id": "V_CHM_04", "name": "Karnaprayag", "coords": [79.20, 30.22, 79.28, 30.30], "pop": 12500},
        {"id": "V_CHM_05", "name": "Gopeshwar", "coords": [79.28, 30.38, 79.36, 30.45], "pop": 21000},
        {"id": "V_CHM_06", "name": "Pipalkoti", "coords": [79.38, 30.40, 79.46, 30.47], "pop": 7800},
    ]

    village_features = []
    for v in villages:
        w, s, e, n = v["coords"]
        poly = Polygon([[w, s], [e, s], [e, n], [w, n], [w, s]])
        village_features.append({
            "type": "Feature",
            "geometry": mapping(poly),
            "properties": {
                "village_id": v["id"],
                "village_name": v["name"],
                "district": "Chamoli",
                "state": "Uttarakhand",
                "population": v["pop"],
                "source": "Survey of India / OpenStreetMap Reference",
            },
        })

    villages_geojson = {"type": "FeatureCollection", "features": village_features}
    with open(aoi_dir / "villages.geojson", "w", encoding="utf-8") as f:
        json.dump(villages_geojson, f, indent=2)
    print(f"Generated Village polygons for Chamoli ({len(villages)} villages)")


if __name__ == "__main__":
    generate_wayanad_demo()
    generate_chamoli_demo()
    print("Seed demo data generation completed successfully!")
