"""
Unit tests for AnalysisGrid and Coordinate Transforms.
"""
import pytest
from backend.app.config import BoundingBox
from backend.app.preprocessing.grid import AnalysisGrid


def test_analysis_grid_creation():
    bbox = BoundingBox(min_lon=75.8, min_lat=11.45, max_lon=76.35, max_lat=11.95)
    grid = AnalysisGrid(bbox, resolution_deg=0.01, utm_epsg=32643)

    assert grid.rows == 50
    assert grid.cols == 55
    assert grid.dx_meters > 800 and grid.dx_meters < 1300
    assert grid.dy_meters > 800 and grid.dy_meters < 1300
    assert grid.cell_area_sqkm > 0.8 and grid.cell_area_sqkm < 1.6
    assert grid.lon_grid.shape == (50, 55)
    assert grid.lat_grid.shape == (50, 55)
