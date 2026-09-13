"""
Integration tests for FastAPI REST API endpoints using httpx TestClient with lifespan context.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "data_status" in data
    assert data["data_status"]["dem_loaded"] is True


def test_aoi_endpoints(client):
    res_list = client.get("/aoi")
    assert res_list.status_code == 200
    aois = res_list.json()
    assert len(aois) >= 2
    ids = [a["id"] for a in aois]
    assert "wayanad" in ids
    assert "chamoli" in ids

    res_curr = client.get("/aoi/current")
    assert res_curr.status_code == 200

    res_switch = client.post("/aoi/select/chamoli")
    assert res_switch.status_code == 200
    assert res_switch.json()["active_aoi"] == "chamoli"


def test_process_pipeline(client):
    res = client.post("/process?aoi=wayanad")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["aoi"] == "wayanad"
    assert data["villages_analyzed"] > 0
    assert data["alerts_generated"] > 0


def test_risk_endpoints(client):
    res_risk = client.get("/risk")
    assert res_risk.status_code == 200
    data = res_risk.json()
    assert "cells" in data
    assert len(data["cells"]) > 0

    res_point = client.get("/risk/point?lat=11.60&lon=76.10")
    assert res_point.status_code == 200
    pt_data = res_point.json()
    assert "landslide_risk" in pt_data
    assert "factors" in pt_data
    assert "dominant_factor" in pt_data["factors"]


def test_leadtime_endpoint(client):
    res = client.get("/leadtime")
    assert res.status_code == 200
    data = res.json()
    assert "caine_threshold_intensity_mm_hr" in data
    assert "scientific_disclaimer" in data


def test_alerts_endpoint(client):
    res = client.get("/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    assert alerts[0]["simulated"] is True


def test_villages_and_geojson_endpoints(client):
    res_v = client.get("/villages")
    assert res_v.status_code == 200
    villages = res_v.json()
    assert len(villages) > 0

    res_geo = client.get("/villages/geojson")
    assert res_geo.status_code == 200
    geojson = res_geo.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0


def test_backtest_endpoint(client):
    res = client.get("/backtest")
    assert res.status_code == 200
    data = res.json()
    assert "rain_only_baseline" in data
    assert "full_weighted_index" in data
    assert data["full_weighted_index"]["roc_auc"] >= data["rain_only_baseline"]["roc_auc"]


def test_reports_endpoint(client):
    res_rep = client.get("/reports")
    assert res_rep.status_code == 200
    rep = res_rep.json()
    assert "report_title" in rep
    assert "summary" in rep

    res_md = client.get("/reports/markdown")
    assert res_md.status_code == 200
    assert "# SH-304 Early Warning" in res_md.text
