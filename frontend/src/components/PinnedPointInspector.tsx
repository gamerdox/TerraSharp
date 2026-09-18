import React from "react";
import { PinPointLiveResult } from "../types";

interface Props {
  data: PinPointLiveResult | null;
  loading: boolean;
  onClose: () => void;
  onGenerateGrid?: (lat: number, lon: number) => void;
  generatingGrid?: boolean;
}

export const PinnedPointInspector: React.FC<Props> = ({
  data,
  loading,
  onClose,
  onGenerateGrid,
  generatingGrid = false,
}) => {
  if (!data && !loading) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: "20px",
        right: "20px",
        zIndex: 2500,
        width: "390px",
        maxWidth: "calc(100vw - 40px)",
        maxHeight: "calc(100vh - 120px)",
        overflowY: "auto",
        backgroundColor: "#0f172a",
        border: "1px solid #334155",
        borderRadius: "12px",
        padding: "18px",
        color: "#f8fafc",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.05)",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid #334155",
          paddingBottom: "10px",
          marginBottom: "14px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            style={{
              display: "inline-block",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              backgroundColor: "#f43f5e",
              boxShadow: "0 0 10px #f43f5e",
            }}
          />
          <h3 style={{ fontSize: "15px", fontWeight: "700", margin: 0, color: "#f8fafc" }}>
            Live Pinpoint Predictor
          </h3>
        </div>
        <button
          onClick={onClose}
          style={{
            background: "transparent",
            border: "none",
            color: "#94a3b8",
            cursor: "pointer",
            fontSize: "18px",
            lineHeight: 1,
            padding: "4px 8px",
            borderRadius: "4px",
          }}
          title="Close Inspector"
        >
          ✕
        </button>
      </div>

      {loading && (
        <div style={{ padding: "30px 0", textAlign: "center" }}>
          <div
            style={{
              display: "inline-block",
              width: "28px",
              height: "28px",
              border: "3px solid #3b82f6",
              borderTopColor: "transparent",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          />
          <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "12px", fontFamily: "monospace" }}>
            Querying 30m DEM stencil & live rainfall feeds...
          </p>
        </div>
      )}

      {!loading && data && (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {/* Coordinates Bar */}
          <div
            style={{
              backgroundColor: "#1e293b",
              borderRadius: "8px",
              padding: "8px 12px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontSize: "12px",
              fontFamily: "monospace",
              border: "1px solid #334155",
            }}
          >
            <div>
              <span style={{ color: "#64748b" }}>LAT:</span> {data.latitude.toFixed(4)}°
            </div>
            <div>
              <span style={{ color: "#64748b" }}>LON:</span> {data.longitude.toFixed(4)}°
            </div>
            <div style={{ color: "#38bdf8", fontWeight: "600" }}>{data.elevation_m}m ASL</div>
          </div>

          {/* Action Button: Generate Full Grid for This Location */}
          {onGenerateGrid && (
            <button
              onClick={() => onGenerateGrid(data.latitude, data.longitude)}
              disabled={generatingGrid}
              style={{
                width: "100%",
                padding: "10px 14px",
                fontSize: "13px",
                fontWeight: "700",
                borderRadius: "8px",
                border: "none",
                cursor: generatingGrid ? "not-allowed" : "pointer",
                backgroundColor: generatingGrid ? "#475569" : "#2563eb",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                boxShadow: "0 4px 12px rgba(37, 99, 235, 0.4)",
                transition: "background 0.2s",
              }}
            >
              {generatingGrid ? (
                <>
                  <span
                    style={{
                      display: "inline-block",
                      width: "14px",
                      height: "14px",
                      border: "2px solid #ffffff",
                      borderTopColor: "transparent",
                      borderRadius: "50%",
                      animation: "spin 1s linear infinite",
                    }}
                  />
                  <span>Generating Full Area Squares...</span>
                </>
              ) : (
                <>
                  <span>🗺️</span>
                  <span>Generate Full Risk Grid for this Area</span>
                </>
              )}
            </button>
          )}

          {/* False-Alarm Mitigation Gate Card */}
          <div
            style={{
              padding: "10px 12px",
              borderRadius: "8px",
              border: data.false_alarm_mitigation.suppressed
                ? "1px solid #059669"
                : data.alert_state === "CRITICAL"
                ? "1px solid #dc2626"
                : "1px solid #334155",
              backgroundColor: data.false_alarm_mitigation.suppressed
                ? "rgba(6, 78, 59, 0.4)"
                : data.alert_state === "CRITICAL"
                ? "rgba(127, 29, 29, 0.4)"
                : "#1e293b",
              fontSize: "12px",
              lineHeight: 1.4,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontWeight: "700",
                marginBottom: "4px",
              }}
            >
              <span
                style={{
                  color: data.false_alarm_mitigation.suppressed
                    ? "#34d399"
                    : data.alert_state === "CRITICAL"
                    ? "#f87171"
                    : "#38bdf8",
                }}
              >
                {data.false_alarm_mitigation.suppressed
                  ? "🛡️ FALSE ALARM SUPPRESSED"
                  : "⚡ PREDICTION CONFIDENCE"}
              </span>
              <span
                style={{
                  fontSize: "10px",
                  fontFamily: "monospace",
                  fontWeight: "700",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  backgroundColor: "rgba(0,0,0,0.5)",
                  color: "#f8fafc",
                }}
              >
                {data.false_alarm_mitigation.confidence_score_pct}% CONFIDENCE
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "11px", color: "#cbd5e1" }}>
              {data.false_alarm_mitigation.status_message}
            </p>
          </div>

          {/* Risk Scores Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            {/* Landslide Risk */}
            <div
              style={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                padding: "10px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  textTransform: "uppercase",
                  color: "#94a3b8",
                  fontWeight: "700",
                  marginBottom: "4px",
                }}
              >
                Landslide Risk
              </div>
              <div
                style={{
                  fontSize: "22px",
                  fontWeight: "800",
                  fontFamily: "monospace",
                  color:
                    data.landslide_risk >= 0.75
                      ? "#ef4444"
                      : data.landslide_risk >= 0.5
                      ? "#f97316"
                      : data.landslide_risk >= 0.25
                      ? "#eab308"
                      : "#22c55e",
                }}
              >
                {(data.landslide_risk * 100).toFixed(0)}%
              </div>
              <div
                style={{
                  marginTop: "6px",
                  display: "inline-block",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  fontSize: "10px",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  backgroundColor: "rgba(0,0,0,0.3)",
                  color: "#e2e8f0",
                }}
              >
                {data.risk_class}
              </div>
            </div>

            {/* Flash Flood Risk */}
            <div
              style={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                padding: "10px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  textTransform: "uppercase",
                  color: "#94a3b8",
                  fontWeight: "700",
                  marginBottom: "4px",
                }}
              >
                Flash Flood Risk
              </div>
              <div
                style={{
                  fontSize: "22px",
                  fontWeight: "800",
                  fontFamily: "monospace",
                  color: data.flash_flood_risk > 0.5 ? "#38bdf8" : "#94a3b8",
                }}
              >
                {(data.flash_flood_risk * 100).toFixed(0)}%
              </div>
              <div
                style={{
                  marginTop: "6px",
                  display: "inline-block",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  fontSize: "10px",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  backgroundColor: "rgba(0,0,0,0.3)",
                  color: "#e2e8f0",
                }}
              >
                {data.flash_flood_risk > 0.5 ? "ELEVATED" : "MODERATE"}
              </div>
            </div>
          </div>

          {/* Topography Card */}
          <div
            style={{
              backgroundColor: "#1e293b",
              borderRadius: "8px",
              padding: "10px 12px",
              border: "1px solid #334155",
            }}
          >
            <div
              style={{
                fontSize: "12px",
                fontWeight: "700",
                color: "#e2e8f0",
                marginBottom: "6px",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <span>🏔️ Topography (Horn 3×3)</span>
              <span style={{ fontSize: "10px", color: "#64748b" }}>SRTM 30m</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8" }}>Slope:</span>{" "}
                <strong style={{ fontFamily: "monospace", color: data.slope_deg >= 25 ? "#f97316" : "#f8fafc" }}>
                  {data.slope_deg}° {data.slope_pct ? `(${data.slope_pct}%)` : ""}
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8" }}>Aspect:</span>{" "}
                <strong style={{ fontFamily: "monospace" }}>{data.aspect_deg}°</strong>
              </div>
            </div>
          </div>

          {/* Live Rainfall Feeds */}
          <div
            style={{
              backgroundColor: "#1e293b",
              borderRadius: "8px",
              padding: "10px 12px",
              border: "1px solid #334155",
            }}
          >
            <div
              style={{
                fontSize: "12px",
                fontWeight: "700",
                color: "#e2e8f0",
                marginBottom: "8px",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <span>🌧️ Live Rainfall Feeds</span>
              <span style={{ fontSize: "10px", color: "#38bdf8" }}>Hourly Live</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "6px", textAlign: "center" }}>
              <div style={{ backgroundColor: "#0f172a", padding: "6px", borderRadius: "6px", border: "1px solid #334155" }}>
                <div style={{ fontSize: "10px", color: "#64748b" }}>24 Hours</div>
                <div style={{ fontSize: "12px", fontWeight: "700", fontFamily: "monospace" }}>
                  {data.rainfall_24h_mm} mm
                </div>
              </div>
              <div style={{ backgroundColor: "#0f172a", padding: "6px", borderRadius: "6px", border: "1px solid #334155" }}>
                <div style={{ fontSize: "10px", color: "#64748b" }}>15 Days</div>
                <div style={{ fontSize: "12px", fontWeight: "700", fontFamily: "monospace" }}>
                  {data.rainfall_15d_mm} mm
                </div>
              </div>
              <div style={{ backgroundColor: "#0f172a", padding: "6px", borderRadius: "6px", border: "1px solid #334155" }}>
                <div style={{ fontSize: "10px", color: "#64748b" }}>Rate</div>
                <div style={{ fontSize: "12px", fontWeight: "700", fontFamily: "monospace", color: "#38bdf8" }}>
                  {data.current_intensity_mm_hr} mm/h
                </div>
              </div>
            </div>
          </div>

          {/* Soil Moisture & Caine Lead-Time */}
          <div
            style={{
              backgroundColor: "#1e293b",
              borderRadius: "8px",
              padding: "10px 12px",
              border: "1px solid #334155",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              fontSize: "12px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ color: "#94a3b8" }}>Soil Moisture Saturation:</span>
              <strong style={{ fontFamily: "monospace" }}>{data.soil_saturation_pct}%</strong>
            </div>

            <div style={{ width: "100%", height: "6px", backgroundColor: "#0f172a", borderRadius: "4px", overflow: "hidden" }}>
              <div
                style={{
                  height: "100%",
                  width: `${Math.min(100, data.soil_saturation_pct)}%`,
                  backgroundColor:
                    data.soil_saturation_pct > 70
                      ? "#ef4444"
                      : data.soil_saturation_pct > 40
                      ? "#eab308"
                      : "#22c55e",
                  transition: "width 0.4s",
                }}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "4px", borderTop: "1px solid #334155" }}>
              <span style={{ color: "#94a3b8" }}>Caine (1980) Lead-Time:</span>
              <strong style={{ fontFamily: "monospace", color: "#38bdf8" }}>
                {data.caine_threshold.estimated_lead_time_hours} hrs
              </strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "11px" }}>
              <span style={{ color: "#64748b" }}>Threshold Status:</span>
              <span style={{ fontFamily: "monospace", color: "#cbd5e1" }}>
                {data.caine_threshold.status}
              </span>
            </div>
          </div>

          {/* Footer Provenance */}
          <div
            style={{
              fontSize: "10px",
              color: "#64748b",
              display: "flex",
              justifyContent: "space-between",
              paddingTop: "6px",
              borderTop: "1px solid #334155",
            }}
          >
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "220px" }}>
              {data.data_provenance.terrain_source}
            </span>
            <span>{new Date(data.data_provenance.fetched_at).toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};
