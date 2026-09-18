"""
Alert System Endpoints for TerraSharp (SH-304).
Provides active tiered alerts, stateful audit transition history,
real SMTP / simulated email dispatch logs, and on-demand test alert dispatches.
"""
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Query, HTTPException

from backend.app.pipeline import pipeline_state, PipelineOrchestrator
from backend.app.models.domain import AlertState, HazardType, EmailStatus
from backend.app.models.schemas import (
    AlertItem,
    AlertTransitionItem,
    EmailDispatchRecord,
    TestEmailRequest,
    TestEmailResponse,
    ContributingFactors,
)
from backend.app.alerts.engine import alert_engine
from backend.app.alerts.email_service import email_service
from backend.app.alerts.personal_monitor import personal_monitor
from backend.app.config import settings

router = APIRouter(prefix="/alerts", tags=["Alert Engine"])


class DangerzoneMonitorRequest(BaseModel):
    email: str
    lat: float
    lon: float
    location_name: Optional[str] = None
    force_dispatch: bool = False


@router.get("", response_model=List[AlertItem])
def list_active_alerts():
    """
    Returns active alerts for all settlements within the current AOI.
    Stateful evaluation reflects hysteresis, persistence, and cooldown gates.
    """
    if not pipeline_state.alerts:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    return pipeline_state.alerts


@router.get("/history", response_model=List[AlertTransitionItem])
def get_alert_transition_history(limit: int = Query(50, ge=1, le=200)):
    """
    Returns the chronological audit trail of state transitions
    (NORMAL -> WATCH -> WARNING -> CRITICAL -> RECOVERY).
    """
    return alert_engine.get_history(limit=limit)


@router.get("/emails", response_model=List[EmailDispatchRecord])
def get_email_dispatch_log(limit: int = Query(50, ge=1, le=200)):
    """
    Returns the log of emergency email dispatches with delivery status
    (SENT, FAILED, QUEUED, SIMULATED, SUPPRESSED_COOLDOWN).
    """
    return email_service.get_history(limit=limit)


@router.post("/test-email", response_model=TestEmailResponse)
def trigger_test_alert_email(req: TestEmailRequest):
    """
    Dispatches an immediate test early warning alert email to verify
    SMTP configuration, network connectivity, and template formatting.
    """
    recipients = [req.recipient_email] if req.recipient_email else settings.alert_recipient_emails
    if not recipients:
        recipients = ["disaster-response@kerala.gov.in"]

    sample_factors = ContributingFactors(
        rainfall_score=0.88,
        slope_score=0.75,
        soil_proxy_score=0.68,
        history_score=0.50,
        weights_used=settings.risk_weights.get("weights", {}),
        dominant_factor="Continuous Monsoon Deluge (>200mm/24h)",
        explanation="Test alert verification: slope and precipitation thresholds breached.",
    )

    dispatches = email_service.dispatch_alert(
        alert_id=f"TEST-{uuid.uuid4().hex[:6].upper()}" if 'uuid' in dir() else "TEST-VERIFY",
        location_name=req.village_name,
        coordinates={"lat": 11.5524, "lon": 76.1532},
        hazard_type=HazardType.LANDSLIDE,
        alert_state=req.severity,
        risk_score=0.82 if req.severity == AlertState.CRITICAL else 0.68,
        factors=sample_factors,
        estimated_lead_time_hours=2.5,
        recommended_action=alert_engine.get_recommended_action(HazardType.LANDSLIDE, req.severity),
        confidence_score=0.95,
        data_freshness="FRESH",
        recipients=recipients,
        is_test=True,
    )

    first = dispatches[0] if dispatches else None
    status = first.status if first else EmailStatus.FAILED
    msg = (
        f"Real test email successfully sent to {', '.join(recipients)}"
        if status == EmailStatus.SENT
        else f"Simulated test alert recorded (SMTP not configured in .env). Target: {', '.join(recipients)}"
        if status == EmailStatus.SIMULATED
        else f"Failed to send test email: {first.error_message if first else 'Unknown error'}"
    )

    return TestEmailResponse(
        status=status,
        message=msg,
        dispatch_record=first,
    )


@router.post("/evaluate", response_model=List[AlertItem])
def force_re_evaluate_alerts():
    """
    Forces immediate re-evaluation of all settlement risk scores
    against the stateful hysteresis and persistence engine.
    """
    if not pipeline_state.village_summaries:
        PipelineOrchestrator().run(pipeline_state.current_aoi)

    fresh_alerts = []
    for v_sum in pipeline_state.village_summaries:
        factors = ContributingFactors(
            rainfall_score=min(1.0, v_sum.max_landslide_risk * 1.1),
            slope_score=min(1.0, v_sum.max_landslide_risk * 0.9),
            soil_proxy_score=0.60,
            history_score=0.20,
            weights_used=settings.risk_weights.get("weights", {}),
            dominant_factor=v_sum.dominant_factor,
            explanation=f"Evaluated risk {v_sum.max_landslide_risk:.2f}",
        )
        alert = alert_engine.evaluate_village(
            village_id=v_sum.village_id,
            village_name=v_sum.name,
            coordinates=v_sum.coordinates_center,
            landslide_risk=v_sum.max_landslide_risk,
            flash_flood_risk=v_sum.max_flash_flood_risk,
            factors=factors,
            lead_time_hours=pipeline_state.lead_time.estimated_lead_time_hours if pipeline_state.lead_time else None,
            data_completeness=1.0,
            data_freshness="FRESH",
        )
        fresh_alerts.append(alert)

    pipeline_state.alerts = fresh_alerts
    return fresh_alerts


@router.post("/monitor-zone")
def monitor_user_dangerzone(req: DangerzoneMonitorRequest):
    """
    Evaluates real-time danger zone for user coordinates and dispatches
    real email alerts if in Red Zone (High Alert) or Yellow Zone (Normal Alert).
    Driven strictly by authentic SRTM DEM slope, Open-Meteo rainfall, and Caine threshold physics.
    """
    if not req.email or "@" not in req.email or "." not in req.email:
        raise HTTPException(status_code=400, detail="A valid email address is required.")
    if req.lat < -90.0 or req.lat > 90.0 or req.lon < -180.0 or req.lon > 180.0:
        raise HTTPException(status_code=400, detail="Invalid coordinates.")

    try:
        return personal_monitor.evaluate_user_location(
            email=req.email,
            lat=req.lat,
            lon=req.lon,
            location_name=req.location_name,
            force_dispatch=req.force_dispatch,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dangerzone evaluation error: {str(e)}")


@router.get("/monitor-zone/activity")
def get_monitor_activity():
    """Returns recent personal dangerzone activity log."""
    return personal_monitor.get_recent_activity()


@router.get("/smtp-status")
def get_smtp_status():
    """Returns SMTP configuration diagnostic status."""
    is_ready = email_service.is_smtp_configured()
    return {
        "configured": is_ready,
        "smtp_host": settings.smtp_host or None,
        "smtp_port": settings.smtp_port,
        "smtp_from": settings.smtp_from or None,
        "smtp_use_tls": settings.smtp_use_tls,
        "mode": "REAL_SMTP" if is_ready else "SIMULATED_TEST_MODE",
        "notice": (
            "Ready to deliver real emails to inboxes via SMTP TLS."
            if is_ready
            else "SMTP not configured in backend .env. Emails are recorded honestly as SIMULATED. Set SMTP_HOST/USER/PASSWORD in .env for real inbox delivery."
        ),
    }

