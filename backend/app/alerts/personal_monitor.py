"""
Personal Dangerzone Monitor for TerraSharp.
Monitors user coordinates against authentic physical hazard data, classifies danger zones,
enforces stateful hysteresis and anti-spam cooldowns, and dispatches real email notifications.

Danger Zone Tiers:
  - RED ZONE (High Alert): Risk >= 0.60 or Caine Threshold Breached (I/Ic >= 1.0).
  - YELLOW ZONE (Normal Alert): 0.35 <= Risk < 0.60.
  - GREEN ZONE (Safe): Risk < 0.35 (No alarm email dispatched).
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple

from backend.app.ingestion.live_point_fetcher import live_point_fetcher
from backend.app.alerts.email_service import email_service
from backend.app.models.domain import AlertState, HazardType, EmailStatus
from backend.app.models.schemas import EmailDispatchRecord

logger = logging.getLogger(__name__)

# Danger Zone Definitions
ZONE_RED = "RED"       # High Alert
ZONE_YELLOW = "YELLOW" # Normal Alert
ZONE_GREEN = "GREEN"   # Safe


class UserZoneState:
    def __init__(self, email: str):
        self.email = email
        self.last_zone: str = ZONE_GREEN
        self.last_lat: float = 0.0
        self.last_lon: float = 0.0
        self.last_risk: float = 0.0
        self.last_dispatched_at: Optional[datetime] = None
        self.last_dispatched_zone: Optional[str] = None
        self.evaluation_count: int = 0


class PersonalDangerzoneMonitor:
    def __init__(self, cooldown_seconds: int = 1800):
        self.cooldown_seconds = cooldown_seconds
        self._user_states: Dict[str, UserZoneState] = {}
        self.activity_log: List[Dict[str, Any]] = []

    def _get_or_create_state(self, email: str) -> UserZoneState:
        clean_email = email.strip().lower()
        if clean_email not in self._user_states:
            self._user_states[clean_email] = UserZoneState(clean_email)
        return self._user_states[clean_email]

    def evaluate_user_location(
        self,
        email: str,
        lat: float,
        lon: float,
        location_name: Optional[str] = None,
        force_dispatch: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluates real-time hazard data for (lat, lon) and manages email alerting.
        Zero-Fake Guarantee: Driven strictly by live SRTM DEM slope, Open-Meteo precipitation,
        and Caine threshold physics.
        """
        clean_email = email.strip().lower()
        now = datetime.now(timezone.utc)
        state = self._get_or_create_state(clean_email)
        state.evaluation_count += 1

        # 1. Fetch authentic multi-factor point prediction
        point_data = live_point_fetcher.evaluate_live_pinpoint(lat, lon)

        ls_risk = point_data["landslide_risk"]
        ff_risk = point_data["flash_flood_risk"]
        peak_risk = max(ls_risk, ff_risk)

        caine = point_data.get("caine_threshold", {})
        caine_ratio = caine.get("intensity_ratio", 0.0)
        caine_breached = caine_ratio >= 1.0

        # 2. Danger Zone Classification
        # RED ZONE (High Alert): High risk or physical threshold breach
        if peak_risk >= 0.60 or caine_breached:
            current_zone = ZONE_RED
            zone_title = "HIGH ALERT (Red Zone)"
            hazard_level = "CRITICAL / HIGH DANGER"
        # YELLOW ZONE (Normal Alert): Moderate risk
        elif peak_risk >= 0.35:
            current_zone = ZONE_YELLOW
            zone_title = "NORMAL ALERT (Yellow Zone)"
            hazard_level = "MODERATE HAZARD / ELEVATED WATCH"
        # GREEN ZONE (Safe)
        else:
            current_zone = ZONE_GREEN
            zone_title = "SAFE (Green Zone)"
            hazard_level = "NORMAL / LOW HAZARD"

        # 3. Email Dispatch Decision (Cooldown & Escalation Rules)
        should_send = False
        dispatch_reason = ""

        if force_dispatch:
            should_send = True
            dispatch_reason = "Manual on-demand verification requested."
        elif current_zone == ZONE_GREEN:
            should_send = False
            dispatch_reason = "Location is within safe bounds (Green Zone). No email required."
        elif current_zone == ZONE_RED:
            # Escalation from Green or Yellow -> Red: IMMEDIATE alert
            if state.last_dispatched_zone != ZONE_RED:
                should_send = True
                dispatch_reason = f"ESCALATION: Entered High Alert Red Zone (Risk: {peak_risk:.2f})."
            else:
                # Still in Red: Check cooldown window
                if state.last_dispatched_at is None or (now - state.last_dispatched_at) >= timedelta(seconds=self.cooldown_seconds):
                    should_send = True
                    dispatch_reason = f"Cooldown window ({self.cooldown_seconds // 60}m) expired while in Red Zone."
                else:
                    cooldown_remaining = int(self.cooldown_seconds - (now - state.last_dispatched_at).total_seconds())
                    dispatch_reason = f"Red Zone active. Re-notification suppressed by cooldown ({cooldown_remaining}s remaining)."
        elif current_zone == ZONE_YELLOW:
            # Entry into Yellow from Green
            if state.last_dispatched_zone is None or state.last_dispatched_zone == ZONE_GREEN:
                should_send = True
                dispatch_reason = f"Entered Normal Alert Yellow Zone (Risk: {peak_risk:.2f})."
            elif state.last_dispatched_zone == ZONE_RED:
                # De-escalated to Yellow: inform user
                should_send = True
                dispatch_reason = f"DE-ESCALATION: Risk decreased from Red Zone to Yellow Zone (Risk: {peak_risk:.2f})."
            else:
                # Still in Yellow: Check cooldown
                if state.last_dispatched_at is None or (now - state.last_dispatched_at) >= timedelta(seconds=self.cooldown_seconds):
                    should_send = True
                    dispatch_reason = f"Cooldown window ({self.cooldown_seconds // 60}m) expired while in Yellow Zone."
                else:
                    cooldown_remaining = int(self.cooldown_seconds - (now - state.last_dispatched_at).total_seconds())
                    dispatch_reason = f"Yellow Zone active. Re-notification suppressed by cooldown ({cooldown_remaining}s remaining)."

        # 4. Dispatch Email if needed
        email_record: Optional[EmailDispatchRecord] = None
        email_status = "NOT_TRIGGERED"
        loc_display = location_name or f"Coordinates ({lat:.4f}°N, {lon:.4f}°E)"

        if should_send:
            records = email_service.dispatch_dangerzone_alert(
                recipient_email=clean_email,
                zone=current_zone,
                lat=lat,
                lon=lon,
                location_name=loc_display,
                point_data=point_data,
                dispatch_reason=dispatch_reason,
                is_test=force_dispatch,
            )
            if records:
                email_record = records[0]
                email_status = email_record.status.value
                state.last_dispatched_at = now
                state.last_dispatched_zone = current_zone

        # Update user tracker
        state.last_zone = current_zone
        state.last_lat = lat
        state.last_lon = lon
        state.last_risk = peak_risk

        summary = {
            "email": clean_email,
            "latitude": lat,
            "longitude": lon,
            "location_name": loc_display,
            "zone": current_zone,
            "zone_title": zone_title,
            "hazard_level": hazard_level,
            "peak_risk": round(peak_risk, 3),
            "landslide_risk": ls_risk,
            "flash_flood_risk": ff_risk,
            "slope_deg": point_data["slope_deg"],
            "slope_pct": point_data.get("slope_pct", round(point_data["slope_deg"] * 1.77, 1)),
            "elevation_m": point_data["elevation_m"],
            "rainfall_24h_mm": point_data["rainfall_24h_mm"],
            "rainfall_15d_mm": point_data["rainfall_15d_mm"],
            "soil_saturation_pct": point_data["soil_saturation_pct"],
            "caine_intensity_ratio": caine_ratio,
            "false_alarm_suppressed": point_data["false_alarm_mitigation"]["suppressed"],
            "email_dispatched": should_send,
            "email_status": email_status,
            "dispatch_reason": dispatch_reason,
            "evaluated_at": now.isoformat(),
            "smtp_configured": email_service.is_smtp_configured(),
        }

        # Keep session log
        self.activity_log.insert(0, summary)
        if len(self.activity_log) > 100:
            self.activity_log.pop()

        return summary

    def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.activity_log[:limit]


# Global singleton
personal_monitor = PersonalDangerzoneMonitor(cooldown_seconds=1800)
