from unittest.mock import patch, MagicMock
import pytest
from backend.app.alerts.email_service import EmailService
from backend.app.models.domain import AlertState, HazardType, EmailStatus
from backend.app.models.schemas import ContributingFactors


@pytest.fixture
def email_svc():
    svc = EmailService()
    svc.dispatch_records.clear()
    return svc


def test_format_email_content(email_svc):
    factors = ContributingFactors(
        rainfall_score=0.85,
        slope_score=0.70,
        soil_proxy_score=0.60,
        history_score=0.30,
        weights_used={},
        dominant_factor="Continuous Monsoon Deluge",
        explanation="Testing format content",
    )
    subject, plain_text, html_content = email_svc.format_email_content(
        alert_id="ALT-1234",
        location_name="Mundakkai East",
        coordinates={"lat": 11.53, "lon": 76.13},
        hazard_type=HazardType.LANDSLIDE,
        alert_state=AlertState.CRITICAL,
        risk_score=0.85,
        factors=factors,
        estimated_lead_time_hours=1.8,
        recommended_action="Immediate evacuation of low-lying runout zone.",
        confidence_score=0.92,
        data_freshness="FRESH",
    )

    assert "CRITICAL" in subject
    assert "Mundakkai East" in subject
    assert "ALT-1234" in plain_text
    assert "1.8 Hours" in plain_text
    assert "Continuous Monsoon Deluge" in plain_text
    assert "CRITICAL" in html_content
    assert "#dc2626" in html_content


def test_simulated_dispatch_without_smtp(email_svc):
    # When smtp_host is empty, dispatch should honestly record SIMULATED
    with patch("backend.app.alerts.email_service.settings.smtp_host", ""):
        assert not email_svc.is_smtp_configured()
        dispatches = email_svc.dispatch_alert(
            alert_id="ALT-SIM-01",
            location_name="Chooralmala",
            coordinates={"lat": 11.52, "lon": 76.12},
            hazard_type=HazardType.LANDSLIDE,
            alert_state=AlertState.WARNING,
            risk_score=0.68,
            recipients=["test@example.com"],
        )
        assert len(dispatches) == 1
        assert dispatches[0].status == EmailStatus.SIMULATED
        assert dispatches[0].simulated is True
        assert "SMTP not configured" in dispatches[0].error_message


def test_real_smtp_dispatch_mocked(email_svc):
    # When smtp_host is configured, it connects to smtplib.SMTP
    with patch("backend.app.alerts.email_service.settings.smtp_host", "smtp.gmail.com"), \
         patch("backend.app.alerts.email_service.settings.smtp_port", 587), \
         patch("backend.app.alerts.email_service.settings.smtp_user", "test@gmail.com"), \
         patch("backend.app.alerts.email_service.settings.smtp_password", "secret"), \
         patch("smtplib.SMTP") as mock_smtp:

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        assert email_svc.is_smtp_configured()
        dispatches = email_svc.dispatch_alert(
            alert_id="ALT-REAL-01",
            location_name="Vythiri",
            coordinates={"lat": 11.55, "lon": 76.04},
            hazard_type=HazardType.LANDSLIDE,
            alert_state=AlertState.CRITICAL,
            risk_score=0.91,
            recipients=["emergency-response@gov.in"],
        )

        assert len(dispatches) == 1
        assert dispatches[0].status == EmailStatus.SENT
        assert dispatches[0].simulated is False
        assert mock_server.send_message.called


def test_smtp_failure_handling(email_svc):
    with patch("backend.app.alerts.email_service.settings.smtp_host", "smtp.invalid.domain"), \
         patch("backend.app.alerts.email_service.settings.smtp_port", 587), \
         patch("smtplib.SMTP", side_effect=Exception("Connection refused")):

        dispatches = email_svc.dispatch_alert(
            alert_id="ALT-FAIL-01",
            location_name="Puthumala",
            coordinates={"lat": 11.51, "lon": 76.11},
            hazard_type=HazardType.LANDSLIDE,
            alert_state=AlertState.WARNING,
            risk_score=0.72,
            recipients=["test@gov.in"],
        )

        assert len(dispatches) == 1
        assert dispatches[0].status == EmailStatus.FAILED
        assert "Connection refused" in dispatches[0].error_message
