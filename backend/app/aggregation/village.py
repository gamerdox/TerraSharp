"""
Village Aggregation Module.
Performs spatial overlay of analysis grid cells onto administrative village polygons,
computing mean risk, peak risk, and critical area proportions.
"""
from typing import Dict, Any, List, Tuple
import json
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, mapping

from backend.app.preprocessing.grid import AnalysisGrid
from backend.app.models.domain import RiskLevel, AlertState, HazardType
from backend.app.models.schemas import VillageRiskSummary, ContributingFactors
from backend.app.scoring.classifier import classify_risk_score
from backend.app.alerts.engine import determine_alert_state, get_recommended_action


def aggregate_grid_to_villages(
    villages_gdf: gpd.GeoDataFrame,
    grid: AnalysisGrid,
    landslide_risk_grid: np.ndarray,
    flash_flood_risk_grid: np.ndarray,
    rainfall_score_grid: np.ndarray,
    slope_norm_grid: np.ndarray,
    soil_proxy_grid: np.ndarray,
    history_norm_grid: np.ndarray,
) -> Tuple[List[VillageRiskSummary], Dict[str, Any]]:
    """
    Overlays 2D risk rasters onto village polygons and aggregates metrics.

    Returns:
      summaries: list of VillageRiskSummary objects
      enriched_geojson: GeoJSON FeatureCollection with attached risk properties
    """
    rows, cols = grid.rows, grid.cols
    lons = grid.lons
    lats = grid.lats

    # Convert grid cell centers to a point array
    lon_mesh, lat_mesh = grid.lon_grid, grid.lat_grid
    points_flat = [Point(x, y) for x, y in zip(lon_mesh.ravel(), lat_mesh.ravel())]
    grid_points_gdf = gpd.GeoDataFrame(
        {
            "cell_idx": np.arange(len(points_flat)),
            "row": np.repeat(np.arange(rows), cols),
            "col": np.tile(np.arange(cols), rows),
        },
        geometry=points_flat,
        crs=grid.target_crs,
    )

    # Spatial join: match grid cells to villages
    joined = gpd.sjoin(grid_points_gdf, villages_gdf, how="inner", predicate="within")

    summaries: List[VillageRiskSummary] = []
    enriched_features = []

    for idx, village_row in villages_gdf.iterrows():
        v_id = village_row.get("village_id", f"V_{idx}")
        v_name = village_row.get("village_name", f"Village {idx}")
        geom = village_row.geometry
        centroid = geom.centroid

        # Filter cells falling inside this village
        v_cells = joined[joined["village_id"] == v_id] if "village_id" in joined.columns else joined[joined.index_right == idx]

        if len(v_cells) > 0:
            r_idx = v_cells["row"].values
            c_idx = v_cells["col"].values

            ls_vals = landslide_risk_grid[r_idx, c_idx]
            ff_vals = flash_flood_risk_grid[r_idx, c_idx]
            rain_vals = rainfall_score_grid[r_idx, c_idx]
            slope_vals = slope_norm_grid[r_idx, c_idx]
            soil_vals = soil_proxy_grid[r_idx, c_idx]
            hist_vals = history_norm_grid[r_idx, c_idx]

            mean_ls = float(np.mean(ls_vals))
            max_ls = float(np.max(ls_vals))
            mean_ff = float(np.mean(ff_vals))
            max_ff = float(np.max(ff_vals))
            critical_pct = float(np.sum(ls_vals >= 0.75) / len(ls_vals) * 100)

            # Determine dominant factor
            avg_rain = float(np.mean(rain_vals))
            avg_slope = float(np.mean(slope_vals))
            avg_soil = float(np.mean(soil_vals))
            avg_hist = float(np.mean(hist_vals))

            factors = {
                "Rainfall": avg_rain * 0.35,
                "Slope Steepness": avg_slope * 0.30,
                "Soil Saturation (Proxy)": avg_soil * 0.20,
                "Historical Hazard": avg_hist * 0.15,
            }
            dominant_factor = max(factors, key=factors.get)

        else:
            # Fallback if village polygon is smaller than cell center spacing: sample centroid
            c = int(np.clip((centroid.x - grid.min_lon) / grid.resolution_deg, 0, cols - 1))
            r = int(np.clip((grid.max_lat - centroid.y) / grid.resolution_deg, 0, rows - 1))

            mean_ls = max_ls = float(landslide_risk_grid[r, c])
            mean_ff = max_ff = float(flash_flood_risk_grid[r, c])
            critical_pct = 100.0 if mean_ls >= 0.75 else 0.0
            dominant_factor = "Terrain & Rainfall"

        # Determine overall village alert state using conservative peak risk
        alert_state = determine_alert_state(max_ls)
        risk_class = classify_risk_score(max_ls)
        hazard = HazardType.LANDSLIDE if max_ls >= max_ff else HazardType.FLASH_FLOOD
        rec_action = get_recommended_action(hazard, alert_state)

        # Approximate area in sq km
        area_sqkm = round(float(geom.area * 111.0 * 111.0), 2)  # rough deg to km conversion

        summary = VillageRiskSummary(
            village_id=str(v_id),
            name=str(v_name),
            area_sqkm=area_sqkm,
            mean_landslide_risk=round(mean_ls, 3),
            max_landslide_risk=round(max_ls, 3),
            mean_flash_flood_risk=round(mean_ff, 3),
            max_flash_flood_risk=round(max_ff, 3),
            risk_class=risk_class,
            alert_state=alert_state,
            critical_area_pct=round(critical_pct, 1),
            dominant_factor=dominant_factor,
            recommended_action=rec_action,
            coordinates_center={"lon": round(float(centroid.x), 4), "lat": round(float(centroid.y), 4)},
        )
        summaries.append(summary)

        # Enriched GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                **village_row.to_dict(),
                "geometry": None,  # avoid duplicate geometry field in properties
                "mean_landslide_risk": round(mean_ls, 3),
                "max_landslide_risk": round(max_ls, 3),
                "mean_flash_flood_risk": round(mean_ff, 3),
                "max_flash_flood_risk": round(max_ff, 3),
                "risk_class": risk_class.value,
                "alert_state": alert_state.value,
                "critical_area_pct": round(critical_pct, 1),
                "dominant_factor": dominant_factor,
                "recommended_action": rec_action,
            },
        }
        # Clean non-serializable objects from properties
        cleaned_props = {k: v for k, v in feature["properties"].items() if k != "geometry" and not isinstance(v, (np.generic,))}
        feature["properties"] = cleaned_props
        enriched_features.append(feature)

    enriched_geojson = {
        "type": "FeatureCollection",
        "features": enriched_features,
    }

    return summaries, enriched_geojson
