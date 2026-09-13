"""
Unit tests for Lead-Time Estimation (Caine 1980) and Alert Engine.
"""
import pytest
from backend.app.leadtime.caine_threshold import evaluate_caine_lead_time
from backend.app.alerts.engine import AlertEngine, determine_alert_state
from backend.app.models.domain import AlertState, RiskLevel, HazardType
from backend.app.models.schemas import ContributingFactors


def test_caine_threshold_evaluation():
    # At D = 24 hours: I_crit = 14.82 * (24 ^ -0.39) approx 4.29 mm/hr
    # If intensity is 20 mm/hr, threshold is breached
    res_breach = evaluate_caine_lead_time(current_intensity_mm_hr=20.0, duration_hours=24.0)
    assert res_breach.status == "THRESHOLD_BREACHED"
    assert res_breach.estimated_lead_time_hours == 0.0

    # If intensity is 2.0 mm/hr and trend is 0.5 mm/hr^2
    res_approaching = evaluate_caine_lead_time(
        current_intensity_mm_hr=2.0, duration_hours=24.0, trend_alpha_mm_hr2=0.5
    )
    assert res_approaching.status == "APPROACHING_THRESHOLD"
    assert res_approaching.estimated_lead_time_hours > 0
    assert "Caine (1980)" in res_approaching.scientific_disclaimer


def test_alert_engine_transitions():
    assert determine_alert_state(0.15) == AlertState.NORMAL
    assert determine_alert_state(0.35) == AlertState.WATCH
    assert determine_alert_state(0.60) == AlertState.WARNING
    assert determine_alert_state(0.85) == AlertState.CRITICAL

    engine = AlertEngine()
    factors = ContributingFactors(
        rainfall_score=0.9,
        slope_score=0.8,
        soil_proxy_score=0.7,
        history_score=0.6,
        weights_used={},
        dominant_factor="Heavy Rainfall",
        explanation="Test explanation",
    )

    alert = engine.generate_village_alert(
        village_id="V01",
        village_name="Mundakkai",
        coordinates={"lat": 11.5, "lon": 76.1},
        landslide_risk=0.82,
        flash_flood_risk=0.45,
        factors=factors,
        lead_time_hours=0.0,
    )

    assert alert.alert_state == AlertState.CRITICAL
    assert alert.hazard_type == HazardType.LANDSLIDE
    assert alert.simulated is True
    assert "EVACUATION" in alert.recommended_action
