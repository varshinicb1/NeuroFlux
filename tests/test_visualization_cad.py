"""Tests for ParaView visualization and FreeCAD CAD export."""

import pytest
from pathlib import Path

from neuroflux.core.config import ExternalToolConfig
from neuroflux.visualization import ParaViewLauncher, ResultVisualizer
from neuroflux.cad import FreeCADExporter, STEPExportResult


def test_paraview_launcher_detection():
    """Test ParaView detection via ExternalToolConfig."""
    config = ExternalToolConfig.auto_detect()
    launcher = ParaViewLauncher(config)
    
    # Should not error even if ParaView not installed
    is_avail = launcher.is_available()
    assert isinstance(is_avail, bool)


def test_freecad_exporter_detection():
    """Test FreeCAD detection via ExternalToolConfig."""
    config = ExternalToolConfig.auto_detect()
    exporter = FreeCADExporter(config)
    
    # Should not error even if FreeCAD not installed
    is_avail = exporter.is_available()
    assert isinstance(is_avail, bool)


def test_step_export_result_dataclass():
    """Test STEPExportResult dataclass."""
    result = STEPExportResult(success=True, step_path=Path("test.step"), message="OK")
    assert result.success is True
    assert result.step_path == Path("test.step")
    assert result.message == "OK"


def test_result_visualizer_without_paraview():
    """Test ResultVisualizer handles missing ParaView gracefully."""
    # Create config with no ParaView path
    config = ExternalToolConfig()
    visualizer = ResultVisualizer(config)
    
    # Should return all False when ParaView not available
    results = visualizer.visualize_design_run(Path("/nonexistent"))
    assert results == {"thermal": False, "elmer": False}


def test_freecad_export_without_freecad():
    """Test FreeCAD export returns proper error when FreeCAD not available."""
    # Create config with no FreeCAD path
    config = ExternalToolConfig()
    exporter = FreeCADExporter(config)
    
    from neuroflux.core.models import MachineGeometry, AFPMTopology
    
    geometry = MachineGeometry(
        D_out=0.2,
        k_D=0.6,
        l_s=0.03,
        g=0.001,
        l_PM=0.005,
        w_PM=0.04,
        p=8,
        Q=18,
        topology=AFPMTopology.DSSR_SLOTTED,
    )
    
    result = exporter.export_stator_step(geometry, "test.step")
    assert result.success is False
    assert "FreeCAD not found" in result.message


def test_paraview_launcher_without_paraview():
    """Test ParaView launcher returns False when not available."""
    config = ExternalToolConfig()
    launcher = ParaViewLauncher(config)
    
    # Should return False when ParaView not available
    result = launcher.launch(["test.vtk"])
    assert result is False
