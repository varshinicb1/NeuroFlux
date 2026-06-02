"""Visualization and post-processing for NeuroFlux.

Integrates ParaView for 3D result visualization from:
- Thermal FEA3D VTK outputs
- Elmer FEM results
- Gmsh meshes
"""

from neuroflux.visualization.paraview_utils import ParaViewLauncher, ResultVisualizer

__all__ = ["ParaViewLauncher", "ResultVisualizer"]
