"""
Terrain processing modules: Slope, Aspect, and Drainage.
"""
from backend.app.terrain.slope import compute_slope_and_aspect
from backend.app.terrain.drainage import compute_d8_flow_accumulation

__all__ = [
    "compute_slope_and_aspect",
    "compute_d8_flow_accumulation",
]
