"""CAD export and manipulation for NeuroFlux.

Integrates FreeCAD for:
- STEP file export for manufacturing
- Parametric CAD model generation
- Assembly export
"""

from neuroflux.cad.freecad_export import FreeCADExporter, STEPExportResult

__all__ = ["FreeCADExporter", "STEPExportResult"]
