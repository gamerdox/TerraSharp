"""
Flash-Flood Risk Scoring Module.
Combines rainfall intensity, upstream contributing drainage (flow accumulation),
and valley topographic concavity.
Explicitly disclaims 2D hydrodynamic simulation while providing robust geospatial data fusion.
"""
from typing import Dict, Any, Tuple
import numpy as np

from backend.app.models.domain import RiskLevel, ProvenanceTag
from backend.app.scoring.classifier import classify_risk_score


class FlashFloodRiskScorer:
    def __init__(self, weights_config: Dict[str, Any]):
        ff_weights = weights_config.get("flash_flood_weights", {})
        self.w_rainfall = float(ff_weights.get("rainfall", {}).get("weight", 0.50))
        self.w_flow_accum = float(ff_weights.get("flow_accumulation", {}).get("weight", 0.35))
        self.w_valley = float(ff_weights.get("valley_flatness", {}).get("weight", 0.15))

        total = self.w_rainfall + self.w_flow_accum + self.w_valley
        if abs(total - 1.0) > 1e-4:
            self.w_rainfall /= total
            self.w_flow_accum /= total
            self.w_valley /= total

    def compute_flash_flood_grid(
        self,
        rainfall_24h_norm: np.ndarray,
        flow_accum_norm: np.ndarray,
        slope_norm: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Calculates flash-flood risk grid.
        Valley bottoms = (1.0 - slope_norm). Flat areas with high flow accumulation
        and intense rainfall experience peak flash flooding.
        """
        valley_flatness = 1.0 - slope_norm

        ff_risk_grid = (
            self.w_rainfall * rainfall_24h_norm
            + self.w_flow_accum * flow_accum_norm
            + self.w_valley * valley_flatness
        )
        ff_risk_grid = np.clip(ff_risk_grid, 0.0, 1.0).astype(np.float32)
        ff_classes = classify_risk_score(ff_risk_grid)

        metadata = {
            "formula": "w_rainfall * rainfall_24h_norm + w_flow_accum * flow_accum_norm + w_valley * (1 - slope_norm)",
            "weights": {
                "rainfall": self.w_rainfall,
                "flow_accumulation": self.w_flow_accum,
                "valley_flatness": self.w_valley,
            },
            "mean_flash_flood_risk": round(float(np.mean(ff_risk_grid)), 3),
            "max_flash_flood_risk": round(float(np.max(ff_risk_grid)), 3),
            "high_flash_flood_cells_count": int(np.sum(ff_risk_grid >= 0.50)),
            "provenance": ProvenanceTag.MODELLED.value,
            "disclaimer": (
                "Flash flood index is a topographic and precipitation data-fusion heuristic. "
                "It does NOT claim Saint-Venant 2D hydraulic/hydrodynamic numerical wave routing."
            ),
        }

        return ff_risk_grid, ff_classes, metadata
