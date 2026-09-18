import React, { useState, useEffect, useRef } from "react";
import {
  DangerzoneMonitorResponse,
  SMTPStatus,
} from "../types";
import {
  monitorDangerzone,
  fetchSmtpStatus,
} from "../api";
import { ShieldCheck, AlertTriangle, AlertOctagon, Mail, Send, Radio, CheckCircle, HelpCircle, RefreshCw } from "lucide-react";

interface Props {
  pinnedLocation: { lat: number; lon: number } | null;
  pinnedPlaceName: string | null;
}

export const PersonalDangerzoneMonitor: React.FC<Props> = ({
  pinnedLocation,
  pinnedPlaceName,
}) => {
  const [email, setEmail] = useState<string>(() => {
    return localStorage.getItem("terrasharp_alert_email") || "";
  });
  const [isMonitoring, setIsMonitoring] = useState<boolean>(false);
  const [trackingMode, setTrackingMode] = useState<"gps" | "pin">("pin");
  const [userGps, setUserGps] = useState<{ lat: number; lon: number } | null>(null);
  const [gpsError, setGpsError] = useState<string | null>(null);

  const [latestResult, setLatestResult] = useState<DangerzoneMonitorResponse | null>(null);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [smtpStatus, setSmtpStatus] = useState<SMTPStatus | null>(null);
  const [showSmtpGuide, setShowSmtpGuide] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Sync email to localStorage
  const handleEmailChange = (val: string) => {
    setEmail(val);
    localStorage.setItem("terrasharp_alert_email", val);
  };

  // Load SMTP status on mount
  useEffect(() => {
    fetchSmtpStatus()
      .then(setSmtpStatus)
      .catch((err) => console.warn("Could not check SMTP status:", err));
  }, []);

  // Browser GPS Watcher
  useEffect(() => {
    if (!isMonitoring || trackingMode !== "gps") return;

    if (!navigator.geolocation) {
      setGpsError("Browser Geolocation is not supported.");
      return;
    }

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setUserGps({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setGpsError(null);
      },
      (err) => {
        console.warn("GPS error:", err);
        setGpsError("Unable to acquire GPS location. Check permissions.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [isMonitoring, trackingMode]);

  // Periodic Dangerzone Check
  useEffect(() => {
    if (!isMonitoring || !email || !email.includes("@")) return;

    const targetCoords =
      trackingMode === "gps"
        ? userGps
        : pinnedLocation || { lat: 11.55, lon: 76.15 };

    if (!targetCoords) return;

    const runCheck = async () => {
      try {
        setEvaluating(true);
        const res = await monitorDangerzone({
          email: email.trim(),
          lat: targetCoords.lat,
          lon: targetCoords.lon,
          location_name: trackingMode === "pin" ? pinnedPlaceName || undefined : "My Live GPS Location",
          force_dispatch: false,
        });
        setLatestResult(res);
        if (res.email_dispatched) {
          setStatusMessage(
            res.zone === "RED"
              ? "🚨 CRITICAL HIGH ALERT! Urgent warning email dispatched to your inbox!"
              : "⚠️ NORMAL ALERT: Weather & terrain advisory email dispatched."
          );
        }
      } catch (err: any) {
        console.error("Dangerzone evaluation failed:", err);
      } finally {
        setEvaluating(false);
      }
    };

    // Run immediately once, then every 60s
    runCheck();
    const interval = setInterval(runCheck, 60000);
    return () => clearInterval(interval);
  }, [isMonitoring, trackingMode, userGps, pinnedLocation, email]);

  // Trigger Instant On-Demand Evaluation & Email Test
  const handleImmediateCheck = async (forceDispatch = false) => {
    if (!email || !email.includes("@")) {
      setStatusMessage("Please enter a valid email address first.");
      return;
    }

    const targetCoords =
      trackingMode === "gps"
        ? userGps
        : pinnedLocation || { lat: 11.55, lon: 76.15 };

    if (!targetCoords) {
      setStatusMessage("No coordinates available to inspect. Drag the map pin or turn on GPS.");
      return;
    }

    try {
      setEvaluating(true);
      setStatusMessage(null);
      const res = await monitorDangerzone({
        email: email.trim(),
        lat: targetCoords.lat,
        lon: targetCoords.lon,
        location_name: trackingMode === "pin" ? pinnedPlaceName || undefined : "My Live GPS Location",
        force_dispatch: forceDispatch,
      });
      setLatestResult(res);

      if (res.email_dispatched) {
        setStatusMessage(
          res.zone === "RED"
            ? `🚨 HIGH ALERT (Red Zone)! Warning email delivered to ${email}.`
            : res.zone === "YELLOW"
            ? `⚠️ NORMAL ALERT (Yellow Zone)! Advisory email delivered to ${email}.`
            : `Verified test email delivered to ${email}.`
        );
      } else {
        setStatusMessage(
          `Location is SAFE (Green Zone - Risk: ${res.peak_risk.toFixed(2)}). No alarm email needed.`
        );
      }
    } catch (err: any) {
      setStatusMessage(`Evaluation error: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  const activeCoords =
    trackingMode === "gps"
      ? userGps || { lat: 11.55, lon: 76.15 }
      : pinnedLocation || { lat: 11.55, lon: 76.15 };

  return (
    <div
      style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "10px",
        padding: "16px 20px",
        margin: "0 24px 16px 24px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
      }}
    >
      {/* Top Banner & Title */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              backgroundColor: "rgba(220, 38, 38, 0.15)",
              color: "#ef4444",
            }}
          >
            <AlertOctagon size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "800", color: "#f8fafc" }}>
                Personal Dangerzone Email Alert Engine
              </h3>
              <span
                style={{
                  fontSize: "10px",
                  padding: "2px 8px",
                  borderRadius: "12px",
                  fontWeight: "700",
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  color: "#34d399",
                  border: "1px solid rgba(16, 185, 129, 0.4)",
                }}
              >
                ZERO FAKE ALERTS
              </span>
            </div>
            <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "var(--text-muted)" }}>
              Monitors your position in real-time. Red Zone = High Alert email, Yellow Zone = Normal Alert email, Green = Safe.
            </p>
          </div>
        </div>

        {/* SMTP Status Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {smtpStatus && (
            <button
              onClick={() => setShowSmtpGuide(!showSmtpGuide)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "4px 10px",
                borderRadius: "6px",
                fontSize: "11px",
                fontWeight: "600",
                cursor: "pointer",
                border: smtpStatus.configured ? "1px solid #059669" : "1px solid #d97706",
                backgroundColor: smtpStatus.configured ? "rgba(5, 150, 105, 0.15)" : "rgba(217, 119, 6, 0.15)",
                color: smtpStatus.configured ? "#34d399" : "#fbbf24",
              }}
              title="Click to view SMTP configuration"
            >
              {smtpStatus.configured ? <CheckCircle size={13} /> : <HelpCircle size={13} />}
              <span>{smtpStatus.configured ? "Real SMTP Connected (TLS)" : "SMTP Not Configured (.env)"}</span>
            </button>
          )}
        </div>
      </div>

      {/* SMTP Setup Modal / Accordion */}
      {showSmtpGuide && (
        <div
          style={{
            marginTop: "12px",
            padding: "12px 16px",
            borderRadius: "8px",
            backgroundColor: "#0b1329",
            border: "1px solid #334155",
            fontSize: "12px",
            color: "#cbd5e1",
            lineHeight: 1.5,
          }}
        >
          <div style={{ fontWeight: "700", color: "#38bdf8", marginBottom: "4px" }}>
            📧 Real SMTP Configuration Guide
          </div>
          <p style={{ margin: "0 0 8px 0" }}>
            TerraSharp sends <strong>real TLS emails directly to your inbox</strong>. If credentials are not set in your backend <code>.env</code>, it runs in transparent simulated mode so you can test risk logic without spamming:
          </p>
          <pre
            style={{
              backgroundColor: "#020617",
              padding: "8px 12px",
              borderRadius: "6px",
              fontSize: "11px",
              color: "#38bdf8",
              fontFamily: "monospace",
              margin: 0,
            }}
          >
{`# In D:\landslide_proto\.env:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_USE_TLS=true
SMTP_FROM=your-email@gmail.com`}
          </pre>
        </div>
      )}

      {/* Controls Bar: Email Input, Tracking Mode, Actions */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.4fr 1.1fr auto auto",
          gap: "12px",
          alignItems: "center",
          marginTop: "16px",
        }}
      >
        {/* Email Input */}
        <div style={{ position: "relative" }}>
          <Mail
            size={16}
            style={{
              position: "absolute",
              left: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "#64748b",
            }}
          />
          <input
            type="email"
            value={email}
            onChange={(e) => handleEmailChange(e.target.value)}
            placeholder="Enter your personal email (e.g. user@gmail.com)"
            style={{
              width: "100%",
              padding: "9px 12px 9px 36px",
              fontSize: "13px",
              borderRadius: "6px",
              border: "1px solid #334155",
              backgroundColor: "#0f172a",
              color: "#f8fafc",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* Tracking Mode Toggle */}
        <div style={{ display: "flex", gap: "6px" }}>
          <button
            onClick={() => setTrackingMode("pin")}
            style={{
              flex: 1,
              padding: "8px 10px",
              fontSize: "12px",
              fontWeight: "600",
              borderRadius: "6px",
              border: "1px solid",
              borderColor: trackingMode === "pin" ? "#3b82f6" : "#334155",
              backgroundColor: trackingMode === "pin" ? "rgba(59, 130, 246, 0.2)" : "transparent",
              color: trackingMode === "pin" ? "#60a5fa" : "#94a3b8",
              cursor: "pointer",
            }}
          >
            📍 Map Pin ({activeCoords.lat.toFixed(2)}°, {activeCoords.lon.toFixed(2)}°)
          </button>
          <button
            onClick={() => setTrackingMode("gps")}
            style={{
              flex: 1,
              padding: "8px 10px",
              fontSize: "12px",
              fontWeight: "600",
              borderRadius: "6px",
              border: "1px solid",
              borderColor: trackingMode === "gps" ? "#10b981" : "#334155",
              backgroundColor: trackingMode === "gps" ? "rgba(16, 185, 129, 0.2)" : "transparent",
              color: trackingMode === "gps" ? "#34d399" : "#94a3b8",
              cursor: "pointer",
            }}
          >
            📡 Live GPS
          </button>
        </div>

        {/* Start/Stop Monitoring Toggle */}
        <button
          onClick={() => setIsMonitoring(!isMonitoring)}
          style={{
            padding: "9px 16px",
            fontSize: "13px",
            fontWeight: "700",
            borderRadius: "6px",
            border: "none",
            cursor: "pointer",
            backgroundColor: isMonitoring ? "#dc2626" : "#2563eb",
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            transition: "all 0.2s",
          }}
        >
          <Radio size={15} />
          <span>{isMonitoring ? "Stop Monitoring" : "Enable Monitoring"}</span>
        </button>

        {/* Instant Check & Email Now Button */}
        <button
          onClick={() => handleImmediateCheck(true)}
          disabled={evaluating}
          style={{
            padding: "9px 16px",
            fontSize: "13px",
            fontWeight: "700",
            borderRadius: "6px",
            border: "1px solid #f59e0b",
            backgroundColor: "rgba(245, 158, 11, 0.15)",
            color: "#fbbf24",
            cursor: evaluating ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
          title="Evaluates the current location and dispatches an alert email to verify functionality"
        >
          {evaluating ? (
            <RefreshCw size={15} style={{ animation: "spin 1s linear infinite" }} />
          ) : (
            <Send size={15} />
          )}
          <span>Check & Email Me Now</span>
        </button>
      </div>

      {gpsError && (
        <div style={{ marginTop: "8px", fontSize: "11px", color: "#f87171" }}>
          ⚠️ {gpsError}
        </div>
      )}

      {statusMessage && (
        <div
          style={{
            marginTop: "10px",
            padding: "8px 12px",
            borderRadius: "6px",
            backgroundColor: "rgba(59, 130, 246, 0.15)",
            border: "1px solid rgba(59, 130, 246, 0.3)",
            fontSize: "12px",
            color: "#93c5fd",
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* Dangerzone Evaluation Card */}
      {latestResult && (
        <div
          style={{
            marginTop: "14px",
            padding: "12px 16px",
            borderRadius: "8px",
            border:
              latestResult.zone === "RED"
                ? "2px solid #dc2626"
                : latestResult.zone === "YELLOW"
                ? "2px solid #d97706"
                : "1px solid #059669",
            backgroundColor:
              latestResult.zone === "RED"
                ? "rgba(220, 38, 38, 0.15)"
                : latestResult.zone === "YELLOW"
                ? "rgba(217, 119, 6, 0.12)"
                : "rgba(5, 150, 105, 0.1)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span
                style={{
                  fontSize: "13px",
                  fontWeight: "800",
                  padding: "4px 10px",
                  borderRadius: "6px",
                  color: "#ffffff",
                  backgroundColor:
                    latestResult.zone === "RED"
                      ? "#dc2626"
                      : latestResult.zone === "YELLOW"
                      ? "#d97706"
                      : "#059669",
                }}
              >
                {latestResult.zone_title}
              </span>
              <span style={{ fontSize: "12px", color: "#f8fafc", fontWeight: "600" }}>
                {latestResult.location_name} ({latestResult.latitude.toFixed(4)}°, {latestResult.longitude.toFixed(4)}°)
              </span>
            </div>

            <div style={{ fontSize: "11px", fontFamily: "monospace", color: "#cbd5e1" }}>
              Evaluated at: {new Date(latestResult.evaluated_at).toLocaleTimeString()} • Status:{" "}
              <strong style={{ color: latestResult.email_dispatched ? "#34d399" : "#94a3b8" }}>
                {latestResult.email_status}
              </strong>
            </div>
          </div>

          {/* Physical Metrics Row */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
              gap: "8px",
              marginTop: "10px",
            }}
          >
            <div style={{ backgroundColor: "#0b1329", padding: "8px 10px", borderRadius: "6px", border: "1px solid #334155" }}>
              <div style={{ fontSize: "10px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>
                Terrain Slope
              </div>
              <div style={{ fontSize: "14px", fontWeight: "800", color: latestResult.slope_deg >= 25 ? "#f87171" : "#38bdf8", marginTop: "2px" }}>
                {latestResult.slope_deg.toFixed(1)}° ({latestResult.slope_pct.toFixed(1)}%)
              </div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>Horn SRTM 30m</div>
            </div>

            <div style={{ backgroundColor: "#0b1329", padding: "8px 10px", borderRadius: "6px", border: "1px solid #334155" }}>
              <div style={{ fontSize: "10px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>
                24h Rainfall
              </div>
              <div style={{ fontSize: "14px", fontWeight: "800", color: "#38bdf8", marginTop: "2px" }}>
                {latestResult.rainfall_24h_mm.toFixed(1)} mm
              </div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>Open-Meteo Live</div>
            </div>

            <div style={{ backgroundColor: "#0b1329", padding: "8px 10px", borderRadius: "6px", border: "1px solid #334155" }}>
              <div style={{ fontSize: "10px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>
                Soil Saturation
              </div>
              <div style={{ fontSize: "14px", fontWeight: "800", color: latestResult.soil_saturation_pct > 70 ? "#f87171" : "#38bdf8", marginTop: "2px" }}>
                {latestResult.soil_saturation_pct.toFixed(1)}%
              </div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>API14 Proxy</div>
            </div>

            <div style={{ backgroundColor: "#0b1329", padding: "8px 10px", borderRadius: "6px", border: "1px solid #334155" }}>
              <div style={{ fontSize: "10px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>
                Caine Threshold
              </div>
              <div style={{ fontSize: "14px", fontWeight: "800", color: latestResult.caine_intensity_ratio >= 1.0 ? "#f87171" : "#34d399", marginTop: "2px" }}>
                {latestResult.caine_intensity_ratio.toFixed(2)}x
              </div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>Ratio (I / Ic)</div>
            </div>

            <div style={{ backgroundColor: "#0b1329", padding: "8px 10px", borderRadius: "6px", border: "1px solid #334155" }}>
              <div style={{ fontSize: "10px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>
                Peak Hazard Risk
              </div>
              <div style={{ fontSize: "14px", fontWeight: "800", color: latestResult.peak_risk >= 0.6 ? "#f87171" : latestResult.peak_risk >= 0.35 ? "#fbbf24" : "#34d399", marginTop: "2px" }}>
                {latestResult.peak_risk.toFixed(2)} / 1.00
              </div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>Combined Physics</div>
            </div>
          </div>

          <div style={{ marginTop: "8px", fontSize: "11px", color: "#cbd5e1" }}>
            <strong>Reason: </strong> {latestResult.dispatch_reason}
          </div>
        </div>
      )}
    </div>
  );
};
