"""
Core abstractions for NeuroFlux.

Contains the Engine protocol, shared data models, material database,
physical constants, and exception hierarchy.
"""

from neuroflux.core.constants import PhysicalConstants
from neuroflux.core.engine_base import Engine, EngineCapabilities, EngineMetadata
from neuroflux.core.exceptions import (
    ConvergenceError,
    EngineError,
    MaterialNotFoundError,
    TopologyNotSupportedError,
)
from neuroflux.core.models import (
    AFPMTopology,
    EngineResult,
    MachineGeometry,
    MagnetConfiguration,
    MagnetType,
    MaterialProperties,
    OperatingPoint,
    PlaneResult,
    WindingParameters,
)

__all__ = [
    "PhysicalConstants",
    "Engine",
    "EngineCapabilities",
    "EngineMetadata",
    "ConvergenceError",
    "EngineError",
    "MaterialNotFoundError",
    "TopologyNotSupportedError",
    "AFPMTopology",
    "EngineResult",
    "MachineGeometry",
    "MagnetConfiguration",
    "MagnetType",
    "MaterialProperties",
    "OperatingPoint",
    "PlaneResult",
    "WindingParameters",
]
