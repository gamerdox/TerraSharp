"""
Unit and integration tests for Live Point Fetcher and False-Alarm Mitigation Gate.
"""
import pytest
from backend.app.ingestion.live_point_fetcher import LivePointFetcher


def test_live_point_fetcher_slope_horn_geometry():
    fetcher = LivePointFetcher()
    # Test known location (Wayanad or Chamoli)
    res = fetcher.fetch_point_terrain(11.55, 76.15)
    assert "elevation_m" in res
    assert "slope_deg" in res
    assert 0.0 <= res["slope_deg"] <= 90.0
    assert 0.0 <= res["slope_norm"] <= 1.0


def test_live_point_fetcher_rainfall_15d_decay():
    fetcher = LivePointFetcher()
    rf = fetcher.fetch_point_rainfall(11.55, 76.15)
    assert "rainfall_24h_mm" in rf
    assert "rainfall_15d_mm" in rf
    assert "soil_proxy" in rf
    assert 0.0 <= rf["soil_proxy"] <= 1.0
    assert rf["rainfall_15d_mm"] >= rf["rainfall_24h_mm"]


def test_false_alarm_mitigation_on_flat_plain():
    fetcher = LivePointFetcher()
    # Flat location (Delhi/Kolkata plains)
    res = fetcher.evaluate_live_pinpoint(28.61, 77.20)
    assert res["elevation_m"] < 500.0
    assert res["slope_deg"] < 15.0
    # Landslide risk must be strictly suppressed
    assert res["landslide_risk"] < 0.15
    assert res["false_alarm_mitigation"]["suppressed"] is True
    assert res["false_alarm_mitigation"]["confidence_score_pct"] >= 90.0


def test_live_point_prediction_structure():
    fetcher = LivePointFetcher()
    res = fetcher.evaluate_live_pinpoint(30.45, 79.45)
    required_keys = [
        "latitude", "longitude", "elevation_m", "slope_deg", "aspect_deg",
        "rainfall_24h_mm", "rainfall_3d_mm", "rainfall_15d_mm", "current_intensity_mm_hr",
        "soil_saturation_proxy", "soil_saturation_pct", "landslide_risk", "flash_flood_risk",
        "risk_class", "alert_state", "caine_threshold", "false_alarm_mitigation",
        "dominant_factor", "data_provenance"
    ]
    for k in required_keys:
        assert k in res, f"Missing key {k} in live pinpoint response"
