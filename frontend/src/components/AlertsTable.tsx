import React, { useState } from "react";
import { AlertItem, VillageRiskSummary } from "../types";
import { ShieldAlert, AlertTriangle, CheckCircle, Search } from "lucide-react";

interface AlertsTableProps {
  alerts: AlertItem[];
  villages: VillageRiskSummary[];
  onSelectVillage: (village: VillageRiskSummary) => void;
  selectedVillageId?: string;
}

export const AlertsTable: React.FC<AlertsTableProps> = ({
  alerts,
  villages,
  onSelectVillage,
  selectedVillageId,
}) => {
  const [filter, setFilter] = useState<string>("ALL");
  const [search, setSearch] = useState<string>("");

  const filteredVillages = villages.filter((v) => {
    const matchesFilter =
      filter === "ALL" ||
      (filter === "CRITICAL" && v.alert_state === "CRITICAL") ||
      (filter === "WARNING" && v.alert_state === "WARNING") ||
      (filter === "WATCH" && v.alert_state === "WATCH") ||
      (filter === "NORMAL" && v.alert_state === "NORMAL");

    const matchesSearch = v.name.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getBadgeClass = (state: string) => {
    switch (state) {
      case "CRITICAL": return "badge-critical";
      case "WARNING": return "badge-high";
      case "WATCH": return "badge-moderate";
      default: return "badge-low";
    }
  };

  return (
    <div style={{
      backgroundColor: "var(--bg-secondary)",
      border: "1px solid var(--border-color)",
      borderRadius: "8px",
      overflow: "hidden",
      display: "flex",
      flexDirection: "column",
    }}>
      {/* Header & Filter Controls */}
      <div style={{
        padding: "12px 16px",
        borderBottom: "1px solid var(--border-color)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "10px",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldAlert size={18} color="#ef4444" />
          <h4 style={{ fontSize: "14px", fontWeight: "700" }}>Settlement Alert Roster</h4>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", marginLeft: "4px" }}>
            ({villages.length} Settlements Monitored)
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {/* Search Box */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", backgroundColor: "var(--bg-primary)", padding: "4px 8px", borderRadius: "4px", border: "1px solid var(--border-color)" }}>
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search settlement..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                backgroundColor: "transparent",
                border: "none",
                outline: "none",
                color: "var(--text-primary)",
                fontSize: "12px",
                width: "130px",
              }}
            />
          </div>

          {/* Filter Pills */}
          <div style={{ display: "flex", gap: "4px" }}>
            {["ALL", "CRITICAL", "WARNING", "WATCH", "NORMAL"].map((t) => (
              <button
                key={t}
                onClick={() => setFilter(t)}
                style={{
                  padding: "4px 8px",
                  fontSize: "11px",
                  fontWeight: "600",
                  borderRadius: "4px",
                  border: filter === t ? "1px solid var(--accent-blue)" : "1px solid var(--border-color)",
                  backgroundColor: filter === t ? "rgba(56, 189, 248, 0.2)" : "var(--bg-primary)",
                  color: filter === t ? "var(--accent-blue)" : "var(--text-muted)",
                  cursor: "pointer",
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div style={{ overflowX: "auto", maxHeight: "280px" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
          <thead>
            <tr style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-muted)", borderBottom: "1px solid var(--border-color)" }}>
              <th style={{ padding: "8px 12px" }}>Settlement</th>
              <th style={{ padding: "8px 12px" }}>Status</th>
              <th style={{ padding: "8px 12px" }}>Peak Landslide</th>
              <th style={{ padding: "8px 12px" }}>Peak Flash-Flood</th>
              <th style={{ padding: "8px 12px" }}>Primary Trigger</th>
              <th style={{ padding: "8px 12px" }}>Simulated Evacuation Protocol</th>
            </tr>
          </thead>
          <tbody>
            {filteredVillages.map((v) => {
              const isSelected = v.village_id === selectedVillageId;
              return (
                <tr
                  key={v.village_id}
                  onClick={() => onSelectVillage(v)}
                  style={{
                    borderBottom: "1px solid var(--border-color)",
                    backgroundColor: isSelected ? "rgba(56, 189, 248, 0.15)" : "transparent",
                    cursor: "pointer",
                    transition: "background-color 0.15s ease",
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.03)";
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.backgroundColor = "transparent";
                  }}
                >
                  <td style={{ padding: "8px 12px", fontWeight: "600", color: "var(--text-primary)" }}>
                    {v.name}
                  </td>
                  <td style={{ padding: "8px 12px" }}>
                    <span className={`btn ${getBadgeClass(v.alert_state)}`} style={{ padding: "2px 6px", fontSize: "11px" }}>
                      {v.alert_state}
                    </span>
                  </td>
                  <td style={{ padding: "8px 12px", fontWeight: "700" }} className="mono">
                    {v.max_landslide_risk.toFixed(2)}
                  </td>
                  <td style={{ padding: "8px 12px", fontWeight: "700" }} className="mono">
                    {v.max_flash_flood_risk.toFixed(2)}
                  </td>
                  <td style={{ padding: "8px 12px", color: "var(--text-secondary)" }}>
                    {v.dominant_factor}
                  </td>
                  <td style={{ padding: "8px 12px", color: "var(--text-secondary)", maxWidth: "340px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {v.recommended_action}
                  </td>
                </tr>
              );
            })}
            {filteredVillages.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)" }}>
                  No settlements matching filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
