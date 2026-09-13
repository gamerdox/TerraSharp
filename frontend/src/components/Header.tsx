import React from "react";
import { AOIInfo, SystemHealth } from "../types";
import { ShieldAlert, Play, RefreshCw, BarChart2, FileText, Database, Layers } from "lucide-react";

interface HeaderProps {
  aois: AOIInfo[];
  currentAoi: string;
  onSelectAoi: (id: string) => void;
  onRunPipeline: () => void;
  onOpenBacktest: () => void;
  onOpenProvenance: () => void;
  onOpenExport: () => void;
  loading: boolean;
  health: SystemHealth | null;
}

export const Header: React.FC<HeaderProps> = ({
  aois,
  currentAoi,
  onSelectAoi,
  onRunPipeline,
  onOpenBacktest,
  onOpenProvenance,
  onOpenExport,
  loading,
  health,
}) => {
  const isDemo = health?.mode === "demo" || !health;

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px 24px",
      backgroundColor: "var(--bg-secondary)",
      borderBottom: "1px solid var(--border-color)",
      flexWrap: "wrap",
      gap: "12px",
    }}>
      {/* Brand & Mode */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div style={{
          backgroundColor: "#ef4444",
          color: "white",
          borderRadius: "8px",
          padding: "8px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          <ShieldAlert size={24} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <h1 style={{ fontSize: "18px", fontWeight: "700", letterSpacing: "-0.02em" }}>
              SH-304 HYPER-LOCAL EARLY WARNING
            </h1>
            <span className={isDemo ? "tag-demo" : "tag-derived"}>
              {isDemo ? "DEMO MODE (OFFLINE REPRODUCIBLE)" : "LIVE DATA MODE"}
            </span>
          </div>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            Data-Fusion Early Warning • GPM IMERG + SRTM 30m + Antecedent Soil Proxy + NASA GLC
          </p>
        </div>
      </div>

      {/* Controls & Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
        {/* AOI Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", backgroundColor: "var(--bg-primary)", padding: "4px 8px", borderRadius: "6px", border: "1px solid var(--border-color)" }}>
          <Layers size={16} color="var(--text-muted)" />
          <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "500" }}>AOI:</span>
          <select
            value={currentAoi}
            onChange={(e) => onSelectAoi(e.target.value)}
            disabled={loading}
            style={{
              backgroundColor: "transparent",
              color: "var(--text-primary)",
              border: "none",
              fontSize: "13px",
              fontWeight: "600",
              outline: "none",
              cursor: "pointer",
            }}
          >
            {aois.map((a) => (
              <option key={a.id} value={a.id} style={{ backgroundColor: "var(--bg-secondary)" }}>
                {a.name}
              </option>
            ))}
          </select>
        </div>

        {/* Process Button */}
        <button
          className="btn btn-primary"
          onClick={onRunPipeline}
          disabled={loading}
          title="Run complete spatial data fusion pipeline"
        >
          {loading ? <RefreshCw size={15} className="spin" /> : <Play size={15} />}
          <span>{loading ? "Processing..." : "Run Fusion Pipeline"}</span>
        </button>

        {/* Backtest Modal Trigger */}
        <button
          className="btn btn-secondary"
          onClick={onOpenBacktest}
          title="Compare Full Weighted Model against Rain-Only Baseline"
        >
          <BarChart2 size={15} />
          <span>Back-Testing (GLC)</span>
        </button>

        {/* Provenance Panel Trigger */}
        <button
          className="btn btn-secondary"
          onClick={onOpenProvenance}
          title="Inspect scientific dataset lineage and proxy status"
        >
          <Database size={15} />
          <span>Data Provenance</span>
        </button>

        {/* Export Situation Report */}
        <button
          className="btn btn-secondary"
          onClick={onOpenExport}
          title="Export Situation Report in JSON or Markdown"
        >
          <FileText size={15} />
          <span>Export Report</span>
        </button>
      </div>
    </header>
  );
};
