"""
Tests for Personal Dangerzone Email Alerts and Slope Calculation Accuracy.
Verifies:
- Authentic terrain slope gradient (no 0% slope on mountains)
- Zone classification: Red Zone (High Alert) vs Yellow Zone (Normal Alert) vs Green Zone (Safe)
- Email dispatch decisions, escalation triggers, and anti-spam cooldowns
- API endpoints POST /alerts/monitor-zone and GET /alerts/smtp-status
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.alerts.personal_monitor import PersonalDangerzoneMonitor, ZONE_RED, ZONE_YELLOW, ZONE_GREEN
from backend.app.ingestion.live_point_fetcher import live_point_fetcher


@pytest.fixture
def client():
    return TestClient(app)


def test_mountain_slope_not_zero():
    """Verify that mountain coordinates compute authentic non-zero slope degrees and grade %."""
    # Wayanad coordinates
    res = live_point_fetcher.fetch_point_terrain(11.55, 76.15)
    assert res["elevation_m"] > 500.0, "Should be high elevation"
    assert res["slope_deg"] > 0.0, "Slope degrees on mountain must not be 0.0"
    assert res["slope_pct"] > 0.0, "Slope % grade on mountain must not be 0.0"
    assert res["slope_norm"] > 0.0, "Normalized slope hazard must not be 0.0"


def test_personal_dangerzone_green_safe():
    """Green Zone (risk < 0.35) should not dispatch alarm email."""
    monitor = PersonalDangerzoneMonitor(cooldown_seconds=1800)
    
    mock_point = {
        "landslide_risk": 0.12,
        "flash_flood_risk": 0.08,
        "elevation_m": 850.0,
        "slope_deg": 12.0,
        "slope_pct": 21.3,
        "rainfall_24h_mm": 5.0,
        "rainfall_15d_mm": 20.0,
        "soil_saturation_pct": 25.0,
        "caine_threshold": {"intensity_ratio": 0.15, "status": "SAFE"},
        "false_alarm_mitigation": {"suppressed": False},
    }
    
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=mock_point):
        res = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res["zone"] == ZONE_GREEN
        assert res["email_dispatched"] is False
        assert "Green Zone" in res["dispatch_reason"]


def test_personal_dangerzone_yellow_normal_alert():
    """Yellow Zone (0.35 <= risk < 0.60) should dispatch Normal Alert email."""
    monitor = PersonalDangerzoneMonitor(cooldown_seconds=1800)
    
    mock_point = {
        "landslide_risk": 0.45,
        "flash_flood_risk": 0.30,
        "elevation_m": 920.0,
        "slope_deg": 22.0,
        "slope_pct": 40.4,
        "rainfall_24h_mm": 45.0,
        "rainfall_15d_mm": 120.0,
        "soil_saturation_pct": 55.0,
        "caine_threshold": {"intensity_ratio": 0.70, "status": "ELEVATED"},
        "false_alarm_mitigation": {"suppressed": False},
    }
    
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=mock_point):
        res = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res["zone"] == ZONE_YELLOW
        assert res["email_dispatched"] is True
        assert "Normal Alert Yellow Zone" in res["dispatch_reason"]


def test_personal_dangerzone_red_high_alert():
    """Red Zone (risk >= 0.60) should dispatch High Alert email."""
    monitor = PersonalDangerzoneMonitor(cooldown_seconds=1800)
    
    mock_point = {
        "landslide_risk": 0.78,
        "flash_flood_risk": 0.65,
        "elevation_m": 1050.0,
        "slope_deg": 32.0,
        "slope_pct": 62.5,
        "rainfall_24h_mm": 140.0,
        "rainfall_15d_mm": 350.0,
        "soil_saturation_pct": 85.0,
        "caine_threshold": {"intensity_ratio": 1.45, "status": "BREACHED"},
        "false_alarm_mitigation": {"suppressed": False},
    }
    
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=mock_point):
        res = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res["zone"] == ZONE_RED
        assert res["email_dispatched"] is True
        assert "High Alert Red Zone" in res["dispatch_reason"]


def test_personal_dangerzone_escalation_and_cooldown():
    """Escalating from Yellow to Red immediately bypasses cooldown."""
    monitor = PersonalDangerzoneMonitor(cooldown_seconds=1800)
    
    # 1. First evaluation: Yellow Zone
    yellow_point = {
        "landslide_risk": 0.40,
        "flash_flood_risk": 0.20,
        "elevation_m": 900.0,
        "slope_deg": 20.0,
        "slope_pct": 36.4,
        "rainfall_24h_mm": 30.0,
        "rainfall_15d_mm": 80.0,
        "soil_saturation_pct": 50.0,
        "caine_threshold": {"intensity_ratio": 0.5, "status": "SAFE"},
        "false_alarm_mitigation": {"suppressed": False},
    }
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=yellow_point):
        res1 = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res1["zone"] == ZONE_YELLOW
        assert res1["email_dispatched"] is True

    # 2. Second evaluation: still Yellow Zone (Cooldown suppresses email)
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=yellow_point):
        res2 = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res2["zone"] == ZONE_YELLOW
        assert res2["email_dispatched"] is False
        assert "suppressed by cooldown" in res2["dispatch_reason"]

    # 3. Third evaluation: Escalation to Red Zone (Must dispatch immediately!)
    red_point = {
        "landslide_risk": 0.72,
        "flash_flood_risk": 0.50,
        "elevation_m": 900.0,
        "slope_deg": 20.0,
        "slope_pct": 36.4,
        "rainfall_24h_mm": 120.0,
        "rainfall_15d_mm": 250.0,
        "soil_saturation_pct": 80.0,
        "caine_threshold": {"intensity_ratio": 1.2, "status": "BREACHED"},
        "false_alarm_mitigation": {"suppressed": False},
    }
    with patch.object(live_point_fetcher, "evaluate_live_pinpoint", return_value=red_point):
        res3 = monitor.evaluate_user_location("user@example.com", 11.55, 76.15)
        assert res3["zone"] == ZONE_RED
        assert res3["email_dispatched"] is True
        assert "ESCALATION" in res3["dispatch_reason"]


def test_api_monitor_zone_endpoint(client):
    """Test POST /alerts/monitor-zone API endpoint."""
    payload = {
        "email": "emergency-officer@wayanad.gov.in",
        "lat": 11.55,
        "lon": 76.15,
        "location_name": "Meppadi Hill",
        "force_dispatch": True,
    }
    resp = client.post("/alerts/monitor-zone", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "emergency-officer@wayanad.gov.in"
    assert data["zone"] in ["RED", "YELLOW", "GREEN"]
    assert "slope_deg" in data
    assert "slope_pct" in data
    assert data["email_dispatched"] is True  # forced test


def test_api_smtp_status_endpoint(client):
    """Test GET /alerts/smtp-status API endpoint."""
    resp = client.get("/alerts/smtp-status")
    assert resp.status_code == 200
    data = resp.json()
    assert "configured" in data
    assert "mode" in data
    assert data["mode"] in ["REAL_SMTP", "SIMULATED_TEST_MODE"]
