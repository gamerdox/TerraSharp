"""
Unit tests for Terrain Processing (Horn Slope and D8 Flow Accumulation).
"""
import numpy as np
import pytest
from backend.app.terrain.slope import compute_slope_and_aspect
from backend.app.terrain.drainage import compute_d8_flow_accumulation


def test_horn_slope_flat_plane():
    # Completely flat surface: slope must be 0 degrees
    elev = np.full((20, 20), 500.0, dtype=np.float32)
    slope_deg, aspect_deg, slope_norm, meta = compute_slope_and_aspect(elev, 100.0, 100.0)

    # Interior cells must be 0
    assert np.allclose(slope_deg[1:-1, 1:-1], 0.0, atol=1e-3)
    assert np.allclose(slope_norm[1:-1, 1:-1], 0.0, atol=1e-3)


def test_horn_slope_known_gradient():
    # 45-degree planar slope: dz/dx = 1.0 (dz = 100m for dx = 100m)
    x = np.arange(20) * 100.0
    elev = np.tile(x, (20, 1)).astype(np.float32)
    slope_deg, aspect_deg, slope_norm, meta = compute_slope_and_aspect(elev, 100.0, 100.0)

    # Interior slope must equal 45 degrees
    assert np.allclose(slope_deg[2:-2, 2:-2], 45.0, atol=0.5)


def test_d8_flow_accumulation():
    # V-shaped valley draining toward center column (col 5)
    rows, cols = 10, 11
    elev = np.zeros((rows, cols), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            # Uphill away from center column and uphill toward top row
            elev[r, c] = 1000.0 - (r * 10.0) + abs(c - 5) * 50.0

    flow_accum, norm_accum, meta = compute_d8_flow_accumulation(elev, 100.0, 100.0)

    # Center valley bottom at bottom row should have highest accumulation
    assert flow_accum[rows - 1, 5] > 10.0
    assert norm_accum[rows - 1, 5] > 0.5
