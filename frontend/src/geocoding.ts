/**
 * Geocoding and Reverse-Geocoding Service for TerraSharp.
 * Utilizes OpenStreetMap-based Photon API with Nominatim fallback.
 * 100% Free, Zero API Keys, CORS-enabled, In-Memory Cached.
 */

export interface GeocodingResult {
  id: string;
  name: string;
  display_name: string;
  lat: number;
  lon: number;
  type?: string;
  country?: string;
}

// In-memory caches to prevent redundant network calls
const searchCache = new Map<string, GeocodingResult[]>();
const reverseCache = new Map<string, string>();

/**
 * Format a clean place label from Photon feature properties
 */
function formatPhotonLabel(p: Record<string, any>): { name: string; display_name: string } {
  const primary = p.name || p.street || p.district || p.city || p.county || "Location";
  const parts: string[] = [];

  if (p.district && p.district !== primary) parts.push(p.district);
  if (p.city && p.city !== primary) parts.push(p.city);
  if (p.county && p.county !== primary && p.county !== p.city) parts.push(p.county);
  if (p.state) parts.push(p.state);
  if (p.country) parts.push(p.country);

  const secondary = parts.slice(0, 3).join(", ");
  const display_name = secondary ? `${primary}, ${secondary}` : primary;
  return { name: primary, display_name };
}

/**
 * Search places by text query (villages, towns, cities, districts, landmarks)
 */
export async function searchPlaces(query: string): Promise<GeocodingResult[]> {
  const clean = query.trim();
  if (clean.length < 2) return [];

  const cacheKey = clean.toLowerCase();
  if (searchCache.has(cacheKey)) {
    return searchCache.get(cacheKey)!;
  }

  try {
    const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(clean)}&limit=6`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Photon search error: ${res.status}`);

    const data = await res.json();
    const results: GeocodingResult[] = (data.features || []).map((feat: any, idx: number) => {
      const coords = feat.geometry?.coordinates || [0, 0];
      const p = feat.properties || {};
      const { name, display_name } = formatPhotonLabel(p);
      return {
        id: `${p.osm_id || idx}-${coords[1]}-${coords[0]}`,
        name,
        display_name,
        lat: Number(coords[1]),
        lon: Number(coords[0]),
        type: p.type || p.osm_value,
        country: p.country,
      };
    });

    searchCache.set(cacheKey, results);
    return results;
  } catch (err) {
    console.warn("Photon search failed, trying fallback Nominatim...", err);
    try {
      const nomUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(clean)}&format=json&limit=5`;
      const nomRes = await fetch(nomUrl, {
        headers: { Accept: "application/json" },
      });
      if (!nomRes.ok) return [];
      const nomData = await nomRes.json();
      const results: GeocodingResult[] = nomData.map((item: any) => ({
        id: `nom-${item.place_id}`,
        name: item.name || item.display_name.split(",")[0],
        display_name: item.display_name,
        lat: parseFloat(item.lat),
        lon: parseFloat(item.lon),
        type: item.type,
      }));
      searchCache.set(cacheKey, results);
      return results;
    } catch (nomErr) {
      console.error("All geocoding services failed:", nomErr);
      return [];
    }
  }
}

/**
 * Reverse geocode a latitude/longitude coordinate to a human-readable place name.
 */
export async function reverseGeocode(lat: number, lon: number): Promise<string> {
  const roundedLat = Number(lat.toFixed(4));
  const roundedLon = Number(lon.toFixed(4));
  const cacheKey = `${roundedLat},${roundedLon}`;

  if (reverseCache.has(cacheKey)) {
    return reverseCache.get(cacheKey)!;
  }

  try {
    const url = `https://photon.komoot.io/reverse?lat=${roundedLat}&lon=${roundedLon}`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Photon reverse error: ${res.status}`);

    const data = await res.json();
    const feat = data.features?.[0];
    if (feat && feat.properties) {
      const { display_name } = formatPhotonLabel(feat.properties);
      if (display_name && display_name !== "Location") {
        reverseCache.set(cacheKey, display_name);
        return display_name;
      }
    }
  } catch (err) {
    console.warn("Photon reverse geocode failed, trying Nominatim...", err);
  }

  // Fallback to Nominatim
  try {
    const nomUrl = `https://nominatim.openstreetmap.org/reverse?lat=${roundedLat}&lon=${roundedLon}&format=json`;
    const nomRes = await fetch(nomUrl, { headers: { Accept: "application/json" } });
    if (nomRes.ok) {
      const nomData = await nomRes.json();
      if (nomData.display_name) {
        const parts = nomData.display_name.split(", ").slice(0, 4).join(", ");
        reverseCache.set(cacheKey, parts);
        return parts;
      }
    }
  } catch (nomErr) {
    console.warn("Nominatim reverse geocode failed:", nomErr);
  }

  // Graceful fallback to formatted coordinates
  const fallback = `${roundedLat.toFixed(4)}°, ${roundedLon.toFixed(4)}°`;
  reverseCache.set(cacheKey, fallback);
  return fallback;
}
