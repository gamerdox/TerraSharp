"""
Live Grid Data Fetcher — Real Elevation & Rainfall from Open-Meteo APIs.

Batch-fetches SRTM 30m elevation and 15-day hourly precipitation for entire
analysis grids using high-efficiency multi-coordinate requests with backoff.
Writes results as properly georeferenced GeoTIFFs that plug directly into
the existing raster pipeline.

APIs Used:
  - Elevation: https://api.open-meteo.com/v1/elevation  (SRTM/Copernicus 30m)
  - Rainfall:  https://api.open-meteo.com/v1/forecast    (ERA5/ECMWF reanalysis + forecast)

Both are free, keyless, and provide global coverage.
"""
import json
import logging
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import rasterio
from rasterio.transform import from_bounds

logger = logging.getLogger(__name__)

# Safe batch sizes to prevent exceeding request size or minutely limits
ELEVATION_BATCH_SIZE = 100
RAINFALL_BATCH_SIZE = 25

API_DELAY_SEC = 0.50
REQUEST_TIMEOUT_SEC = 20.0
USER_AGENT = "TerraSharp-SH304/1.0"


def _api_get(url: str, timeout: float = REQUEST_TIMEOUT_SEC, max_retries: int = 3) -> Any:
    """Helper to make a GET request and parse JSON response with automatic 429 backoff."""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429:
                wait_sec = 62.0  # Open-Meteo explicitly requires 60 seconds reset for minutely limits
                logger.warning(
                    f"Open-Meteo minutely rate limit reached. Pausing {wait_sec:.0f}s "
                    f"for rate window reset (attempt {attempt+1}/{max_retries})..."
                )
                time.sleep(wait_sec)
            else:
                logger.warning(f"HTTP Error {err.code}: {err.reason}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2.0)
        except Exception as e:
            logger.warning(f"API request failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2.0)
    raise RuntimeError(f"Failed to fetch data from {url} after {max_retries} attempts")


def fetch_dem_grid(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    rows: int,
    cols: int,
) -> np.ndarray:
    """
    Fetches real SRTM 30m elevation data for a grid of coordinates from Open-Meteo.
    Uses multi-coordinate batch requests (up to 100 points per call).
    Returns a 2D numpy array of shape (rows, cols) with elevation in meters.
    """
    lons = np.linspace(min_lon, max_lon, cols, endpoint=False) + (max_lon - min_lon) / (2 * cols)
    lats = np.linspace(max_lat, min_lat, rows, endpoint=False) - (max_lat - min_lat) / (2 * rows)

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    flat_lats = lat_grid.ravel()
    flat_lons = lon_grid.ravel()
    total_points = len(flat_lats)

    logger.info(f"Fetching real DEM for {rows}x{cols} grid ({total_points} points) from Open-Meteo...")

    elevations = np.full(total_points, 500.0, dtype=np.float32)
    fetched_count = 0

    for start_idx in range(0, total_points, ELEVATION_BATCH_SIZE):
        end_idx = min(start_idx + ELEVATION_BATCH_SIZE, total_points)
        batch_lats = flat_lats[start_idx:end_idx]
        batch_lons = flat_lons[start_idx:end_idx]

        lats_str = ",".join(f"{lt:.5f}" for lt in batch_lats)
        lons_str = ",".join(f"{ln:.5f}" for ln in batch_lons)

        url = f"https://api.open-meteo.com/v1/elevation?latitude={lats_str}&longitude={lons_str}"

        try:
            data = _api_get(url)
            batch_elevs = data.get("elevation", [])
            if len(batch_elevs) == len(batch_lats):
                for i, elev in enumerate(batch_elevs):
                    elevations[start_idx + i] = float(elev) if elev is not None else 500.0
                fetched_count += len(batch_elevs)
        except Exception as e:
            logger.warning(f"DEM batch {start_idx}-{end_idx} failed: {e}")

        if end_idx < total_points:
            time.sleep(API_DELAY_SEC)

    logger.info(
        f"DEM fetch complete: {fetched_count}/{total_points} points. "
        f"Elevation range: {elevations.min():.0f}m - {elevations.max():.0f}m"
    )

    return elevations.reshape(rows, cols)


def fetch_rainfall_grid(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    rf_rows: int,
    rf_cols: int,
    past_days: int = 15,
) -> Tuple[List[np.ndarray], Dict[str, Any]]:
    """
    Fetches real hourly precipitation for a grid from Open-Meteo forecast API.
    Uses multi-coordinate batch requests (up to 25 locations per call).

    Returns:
      - daily_grids: List of 2D arrays, one per day (rf_rows × rf_cols), values in mm
      - metadata: Dict with dates, intensity, trend info
    """
    lons = np.linspace(min_lon, max_lon, rf_cols, endpoint=False) + (max_lon - min_lon) / (2 * rf_cols)
    lats = np.linspace(max_lat, min_lat, rf_rows, endpoint=False) - (max_lat - min_lat) / (2 * rf_rows)

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    flat_lats = lat_grid.ravel()
    flat_lons = lon_grid.ravel()
    total_cells = len(flat_lats)

    logger.info(f"Fetching real rainfall for {rf_rows}x{rf_cols} grid ({total_cells} cells) from Open-Meteo...")

    expected_hours = (past_days + 1) * 24
    all_hourly = np.zeros((rf_rows, rf_cols, expected_hours), dtype=np.float32)

    fetched_count = 0
    dates_set = set()

    for start_idx in range(0, total_cells, RAINFALL_BATCH_SIZE):
        end_idx = min(start_idx + RAINFALL_BATCH_SIZE, total_cells)
        batch_lats = flat_lats[start_idx:end_idx]
        batch_lons = flat_lons[start_idx:end_idx]

        lats_str = ",".join(f"{lt:.4f}" for lt in batch_lats)
        lons_str = ",".join(f"{ln:.4f}" for ln in batch_lons)

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lats_str}&longitude={lons_str}"
            f"&hourly=precipitation&past_days={past_days}&forecast_days=1"
        )

        try:
            data = _api_get(url)
            items = data if isinstance(data, list) else [data]
            for i, item in enumerate(items):
                cell_idx = start_idx + i
                if cell_idx >= total_cells:
                    break
                r = cell_idx // rf_cols
                c = cell_idx % rf_cols

                hourly = item.get("hourly", {})
                precip = hourly.get("precipitation", [])
                times = hourly.get("time", [])

                if precip:
                    n = min(len(precip), expected_hours)
                    for h_idx in range(n):
                        val = precip[h_idx]
                        all_hourly[r, c, h_idx] = float(val) if val is not None else 0.0

                    for t in times:
                        if t:
                            dates_set.add(t[:10])

                    fetched_count += 1
        except Exception as e:
            logger.warning(f"Rainfall batch {start_idx}-{end_idx} failed: {e}")

        if end_idx < total_cells:
            time.sleep(API_DELAY_SEC)

    logger.info(f"Rainfall fetch complete: {fetched_count}/{total_cells} cells")

    dates = sorted(dates_set)
    if len(dates) < past_days:
        today = datetime.now(timezone.utc).date()
        dates = [(today - timedelta(days=past_days - i)).isoformat() for i in range(past_days + 1)]

    daily_grids = []
    num_days = min(len(dates), all_hourly.shape[2] // 24)
    for d in range(num_days):
        start_h = d * 24
        end_h = start_h + 24
        if end_h > all_hourly.shape[2]:
            break
        daily = np.sum(all_hourly[:, :, start_h:end_h], axis=2).astype(np.float32)
        daily_grids.append(daily)

    if daily_grids:
        last_day = daily_grids[-1]
        mean_intensity = float(np.mean(last_day)) / 24.0
        if len(daily_grids) >= 4:
            prev_intensity = float(np.mean(daily_grids[-4])) / 24.0
            trend_alpha = (mean_intensity - prev_intensity) / 72.0
        else:
            trend_alpha = 0.0
    else:
        mean_intensity = 0.0
        trend_alpha = 0.0

    metadata = {
        "dates": dates[:num_days],
        "num_days": num_days,
        "current_intensity_mm_hr": round(mean_intensity, 3),
        "trend_alpha_mm_hr2": round(trend_alpha, 4),
        "fetched_cells": fetched_count,
        "total_cells": total_cells,
    }

    return daily_grids, metadata


def write_grid_geotiff(
    array: np.ndarray,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    output_path: str,
    source_tag: str = "Open-Meteo Live Data",
    nodata: float = -9999.0,
) -> None:
    """Writes a 2D numpy array as a georeferenced GeoTIFF."""
    rows, cols = array.shape
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=nodata,
    ) as dst:
        dst.write(array.astype(np.float32), 1)
        dst.update_tags(
            source=source_tag,
            resolution="~1km analysis grid",
            datum="WGS84",
            fetched_at=datetime.now(timezone.utc).isoformat(),
            tag="LIVE_API_DATA",
        )


