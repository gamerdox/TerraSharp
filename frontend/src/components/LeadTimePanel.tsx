import React from "react";
import { LeadTimeEvaluation } from "../types";
import { Clock, AlertOctagon, TrendingUp, HelpCircle } from "lucide-react";

interface LeadTimePanelProps {
  leadTime: LeadTimeEvaluation | null;
}

export const LeadTimePanel: React.FC<LeadTimePanelProps> = ({ leadTime }) => {
  if (!leadTime) return null;

  const isBreached = leadTime.status === "THRESHOLD_BREACHED";
  const isApproaching = leadTime.status === "APPROACHING_THRESHOLD";

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
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Clock size={18} color="var(--accent-blue)" />
          <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>
            Lead-Time Estimator (Caine 1980)
          </h4>
        </div>
        <span className={isBreached ? "badge-critical" : isApproaching ? "badge-high" : "badge-low"} style={{ padding: "2px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "700" }}>
          {isBreached ? "THRESHOLD BREACHED" : isApproaching ? "APPROACHING THRESHOLD" : "BELOW THRESHOLD"}
        </span>
      </div>

      {/* Main Gauge / Indicator */}
      <div style={{
        backgroundColor: "var(--bg-primary)",
        padding: "12px",
        borderRadius: "6px",
        border: "1px solid var(--border-color)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <div>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>
            Estimated Lead Time to Threshold
          </span>
          <div style={{ fontSize: "22px", fontWeight: "800", color: isBreached ? "#ef4444" : isApproaching ? "#f97316" : "#22c55e", marginTop: "2px" }}>
            {isBreached ? "~0.0 Hours (Critical)" : leadTime.estimated_lead_time_hours ? `~${leadTime.estimated_lead_time_hours.toFixed(1)} Hours` : "Stable"}
          </div>
          {leadTime.uncertainty_range_hours && (
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              Uncertainty: {leadTime.uncertainty_range_hours[0].toFixed(1)} – {leadTime.uncertainty_range_hours[1].toFixed(1)} hrs (±30%)
            </span>
          )}
        </div>

        <div style={{ textAlign: "right" }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>
            Current Intensity
          </span>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)" }}>
            {leadTime.current_intensity_mm_hr.toFixed(1)} <span style={{ fontSize: "11px", fontWeight: "normal" }}>mm/hr</span>
          </div>
          <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
            Crit: {leadTime.caine_threshold_intensity_mm_hr.toFixed(1)} mm/hr
          </span>
        </div>
      </div>

      {/* Metric Breakdown */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "11px" }}>
        <div style={{ backgroundColor: "var(--bg-primary)", padding: "6px 8px", borderRadius: "4px" }}>
          <span style={{ color: "var(--text-muted)" }}>Storm Duration:</span>{" "}
          <strong style={{ color: "var(--text-primary)" }}>{leadTime.duration_hours} hrs</strong>
        </div>
        <div style={{ backgroundColor: "var(--bg-primary)", padding: "6px 8px", borderRadius: "4px" }}>
          <span style={{ color: "var(--text-muted)" }}>Rate of Intensification:</span>{" "}
          <strong style={{ color: "var(--text-primary)" }}>+{leadTime.rainfall_trend_alpha_mm_hr2.toFixed(3)} mm/hr²</strong>
        </div>
      </div>

      {/* Scientific Limitation Disclaimer */}
      <div style={{
        fontSize: "11px",
        color: "var(--text-secondary)",
        lineHeight: "1.35",
        padding: "8px",
        backgroundColor: "rgba(234, 179, 8, 0.1)",
        border: "1px solid rgba(234, 179, 8, 0.25)",
        borderRadius: "4px",
      }}>
        <strong>Scientific Limitation: </strong>
        {leadTime.scientific_disclaimer}
      </div>
    </div>
  );
};
