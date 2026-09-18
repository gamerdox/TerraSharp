import pytest
from datetime import datetime, timezone, timedelta
from backend.app.alerts.engine import StatefulAlertEngine, ESCALATION_THRESHOLDS, DE_ESCALATION_THRESHOLDS
from backend.app.models.domain import AlertState, HazardType, EmailStatus
from backend.app.models.schemas import ContributingFactors
from backend.app.config import settings


@pytest.fixture
def clean_engine():
    engine = StatefulAlertEngine()
    engine.reset()
    return engine


@pytest.fixture
def dummy_factors():
    return ContributingFactors(
        rainfall_score=0.75,
        slope_score=0.80,
        soil_proxy_score=0.65,
        history_score=0.40,
        weights_used={},
        dominant_factor="Continuous Monsoon Rain",
        explanation="Slope saturation threshold exceeded",
    )


def test_escalation_flow(clean_engine, dummy_factors):
    v_id = "V_TEST_01"
    v_name = "Chooralmala Sector A"
    coords = {"lat": 11.52, "lon": 76.12}

    # Step 1: Normal baseline
    alert1 = clean_engine.evaluate_village(v_id, v_name, coords, 0.20, 0.15, dummy_factors)
    assert alert1.alert_state == AlertState.NORMAL

    # Step 2: Escalate to WATCH (>= 0.35)
    alert2 = clean_engine.evaluate_village(v_id, v_name, coords, 0.40, 0.20, dummy_factors)
    assert alert2.alert_state == AlertState.WATCH

    # Step 3: Escalate to WARNING (>= 0.60)
    alert3 = clean_engine.evaluate_village(v_id, v_name, coords, 0.65, 0.30, dummy_factors)
    assert alert3.alert_state == AlertState.WARNING

    # Step 4: Escalate to CRITICAL (>= 0.80)
    alert4 = clean_engine.evaluate_village(v_id, v_name, coords, 0.88, 0.50, dummy_factors)
    assert alert4.alert_state == AlertState.CRITICAL

    # Verify history recorded all transitions
    history = clean_engine.get_history()
    assert len(history) >= 3
    # Latest should be CRITICAL
    assert history[0].to_state == AlertState.CRITICAL


def test_hysteresis_deadband(clean_engine, dummy_factors):
    v_id = "V_TEST_HYST"
    v_name = "Meppadi Ridge"
    coords = {"lat": 11.55, "lon": 76.15}

    # Escalate to CRITICAL with 0.85
    clean_engine.evaluate_village(v_id, v_name, coords, 0.85, 0.40, dummy_factors)
    assert clean_engine.trackers[v_id].current_state == AlertState.CRITICAL

    # Small drop to 0.75: Should STAY in CRITICAL due to hysteresis floor (0.70)
    alert_hold = clean_engine.evaluate_village(v_id, v_name, coords, 0.75, 0.40, dummy_factors)
    assert alert_hold.alert_state == AlertState.CRITICAL
    assert "Hysteresis lock" in alert_hold.trigger_reason

    # Drop to 0.65 (below 0.70): De-escalates to WARNING
    alert_drop = clean_engine.evaluate_village(v_id, v_name, coords, 0.65, 0.40, dummy_factors)
    assert alert_drop.alert_state == AlertState.WARNING

    # Drop to 0.40 (below 0.50): De-escalates from WARNING to WATCH
    alert_watch = clean_engine.evaluate_village(v_id, v_name, coords, 0.40, 0.10, dummy_factors)
    assert alert_watch.alert_state == AlertState.WATCH

    # Drop to 0.20 (below 0.25): De-escalates from WATCH to RECOVERY
    alert_rec = clean_engine.evaluate_village(v_id, v_name, coords, 0.20, 0.10, dummy_factors)
    assert alert_rec.alert_state == AlertState.RECOVERY

    # Drop to 0.10 (below 0.15): Returns to NORMAL
    alert_norm = clean_engine.evaluate_village(v_id, v_name, coords, 0.10, 0.05, dummy_factors)
    assert alert_norm.alert_state == AlertState.NORMAL


def test_cooldown_suppression(clean_engine, dummy_factors):
    v_id = "V_TEST_COOL"
    v_name = "Mundakkai Valley"
    coords = {"lat": 11.54, "lon": 76.14}

    # Initial escalation to WARNING: dispatches email
    alert1 = clean_engine.evaluate_village(v_id, v_name, coords, 0.65, 0.30, dummy_factors)
    assert alert1.alert_state == AlertState.WARNING
    assert alert1.email_status in [EmailStatus.SIMULATED, EmailStatus.SENT]

    # Immediate second evaluation at 0.66 (still WARNING): should be SUPPRESSED_COOLDOWN
    alert2 = clean_engine.evaluate_village(v_id, v_name, coords, 0.66, 0.30, dummy_factors)
    assert alert2.alert_state == AlertState.WARNING
    assert alert2.email_status == EmailStatus.SUPPRESSED_COOLDOWN

    # Escalation to CRITICAL overrides cooldown immediately!
    alert3 = clean_engine.evaluate_village(v_id, v_name, coords, 0.85, 0.30, dummy_factors)
    assert alert3.alert_state == AlertState.CRITICAL
    assert alert3.email_status in [EmailStatus.SIMULATED, EmailStatus.SENT]
