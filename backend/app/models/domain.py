"""
Domain constants, enumerations, and provenance tags for scientific honesty.
"""
from enum import Enum


class ProvenanceTag(str, Enum):
    OBSERVED = "OBSERVED"        # Directly measured physical observation (e.g. Ground station)
    DERIVED = "DERIVED"          # Geometrically or mathematically computed from elevation (e.g. slope, flow accumulation)
    PROXY = "PROXY"              # Indirect physical estimator (e.g. Antecedent Rainfall for Soil Saturation)
    MODELLED = "MODELLED"        # Output of empirical/weighted risk index formula
    ESTIMATED = "ESTIMATED"      # Projected forward in time under dynamic trend (e.g. Lead Time)
    DEMO = "DEMO"                # Deterministic synthetic or cached historical scenario
    SYNTHETIC = "SYNTHETIC"      # Procedurally generated or fallback proxy data


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AlertState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class HazardType(str, Enum):
    LANDSLIDE = "LANDSLIDE"
    FLASH_FLOOD = "FLASH_FLOOD"
    MULTI_HAZARD = "MULTI_HAZARD"
