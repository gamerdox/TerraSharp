"""
Unit tests for Rainfall Features and Soil-Saturation Proxy.
"""
import numpy as np
import pytest
from backend.app.soil.proxy import compute_soil_saturation_proxy
from backend.app.models.domain import ProvenanceTag


def test_soil_saturation_proxy_bounds_and_decay():
    # Test low antecedent rainfall
    r3_low = np.full((5, 5), 10.0, dtype=np.float32)
    r15_low = np.full((5, 5), 30.0, dtype=np.float32)

    proxy_low, meta_low = compute_soil_saturation_proxy(r3_low, r15_low)
    assert np.all(proxy_low >= 0.0) and np.all(proxy_low <= 1.0)
    assert np.all(proxy_low < 0.20)
    assert meta_low["provenance"] == ProvenanceTag.PROXY.value

    # Test extreme antecedent deluge saturating soil profile
    r3_high = np.full((5, 5), 450.0, dtype=np.float32)
    r15_high = np.full((5, 5), 1200.0, dtype=np.float32)

    proxy_high, meta_high = compute_soil_saturation_proxy(r3_high, r15_high)
    assert np.all(proxy_high == 1.0)  # Clipped to 1.0
