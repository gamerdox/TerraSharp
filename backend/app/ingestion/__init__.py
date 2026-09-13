"""
Data Ingestion modules for GPM IMERG, SRTM DEM, NASA GLC, and Administrative Boundaries.
"""
from backend.app.ingestion.nasa_gpm import IMERGIngestionClient
from backend.app.ingestion.dem_ingest import DEMIngestionClient
from backend.app.ingestion.glc_ingest import GLCIngestionClient
from backend.app.ingestion.boundaries import BoundaryIngestionClient

__all__ = [
    "IMERGIngestionClient",
    "DEMIngestionClient",
    "GLCIngestionClient",
    "BoundaryIngestionClient",
]
