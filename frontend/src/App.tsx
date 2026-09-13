import React, { useState, useEffect } from "react";
import {
  AOIInfo,
  GridCell,
  PointRiskDetail,
  LeadTimeEvaluation,
  AlertItem,
  VillageRiskSummary,
  BacktestComparison,
  SystemHealth,
  PinPointLiveResult,
} from "./types";
import {
  fetchHealth,
  fetchAOIs,
  switchAOI,
  triggerPipeline,
  fetchRiskGrid,
  fetchPointRisk,
  fetchLivePinpoint,
  createAoiFromPin,
  fetchLeadTime,
  fetchAlerts,
  fetchVillages,
  fetchVillagesGeoJSON,
  fetchBacktest,
  fetchGlcEvents,
} from "./api";

import { Header } from "./components/Header";
import { MapViewer } from "./components/MapViewer";
import { RiskLegend, ActiveRasterLayer } from "./components/RiskLegend";
import { ContributingFactorPanel } from "./components/ContributingFactorPanel";
import { LeadTimePanel } from "./components/LeadTimePanel";
import { AlertsTable } from "./components/AlertsTable";
import { BacktestModal } from "./components/BacktestModal";
import { ProvenancePanel } from "./components/ProvenancePanel";
import { ExportReportModal } from "./components/ExportReportModal";
import { PinnedPointInspector } from "./components/PinnedPointInspector";

