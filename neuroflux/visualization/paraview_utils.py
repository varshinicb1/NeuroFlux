"""ParaView integration for result visualization.

Launches ParaView with result files for interactive 3D visualization.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from neuroflux.core.config import ExternalToolConfig


class ParaViewLauncher:
    """Launch ParaView to visualize simulation results."""

    def __init__(self, config: ExternalToolConfig | None = None) -> None:
        self._config = config or ExternalToolConfig.auto_detect()

    def is_available(self) -> bool:
        """Check if ParaView is available."""
        return self._config.paraview_available()

    def launch(self, file_paths: Sequence[str | Path], script: str | None = None) -> bool:
        """Launch ParaView with result files.
        
        Args:
            file_paths: List of VTK, VTU, or other ParaView-readable files
            script: Optional Python script to run in ParaView
            
        Returns:
            True if launch succeeded
        """
        paraview_exe = self._config.get_paraview()
        if not paraview_exe:
            return False

        cmd = [paraview_exe]
        
        # Add data files
        for path in file_paths:
            cmd.extend(["--data", str(path)])
        
        # Add Python script if provided
        if script:
            cmd.extend(["--script", script])

        try:
            # Launch ParaView (non-blocking)
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent process
            )
            return True
        except (OSError, subprocess.SubprocessError):
            return False

    def launch_thermal_results(self, vtk_path: str | Path) -> bool:
        """Launch ParaView with thermal FEA results.
        
        Args:
            vtk_path: Path to VTK file from thermal FEA
            
        Returns:
            True if launch succeeded
        """
        return self.launch([vtk_path])

    def launch_elmer_results(self, result_dir: str | Path) -> bool:
        """Launch ParaView with Elmer results.
        
        Args:
            result_dir: Directory containing Elmer VTU files
            
        Returns:
            True if launch succeeded
        """
        result_dir = Path(result_dir)
        if not result_dir.exists():
            return False

        # Find all VTU/VTK files in results directory
        files = list(result_dir.glob("*.vtu")) + list(result_dir.glob("*.vtk"))
        if not files:
            return False

        return self.launch(files)


class ResultVisualizer:
    """High-level interface for visualizing simulation results."""

    def __init__(self, config: ExternalToolConfig | None = None) -> None:
        self._launcher = ParaViewLauncher(config)

    def visualize_design_run(self, design_run_dir: str | Path) -> dict[str, bool]:
        """Visualize all results from a design run.
        
        Args:
            design_run_dir: Path to design run output directory
            
        Returns:
            Dictionary mapping result types to success status
        """
        design_run_dir = Path(design_run_dir)
        results = {
            "thermal": False,
            "elmer": False,
        }

        if not self._launcher.is_available():
            return results

        # Find thermal FEA results
        thermal_vtk = design_run_dir / "thermal_fea3d" / "thermal_fea3d.vtk"
        if thermal_vtk.exists():
            results["thermal"] = self._launcher.launch_thermal_results(thermal_vtk)

        # Find Elmer results
        elmer_results = design_run_dir / "results"
        if elmer_results.exists():
            results["elmer"] = self._launcher.launch_elmer_results(elmer_results)

        return results

    def visualize_validation_results(self, validation_dir: str | Path) -> dict[str, bool]:
        """Visualize all results from validation output.
        
        Args:
            validation_dir: Path to validation output directory
            
        Returns:
            Dictionary mapping result types to success status
        """
        validation_dir = Path(validation_dir)
        results = {
            "thermal": False,
            "elmer": False,
        }

        if not self._launcher.is_available():
            return results

        # Find thermal FEA results
        thermal_vtk = validation_dir / "thermal_fea3d" / "thermal_fea3d.vtk"
        if thermal_vtk.exists():
            results["thermal"] = self._launcher.launch_thermal_results(thermal_vtk)

        # Find Elmer results in solver handoffs
        elmer_case = validation_dir / "solver_handoffs" / "elmer_case" / "results"
        if elmer_case.exists():
            results["elmer"] = self._launcher.launch_elmer_results(elmer_case)

        return results