def is_cache_valid(file_path: Path, max_age_hours: float) -> bool:
    """Check if a cached file exists and is younger than max_age_hours."""
    if not file_path.exists():
        return False
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(timezone.utc) - mtime
    return age < timedelta(hours=max_age_hours)


def generate_live_dem(
    aoi_key: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    output_dir: Path,
    cache_hours: float = 24.0,
) -> Path:
    """
    Generates a real DEM GeoTIFF for an AOI by fetching from Open-Meteo elevation API.
    """
    dem_path = output_dir / "dem.tif"

    if is_cache_valid(dem_path, cache_hours):
        logger.info(f"Using cached live DEM for {aoi_key} (age < {cache_hours}h)")
        return dem_path

    output_dir.mkdir(parents=True, exist_ok=True)

    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    # ~20x20 grid points (~2.5km cells) - only 4-5 API batches, well within limits
    rows = max(12, min(20, int(lat_span / 0.025)))
    cols = max(12, min(20, int(lon_span / 0.025)))

    dem_array = fetch_dem_grid(min_lon, min_lat, max_lon, max_lat, rows, cols)

    write_grid_geotiff(
        dem_array,
        min_lon, min_lat, max_lon, max_lat,
        str(dem_path),
        source_tag=f"SRTM 30m DEM via Open-Meteo ({aoi_key})",
    )

    logger.info(f"Wrote live DEM for {aoi_key}: {dem_path} ({rows}x{cols})")
    return dem_path


