import React from "react";
import { X, Database, ExternalLink, ShieldCheck } from "lucide-react";

interface ProvenancePanelProps {
  onClose: () => void;
}

export const ProvenancePanel: React.FC<ProvenancePanelProps> = ({ onClose }) => {
  const datasets = [
    {
      name: "NASA GPM IMERG Final Daily (v07)",
      official_url: "https://earthdata.nasa.gov/dashboard/data-catalog/GPM_3IMERGDF.v07",
      resolution: "0.1° (~10 km) native, resampled to 0.01° (~1.1 km)",
      temporal: "Daily (2024 monsoon series)",
      provenance: "OBSERVED / DEMO",
      notes: "Primary precipitation forcing. Used to derive 24h intensity, 3-day accumulation, and 15-day antecedent rainfall.",
    },
    {
      name: "SRTM GL1 30m Global DEM",
      official_url: "https://opentopography.org/ / https://lpdaac.usgs.gov/products/srtmgl1v003/",
      resolution: "1 arc-second (~30 m)",
      temporal: "Static topographic baseline",
      provenance: "DERIVED (Horn Slope) / DEMO",
      notes: "Used to compute finite-difference slope gradient (degrees) and D8 hydrological upstream contributing flow accumulation.",
    },
    {
      name: "Antecedent Soil Moisture Proxy",
      official_url: "Derived proxy from GPM IMERG time series",
      resolution: "0.01° (~1.1 km)",
      temporal: "Rolling 15-day exponential decay window",
      provenance: "PROXY",
      notes: "CRITICAL: Strictly an antecedent precipitation decay estimator. NOT a direct in-situ sensor or satellite microwave radiometer reading.",
    },
    {
      name: "NASA Global Landslide Catalog (GLC)",
      official_url: "https://data.nasa.gov/dataset/global-landslide-catalog-export",
      resolution: "Point inventory coordinates",
      temporal: "2010–2024 historical occurrences",
      provenance: "OBSERVED / DEMO",
      notes: "Historical event locations and triggers. Unrecorded cells are imputed using AOI-median to prevent false-negative hazard bias.",
    },
    {
      name: "Administrative Village Boundaries",
      official_url: "Authoritative Open Administrative Boundaries / Survey of India",
      resolution: "Cadastral village polygon vectors",
      temporal: "Current administrative boundary release",
      provenance: "OBSERVED",
      notes: "Used for spatial aggregation of grid cell hazards into actionable local administrative alerts.",
    },
  ];

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
        maxWidth: "880px",
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
              <Database size={20} color="var(--accent-blue)" />
              <h2 style={{ fontSize: "18px", fontWeight: "700" }}>
                Data Source Provenance & Scientific Lineage
              </h2>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
              Transparent record of all environmental layers, source repositories, and proxy disclaimers
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

        {/* Dataset Table */}
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
            <thead>
              <tr style={{ backgroundColor: "var(--bg-primary)", borderBottom: "1px solid var(--border-color)" }}>
                <th style={{ padding: "10px 12px" }}>Dataset / Indicator</th>
                <th style={{ padding: "10px 12px" }}>Resolution</th>
                <th style={{ padding: "10px 12px" }}>Tag</th>
                <th style={{ padding: "10px 12px" }}>Scientific Function & Lineage</th>
                <th style={{ padding: "10px 12px" }}>Source</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--border-color)" }}>
                  <td style={{ padding: "10px 12px", fontWeight: "600", color: "var(--text-primary)" }}>
                    {d.name}
                  </td>
                  <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>
                    {d.resolution}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <span className={d.provenance.includes("PROXY") ? "tag-proxy" : d.provenance.includes("DEMO") ? "tag-demo" : "tag-derived"}>
                      {d.provenance}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", color: "var(--text-secondary)", lineHeight: "1.4", maxWidth: "260px" }}>
                    {d.notes}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    {d.official_url.startsWith("http") ? (
                      <a
                        href={d.official_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: "var(--accent-blue)", display: "inline-flex", alignItems: "center", gap: "4px", textDecoration: "none" }}
                      >
                        Official <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>Internal Model</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Scientific Honesty Commitments */}
        <div style={{
          backgroundColor: "rgba(34, 197, 94, 0.08)",
          border: "1px solid rgba(34, 197, 94, 0.25)",
          borderRadius: "8px",
          padding: "14px 18px",
          fontSize: "12px",
          lineHeight: "1.5",
          color: "var(--text-secondary)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <ShieldCheck size={16} color="#4ade80" />
            <strong style={{ color: "var(--text-primary)" }}>Strict Scientific Honesty Policy</strong>
          </div>
          <p>
            1. <strong>Soil Saturation:</strong> Explicitly marked as an antecedent rainfall proxy. We never claim direct in-situ soil moisture sensor readings.
          </p>
          <p>
            2. <strong>Missing Historical Data:</strong> Unrecorded areas are imputed with the neutral AOI-median, avoiding false negative hazard bias.
          </p>
          <p>
            3. <strong>Lead Time:</strong> Computed via the Caine (1980) global empirical threshold ($I = 14.82 \times D^{-0.39}$); framed strictly as estimated time to threshold under current rainfall trend, not a deterministic event prophecy.
          </p>
          <p>
            4. <strong>Evacuation Alerts:</strong> All evacuation notices are simulated early-warning advisories designed for operational decision-support demonstration.
          </p>
        </div>
      </div>
    </div>
  );
};
