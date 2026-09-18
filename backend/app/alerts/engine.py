"""
Stateful Alert Engine for TerraSharp (SH-304).
Implements state transitions across NORMAL -> WATCH -> WARNING -> CRITICAL -> RECOVERY.
Includes:
- Hysteresis (asymmetric thresholds to prevent alert chatter/oscillation)
- Persistence (consecutive cycle confirmation for non-emergency changes)
- Cooldown windows to avoid email/SMS storming
- Deduplication and escalation/de-escalation tracking
- Comprehensive audit history of all state transitions
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from backend.app.config import settings
from backend.app.models.domain import AlertState, RiskLevel, HazardType, ProvenanceTag, EmailStatus
from backend.app.models.schemas import AlertItem, AlertTransitionItem, ContributingFactors
from backend.app.scoring.classifier import classify_risk_score
from backend.app.alerts.email_service import email_service

logger = logging.getLogger(__name__)


# Hysteresis Thresholds:
# Escalation requires crossing the higher threshold.
# De-escalation requires falling below the lower threshold (deadband = 0.10).
ESCALATION_THRESHOLDS = {
    AlertState.WATCH: 0.35,
    AlertState.WARNING: 0.60,
    AlertState.CRITICAL: 0.80,
}

DE_ESCALATION_THRESHOLDS = {
    AlertState.CRITICAL: 0.70,   # Drop below 0.70 to de-escalate from CRITICAL to WARNING
    AlertState.WARNING: 0.50,    # Drop below 0.50 to de-escalate from WARNING to WATCH
    AlertState.WATCH: 0.25,      # Drop below 0.25 to enter RECOVERY
    AlertState.RECOVERY: 0.15,   # Drop below 0.15 to return to NORMAL
}


def determine_alert_state(risk_score: float) -> AlertState:
    """Stateless classification helper for backward compatibility."""
    if risk_score < 0.25:
        return AlertState.NORMAL
    elif risk_score < 0.50:
        return AlertState.WATCH
    elif risk_score < 0.75:
        return AlertState.WARNING
    else:
        return AlertState.CRITICAL



class VillageStateTracker:
    def __init__(self, village_id: str, village_name: str, coordinates: Dict[str, float]):
        self.village_id = village_id
        self.village_name = village_name
        self.coordinates = coordinates
        self.current_state: AlertState = AlertState.NORMAL
        self.previous_state: AlertState = AlertState.NORMAL
        self.candidate_state: Optional[AlertState] = None
        self.consecutive_in_candidate: int = 0
        self.last_updated: datetime = datetime.now(timezone.utc)
        self.last_dispatched_at: Optional[datetime] = None
        self.last_dispatched_severity: Optional[AlertState] = None
        self.last_risk_score: float = 0.0
        self.last_factors: Optional[ContributingFactors] = None
        self.last_action: str = ""
        self.last_email_status: Optional[EmailStatus] = None


class StatefulAlertEngine:
    def __init__(self):
        self.trackers: Dict[str, VillageStateTracker] = {}
        self.transition_history: List[AlertTransitionItem] = []

    def _get_or_create_tracker(
        self, village_id: str, village_name: str, coordinates: Dict[str, float]
    ) -> VillageStateTracker:
        if village_id not in self.trackers:
            self.trackers[village_id] = VillageStateTracker(village_id, village_name, coordinates)
        return self.trackers[village_id]

    def _determine_target_state_with_hysteresis(
        self, current_state: AlertState, risk_score: float
    ) -> Tuple[AlertState, str]:
        """
        Determines target state applying hysteresis rules against current state.
        Returns (target_state, reason_description).
        """
        # 1. Check for Critical Escalation
        if risk_score >= ESCALATION_THRESHOLDS[AlertState.CRITICAL]:
            return AlertState.CRITICAL, f"Risk score ({risk_score:.2f}) exceeded Critical threshold (0.80)"

        # 2. If currently in CRITICAL:
        if current_state == AlertState.CRITICAL:
            if risk_score < DE_ESCALATION_THRESHOLDS[AlertState.CRITICAL]:
                return AlertState.WARNING, f"Risk score ({risk_score:.2f}) dropped below Critical de-escalation floor (0.70)"
            return AlertState.CRITICAL, f"Hysteresis lock: Risk ({risk_score:.2f}) remains within Critical band (>= 0.70)"

        # 3. Check for Warning Escalation:
        if risk_score >= ESCALATION_THRESHOLDS[AlertState.WARNING]:
            return AlertState.WARNING, f"Risk score ({risk_score:.2f}) exceeded Warning threshold (0.60)"

        # 4. If currently in WARNING:
        if current_state == AlertState.WARNING:
            if risk_score < DE_ESCALATION_THRESHOLDS[AlertState.WARNING]:
                return AlertState.WATCH, f"Risk score ({risk_score:.2f}) dropped below Warning de-escalation floor (0.50)"
            return AlertState.WARNING, f"Hysteresis lock: Risk ({risk_score:.2f}) remains within Warning band (>= 0.50)"

        # 5. Check for Watch Escalation:
        if risk_score >= ESCALATION_THRESHOLDS[AlertState.WATCH]:
            return AlertState.WATCH, f"Risk score ({risk_score:.2f}) exceeded Watch threshold (0.35)"

        # 6. If currently in WATCH:
        if current_state == AlertState.WATCH:
            if risk_score < DE_ESCALATION_THRESHOLDS[AlertState.WATCH]:
                return AlertState.RECOVERY, f"Risk score ({risk_score:.2f}) dropped below Watch floor (0.25); entering Recovery phase"
            return AlertState.WATCH, f"Hysteresis lock: Risk ({risk_score:.2f}) remains within Watch band (>= 0.25)"

        # 7. If currently in RECOVERY:
        if current_state == AlertState.RECOVERY:
            if risk_score < DE_ESCALATION_THRESHOLDS[AlertState.RECOVERY]:
                return AlertState.NORMAL, f"Risk score ({risk_score:.2f}) fully stabilized below 0.15; returning to Normal"
            return AlertState.RECOVERY, f"Residual recovery monitoring: Risk ({risk_score:.2f}) between 0.15 and 0.25"

        # 8. Baseline Normal
        return AlertState.NORMAL, f"Risk score ({risk_score:.2f}) is within Normal baseline (< 0.35)"

    def get_recommended_action(self, hazard_type: HazardType, alert_state: AlertState) -> str:
        actions = {
            (HazardType.LANDSLIDE, AlertState.NORMAL): (
                "Standard seasonal vigilance. Routine inspection of roadside drainage culverts."
            ),
            (HazardType.LANDSLIDE, AlertState.WATCH): (
                "Advisory: Elevated slope saturation. Inspect retaining structures, clear hillside weep holes, "
                "and alert tea plantation and ghat corridor residents."
            ),
            (HazardType.LANDSLIDE, AlertState.WARNING): (
                "EMERGENCY WARNING: Severe slope failure probability. Restrict traffic on steep ghat roads. "
                "Pre-position SDRF rescue units and prepare community relief shelters."
            ),
            (HazardType.LANDSLIDE, AlertState.CRITICAL): (
                "MANDATORY EVACUATION DISPATCH: Catastrophic debris flow imminent. Immediately evacuate all "
                "households within downslope runout fans. Cease all occupancy on slopes >25°."
            ),
            (HazardType.LANDSLIDE, AlertState.RECOVERY): (
                "Post-Event Recovery & Inspection: Rainfall subsided below threshold. Structural civil engineers "
                "must certify slope toes and foundations before allowing repopulation."
            ),
            (HazardType.FLASH_FLOOD, AlertState.NORMAL): "Standard hydrologic monitoring.",
            (HazardType.FLASH_FLOOD, AlertState.WATCH): "Monitor stream headwaters and culverts. Warn low-lying riverbank settlements.",
            (HazardType.FLASH_FLOOD, AlertState.WARNING): "Surge runoff alert. Evacuate riverbeds, suspend bridge crossings, and open diversion spillways.",
            (HazardType.FLASH_FLOOD, AlertState.CRITICAL): "FLASH FLOOD EMERGENCY: Evacuate valley bottoms immediately to higher ground.",
            (HazardType.FLASH_FLOOD, AlertState.RECOVERY): "Runoff surge receding. Inspect inundated bridge abutments and water quality before return.",
            (HazardType.MULTI_HAZARD, AlertState.CRITICAL): (
                "COMBINED MULTI-HAZARD DISASTER: Simultaneous slope debris flow and riverine flash flood surge. "
                "Execute full emergency evacuation protocol."
            ),
        }
        return actions.get(
            (hazard_type, alert_state),
            "Execute local district disaster management plan according to standard operating procedures."
        )

    def evaluate_village(
        self,
        village_id: str,
        village_name: str,
        coordinates: Dict[str, float],
        landslide_risk: float,
        flash_flood_risk: float,
        factors: ContributingFactors,
        lead_time_hours: Optional[float] = None,
        data_completeness: float = 1.0,
        data_freshness: str = "FRESH",
    ) -> AlertItem:
        """
        Statefully evaluates a village, managing hysteresis, persistence, cooldown,
        deduplication, and real email notification dispatch.
        """
        now = datetime.now(timezone.utc)
        tracker = self._get_or_create_tracker(village_id, village_name, coordinates)

        # 1. Determine dominant hazard & peak score
        if landslide_risk >= 0.50 and flash_flood_risk >= 0.50:
            hazard = HazardType.MULTI_HAZARD
            primary_score = max(landslide_risk, flash_flood_risk)
        elif landslide_risk >= flash_flood_risk:
            hazard = HazardType.LANDSLIDE
            primary_score = landslide_risk
        else:
            hazard = HazardType.FLASH_FLOOD
            primary_score = flash_flood_risk

        # 2. Determine target state using hysteresis
        target_state, transition_reason = self._determine_target_state_with_hysteresis(
            tracker.current_state, primary_score
        )

        # 3. Apply Persistence Logic
        # Immediate escalation for emergency risks (score >= 0.85)
        # Otherwise requires candidate confirmation cycles
        state_to_commit = tracker.current_state
        if target_state != tracker.current_state:
            if primary_score >= 0.85 or target_state == AlertState.CRITICAL:
                # Emergency override: escalate immediately
                state_to_commit = target_state
                tracker.consecutive_in_candidate = 1
                tracker.candidate_state = target_state
            elif tracker.candidate_state == target_state:
                tracker.consecutive_in_candidate += 1
                if tracker.consecutive_in_candidate >= settings.alert_persistence_cycles:
                    state_to_commit = target_state
            else:
                tracker.candidate_state = target_state
                tracker.consecutive_in_candidate = 1
                # If persistence cycles > 1, hold previous state
                if settings.alert_persistence_cycles <= 1:
                    state_to_commit = target_state
        else:
            tracker.candidate_state = None
            tracker.consecutive_in_candidate = 0

        # Check if actual state transition occurred
        transition_occurred = state_to_commit != tracker.current_state
        from_state = tracker.current_state

        if transition_occurred:
            tracker.previous_state = tracker.current_state
            tracker.current_state = state_to_commit
            logger.info(f"State transition for {village_name}: {from_state.value} -> {state_to_commit.value} ({transition_reason})")

        tracker.last_risk_score = primary_score
        tracker.last_updated = now
        action = self.get_recommended_action(hazard, tracker.current_state)
        tracker.last_action = action
        tracker.last_factors = factors

        # 4. Manage Email Dispatch & Cooldown
        email_status: Optional[EmailStatus] = None
        should_send_email = False
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

        if tracker.current_state in [AlertState.WARNING, AlertState.CRITICAL]:
            # Trigger conditions:
            # a) Just escalated to WARNING or CRITICAL
            # b) Escalated within warning levels (WARNING -> CRITICAL)
            # c) Cooldown expired and risk still acute
            is_escalation = transition_occurred and (
                (tracker.current_state == AlertState.CRITICAL and from_state != AlertState.CRITICAL) or
                (tracker.current_state == AlertState.WARNING and from_state not in [AlertState.WARNING, AlertState.CRITICAL])
            )

            cooldown_expired = True
            if tracker.last_dispatched_at:
                elapsed_sec = (now - tracker.last_dispatched_at).total_seconds()
                cooldown_expired = elapsed_sec >= settings.alert_cooldown_seconds

            if is_escalation:
                should_send_email = True
            elif cooldown_expired and tracker.current_state in [AlertState.WARNING, AlertState.CRITICAL]:
                should_send_email = True
            else:
                email_status = EmailStatus.SUPPRESSED_COOLDOWN

        if should_send_email and settings.alert_email_enabled:
            dispatches = email_service.dispatch_alert(
                alert_id=alert_id,
                location_name=village_name,
                coordinates=coordinates,
                hazard_type=hazard,
                alert_state=tracker.current_state,
                risk_score=primary_score,
                factors=factors,
                estimated_lead_time_hours=lead_time_hours,
                recommended_action=action,
                confidence_score=data_completeness,
                data_freshness=data_freshness,
            )
            if dispatches:
                email_status = dispatches[0].status
                tracker.last_dispatched_at = now
                tracker.last_dispatched_severity = tracker.current_state

        tracker.last_email_status = email_status

        # 5. Record Transition Event if State Changed
        if transition_occurred:
            transition_item = AlertTransitionItem(
                transition_id=f"TRN-{uuid.uuid4().hex[:8].upper()}",
                village_id=village_id,
                location_name=village_name,
                from_state=from_state,
                to_state=tracker.current_state,
                risk_score=round(primary_score, 3),
                hazard_type=hazard,
                trigger_reason=transition_reason,
                timestamp=now,
                email_status=email_status or EmailStatus.SIMULATED,
                recipients_count=len(settings.alert_recipient_emails),
                data_freshness=data_freshness,
            )
            self.transition_history.insert(0, transition_item)
            # Keep history bounded
            if len(self.transition_history) > 200:
                self.transition_history.pop()

        provenance_dict = {
            "risk_model": ProvenanceTag.MODELLED,
            "soil_layer": ProvenanceTag.PROXY,
            "rainfall_layer": ProvenanceTag.OBSERVED,
            "terrain_layer": ProvenanceTag.DERIVED,
        }

        return AlertItem(
            alert_id=alert_id,
            location_name=village_name,
            coordinates=coordinates,
            hazard_type=hazard,
            alert_state=tracker.current_state,
            risk_score=round(primary_score, 3),
            risk_class=classify_risk_score(primary_score),
            estimated_lead_time_hours=lead_time_hours,
            confidence_score=round(data_completeness, 2),
            contributing_factors=factors,
            recommended_action=action,
            simulated=not email_service.is_smtp_configured(),
            timestamp=now,
            data_provenance=provenance_dict,
            email_status=email_status,
            trigger_reason=transition_reason,
            persistence_count=tracker.consecutive_in_candidate,
            data_freshness=data_freshness,
        )

    def get_history(self, limit: int = 100) -> List[AlertTransitionItem]:
        """Returns chronological list of alert state transitions."""
        return self.transition_history[:limit]

    # Backward-compatibility alias
    generate_village_alert = evaluate_village

    def reset(self):
        """Clears all state trackers for clean test runs."""
        self.trackers.clear()
        self.transition_history.clear()


# Global Singleton Alert Engine
alert_engine = StatefulAlertEngine()
AlertEngine = StatefulAlertEngine  # Backward-compatibility alias


def get_recommended_action(hazard_type: HazardType, alert_state: AlertState) -> str:
    """Module-level helper for recommended mitigation action."""
    return alert_engine.get_recommended_action(hazard_type, alert_state)