def generate_live_rainfall(
    aoi_key: str,
    name: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    output_dir: Path,
    cache_hours: float = 6.0,
) -> Path:
    """
    Generates real rainfall GeoTIFFs for 15 days by fetching from Open-Meteo forecast API.
    Returns path to the rainfall_series.json file.
    """
    series_file = output_dir / "rainfall_series.json"

    if is_cache_valid(series_file, cache_hours):
        logger.info(f"Using cached live rainfall for {aoi_key} (age < {cache_hours}h)")
        return series_file

    output_dir.mkdir(parents=True, exist_ok=True)

    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    # 8x8 to 10x10 grid (~5-7km cells) - only 3-4 API batches
    rf_rows = max(6, min(10, int(lat_span / 0.05)))
    rf_cols = max(6, min(10, int(lon_span / 0.05)))

    daily_grids, meta = fetch_rainfall_grid(
        min_lon, min_lat, max_lon, max_lat, rf_rows, rf_cols
    )

    if not daily_grids or meta.get("fetched_cells", 0) == 0:
        raise RuntimeError(f"Failed to fetch any rainfall data for {aoi_key}")

    dates = meta["dates"]
    rainfall_data = {
        "aoi": aoi_key,
        "description": f"Real-time precipitation data via Open-Meteo for {name}",
        "dates": dates,
        "history_days": len(daily_grids),
        "current_date": dates[-1] if dates else datetime.now(timezone.utc).date().isoformat(),
        "current_intensity_mm_hr": meta["current_intensity_mm_hr"],
        "trend_alpha_mm_hr2": meta["trend_alpha_mm_hr2"],
        "provenance": "OBSERVED",
        "data_source_url": "https://open-meteo.com/ (ERA5/ECMWF reanalysis + forecast)",
        "daily_series": [],
    }

    for i, (grid, date_str) in enumerate(zip(daily_grids, dates)):
        day_file = output_dir / f"rainfall_{date_str}.tif"
        write_grid_geotiff(
            grid,
            min_lon, min_lat, max_lon, max_lat,
            str(day_file),
            source_tag=f"Open-Meteo Precipitation ({date_str})",
        )

        rainfall_data["daily_series"].append({
            "date": date_str,
            "mean_mm": round(float(np.mean(grid)), 1),
            "max_mm": round(float(np.max(grid)), 1),
            "min_mm": round(float(np.min(grid[grid >= 0])) if np.any(grid >= 0) else 0.0, 1),
            "raster_file": day_file.name,
        })

    with open(series_file, "w", encoding="utf-8") as f:
        json.dump(rainfall_data, f, indent=2)

    logger.info(f"Wrote live rainfall for {aoi_key}: {len(daily_grids)} days, {rf_rows}x{rf_cols} grid")
    return series_file
