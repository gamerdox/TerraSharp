"""
Caine (1980) Empirical Rainfall Intensity-Duration Threshold & Lead-Time Estimator.
Formula:
  I_crit = 14.82 * D^(-0.39)
Strictly adheres to scientific honesty: projects time toward threshold under current trend,
never claiming a guaranteed disaster prediction.
"""
from typing import Dict, Any, Optional, List
import numpy as np

from backend.app.models.domain import ProvenanceTag
from backend.app.models.schemas import LeadTimeEvaluation


def evaluate_caine_lead_time(
    current_intensity_mm_hr: float,
    duration_hours: float = 24.0,
    trend_alpha_mm_hr2: float = 0.5,
    location: Optional[Dict[str, float]] = None,
) -> LeadTimeEvaluation:
    """
    Evaluates the Caine (1980) critical threshold and computes estimated lead time
    under the current rate of rainfall intensification.
    """
    alpha_caine = 14.82
    beta_caine = -0.39
    uncertainty_pct = 0.30

    d_eff = max(duration_hours, 1.0)
    i_crit = alpha_caine * (d_eff ** beta_caine)

    i_curr = max(current_intensity_mm_hr, 0.0)

    if i_curr >= i_crit:
        status = "THRESHOLD_BREACHED"
        lead_time = 0.0
        uncertainty_range = [0.0, 0.0]
    elif trend_alpha_mm_hr2 > 0.01:
        # Time to reach threshold under constant intensification rate
        gap = i_crit - i_curr
        lead_time = round(gap / trend_alpha_mm_hr2, 1)
        lower_bound = max(0.0, round(lead_time * (1.0 - uncertainty_pct), 1))
        upper_bound = round(lead_time * (1.0 + uncertainty_pct), 1)
        uncertainty_range = [lower_bound, upper_bound]
        status = "APPROACHING_THRESHOLD"
    else:
        status = "STABLE_BELOW_THRESHOLD"
        lead_time = None
        uncertainty_range = None

    disclaimer = (
        "CRITICAL SCIENTIFIC DISCLAIMER: Estimated time to threshold under current rainfall trend. "
        "This calculation utilizes the Caine (1980) global empirical reference curve (I = 14.82 * D^-0.39). "
        "It does NOT state that a landslide will definitely occur in X hours, nor does it replace "
        "regional geological early warnings issued by the Geological Survey of India (GSI) or IMD."
    )

    return LeadTimeEvaluation(
        location=location,
        current_intensity_mm_hr=round(i_curr, 2),
        duration_hours=round(d_eff, 1),
        caine_threshold_intensity_mm_hr=round(i_crit, 2),
        rainfall_trend_alpha_mm_hr2=round(trend_alpha_mm_hr2, 4),
        estimated_lead_time_hours=lead_time,
        uncertainty_range_hours=uncertainty_range,
        status=status,
        scientific_disclaimer=disclaimer,
        formula="I_crit = 14.82 * D^(-0.39)",
    )
