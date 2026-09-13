"""
Weighted Landslide Risk Index Module.
Implements the transparent, explainable formula:
  Risk = w_rainfall * rainfall_score + w_slope * slope_score + w_soil * soil_score + w_history * history_score
Generates human-readable, transparent contributing factor explanations.
"""
from typing import Dict, Any, Tuple
import numpy as np

from backend.app.config import settings
from backend.app.models.domain import RiskLevel, ProvenanceTag
from backend.app.models.schemas import ContributingFactors
from backend.app.scoring.classifier import classify_risk_score


class LandslideRiskScorer:
    def __init__(self, weights_config: Dict[str, Any]):
        weights_data = weights_config.get("landslide_weights", {})
        self.w_rainfall = float(weights_data.get("rainfall", {}).get("weight", 0.35))
        self.w_slope = float(weights_data.get("slope", {}).get("weight", 0.30))
        self.w_soil = float(weights_data.get("soil_saturation_proxy", {}).get("weight", 0.20))
        self.w_history = float(weights_data.get("historical_density", {}).get("weight", 0.15))

        total = self.w_rainfall + self.w_slope + self.w_soil + self.w_history
        # Normalize weights if sum != 1.0
        if abs(total - 1.0) > 1e-4:
            self.w_rainfall /= total
            self.w_slope /= total
            self.w_soil /= total
            self.w_history /= total

        self.version = weights_config.get("version", "1.0.0")
        self.status = weights_config.get("status", "EXPERT_HEURISTIC_UNRESTRICTED")

    def compute_risk_grid(
        self,
        rainfall_score: np.ndarray,
        slope_norm: np.ndarray,
        soil_proxy: np.ndarray,
        history_norm: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Computes the 2D landslide risk grid and categorical classification.
        """
        risk_grid = (
            self.w_rainfall * rainfall_score
            + self.w_slope * slope_norm
            + self.w_soil * soil_proxy
            + self.w_history * history_norm
        )
        risk_grid = np.clip(risk_grid, 0.0, 1.0).astype(np.float32)
        classes_grid = classify_risk_score(risk_grid)

        metadata = {
            "formula": "w_rainfall * rainfall_score + w_slope * slope_score + w_soil * soil_score + w_history * history_score",
            "weights": {
                "rainfall": self.w_rainfall,
                "slope": self.w_slope,
                "soil_saturation_proxy": self.w_soil,
                "historical_density": self.w_history,
            },
            "weight_version": self.version,
            "weight_status": self.status,
            "mean_risk": round(float(np.mean(risk_grid)), 3),
            "max_risk": round(float(np.max(risk_grid)), 3),
            "very_high_cells_count": int(np.sum(risk_grid >= 0.75)),
            "high_cells_count": int(np.sum((risk_grid >= 0.50) & (risk_grid < 0.75))),
            "provenance": ProvenanceTag.MODELLED.value,
        }

        return risk_grid, classes_grid, metadata

    def explain_point_risk(
        self,
        rainfall_val: float,
        slope_val: float,
        soil_val: float,
        history_val: float,
    ) -> ContributingFactors:
        """
        Generates an explainable breakdown of risk for a single point/cell.
        """
        c_rain = self.w_rainfall * rainfall_val
        c_slope = self.w_slope * slope_val
        c_soil = self.w_soil * soil_val
        c_hist = self.w_history * history_val

        contributions = {
            "Heavy Rainfall": c_rain,
            "Steep Slope": c_slope,
            "Soil Saturation (Proxy)": c_soil,
            "Historical Hazard Zone": c_hist,
        }
        dominant_factor = max(contributions, key=contributions.get)

        total_risk = c_rain + c_slope + c_soil + c_hist
        risk_level = classify_risk_score(total_risk)

        explanation = (
            f"Evaluated as {risk_level.value} risk ({total_risk:.2f}). "
            f"The primary hazard driver is {dominant_factor} (contributing {contributions[dominant_factor]:.2f}), "
            f"with rainfall score at {rainfall_val:.2f}, slope at {slope_val:.2f}, "
            f"antecedent soil moisture proxy at {soil_val:.2f}, and historical density at {history_val:.2f}."
        )

        return ContributingFactors(
            rainfall_score=round(rainfall_val, 3),
            slope_score=round(slope_val, 3),
            soil_proxy_score=round(soil_val, 3),
            history_score=round(history_val, 3),
            weights_used={
                "w_rainfall": self.w_rainfall,
                "w_slope": self.w_slope,
                "w_soil": self.w_soil,
                "w_history": self.w_history,
            },
            dominant_factor=dominant_factor,
            explanation=explanation,
        )