export const App: React.FC = () => {
  // Application Data States
  const [aois, setAois] = useState<AOIInfo[]>([]);
  const [currentAoi, setCurrentAoi] = useState<string>("wayanad");
  const [health, setHealth] = useState<SystemHealth | null>(null);

  const [cells, setCells] = useState<GridCell[]>([]);
  const [villages, setVillages] = useState<VillageRiskSummary[]>([]);
  const [villagesGeoJson, setVillagesGeoJson] = useState<any>(null);
  const [glcEvents, setGlcEvents] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [leadTime, setLeadTime] = useState<LeadTimeEvaluation | null>(null);
  const [backtestData, setBacktestData] = useState<BacktestComparison | null>(null);

  // Selection & UI States
  const [selectedPoint, setSelectedPoint] = useState<PointRiskDetail | null>(null);
  const [selectedVillage, setSelectedVillage] = useState<VillageRiskSummary | null>(null);
  const [activeLayer, setActiveLayer] = useState<ActiveRasterLayer>("landslide");
  const [showVillages, setShowVillages] = useState<boolean>(true);
  const [showGlcMarkers, setShowGlcMarkers] = useState<boolean>(true);

  // Pin-Anywhere Live Prediction States
  const [pinnedLocation, setPinnedLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [pinnedData, setPinnedData] = useState<PinPointLiveResult | null>(null);
  const [pinnedLoading, setPinnedLoading] = useState<boolean>(false);
  const [generatingGrid, setGeneratingGrid] = useState<boolean>(false);

  // Modals
  const [showBacktestModal, setShowBacktestModal] = useState<boolean>(false);
  const [showProvenanceModal, setShowProvenanceModal] = useState<boolean>(false);
  const [showExportModal, setShowExportModal] = useState<boolean>(false);

  // Status
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load initial system data
  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [h, aoiList] = await Promise.all([fetchHealth(), fetchAOIs()]);
      setHealth(h);
      setAois(aoiList);
      const active = h.data_status.active_aoi || "wayanad";
      setCurrentAoi(active);

      await refreshAllData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to load system data.");
    } finally {
      setLoading(false);
    }
  };

  // Refresh all dashboard metrics from backend
  const refreshAllData = async () => {
    try {
      const [gridData, vSummaries, vGeo, lt, alertList, bt, glcList] = await Promise.all([
        fetchRiskGrid(),
        fetchVillages(),
        fetchVillagesGeoJSON(),
        fetchLeadTime(),
        fetchAlerts(),
        fetchBacktest(),
        fetchGlcEvents(),
      ]);

      setCells(gridData.cells || []);
      setVillages(vSummaries);
      setVillagesGeoJson(vGeo);
      setLeadTime(lt);
      setAlerts(alertList);
      setBacktestData(bt);
      setGlcEvents(glcList || []);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Error fetching hazard layers.");
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Handle AOI Change
  const handleAoiChange = async (aoiId: string) => {
    try {
      setLoading(true);
      setCurrentAoi(aoiId);
      setSelectedPoint(null);
      setSelectedVillage(null);
      await switchAOI(aoiId);
      await triggerPipeline(aoiId);
      await refreshAllData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to switch AOI.");
    } finally {
      setLoading(false);
    }
  };

  // Run Pipeline Manually
  const handleRunPipeline = async () => {
    try {
      setLoading(true);
      await triggerPipeline(currentAoi);
      await refreshAllData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Pipeline execution failed.");
    } finally {
      setLoading(false);
    }
  };

  // Map Click -> Explainable Point Risk & Live Prediction Pin
  const handleMapClick = async (lat: number, lon: number) => {
    handlePinLocation(lat, lon);
    const activeAoiObj = aois.find((a) => a.id === currentAoi);
    if (activeAoiObj) {
      const { min_lon, min_lat, max_lon, max_lat } = activeAoiObj.bbox;
      if (lat >= min_lat && lat <= max_lat && lon >= min_lon && lon <= max_lon) {
        try {
          const pt = await fetchPointRisk(lat, lon);
          setSelectedPoint(pt);
          setSelectedVillage(null);
        } catch (err) {
          console.warn("Grid point query error:", err);
        }
      } else {
        setSelectedPoint(null);
        setSelectedVillage(null);
      }
    }
  };

  // Pin Location -> Live Real-Time Multi-Factor Evaluation
  const handlePinLocation = async (lat: number, lon: number) => {
    setPinnedLocation({ lat, lon });
    setPinnedLoading(true);
    try {
      const res = await fetchLivePinpoint(lat, lon);
      setPinnedData(res);
    } catch (err: any) {
      console.error("Failed to evaluate live pinpoint:", err);
      setErrorMsg("Failed to query live metrics for pinned location.");
    } finally {
      setPinnedLoading(false);
    }
  };

  // Generate Full Area Risk Grid (Squares) from Pinned Location
  const handleGenerateGridFromPin = async (lat: number, lon: number) => {
    try {
      setGeneratingGrid(true);
      setLoading(true);
      const res = await createAoiFromPin(lat, lon);
      const newAoiId = res.active_aoi;
      setCurrentAoi(newAoiId);
      const aoiList = await fetchAOIs();
      setAois(aoiList);
      await refreshAllData();
      setPinnedData(null);
      setPinnedLocation(null);
    } catch (err: any) {
      console.error("Failed to generate AOI grid:", err);
      setErrorMsg(err.message || "Failed to generate area risk grid.");
    } finally {
      setGeneratingGrid(false);
      setLoading(false);
    }
  };

  // Select Village from Table or Polygon
  const handleSelectVillage = (v: VillageRiskSummary) => {
    setSelectedVillage(v);
    setSelectedPoint(null);
  };

  // Map center from active AOI config
  const activeAoiObj = aois.find((a) => a.id === currentAoi);
  const center = activeAoiObj ? activeAoiObj.center : { lat: 11.70, lon: 76.08 };
  const zoom = activeAoiObj ? activeAoiObj.default_zoom : 11;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", backgroundColor: "var(--bg-primary)" }}>
      {/* Header */}
      <Header
        aois={aois}
        currentAoi={currentAoi}
        onSelectAoi={handleAoiChange}
        onRunPipeline={handleRunPipeline}
        onOpenBacktest={() => setShowBacktestModal(true)}
        onOpenProvenance={() => setShowProvenanceModal(true)}
        onOpenExport={() => setShowExportModal(true)}
        loading={loading}
        health={health}
      />

      {/* Error banner if any */}
      {errorMsg && (
        <div style={{
          backgroundColor: "#dc2626",
          color: "white",
          padding: "8px 24px",
          fontSize: "13px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <span><strong>Notice:</strong> {errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} style={{ background: "transparent", border: "none", color: "white", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {/* Main Grid Content */}
      <main style={{
        display: "grid",
        gridTemplateColumns: "1fr 380px",
        gap: "16px",
        padding: "16px 24px",
        flex: 1,
      }}>
        {/* Left: Map & Legend */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", height: "100%", position: "relative" }}>
          <div style={{ flex: 1, minHeight: "480px", position: "relative" }}>
            <MapViewer
              center={center}
              zoom={zoom}
              cells={cells}
              villagesGeoJson={villagesGeoJson}
              glcEvents={glcEvents}
              activeLayer={activeLayer}
              showVillages={showVillages}
              showGlcMarkers={showGlcMarkers}
              onMapClick={handleMapClick}
              onSelectVillage={handleSelectVillage}
              selectedVillage={selectedVillage}
              pinnedLocation={pinnedLocation}
              onPinLocation={handlePinLocation}
            />

            {/* Live Pinpoint Inspector Floating Overlay */}
            <PinnedPointInspector
              data={pinnedData}
              loading={pinnedLoading}
              onClose={() => {
                setPinnedData(null);
                setPinnedLocation(null);
              }}
              onGenerateGrid={handleGenerateGridFromPin}
              generatingGrid={generatingGrid}
            />
          </div>

          <RiskLegend
            activeLayer={activeLayer}
            onLayerChange={setActiveLayer}
            showVillages={showVillages}
            onToggleVillages={() => setShowVillages(!showVillages)}
            showGlcMarkers={showGlcMarkers}
            onToggleGlc={() => setShowGlcMarkers(!showGlcMarkers)}
          />
        </div>

        {/* Right Sidebar: Lead Time & Explainability */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <LeadTimePanel leadTime={leadTime} />

          <ContributingFactorPanel
            pointDetail={selectedPoint}
            selectedVillage={selectedVillage}
            onClear={() => {
              setSelectedPoint(null);
              setSelectedVillage(null);
            }}
          />
        </div>
      </main>

      {/* Bottom Full-Width Alerts Table */}
      <section style={{ padding: "0 24px 24px" }}>
        <AlertsTable
          alerts={alerts}
          villages={villages}
          onSelectVillage={handleSelectVillage}
          selectedVillageId={selectedVillage?.village_id}
        />
      </section>

      {/* Modals */}
      {showBacktestModal && (
        <BacktestModal
          data={backtestData}
          onClose={() => setShowBacktestModal(false)}
        />
      )}

      {showProvenanceModal && (
        <ProvenancePanel
          onClose={() => setShowProvenanceModal(false)}
        />
      )}

      {showExportModal && (
        <ExportReportModal
          onClose={() => setShowExportModal(false)}
        />
      )}
    </div>
  );
};
