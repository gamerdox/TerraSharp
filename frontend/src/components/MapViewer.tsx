import React, { useEffect, useRef } from "react";
import L from "leaflet";
import { GridCell, VillageRiskSummary, PointRiskDetail } from "../types";
import { ActiveRasterLayer } from "./RiskLegend";

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
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  const gridLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const villageLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());
  const glcLayerGroupRef = useRef<L.LayerGroup>(L.layerGroup());

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

      // Clean dark CartoDB basemap
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; OpenStreetMap',
        maxZoom: 19,
      }).addTo(map);

      gridLayerGroupRef.current.addTo(map);
      villageLayerGroupRef.current.addTo(map);
      glcLayerGroupRef.current.addTo(map);

      map.on("click", (e: L.LeafletMouseEvent) => {
        onMapClick(e.latlng.lat, e.latlng.lng);
      });

      mapInstanceRef.current = map;
    }

    return () => {
      // clean-up if unmounted
    };
  }, []);

  // Update center & zoom when AOI changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([center.lat, center.lon], zoom, { animate: true });
    }
  }, [center.lat, center.lon, zoom]);

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

  return (
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
  );
};
