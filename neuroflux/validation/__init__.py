"""Phase 2: 3D Validation Pipeline for NeuroFlux.

This module integrates all external solvers (Gmsh, Elmer, Palace, Thermal FEA)
into a unified validation workflow that can be triggered from the design engine.
"""

from neuroflux.validation.pipeline import ValidationPipeline, ValidationResult, ValidationSpec

__all__ = ["ValidationPipeline", "ValidationResult", "ValidationSpec"]
