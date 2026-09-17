import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { GridCell, VillageRiskSummary } from "../types";
import { ActiveRasterLayer } from "./RiskLegend";
import { LocationSelectionBar } from "./LocationSelectionBar";

interface MapViewerProps {
  center: { lat: number; lon: number };
  zoom: number;
  cells: GridCell[];
  villagesGeoJson: any;
  glcEvents: any[];
  activeLayer: ActiveRasterLayer;
  showVillages: boolean;
  showGlcMarkers: boolean;
  onMapClick: (lat: number, lon: number) => void;
  onSelectVillage: (village: VillageRiskSummary) => void;
  selectedVillage: VillageRiskSummary | null;
  pinnedLocation?: { lat: number; lon: number } | null;
  onPinLocation?: (lat: number, lon: number, placeName?: string) => void;
}

export const MapViewer: React.FC<MapViewerProps> = ({
  center,
  zoom,
  cells,
  villagesGeoJson,
  glcEvents,
  activeLayer,
  showVillages,
  showGlcMarkers,
  onMapClick,
  onSelectVillage,
  selectedVillage,
  pinnedLocation,
  onPinLocation,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  const baseLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const gridLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const villageLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const glcLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const pinnedLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());

  // Basemap options: dark (Esri Dark Canvas), satellite (Esri World Imagery), osm (OpenStreetMap)
  const [basemap, setBasemap] = useState<"dark" | "satellite" | "osm">("dark");

  // Helper for color scale based on value [0, 1]
  const getColorForVal = (val: number): string => {
    if (val < 0.25) return "#22c55e"; // Low - green
    if (val < 0.50) return "#eab308"; // Moderate - yellow
    if (val < 0.75) return "#f97316"; // High - orange
    return "#ef4444"; // Very High - red
  };

  // Helper for layer-specific value normalization
  const getCellLayerValue = (cell: GridCell, layer: ActiveRasterLayer): number => {
    switch (layer) {
      case "landslide": return cell.landslide_risk;
      case "flash_flood": return cell.flash_flood_risk;
      case "slope": return Math.min(cell.slope_deg / 50.0, 1.0);
      case "rainfall": return Math.min(cell.rainfall_24h_mm / 250.0, 1.0);
      case "soil_proxy": return cell.soil_proxy;
      default: return cell.landslide_risk;
    }
  };

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [center.lat, center.lon],
        zoom: zoom,
        zoomControl: false,
      });

      L.control.zoom({ position: "bottomright" }).addTo(map);

      baseLayerGroupRef.current.addTo(map);
      gridLayerGroupRef.current.addTo(map);
      villageLayerGroupRef.current.addTo(map);
      glcLayerGroupRef.current.addTo(map);
      pinnedLayerGroupRef.current.addTo(map);

      map.on("click", (e: L.LeafletMouseEvent) => {
        onMapClick(e.latlng.lat, e.latlng.lng);
      });

      mapInstanceRef.current = map;
    }
  }, []);

  // Update center & zoom when AOI changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([center.lat, center.lon], zoom, { animate: true });
    }
  }, [center.lat, center.lon, zoom]);

  // Update Basemap Tiles (100% Free, NO API Key, NO Watermarks)
  useEffect(() => {
    const group = baseLayerGroupRef.current;
    group.clearLayers();

    if (basemap === "satellite") {
      // Esri World Imagery (High-Res Satellite)
      const satLayer = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        {
          attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS",
          maxZoom: 19,
        }
      );
      group.addLayer(satLayer);

      // Add hybrid reference overlay for place names, borders, and roads
      const satLabels = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 19,
        }
      );
      group.addLayer(satLabels);
    } else if (basemap === "osm") {
      // Standard OpenStreetMap
      const osmLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      });
      group.addLayer(osmLayer);
    } else {
      // Esri World Dark Gray Canvas (Sleek dark theme, zero watermark, zero key required)
      const darkBase = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        {
          attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
          maxZoom: 16,
        }
      );
      const darkRef = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 16,
        }
      );
      group.addLayer(darkBase);
      group.addLayer(darkRef);
    }
  }, [basemap]);

  // Render Grid Cells Heatmap
  useEffect(() => {
    const group = gridLayerGroupRef.current;
    group.clearLayers();

    if (!cells || cells.length === 0) return;

    // Fixed cell size ~0.01 degree (~1100m)
    const halfSize = 0.005;

    cells.forEach((c) => {
      const val = getCellLayerValue(c, activeLayer);
      const color = getColorForVal(val);

      const bounds: L.LatLngBoundsLiteral = [
        [c.lat - halfSize, c.lon - halfSize],
        [c.lat + halfSize, c.lon + halfSize],
      ];

      const rect = L.rectangle(bounds, {
        color: color,
        weight: 0.5,
        fillColor: color,
        fillOpacity: 0.45,
      });

      rect.bindTooltip(
        `<div style="font-size:12px;">
          <strong>${activeLayer.toUpperCase()}</strong>: ${(val * 100).toFixed(0)}%<br/>
          Elev: ${c.elevation_m}m | Slope: ${c.slope_deg}°<br/>
          Rain 24h: ${c.rainfall_24h_mm}mm | Soil Proxy: ${(c.soil_proxy * 100).toFixed(0)}%
        </div>`,
        { sticky: true }
      );

      rect.on("click", (e) => {
        L.DomEvent.stopPropagation(e);
        onMapClick(c.lat, c.lon);
      });

      group.addLayer(rect);
    });
  }, [cells, activeLayer]);

  // Render Village Boundaries
  useEffect(() => {
    const group = villageLayerGroupRef.current;
    group.clearLayers();

    if (!showVillages || !villagesGeoJson) return;

    const geoLayer = L.geoJSON(villagesGeoJson, {
      style: (feature) => {
        const p = feature?.properties;
        const isSelected = selectedVillage && selectedVillage.village_id === p?.village_id;
        const state = p?.alert_state || "NORMAL";
        let strokeColor = "#38bdf8";
        if (state === "CRITICAL") strokeColor = "#ef4444";
        else if (state === "WARNING") strokeColor = "#f97316";

        return {
          color: isSelected ? "#ffffff" : strokeColor,
          weight: isSelected ? 3.5 : 2.0,
          dashArray: isSelected ? undefined : "3, 4",
          fillColor: strokeColor,
          fillOpacity: 0.12,
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindTooltip(
          `<div style="font-size:12px;">
            <strong>${p.village_name || p.name}</strong> (${p.alert_state})<br/>
            Peak LS Risk: ${p.max_landslide_risk ?? 'N/A'}<br/>
            Pop: ${p.population ? p.population.toLocaleString() : 'N/A'}
          </div>`,
          { sticky: true }
        );

        layer.on("click", (e) => {
          L.DomEvent.stopPropagation(e);
          if (p.village_id) {
            onSelectVillage({
              village_id: p.village_id,
              name: p.village_name || p.name,
              area_sqkm: p.area_sqkm || 15.0,
              mean_landslide_risk: p.mean_landslide_risk || 0.5,
              max_landslide_risk: p.max_landslide_risk || 0.7,
              mean_flash_flood_risk: p.mean_flash_flood_risk || 0.4,
              max_flash_flood_risk: p.max_flash_flood_risk || 0.5,
              risk_class: p.risk_class || "HIGH",
              alert_state: p.alert_state || "WARNING",
              critical_area_pct: p.critical_area_pct || 20.0,
              dominant_factor: p.dominant_factor || "Heavy Rainfall",
              recommended_action: p.recommended_action || "Maintain vigilance.",
              coordinates_center: { lat: 0, lon: 0 },
            });
          }
        });
      },
    });

    group.addLayer(geoLayer);
  }, [showVillages, villagesGeoJson, selectedVillage]);

  // Render NASA GLC Historical Landslide Points
  useEffect(() => {
    const group = glcLayerGroupRef.current;
    group.clearLayers();

    if (!showGlcMarkers || !glcEvents) return;

    glcEvents.forEach((ev) => {
      const coords = ev.geometry ? ev.geometry.coordinates : ev.coordinates;
      if (!coords || coords.length !== 2) return;
      const [lon, lat] = coords;
      const p = ev.properties || ev;

      const marker = L.circleMarker([lat, lon], {
        radius: 7,
        fillColor: "#ef4444",
        color: "#ffffff",
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.9,
      });

      marker.bindPopup(
        `<div style="font-size:12px; line-height:1.4;">
          <strong style="color:#ef4444;">NASA GLC Historical Event</strong><br/>
          <strong>Date:</strong> ${p.date || 'Unknown'}<br/>
          <strong>Location:</strong> ${p.location || 'AOI'}<br/>
          <strong>Category:</strong> ${p.landslide_category || 'Debris flow'}<br/>
          <strong>Fatalities:</strong> ${p.fatalities ?? 0}<br/>
          <strong>Trigger:</strong> ${p.trigger || 'Rainfall'}
        </div>`
      );

      group.addLayer(marker);
    });
  }, [showGlcMarkers, glcEvents]);

  // Render Pinned Location Marker
  useEffect(() => {
    const group = pinnedLayerGroupRef.current;
    group.clearLayers();

    if (!pinnedLocation) return;

    const pinIcon = L.divIcon({
      className: "custom-pinned-marker",
      html: `
        <div style="position:relative; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:grab;">
          <span style="position:absolute; width:34px; height:34px; border-radius:50%; background:rgba(244,63,94,0.45); animation:ping 1.4s cubic-bezier(0,0,0.2,1) infinite;"></span>
          <span style="position:relative; width:16px; height:16px; border-radius:50%; background:#f43f5e; border:2px solid white; box-shadow:0 0 14px rgba(244,63,94,0.9);"></span>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });

    const marker = L.marker([pinnedLocation.lat, pinnedLocation.lon], {
      icon: pinIcon,
      draggable: true,
    });

    marker.bindTooltip(
      `<div style="font-size:12px; font-weight:bold;">
        📍 DRAGGABLE PIN: ${pinnedLocation.lat.toFixed(4)}°, ${pinnedLocation.lon.toFixed(4)}°
        <div style="font-size:10px; font-weight:normal; opacity:0.85; margin-top:2px;">
          Drag anywhere to analyze new coordinates
        </div>
      </div>`,
      { permanent: false, direction: "top", offset: [0, -12] }
    );

    marker.on("dragend", (e: L.LeafletEvent) => {
      const latlng = (e.target as L.Marker).getLatLng();
      if (onPinLocation) onPinLocation(latlng.lat, latlng.lng);
      onMapClick(latlng.lat, latlng.lng);
    });

    group.addLayer(marker);
  }, [pinnedLocation]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: "450px" }}>
      {/* Map Container */}
      <div
        ref={mapContainerRef}
        style={{
          width: "100%",
          height: "100%",
          minHeight: "450px",
          borderRadius: "8px",
          overflow: "hidden",
          border: "1px solid var(--border-color)",
        }}
      />

      {/* 3-Way Synchronized Location Selection Bar (Top Left / Center) */}
      <div
        style={{
          position: "absolute",
          top: "12px",
          left: "12px",
          right: "210px",
          maxWidth: "700px",
          zIndex: 1000,
        }}
      >
        <LocationSelectionBar
          currentLocation={pinnedLocation || null}
          onLocationChange={(lat, lon, placeName) => {
            if (mapInstanceRef.current) {
              mapInstanceRef.current.flyTo(
                [lat, lon],
                Math.max(mapInstanceRef.current.getZoom(), 11),
                { animate: true }
              );
            }
            if (onPinLocation) onPinLocation(lat, lon, placeName);
            onMapClick(lat, lon);
          }}
        />
      </div>

      {/* Floating Basemap Selector (Top Right) */}
      <div
        style={{
          position: "absolute",
          top: "12px",
          right: "12px",
          zIndex: 1000,
          backgroundColor: "rgba(15, 23, 42, 0.85)",
          backdropFilter: "blur(4px)",
          border: "1px solid var(--border-color)",
          borderRadius: "6px",
          padding: "4px",
          display: "flex",
          gap: "4px",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.4)",
        }}
      >
        <button
          onClick={() => setBasemap("dark")}
          style={{
            padding: "4px 8px",
            fontSize: "11px",
            fontWeight: "600",
            borderRadius: "4px",
            border: "none",
            cursor: "pointer",
            backgroundColor: basemap === "dark" ? "#2563eb" : "transparent",
            color: basemap === "dark" ? "#ffffff" : "var(--text-secondary)",
          }}
          title="Dark Canvas (No Key Required)"
        >
          🌙 Dark
        </button>
        <button
          onClick={() => setBasemap("satellite")}
          style={{
            padding: "4px 8px",
            fontSize: "11px",
            fontWeight: "600",
            borderRadius: "4px",
            border: "none",
            cursor: "pointer",
            backgroundColor: basemap === "satellite" ? "#2563eb" : "transparent",
            color: basemap === "satellite" ? "#ffffff" : "var(--text-secondary)",
          }}
          title="Esri Satellite Imagery (No Key Required)"
        >
          🛰️ Satellite
        </button>
        <button
          onClick={() => setBasemap("osm")}
          style={{
            padding: "4px 8px",
            fontSize: "11px",
            fontWeight: "600",
            borderRadius: "4px",
            border: "none",
            cursor: "pointer",
            backgroundColor: basemap === "osm" ? "#2563eb" : "transparent",
            color: basemap === "osm" ? "#ffffff" : "var(--text-secondary)",
          }}
          title="OpenStreetMap Streets (No Key Required)"
        >
          🗺️ Streets
        </button>
      </div>
    </div>
  );
};
