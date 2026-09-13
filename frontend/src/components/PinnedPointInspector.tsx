import React from "react";
import { PinPointLiveResult } from "../types";

interface Props {
  data: PinPointLiveResult | null;
  loading: boolean;
  onClose: () => void;
}

export const PinnedPointInspector: React.FC<Props> = ({ data, loading, onClose }) => {
  if (!data && !loading) return null;

  return (
    <div className="absolute top-20 right-6 z-[1000] w-96 max-w-[calc(100vw-3rem)] max-h-[calc(100vh-7rem)] overflow-y-auto bg-slate-900/95 backdrop-blur border border-slate-700 shadow-2xl rounded-xl p-5 text-slate-100 animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-750 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
          </span>
          <h3 className="font-semibold text-base text-slate-100 flex items-center gap-1.5">
            Live Pinpoint Predictor
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 text-lg leading-none p-1 rounded hover:bg-slate-800 transition"
          title="Close Inspector"
        >
          ✕
        </button>
      </div>

      {loading && (
        <div className="py-12 flex flex-col items-center justify-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
          <p className="text-xs text-slate-400 font-mono animate-pulse">
            Querying 30m DEM stencil & live rainfall feeds...
          </p>
        </div>
      )}

      {!loading && data && (
        <div className="space-y-4">
          {/* Coordinates Bar */}
          <div className="bg-slate-800/80 rounded-lg p-2.5 flex items-center justify-between text-xs font-mono text-slate-300 border border-slate-700/50">
            <div>
              <span className="text-slate-500">LAT:</span> {data.latitude.toFixed(4)}°
            </div>
            <div>
              <span className="text-slate-500">LON:</span> {data.longitude.toFixed(4)}°
            </div>
            <div className="text-indigo-400 font-medium">
              {data.elevation_m}m ASL
            </div>
          </div>

          {/* False-Alarm Mitigation Gate Card */}
          <div
            className={`p-3 rounded-lg border text-xs leading-relaxed ${
              data.false_alarm_mitigation.suppressed
                ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-200"
                : data.alert_state === "CRITICAL"
                ? "bg-rose-950/40 border-rose-500/50 text-rose-200"
                : "bg-slate-800/80 border-slate-700 text-slate-300"
            }`}
          >
            <div className="flex items-center justify-between font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                {data.false_alarm_mitigation.suppressed ? "🛡️ FALSE ALARM SUPPRESSED" : "⚡ PREDICTION CONFIDENCE"}
              </span>
              <span className="px-1.5 py-0.5 rounded bg-black/40 text-[10px] font-mono font-bold">
                {data.false_alarm_mitigation.confidence_score_pct}% CONFIDENCE
              </span>
            </div>
            <p className="text-[11px] opacity-90">
              {data.false_alarm_mitigation.status_message}
            </p>
          </div>

          {/* Risk Scores Grid */}
          <div className="grid grid-cols-2 gap-2.5">
            {/* Landslide Risk */}
            <div className="bg-slate-800/60 border border-slate-700/70 rounded-lg p-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">
                Landslide Hazard
              </div>
              <div className="text-xl font-bold font-mono text-slate-100 flex items-baseline gap-1">
                {(data.landslide_risk * 100).toFixed(0)}
                <span className="text-xs font-normal text-slate-400">%</span>
              </div>
              <div className="mt-1.5 inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-700/80 text-slate-200">
                {data.risk_class}
              </div>
            </div>

            {/* Flash Flood Risk */}
            <div className="bg-slate-800/60 border border-slate-700/70 rounded-lg p-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">
                Flash Flood Risk
              </div>
              <div className="text-xl font-bold font-mono text-slate-100 flex items-baseline gap-1">
                {(data.flash_flood_risk * 100).toFixed(0)}
                <span className="text-xs font-normal text-slate-400">%</span>
              </div>
              <div className="mt-1.5 inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-700/80 text-slate-200">
                {data.flash_flood_risk > 0.5 ? "ELEVATED" : "MODERATE"}
              </div>
            </div>
          </div>

          {/* Metrics Detail Tabs/Sections */}
          <div className="space-y-2 text-xs">
            {/* Topography */}
            <div className="bg-slate-800/40 rounded-lg p-2.5 border border-slate-700/50">
              <div className="font-semibold text-slate-300 mb-2 flex items-center justify-between">
                <span>🏔️ Topography (Horn 3x3)</span>
                <span className="text-[10px] text-slate-400">SRTM 30m</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div>
                  <span className="text-slate-500">Slope Gradient:</span>{" "}
                  <span className={`font-mono font-medium ${data.slope_deg >= 25 ? "text-amber-400 font-bold" : ""}`}>
                    {data.slope_deg}°
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">Aspect / Facing:</span>{" "}
                  <span className="font-mono">{data.aspect_deg}°</span>
                </div>
              </div>
            </div>

            {/* Live Rainfall */}
            <div className="bg-slate-800/40 rounded-lg p-2.5 border border-slate-700/50">
              <div className="font-semibold text-slate-300 mb-2 flex items-center justify-between">
                <span>🌧️ Live Rainfall Feeds</span>
                <span className="text-[10px] text-indigo-400">Hourly Real-Time</span>
              </div>
              <div className="grid grid-cols-3 gap-1.5 text-center font-mono">
                <div className="bg-slate-900/60 p-1.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">24 Hours</div>
                  <div className="text-xs font-bold text-slate-200">{data.rainfall_24h_mm} mm</div>
                </div>
                <div className="bg-slate-900/60 p-1.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">15 Days</div>
                  <div className="text-xs font-bold text-slate-200">{data.rainfall_15d_mm} mm</div>
                </div>
                <div className="bg-slate-900/60 p-1.5 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-400">Rate</div>
                  <div className="text-xs font-bold text-indigo-300">{data.current_intensity_mm_hr} mm/h</div>
                </div>
              </div>
            </div>

            {/* Soil Saturation & Lead Time */}
            <div className="bg-slate-800/40 rounded-lg p-2.5 border border-slate-700/50 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Soil Moisture Proxy:</span>
                <span className="font-mono font-semibold text-slate-200">
                  {data.soil_saturation_pct}%
                </span>
              </div>
              {/* Progress bar */}
              <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    data.soil_saturation_pct > 70
                      ? "bg-rose-500"
                      : data.soil_saturation_pct > 40
                      ? "bg-amber-400"
                      : "bg-emerald-400"
                  }`}
                  style={{ width: `${Math.min(100, data.soil_saturation_pct)}%` }}
                ></div>
              </div>

              <div className="flex justify-between items-center pt-1 border-t border-slate-750">
                <span className="text-slate-400">Caine (1980) Lead-Time:</span>
                <span className="font-mono font-semibold text-indigo-300">
                  {data.caine_threshold.estimated_lead_time_hours} hrs
                </span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span>Threshold Status:</span>
                <span className="font-mono text-slate-300">{data.caine_threshold.status}</span>
              </div>
            </div>
          </div>

          {/* Provenance Footer */}
          <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between items-center">
            <span className="truncate max-w-[200px]" title={data.data_provenance.terrain_source}>
              Data: {data.data_provenance.terrain} + {data.data_provenance.rainfall}
            </span>
            <span>{new Date(data.data_provenance.fetched_at).toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};
