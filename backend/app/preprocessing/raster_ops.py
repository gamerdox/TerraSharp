"""
Raster operations for clipping, resampling, and spatial alignment.
Ensures all environmental layers match the AnalysisGrid dimensions exactly.
"""
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

from backend.app.preprocessing.grid import AnalysisGrid


def resample_raster_to_grid(
    src_raster_path: str,
    target_grid: AnalysisGrid,
    resampling_method: Resampling = Resampling.bilinear,
    nodata_fill: float = 0.0,
) -> np.ndarray:
    """
    Reprojects and resamples any GeoTIFF raster onto the AnalysisGrid.
    Returns a 2D numpy array matching (target_grid.rows, target_grid.cols).
    """
    with rasterio.open(src_raster_path) as src:
        destination = np.full((target_grid.rows, target_grid.cols), nodata_fill, dtype=np.float32)

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=target_grid.transform,
            dst_crs=target_grid.target_crs,
            resampling=resampling_method,
            dst_nodata=nodata_fill,
        )

        # Replace NaN / infinite with nodata_fill
        destination = np.nan_to_num(destination, nan=nodata_fill, posinf=nodata_fill, neginf=nodata_fill)
        return destination


def write_grid_raster(
    data: np.ndarray,
    target_grid: AnalysisGrid,
    out_path: str,
    nodata: float = -9999.0,
    tags: Optional[dict] = None,
):
    """
    Saves a 2D grid array as a georeferenced GeoTIFF conforming to the target_grid.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=target_grid.rows,
        width=target_grid.cols,
        count=1,
        dtype="float32",
        crs=target_grid.target_crs,
        transform=target_grid.transform,
        nodata=nodata,
    ) as dst:
        dst.write(data.astype(np.float32), 1)
        if tags:
            dst.update_tags(**tags)
