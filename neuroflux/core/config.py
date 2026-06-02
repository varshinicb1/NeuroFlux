"""Configuration for external tool paths.

Allows users to specify installation paths for:
- Elmer FEM (ElmerSolver, ElmerGUI, ElmerGrid)
- Gmsh (meshing)
- FreeCAD (CAD operations)
- ParaView (visualization)
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ExternalToolConfig(BaseModel):
    """Configuration paths for external engineering tools.
    
    If paths are not specified, the system will search PATH.
    """
    
    # Elmer FEM paths
    elmer_solver_path: str | None = Field(
        default=None, description="Path to ElmerSolver executable"
    )
    elmer_gui_path: str | None = Field(
        default=None, description="Path to ElmerGUI executable"
    )
    elmer_grid_path: str | None = Field(
        default=None, description="Path to ElmerGrid executable"
    )
    
    # Gmsh path
    gmsh_path: str | None = Field(
        default=None, description="Path to gmsh executable"
    )
    
    # FreeCAD path
    freecad_path: str | None = Field(
        default=None, description="Path to FreeCAD executable"
    )
    
    # ParaView path
    paraview_path: str | None = Field(
        default=None, description="Path to ParaView executable"
    )
    
    model_config = ConfigDict(env_prefix="NEUROFLUX_")
    
    def get_elmer_solver(self) -> str | None:
        """Get ElmerSolver path, checking config then PATH."""
        if self.elmer_solver_path and Path(self.elmer_solver_path).exists():
            return self.elmer_solver_path
        return shutil.which("ElmerSolver")
    
    def get_elmer_gui(self) -> str | None:
        """Get ElmerGUI path, checking config then PATH."""
        if self.elmer_gui_path and Path(self.elmer_gui_path).exists():
            return self.elmer_gui_path
        return shutil.which("ElmerGUI")
    
    def get_gmsh(self) -> str | None:
        """Get Gmsh path, checking config then PATH."""
        if self.gmsh_path and Path(self.gmsh_path).exists():
            return self.gmsh_path
        return shutil.which("gmsh")
    
    def get_freecad(self) -> str | None:
        """Get FreeCAD path, checking config then PATH."""
        if self.freecad_path and Path(self.freecad_path).exists():
            return self.freecad_path
        # Try common FreeCAD executable names
        for name in ["FreeCAD", "freecad", "FreeCADCmd"]:
            path = shutil.which(name)
            if path:
                return path
        return None
    
    def get_paraview(self) -> str | None:
        """Get ParaView path, checking config then PATH."""
        if self.paraview_path and Path(self.paraview_path).exists():
            return self.paraview_path
        # Try common ParaView executable names
        for name in ["paraview", "ParaView", "pvpython"]:
            path = shutil.which(name)
            if path:
                return path
        return None
    
    def elmer_available(self) -> bool:
        """Check if ElmerSolver is available."""
        return self.get_elmer_solver() is not None and self.get_gmsh() is not None
    
    def freecad_available(self) -> bool:
        """Check if FreeCAD is available."""
        return self.get_freecad() is not None
    
    def paraview_available(self) -> bool:
        """Check if ParaView is available."""
        return self.get_paraview() is not None
    
    @classmethod
    def from_env(cls) -> ExternalToolConfig:
        """Load configuration from environment variables."""
        return cls(
            elmer_solver_path=os.getenv("NEUROFLUX_ELMER_SOLVER"),
            elmer_gui_path=os.getenv("NEUROFLUX_ELMER_GUI"),
            elmer_grid_path=os.getenv("NEUROFLUX_ELMER_GRID"),
            gmsh_path=os.getenv("NEUROFLUX_GMSH"),
            freecad_path=os.getenv("NEUROFLUX_FREECAD"),
            paraview_path=os.getenv("NEUROFLUX_PARAVIEW"),
        )
    
    @classmethod
    def auto_detect(cls) -> ExternalToolConfig:
        """Auto-detect installed tools and create config.
        
        First checks environment variables, then falls back to PATH search.
        """
        # Start with environment variable configuration
        config = cls.from_env()
        
        # Try to detect Elmer from PATH if not set via env
        if not config.elmer_solver_path:
            elmer_solver = shutil.which("ElmerSolver")
            if elmer_solver:
                config.elmer_solver_path = elmer_solver
                # Try to find ElmerGUI in same directory
                elmer_dir = Path(elmer_solver).parent
                gui_candidates = ["ElmerGUI.exe", "ElmerGUI", "bin/ElmerGUI.exe", "bin/ElmerGUI"]
                for gui in gui_candidates:
                    gui_path = elmer_dir / gui
                    if gui_path.exists():
                        config.elmer_gui_path = str(gui_path)
                        break
        
        # Try to detect Gmsh from PATH if not set via env
        if not config.gmsh_path:
            gmsh = shutil.which("gmsh")
            if gmsh:
                config.gmsh_path = gmsh
        
        # Try to detect FreeCAD from PATH if not set via env
        if not config.freecad_path:
            freecad = shutil.which("FreeCAD") or shutil.which("FreeCADCmd") or shutil.which("freecad")
            if freecad:
                config.freecad_path = freecad
        
        # Try to detect ParaView from PATH if not set via env
        if not config.paraview_path:
            paraview = shutil.which("paraview") or shutil.which("ParaView") or shutil.which("pvpython")
            if paraview:
                config.paraview_path = paraview
        
        return config
    
    def print_status(self) -> None:
        """Print detection status of all tools."""
        print("External Tool Configuration:")
        print(f"  ElmerSolver: {self.get_elmer_solver() or 'NOT FOUND'}")
        print(f"  ElmerGUI: {self.get_elmer_gui() or 'NOT FOUND'}")
        print(f"  Gmsh: {self.get_gmsh() or 'NOT FOUND'}")
        print(f"  FreeCAD: {self.get_freecad() or 'NOT FOUND'}")
        print(f"  ParaView: {self.get_paraview() or 'NOT FOUND'}")
