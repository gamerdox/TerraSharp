import React from "react";
import { BacktestComparison } from "../types";
import { X, CheckCircle2, AlertCircle, BarChart3 } from "lucide-react";

interface BacktestModalProps {
  data: BacktestComparison | null;
  onClose: () => void;
}

export const BacktestModal: React.FC<BacktestModalProps> = ({ data, onClose }) => {
  if (!data) return null;

  const rain = data.rain_only_baseline;
  const full = data.full_weighted_index;

  const deltaAuc = full.roc_auc - rain.roc_auc;
  const deltaFar = rain.false_alarm_rate - full.false_alarm_rate;
  const deltaPrec = full.precision - rain.precision;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.75)",
      backdropFilter: "blur(4px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 9999,
      padding: "20px",
    }}>
      <div style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "12px",
        width: "100%",
        maxWidth: "840px",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <BarChart3 size={20} color="var(--accent-blue)" />
              <h2 style={{ fontSize: "18px", fontWeight: "700" }}>
                Historical Back-Testing & Model Benchmark
              </h2>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
              Evaluated against NASA Global Landslide Catalog (GLC) events for {data.aoi_id.toUpperCase()}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Mandatory Comparison Table */}
        <div>
          <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase", display: "block", marginBottom: "8px" }}>
            Mandatory Comparison: Rain-Only Baseline vs Full Weighted Risk Index
          </span>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", textAlign: "left" }}>
            <thead>
              <tr style={{ backgroundColor: "var(--bg-primary)", borderBottom: "1px solid var(--border-color)" }}>
                <th style={{ padding: "10px 14px" }}>Evaluation Metric</th>
                <th style={{ padding: "10px 14px", color: "#94a3b8" }}>Rain-Only Baseline</th>
                <th style={{ padding: "10px 14px", color: "var(--accent-blue)" }}>Full Weighted Risk Index</th>
                <th style={{ padding: "10px 14px", color: "#4ade80" }}>Delta Improvement (Δ)</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "10px 14px", fontWeight: "600" }}>ROC-AUC</td>
                <td style={{ padding: "10px 14px" }} className="mono">{rain.roc_auc.toFixed(3)}</td>
                <td style={{ padding: "10px 14px", fontWeight: "700", color: "var(--accent-blue)" }} className="mono">
                  {full.roc_auc.toFixed(3)}
                </td>
                <td style={{ padding: "10px 14px", color: "#4ade80", fontWeight: "700" }} className="mono">
                  +{deltaAuc.toFixed(3)}
                </td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "10px 14px", fontWeight: "600" }}>Precision</td>
                <td style={{ padding: "10px 14px" }} className="mono">{(rain.precision * 100).toFixed(1)}%</td>
                <td style={{ padding: "10px 14px", fontWeight: "700", color: "var(--accent-blue)" }} className="mono">
                  {(full.precision * 100).toFixed(1)}%
                </td>
                <td style={{ padding: "10px 14px", color: "#4ade80", fontWeight: "700" }} className="mono">
                  +{((deltaPrec) * 100).toFixed(1)}%
                </td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "10px 14px", fontWeight: "600" }}>Recall (True Positive Rate)</td>
                <td style={{ padding: "10px 14px" }} className="mono">{(rain.recall * 100).toFixed(1)}%</td>
                <td style={{ padding: "10px 14px", fontWeight: "700", color: "var(--accent-blue)" }} className="mono">
                  {(full.recall * 100).toFixed(1)}%
                </td>
                <td style={{ padding: "10px 14px", color: "#4ade80", fontWeight: "700" }} className="mono">
                  {((full.recall - rain.recall) * 100).toFixed(1)}%
                </td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "10px 14px", fontWeight: "600" }}>False Alarm Rate (FAR)</td>
                <td style={{ padding: "10px 14px", color: "#f87171" }} className="mono">{(rain.false_alarm_rate * 100).toFixed(1)}%</td>
                <td style={{ padding: "10px 14px", fontWeight: "700", color: "var(--accent-blue)" }} className="mono">
                  {(full.false_alarm_rate * 100).toFixed(1)}%
                </td>
                <td style={{ padding: "10px 14px", color: "#4ade80", fontWeight: "700" }} className="mono">
                  -{(deltaFar * 100).toFixed(1)}% (Reduction)
                </td>
              </tr>
              <tr>
                <td style={{ padding: "10px 14px", fontWeight: "600" }}>F1-Score</td>
                <td style={{ padding: "10px 14px" }} className="mono">{rain.f1_score.toFixed(3)}</td>
                <td style={{ padding: "10px 14px", fontWeight: "700", color: "var(--accent-blue)" }} className="mono">
                  {full.f1_score.toFixed(3)}
                </td>
                <td style={{ padding: "10px 14px", color: "#4ade80", fontWeight: "700" }} className="mono">
                  +{(full.f1_score - rain.f1_score).toFixed(3)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Confusion Matrices */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          {/* Rain-Only */}
          <div style={{ backgroundColor: "var(--bg-primary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-muted)" }}>
              Rain-Only Baseline Confusion Matrix
            </span>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px", marginTop: "8px", textAlign: "center", fontSize: "12px" }}>
              <div style={{ backgroundColor: "rgba(34, 197, 94, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>TP (Hits)</span>
                <strong className="mono">{rain.true_positives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(239, 68, 68, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>FP (False Alarms)</span>
                <strong className="mono" style={{ color: "#f87171" }}>{rain.false_positives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(239, 68, 68, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>FN (Misses)</span>
                <strong className="mono" style={{ color: "#f87171" }}>{rain.false_negatives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(34, 197, 94, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>TN (Correct Rejections)</span>
                <strong className="mono">{rain.true_negatives}</strong>
              </div>
            </div>
          </div>

          {/* Full Weighted */}
          <div style={{ backgroundColor: "var(--bg-primary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--accent-blue)" }}>
              Full Weighted Index Confusion Matrix
            </span>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px", marginTop: "8px", textAlign: "center", fontSize: "12px" }}>
              <div style={{ backgroundColor: "rgba(34, 197, 94, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>TP (Hits)</span>
                <strong className="mono">{full.true_positives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(34, 197, 94, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>FP (False Alarms)</span>
                <strong className="mono" style={{ color: "#4ade80" }}>{full.false_positives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(239, 68, 68, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>FN (Misses)</span>
                <strong className="mono">{full.false_negatives}</strong>
              </div>
              <div style={{ backgroundColor: "rgba(34, 197, 94, 0.1)", padding: "8px", borderRadius: "4px" }}>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>TN (Correct Rejections)</span>
                <strong className="mono">{full.true_negatives}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Narrative & Scientific Justification */}
        <div style={{
          backgroundColor: "rgba(56, 189, 248, 0.08)",
          border: "1px solid rgba(56, 189, 248, 0.2)",
          borderRadius: "8px",
          padding: "12px 16px",
          fontSize: "12px",
          lineHeight: "1.5",
          color: "var(--text-secondary)",
        }}>
          <strong style={{ color: "var(--text-primary)", display: "block", marginBottom: "4px" }}>
            Why Data Fusion is Scientifically Essential:
          </strong>
          {data.comparison_summary}
        </div>

        {/* Scientific Note */}
        <div style={{ fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.4" }}>
          <strong>Back-Testing Protocol: </strong>
          {data.scientific_note}
        </div>
      </div>
    </div>
  );
};
