"""
Risk Classifier Module.
Classifies normalized continuous risk scores [0, 1] into standardized tiers.
"""
from typing import Tuple, Union
import numpy as np
from backend.app.models.domain import RiskLevel


def classify_risk_score(score: Union[float, np.ndarray]) -> Union[RiskLevel, np.ndarray]:
    """
    Classifies a scalar score or numpy array into RiskLevel:
      [0.00, 0.25) -> LOW
      [0.25, 0.50) -> MODERATE
      [0.50, 0.75) -> HIGH
      [0.75, 1.00] -> VERY_HIGH
    """
    if isinstance(score, (float, int, np.floating)):
        val = float(score)
        if val < 0.25:
            return RiskLevel.LOW
        elif val < 0.50:
            return RiskLevel.MODERATE
        elif val < 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    # Vectorized for numpy array
    classes = np.full(score.shape, RiskLevel.LOW.value, dtype=object)
    classes[(score >= 0.25) & (score < 0.50)] = RiskLevel.MODERATE.value
    classes[(score >= 0.50) & (score < 0.75)] = RiskLevel.HIGH.value
    classes[score >= 0.75] = RiskLevel.VERY_HIGH.value
    return classes
