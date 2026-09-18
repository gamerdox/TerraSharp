"""
Configuration module for SH-304 Early Warning System.
Loads environment variables and YAML configurations.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "configs"
DATA_DIR = BASE_DIR / "data"

# Automatically load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class BoundingBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class AOIConfig(BaseModel):
    name: str
    description: str
    bbox: BoundingBox
    center: Dict[str, float]
    default_zoom: int
    utm_epsg: int
    elevation_range: list[float]


class Settings:
    def __init__(self):
        self.app_name: str = os.getenv("APP_NAME", "SH-304 Hyper-Local Landslide & Flash-Flood Early Warning System")
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.mode: str = os.getenv("MODE", "live").lower()  # 'live' or 'demo'
        self.earthdata_username: str = os.getenv("EARTHDATA_USERNAME", "")
        self.earthdata_password: str = os.getenv("EARTHDATA_PASSWORD", "")
        self.default_aoi: str = os.getenv("DEFAULT_AOI", "wayanad")
        self.grid_res_deg: float = float(os.getenv("ANALYSIS_GRID_RESOLUTION_DEG", "0.01"))

        self.data_raw_dir: Path = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
        self.data_processed_dir: Path = BASE_DIR / os.getenv("DATA_PROCESSED_DIR", "data/processed")
        self.data_cache_dir: Path = BASE_DIR / os.getenv("DATA_CACHE_DIR", "data/cache")
        self.data_demo_dir: Path = BASE_DIR / os.getenv("DATA_DEMO_DIR", "data/demo")
        self.data_live_dir: Path = BASE_DIR / os.getenv("DATA_LIVE_DIR", "data/live")

        # Cache durations for live API-fetched data
        self.live_dem_cache_hours: float = float(os.getenv("LIVE_DEM_CACHE_HOURS", "24.0"))
        self.live_rainfall_cache_hours: float = float(os.getenv("LIVE_RAINFALL_CACHE_HOURS", "6.0"))

        self.config_version: str = os.getenv("CONFIG_VERSION", "1.0.0")
        self.model_version: str = os.getenv("MODEL_VERSION", "1.0.0")

        # SMTP & Real Email Alert Dispatch Settings
        self.smtp_host: str = os.getenv("SMTP_HOST", "")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user: str = os.getenv("SMTP_USER", "")
        self.smtp_password: str = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from: str = os.getenv("SMTP_FROM", "alerts@terrasharp.org")
        self.smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.smtp_timeout_seconds: float = float(os.getenv("SMTP_TIMEOUT_SECONDS", "10.0"))
        
        # Recipients (comma-separated in .env)
        raw_recipients = os.getenv("ALERT_RECIPIENT_EMAILS", "disaster-response@kerala.gov.in,district-collector@wayanad.nic.in")
        self.alert_recipient_emails: list[str] = [e.strip() for e in raw_recipients.split(",") if e.strip()]

        # Alert Engine Dynamics
        self.alert_email_enabled: bool = os.getenv("ALERT_EMAIL_ENABLED", "true").lower() == "true"
        self.alert_cooldown_seconds: float = float(os.getenv("ALERT_COOLDOWN_SECONDS", "1800.0"))  # 30 mins
        self.alert_persistence_cycles: int = int(os.getenv("ALERT_PERSISTENCE_CYCLES", "1"))

        # Load YAML configs
        self.default_config: Dict[str, Any] = self._load_yaml(CONFIG_DIR / "default_config.yaml")
        self.risk_weights: Dict[str, Any] = self._load_yaml(CONFIG_DIR / "risk_weights.yaml")

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_aoi_config(self, aoi_key: Optional[str] = None) -> AOIConfig:
        key = aoi_key or self.default_aoi
        aois = self.default_config.get("aois", {})
        if key not in aois:
            key = "wayanad"
        aoi_data = aois[key]
        return AOIConfig(**aoi_data)


settings = Settings()
