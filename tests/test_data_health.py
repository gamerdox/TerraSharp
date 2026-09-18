import pytest
from backend.app.ingestion.data_health import data_health_service
from backend.app.models.domain import DataFreshnessStatus


def test_data_health_evaluation_wayanad():
    res = data_health_service.evaluate_health("wayanad")
    assert res.active_aoi == "wayanad"
    assert "srtm_dem" in res.layers
    assert "rainfall_feed" in res.layers
    assert "soil_proxy" in res.layers
    assert "glc_events" in res.layers
    assert "admin_boundaries" in res.layers

    # DEM and Rainfall should be valid status (LIVE or CACHED)
    assert res.layers["srtm_dem"].status in [DataFreshnessStatus.LIVE, DataFreshnessStatus.CACHED]
    assert res.layers["rainfall_feed"].status in [DataFreshnessStatus.LIVE, DataFreshnessStatus.CACHED]
    assert res.overall_status in [DataFreshnessStatus.LIVE, DataFreshnessStatus.CACHED]


def test_data_health_evaluation_missing_aoi():
    res = data_health_service.evaluate_health("nonexistent_aoi_999")
    assert res.active_aoi == "nonexistent_aoi_999"
    assert res.layers["srtm_dem"].status == DataFreshnessStatus.UNAVAILABLE
    assert res.layers["rainfall_feed"].status == DataFreshnessStatus.UNAVAILABLE
    assert res.overall_status == DataFreshnessStatus.UNAVAILABLE
