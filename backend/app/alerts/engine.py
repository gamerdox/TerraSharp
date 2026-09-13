"""
Alert Engine Module for SH-304.
Generates tiered alerts (NORMAL, WATCH, WARNING, CRITICAL) with actionable mitigation protocols.
All alert dispatches are strictly simulated for research and operational prototype demonstration.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from backend.app.config import settings
from backend.app.models.domain import AlertState, RiskLevel, HazardType, ProvenanceTag
from backend.app.models.schemas import AlertItem, ContributingFactors
from backend.app.scoring.classifier import classify_risk_score


def determine_alert_state(risk_score: float) -> AlertState:
    if risk_score < 0.25:
        return AlertState.NORMAL
    elif risk_score < 0.50:
        return AlertState.WATCH
    elif risk_score < 0.75:
        return AlertState.WARNING
    else:
        return AlertState.CRITICAL


def get_recommended_action(hazard_type: HazardType, alert_state: AlertState) -> str:
    actions = {
        (HazardType.LANDSLIDE, AlertState.NORMAL): (
            "No immediate evacuation necessary. Maintain standard weather monitoring and drainage checks."
        ),
        (HazardType.LANDSLIDE, AlertState.WATCH): (
            "Notice of elevated slope hazard. Inspect retaining walls and hillside drainage ditches for blockages. "
            "Advise slope-dwelling residents to prepare emergency kits."
        ),
        (HazardType.LANDSLIDE, AlertState.WARNING): (
            "High slope instability detected. Restrict heavy vehicular traffic on ghat corridors. "
            "Stage disaster response teams (NDRF/SDRF) and prepare community relief centers."
        ),
        (HazardType.LANDSLIDE, AlertState.CRITICAL): (
            "[SIMULATED EVACUATION DISPATCH] CRITICAL: Imminent slope failure risk. "
            "Order immediate evacuation of all households in downslope runout zones to pre-identified shelters. "
            "Avoid night occupancy of structures on slopes >30°."
        ),
        (HazardType.FLASH_FLOOD, AlertState.NORMAL): (
            "Normal riverine baseflow. Standard monitoring."
        ),
        (HazardType.FLASH_FLOOD, AlertState.WATCH): (
            "Drainage concentration alert. Warn riverbank settlements, low bridges, and culvert crossings."
        ),
        (HazardType.FLASH_FLOOD, AlertState.WARNING): (
            "Rapid runoff surge warning. Suspend riverbed activities. Prepare upstream gates and warn floodplains."
        ),
        (HazardType.FLASH_FLOOD, AlertState.CRITICAL): (
            "[SIMULATED EVACUATION DISPATCH] CRITICAL: Flash flood surge imminent. "
            "Evacuate valley bottoms and riverbanks immediately to higher elevation ground."
        ),
        (HazardType.MULTI_HAZARD, AlertState.CRITICAL): (
            "[SIMULATED EVACUATION DISPATCH] CRITICAL MULTI-HAZARD: Combined debris flow and flash flood surge. "
            "Execute full community evacuation protocol to high-ground stable relief shelters."
        ),
    }
    return actions.get(
        (hazard_type, alert_state),
        "Execute local district disaster management plan according to standard operating procedures.",
    )


class AlertEngine:
    def __init__(self, model_version: str = "1.0.0", config_version: str = "1.0.0"):
        self.model_version = model_version
        self.config_version = config_version

    def generate_village_alert(
        self,
        village_id: str,
        village_name: str,
        coordinates: Dict[str, float],
        landslide_risk: float,
        flash_flood_risk: float,
        factors: ContributingFactors,
        lead_time_hours: Optional[float] = None,
        data_completeness: float = 1.0,
    ) -> AlertItem:
        # Determine dominant hazard
        if landslide_risk >= 0.50 and flash_flood_risk >= 0.50:
            hazard = HazardType.MULTI_HAZARD
            primary_score = max(landslide_risk, flash_flood_risk)
        elif landslide_risk >= flash_flood_risk:
            hazard = HazardType.LANDSLIDE
            primary_score = landslide_risk
        else:
            hazard = HazardType.FLASH_FLOOD
            primary_score = flash_flood_risk

        alert_state = determine_alert_state(primary_score)
        risk_class = classify_risk_score(primary_score)
        action = get_recommended_action(hazard, alert_state)

        provenance_dict = {
            "risk_model": ProvenanceTag.MODELLED,
            "soil_layer": ProvenanceTag.PROXY,
            "rainfall_layer": ProvenanceTag.DEMO if settings.mode == "demo" else ProvenanceTag.OBSERVED,
            "terrain_layer": ProvenanceTag.DERIVED,
        }

        return AlertItem(
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            location_name=village_name,
            coordinates=coordinates,
            hazard_type=hazard,
            alert_state=alert_state,
            risk_score=round(primary_score, 3),
            risk_class=risk_class,
            estimated_lead_time_hours=lead_time_hours,
            confidence_score=round(data_completeness, 2),
            contributing_factors=factors,
            recommended_action=action,
            simulated=True,
            timestamp=datetime.now(timezone.utc),
            data_provenance=provenance_dict,
        )
