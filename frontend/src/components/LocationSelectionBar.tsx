import React, { useState, useEffect, useRef } from "react";
import { Search, MapPin, Navigation, X, Loader2, Check } from "lucide-react";
import { searchPlaces, reverseGeocode, GeocodingResult } from "../geocoding";

interface LocationSelectionBarProps {
  currentLocation: { lat: number; lon: number } | null;
  onLocationChange: (lat: number, lon: number, placeName?: string) => void;
  disabled?: boolean;
}

const PRESETS = [
  { name: "Wayanad", lat: 11.5524, lon: 76.1532 },
  { name: "Chamoli", lat: 30.4500, lon: 79.4500 },
  { name: "Munnar", lat: 10.0889, lon: 77.0595 },
  { name: "Shimla", lat: 31.1048, lon: 77.1734 },
  { name: "Darjeeling", lat: 27.0410, lon: 88.2663 },
];

export const LocationSelectionBar: React.FC<LocationSelectionBarProps> = ({
  currentLocation,
  onLocationChange,
  disabled = false,
}) => {
  // Input states
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<GeocodingResult[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showDropdown, setShowDropdown] = useState<boolean>(false);

  // Coordinate direct inputs
  const [latInput, setLatInput] = useState<string>(
    currentLocation ? currentLocation.lat.toFixed(4) : ""
  );
  const [lonInput, setLonInput] = useState<string>(
    currentLocation ? currentLocation.lon.toFixed(4) : ""
  );
  const [coordError, setCoordError] = useState<string | null>(null);

  // Place name state
  const [placeLabel, setPlaceLabel] = useState<string>("");
  const [isReverseGeocoding, setIsReverseGeocoding] = useState<boolean>(false);

  // Geolocation state
  const [isLocating, setIsLocating] = useState<boolean>(false);

  const searchTimerRef = useRef<any>(null);
  const reverseTimerRef = useRef<any>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Sync inputs whenever currentLocation changes externally (e.g. from map click or drag)
  useEffect(() => {
    if (currentLocation) {
      setLatInput(currentLocation.lat.toFixed(4));
      setLonInput(currentLocation.lon.toFixed(4));
      setCoordError(null);

      // Trigger debounced reverse-geocoding to display nearest place name
      clearTimeout(reverseTimerRef.current);
      setIsReverseGeocoding(true);
      reverseTimerRef.current = setTimeout(async () => {
        try {
          const name = await reverseGeocode(currentLocation.lat, currentLocation.lon);
          setPlaceLabel(name);
        } catch {
          setPlaceLabel(`${currentLocation.lat.toFixed(4)}°, ${currentLocation.lon.toFixed(4)}°`);
        } finally {
          setIsReverseGeocoding(false);
        }
      }, 350);
    }
    return () => clearTimeout(reverseTimerRef.current);
  }, [currentLocation?.lat, currentLocation?.lon]);

  // Click outside listener for search dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle Search Input Change with Debounce
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value;
    setSearchQuery(q);
    clearTimeout(searchTimerRef.current);

    if (q.trim().length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    searchTimerRef.current = setTimeout(async () => {
      try {
        const results = await searchPlaces(q);
        setSearchResults(results);
        setShowDropdown(results.length > 0);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setIsSearching(false);
      }
    }, 280);
  };

  // Select item from search dropdown
  const handleSelectResult = (res: GeocodingResult) => {
    setSearchQuery(res.name);
    setPlaceLabel(res.display_name);
    setShowDropdown(false);
    setLatInput(res.lat.toFixed(4));
    setLonInput(res.lon.toFixed(4));
    setCoordError(null);
    onLocationChange(res.lat, res.lon, res.display_name);
  };

  // Validate & Apply Manual Coordinate Inputs
  const handleApplyCoordinates = () => {
    const lat = parseFloat(latInput);
    const lon = parseFloat(lonInput);

    if (isNaN(lat) || isNaN(lon)) {
      setCoordError("Invalid numbers");
      return;
    }
    if (lat < -90 || lat > 90) {
      setCoordError("Lat must be -90 to 90");
      return;
    }
    if (lon < -180 || lon > 180) {
      setCoordError("Lon must be -180 to 180");
      return;
    }

    setCoordError(null);
    onLocationChange(lat, lon);
  };

  // Use My Location (Browser Geolocation API)
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setCoordError("Geolocation not supported by browser");
      return;
    }

    setIsLocating(true);
    setCoordError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false);
        const { latitude, longitude } = pos.coords;
        setLatInput(latitude.toFixed(4));
        setLonInput(longitude.toFixed(4));
        onLocationChange(latitude, longitude);
      },
      (err) => {
        setIsLocating(false);
        console.warn("Geolocation error:", err);
        setCoordError(err.message || "Location access denied");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "6px",
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        backdropFilter: "blur(8px)",
        border: "1px solid var(--border-color)",
        borderRadius: "8px",
        padding: "8px 12px",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
      }}
    >
      {/* Primary Row: Place Search + Lat/Lon Inputs + My Location */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        {/* Modality 1: Place Search with Autocomplete */}
        <div ref={dropdownRef} style={{ position: "relative", flex: "1 1 240px", minWidth: "200px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              backgroundColor: "#0b1329",
              border: "1px solid #334155",
              borderRadius: "6px",
              padding: "4px 8px",
              gap: "6px",
            }}
          >
            {isSearching ? (
              <Loader2 size={15} className="animate-spin" color="#38bdf8" />
            ) : (
              <Search size={15} color="#94a3b8" />
            )}
            <input
              type="text"
              placeholder={placeLabel ? `📍 ${placeLabel}` : "Search village, city, district, landmark..."}
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => {
                if (searchResults.length > 0) setShowDropdown(true);
              }}
              disabled={disabled}
              style={{
                background: "transparent",
                border: "none",
                color: "#f8fafc",
                fontSize: "12px",
                width: "100%",
                outline: "none",
              }}
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery("");
                  setSearchResults([]);
                  setShowDropdown(false);
                }}
                style={{ background: "transparent", border: "none", color: "#64748b", cursor: "pointer", padding: "2px" }}
              >
                <X size={13} />
              </button>
            )}
          </div>

          {/* Autocomplete Dropdown */}
          {showDropdown && searchResults.length > 0 && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 4px)",
                left: 0,
                right: 0,
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "6px",
                boxShadow: "0 10px 25px rgba(0,0,0,0.8)",
                zIndex: 3000,
                maxHeight: "220px",
                overflowY: "auto",
              }}
            >
              {searchResults.map((res) => (
                <div
                  key={res.id}
                  onClick={() => handleSelectResult(res)}
                  style={{
                    padding: "8px 10px",
                    cursor: "pointer",
                    borderBottom: "1px solid rgba(51, 65, 85, 0.4)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "2px",
                    transition: "background 0.15s",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#1e293b")}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", fontWeight: "600", color: "#f8fafc" }}>
                    <MapPin size={13} color="#f43f5e" />
                    <span>{res.name}</span>
                    {res.type && (
                      <span style={{ fontSize: "10px", color: "#38bdf8", backgroundColor: "rgba(56,189,248,0.1)", padding: "1px 5px", borderRadius: "3px" }}>
                        {res.type}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", paddingLeft: "19px" }}>
                    {res.display_name}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modality 2: Direct Coordinates (Lat & Lon) */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "nowrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "4px", backgroundColor: "#0b1329", border: "1px solid #334155", borderRadius: "6px", padding: "4px 8px" }}>
            <span style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>LAT:</span>
            <input
              type="text"
              value={latInput}
              onChange={(e) => setLatInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleApplyCoordinates();
              }}
              onBlur={handleApplyCoordinates}
              placeholder="11.5524"
              disabled={disabled}
              style={{
                background: "transparent",
                border: "none",
                color: "#38bdf8",
                fontSize: "12px",
                fontFamily: "monospace",
                width: "68px",
                outline: "none",
                fontWeight: "600",
              }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "4px", backgroundColor: "#0b1329", border: "1px solid #334155", borderRadius: "6px", padding: "4px 8px" }}>
            <span style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>LON:</span>
            <input
              type="text"
              value={lonInput}
              onChange={(e) => setLonInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleApplyCoordinates();
              }}
              onBlur={handleApplyCoordinates}
              placeholder="76.1532"
              disabled={disabled}
              style={{
                background: "transparent",
                border: "none",
                color: "#38bdf8",
                fontSize: "12px",
                fontFamily: "monospace",
                width: "68px",
                outline: "none",
                fontWeight: "600",
              }}
            />
          </div>

          <button
            onClick={handleApplyCoordinates}
            disabled={disabled}
            style={{
              padding: "5px 9px",
              fontSize: "11px",
              fontWeight: "600",
              borderRadius: "6px",
              border: "none",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
            title="Apply exact coordinates and move pin"
          >
            <Check size={12} />
            <span>Go</span>
          </button>
        </div>

        {/* Modality 3: Use My Location */}
        <button
          onClick={handleUseMyLocation}
          disabled={disabled || isLocating}
          style={{
            padding: "5px 10px",
            fontSize: "11px",
            fontWeight: "600",
            borderRadius: "6px",
            border: "1px solid #334155",
            backgroundColor: "rgba(30, 41, 59, 0.8)",
            color: "#f8fafc",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "5px",
            transition: "background 0.2s",
          }}
          title="Detect and jump to your current GPS position"
        >
          {isLocating ? (
            <Loader2 size={13} className="animate-spin" color="#38bdf8" />
          ) : (
            <Navigation size={13} color="#38bdf8" />
          )}
          <span>{isLocating ? "Locating..." : "My Location"}</span>
        </button>
      </div>

      {/* Secondary Sub-Row: Resolved Place Badge + Error Notice + Quick Presets */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "6px" }}>
        {/* Place Resolution Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "#94a3b8" }}>
          {isReverseGeocoding ? (
            <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#38bdf8" }}>
              <Loader2 size={11} className="animate-spin" /> Resolving place name...
            </span>
          ) : placeLabel ? (
            <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#e2e8f0" }}>
              <span style={{ color: "#f43f5e" }}>📍</span>
              <strong>{placeLabel}</strong>
            </span>
          ) : (
            <span>Drag pin or click map anywhere to analyze</span>
          )}
          {coordError && (
            <span style={{ color: "#f87171", fontWeight: "600", marginLeft: "6px" }}>
              ⚠️ {coordError}
            </span>
          )}
        </div>

        {/* Quick Presets */}
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase", fontWeight: "700" }}>
            Quick:
          </span>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              onClick={() => {
                setPlaceLabel(p.name);
                setLatInput(p.lat.toFixed(4));
                setLonInput(p.lon.toFixed(4));
                setCoordError(null);
                onLocationChange(p.lat, p.lon, p.name);
              }}
              disabled={disabled}
              style={{
                padding: "2px 6px",
                fontSize: "10px",
                borderRadius: "4px",
                border: "1px solid #334155",
                backgroundColor: "rgba(15, 23, 42, 0.7)",
                color: "#94a3b8",
                cursor: "pointer",
              }}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
