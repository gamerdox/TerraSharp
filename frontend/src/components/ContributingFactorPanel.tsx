import React from "react";
import { PointRiskDetail, VillageRiskSummary } from "../types";
import { Info, AlertTriangle, Droplets, Mountain, Layers, History } from "lucide-react";

interface ContributingFactorPanelProps {
  pointDetail: PointRiskDetail | null;
  selectedVillage: VillageRiskSummary | null;
  onClear: () => void;
}

export const ContributingFactorPanel: React.FC<ContributingFactorPanelProps> = ({
  pointDetail,
  selectedVillage,
  onClear,
}) => {
  if (!pointDetail && !selectedVillage) {
    return (
      <div style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "8px",
        padding: "16px",
        color: "var(--text-muted)",
        textAlign: "center",
        fontSize: "13px",
      }}>
        <Info size={24} style={{ margin: "0 auto 8px", display: "block", color: "var(--accent-blue)" }} />
        Click anywhere on the map or select a settlement from the Alert Table to inspect explainable hazard factors.
      </div>
    );
  }

  const title = selectedVillage ? selectedVillage.name : `Location (${pointDetail?.lat}, ${pointDetail?.lon})`;
  const lsScore = selectedVillage ? selectedVillage.max_landslide_risk : (pointDetail ? pointDetail.landslide_risk : 0);
  const ffScore = selectedVillage ? selectedVillage.max_flash_flood_risk : (pointDetail ? pointDetail.flash_flood_risk : 0);
  const factors = pointDetail?.factors;
  const dominantFactor = selectedVillage ? selectedVillage.dominant_factor : factors?.dominant_factor;

  const getBadgeClass = (score: number) => {
    if (score >= 0.75) return "badge-critical";
    if (score >= 0.50) return "badge-high";
    if (score >= 0.25) return "badge-moderate";
    return "badge-low";
  };

  return (
    <div style={{
      backgroundColor: "var(--bg-secondary)",
      border: "1px solid var(--border-color)",
      borderRadius: "8px",
      padding: "16px",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
    }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)", fontWeight: "700" }}>
            Explainable Factor Breakdown
          </span>
          <h3 style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)", marginTop: "2px" }}>
            {title}
          </h3>
        </div>
        <button
          onClick={onClear}
          style={{
            background: "transparent",
            border: "none",
            color: "var(--text-muted)",
            fontSize: "12px",
            cursor: "pointer",
          }}
        >
          ✕ Dismiss
        </button>
      </div>

      {/* Score Badges */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
        <div style={{
          backgroundColor: "var(--bg-primary)",
          padding: "10px",
          borderRadius: "6px",
          border: "1px solid var(--border-color)",
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Landslide Risk</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "6px", marginTop: "4px" }}>
            <span style={{ fontSize: "20px", fontWeight: "800" }}>{lsScore.toFixed(2)}</span>
            <span className={`btn ${getBadgeClass(lsScore)}`} style={{ padding: "1px 6px", fontSize: "11px" }}>
              {lsScore >= 0.75 ? "CRITICAL" : lsScore >= 0.50 ? "HIGH" : lsScore >= 0.25 ? "MODERATE" : "LOW"}
            </span>
          </div>
        </div>

        <div style={{
          backgroundColor: "var(--bg-primary)",
          padding: "10px",
          borderRadius: "6px",
          border: "1px solid var(--border-color)",
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Flash-Flood Risk</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "6px", marginTop: "4px" }}>
            <span style={{ fontSize: "20px", fontWeight: "800" }}>{ffScore.toFixed(2)}</span>
            <span className={`btn ${getBadgeClass(ffScore)}`} style={{ padding: "1px 6px", fontSize: "11px" }}>
              {ffScore >= 0.75 ? "CRITICAL" : ffScore >= 0.50 ? "HIGH" : ffScore >= 0.25 ? "MODERATE" : "LOW"}
            </span>
          </div>
        </div>
      </div>

      {/* Primary Driver */}
      <div style={{
        backgroundColor: "rgba(56, 189, 248, 0.1)",
        border: "1px solid rgba(56, 189, 248, 0.3)",
        borderRadius: "6px",
        padding: "10px 12px",
        fontSize: "12px",
      }}>
        <strong style={{ color: "var(--accent-blue)" }}>Primary Driver: </strong>
        <span>{dominantFactor || "Evaluating..."}</span>
      </div>

      {/* Point Factor Bars */}
      {factors && (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase" }}>
            Contributing Weights & Sub-Scores
          </span>

          {/* Rainfall */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "3px" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <Droplets size={14} color="#38bdf8" /> Rainfall Trigger (35%)
              </span>
              <span className="mono">{factors.rainfall_score.toFixed(2)}</span>
            </div>
            <div style={{ height: "6px", background: "var(--bg-primary)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ width: `${factors.rainfall_score * 100}%`, height: "100%", background: "#38bdf8" }} />
            </div>
          </div>

          {/* Slope */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "3px" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <Mountain size={14} color="#f97316" /> Terrain Slope (30%)
              </span>
              <span className="mono">{factors.slope_score.toFixed(2)}</span>
            </div>
            <div style={{ height: "6px", background: "var(--bg-primary)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ width: `${factors.slope_score * 100}%`, height: "100%", background: "#f97316" }} />
            </div>
          </div>

          {/* Soil Proxy */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "3px" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <Layers size={14} color="#eab308" /> Soil Saturation Proxy (20%)
              </span>
              <span className="mono">{factors.soil_proxy_score.toFixed(2)}</span>
            </div>
            <div style={{ height: "6px", background: "var(--bg-primary)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ width: `${factors.soil_proxy_score * 100}%`, height: "100%", background: "#eab308" }} />
            </div>
          </div>

          {/* Historical Density */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "3px" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <History size={14} color="#a855f7" /> NASA GLC History (15%)
              </span>
              <span className="mono">{factors.history_score.toFixed(2)}</span>
            </div>
            <div style={{ height: "6px", background: "var(--bg-primary)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ width: `${factors.history_score * 100}%`, height: "100%", background: "#a855f7" }} />
            </div>
          </div>

          {/* Explainable Text */}
          <div style={{
            marginTop: "6px",
            fontSize: "12px",
            lineHeight: "1.4",
            color: "var(--text-secondary)",
            backgroundColor: "var(--bg-primary)",
            padding: "8px 10px",
            borderRadius: "6px",
            border: "1px solid var(--border-color)",
          }}>
            {factors.explanation}
          </div>
        </div>
      )}

      {/* Action Recommendation */}
      {selectedVillage && (
        <div style={{
          backgroundColor: selectedVillage.alert_state === "CRITICAL" ? "rgba(239, 68, 68, 0.15)" : "var(--bg-primary)",
          border: `1px solid ${selectedVillage.alert_state === "CRITICAL" ? "rgba(239, 68, 68, 0.4)" : "var(--border-color)"}`,
          borderRadius: "6px",
          padding: "10px",
          fontSize: "12px",
        }}>
          <strong style={{ color: selectedVillage.alert_state === "CRITICAL" ? "#f87171" : "var(--text-primary)" }}>
            Recommended Action:
          </strong>
          <p style={{ marginTop: "4px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
            {selectedVillage.recommended_action}
          </p>
        </div>
      )}
    </div>
  );
};
