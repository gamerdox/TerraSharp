import React, { useState, useEffect } from "react";
import { X, Download, Copy, Check, FileCode } from "lucide-react";
import { fetchSituationReport } from "../api";

interface ExportReportModalProps {
  onClose: () => void;
}

export const ExportReportModal: React.FC<ExportReportModalProps> = ({ onClose }) => {
  const [report, setReport] = useState<any>(null);
  const [format, setFormat] = useState<"json" | "markdown">("markdown");
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSituationReport()
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const getMarkdownText = () => {
    if (!report) return "";
    let md = `# ${report.report_title}\n`;
    md += `*Generated: ${report.generated_at} | Operating Mode: ${report.operating_mode}*\n\n`;
    md += `## 1. Executive Summary\n`;
    md += `- **Settlements Analyzed:** ${report.summary.total_settlements_analyzed}\n`;
    md += `- **Critical Settlements:** ${report.summary.critical_settlements_count} (${report.summary.critical_settlements.join(", ")})\n`;
    md += `- **Warning Settlements:** ${report.summary.warning_settlements_count} (${report.summary.warning_settlements.join(", ")})\n`;
    md += `- **Lead-Time Threshold Status:** ${report.summary.lead_time_status} (~${report.summary.estimated_lead_hours ?? 0} hrs)\n\n`;
    md += `## 2. Settlement Risk & Simulated Action Matrix\n\n`;
    md += `| Settlement | Peak Landslide | Peak Flash Flood | Alert Status | Trigger Driver | Evacuation Action |\n`;
    md += `|---|:---:|:---:|:---:|---|---|\n`;
    for (const v of report.villages || []) {
      md += `| ${v.name} | ${v.max_landslide_risk.toFixed(2)} | ${v.max_flash_flood_risk.toFixed(2)} | ${v.alert_state} | ${v.dominant_factor} | ${v.recommended_action} |\n`;
    }
    md += `\n## 3. Scientific Disclaimers & Provenance\n`;
    md += `${report.disclaimer}\n`;
    return md;
  };

  const currentContent = format === "json" ? JSON.stringify(report, null, 2) : getMarkdownText();

  const handleCopy = () => {
    navigator.clipboard.writeText(currentContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([currentContent], {
      type: format === "json" ? "application/json" : "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sh304_situation_report_${report?.aoi?.id || "aoi"}.${format === "json" ? "json" : "md"}`;
    a.click();
    URL.revokeObjectURL(url);
  };

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
        maxWidth: "800px",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <FileCode size={20} color="var(--accent-blue)" />
            <h2 style={{ fontSize: "18px", fontWeight: "700" }}>Export Situation Report</h2>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        {/* Format Selector & Buttons */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: "6px" }}>
            <button
              className={`btn ${format === "markdown" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => setFormat("markdown")}
            >
              Markdown (.md)
            </button>
            <button
              className={`btn ${format === "json" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => setFormat("json")}
            >
              Structured JSON
            </button>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button className="btn btn-secondary" onClick={handleCopy}>
              {copied ? <Check size={14} color="#4ade80" /> : <Copy size={14} />}
              <span>{copied ? "Copied!" : "Copy"}</span>
            </button>
            <button className="btn btn-primary" onClick={handleDownload}>
              <Download size={14} />
              <span>Download File</span>
            </button>
          </div>
        </div>

        {/* Textarea View */}
        <div style={{ flex: 1, minHeight: "340px" }}>
          {loading ? (
            <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
              Generating situation report...
            </div>
          ) : (
            <textarea
              readOnly
              value={currentContent}
              style={{
                width: "100%",
                height: "360px",
                backgroundColor: "var(--bg-primary)",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
                padding: "12px",
                color: "var(--text-primary)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                lineHeight: "1.4",
                resize: "none",
                outline: "none",
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
