import React from "react";

export type ActiveRasterLayer = "landslide" | "flash_flood" | "slope" | "rainfall" | "soil_proxy";

interface RiskLegendProps {
  activeLayer: ActiveRasterLayer;
  onLayerChange: (layer: ActiveRasterLayer) => void;
  showVillages: boolean;
  onToggleVillages: () => void;
  showGlcMarkers: boolean;
  onToggleGlc: () => void;
}

export const RiskLegend: React.FC<RiskLegendProps> = ({
  activeLayer,
  onLayerChange,
  showVillages,
  onToggleVillages,
  showGlcMarkers,
  onToggleGlc,
}) => {
  return (
    <div style={{
      backgroundColor: "var(--bg-secondary)",
      border: "1px solid var(--border-color)",
      borderRadius: "8px",
      padding: "12px 16px",
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.3)",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)", fontWeight: "700" }}>
          Hazard Map Layers
        </span>
        {activeLayer === "soil_proxy" && (
          <span className="tag-proxy">PROXY INDICATOR</span>
        )}
      </div>

      {/* Layer Switcher Buttons */}
      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
        {[
          { id: "landslide", label: "Landslide Risk" },
          { id: "flash_flood", label: "Flash-Flood Risk" },
          { id: "slope", label: "Slope (°)" },
          { id: "rainfall", label: "24h Rain (mm)" },
          { id: "soil_proxy", label: "Soil Saturation (Proxy)" },
        ].map((item) => (
          <button
            key={item.id}
            onClick={() => onLayerChange(item.id as ActiveRasterLayer)}
            style={{
              padding: "5px 10px",
              fontSize: "12px",
              fontWeight: "600",
              borderRadius: "4px",
              cursor: "pointer",
              border: activeLayer === item.id ? "1px solid #38bdf8" : "1px solid var(--border-color)",
              backgroundColor: activeLayer === item.id ? "rgba(56, 189, 248, 0.2)" : "var(--bg-primary)",
              color: activeLayer === item.id ? "#38bdf8" : "var(--text-secondary)",
              transition: "all 0.15s ease",
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Overlays Toggles */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", paddingTop: "4px", borderTop: "1px solid var(--border-color)", fontSize: "12px" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={showVillages}
            onChange={onToggleVillages}
            style={{ accentColor: "#38bdf8", cursor: "pointer" }}
          />
          <span style={{ color: "var(--text-primary)" }}>Village Boundaries</span>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={showGlcMarkers}
            onChange={onToggleGlc}
            style={{ accentColor: "#ef4444", cursor: "pointer" }}
          />
          <span style={{ color: "var(--text-primary)" }}>NASA GLC Historical Events</span>
        </label>
      </div>

      {/* Legend Color Bar */}
      <div style={{ display: "flex", flexDirection: "column", gap: "4px", paddingTop: "4px", borderTop: "1px solid var(--border-color)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--text-muted)" }}>
          <span>Low (0.00 - 0.25)</span>
          <span>Moderate (0.25 - 0.50)</span>
          <span>High (0.50 - 0.75)</span>
          <span>Critical (0.75 - 1.00)</span>
        </div>
        <div style={{
          height: "8px",
          borderRadius: "4px",
          background: "linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444)",
        }} />
      </div>
    </div>
  );
};
