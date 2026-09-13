"""
Unit tests for Scoring & Classification.
"""
import numpy as np
import pytest
from backend.app.config import settings
from backend.app.scoring.weighted_index import LandslideRiskScorer
from backend.app.scoring.classifier import classify_risk_score
from backend.app.models.domain import RiskLevel


def test_classifier_thresholds():
    assert classify_risk_score(0.10) == RiskLevel.LOW
    assert classify_risk_score(0.35) == RiskLevel.MODERATE
    assert classify_risk_score(0.65) == RiskLevel.HIGH
    assert classify_risk_score(0.85) == RiskLevel.VERY_HIGH


def test_weighted_index_bounds_and_weights():
    scorer = LandslideRiskScorer(settings.risk_weights)

    rf = np.full((10, 10), 0.8, dtype=np.float32)
    sl = np.full((10, 10), 0.7, dtype=np.float32)
    so = np.full((10, 10), 0.9, dtype=np.float32)
    hi = np.full((10, 10), 0.5, dtype=np.float32)

    risk_grid, classes_grid, meta = scorer.compute_risk_grid(rf, sl, so, hi)

    expected = 0.35 * 0.8 + 0.30 * 0.7 + 0.20 * 0.9 + 0.15 * 0.5
    assert np.allclose(risk_grid, expected, atol=1e-3)
    assert np.all(risk_grid >= 0.0) and np.all(risk_grid <= 1.0)


def test_explain_point_risk():
    scorer = LandslideRiskScorer(settings.risk_weights)
    factors = scorer.explain_point_risk(0.9, 0.2, 0.1, 0.1)

    assert factors.dominant_factor == "Heavy Rainfall"
    assert "Heavy Rainfall" in factors.explanation
    assert factors.weights_used["w_rainfall"] == 0.35
