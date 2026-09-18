"""
Domain constants, enumerations, and provenance tags for scientific honesty.
"""
from enum import Enum


class ProvenanceTag(str, Enum):
    OBSERVED = "OBSERVED"        # Directly measured physical observation (e.g. Ground station, satellite sensor)
    DERIVED = "DERIVED"          # Geometrically or mathematically computed from elevation (e.g. slope, flow accumulation)
    INTERPOLATED = "INTERPOLATED"# Spatially or temporally re-gridded across unmeasured points
    PROXY = "PROXY"              # Indirect physical estimator (e.g. Antecedent Rainfall for Soil Saturation)
    MODELLED = "MODELLED"        # Output of empirical/weighted risk index formula
    ESTIMATED = "ESTIMATED"      # Projected forward in time under dynamic trend (e.g. Lead Time)
    SIMULATED = "SIMULATED"      # Procedurally generated or test fixture (MUST NEVER be called LIVE)
    DEMO = "DEMO"                # Deterministic cached historical scenario
    SYNTHETIC = "SYNTHETIC"      # Synthetic fallback (legacy alias for SIMULATED)
    CACHED = "CACHED"            # Freshness-validated local store with source timestamp
    UNAVAILABLE = "UNAVAILABLE"  # Upstream source offline/unreachable
    ERROR = "ERROR"              # Computation or numerical boundary failure


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
    RECOVERY = "RECOVERY"


class HazardType(str, Enum):
    LANDSLIDE = "LANDSLIDE"
    FLASH_FLOOD = "FLASH_FLOOD"
    MULTI_HAZARD = "MULTI_HAZARD"


class EmailStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    QUEUED = "QUEUED"
    SIMULATED = "SIMULATED"
    RETRYING = "RETRYING"
    SUPPRESSED_COOLDOWN = "SUPPRESSED_COOLDOWN"


class DataFreshnessStatus(str, Enum):
    LIVE = "LIVE"
    CACHED = "CACHED"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"

