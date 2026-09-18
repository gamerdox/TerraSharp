from fastapi.testclient import TestClient
import pytest
from backend.app.main import app

client = TestClient(app)


def test_api_alerts_active():
    res = client.get("/alerts")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if data:
        assert "alert_id" in data[0]
        assert "alert_state" in data[0]
        assert "risk_score" in data[0]


def test_api_alerts_history():
    res = client.get("/alerts/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_alerts_emails():
    res = client.get("/alerts/emails")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_test_email_dispatch():
    payload = {
        "recipient_email": "test-operator@gov.in",
        "severity": "WARNING",
        "village_name": "Chooralmala Test Zone",
    }
    res = client.post("/alerts/test-email", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["SIMULATED", "SENT"]
    assert "Chooralmala Test Zone" in data["dispatch_record"]["village_name"]


def test_api_health_data():
    res = client.get("/health/data?aoi=wayanad")
    assert res.status_code == 200
    data = res.json()
    assert "overall_status" in data
    assert "layers" in data
    assert "srtm_dem" in data["layers"]
    assert "rainfall_feed" in data["layers"]
