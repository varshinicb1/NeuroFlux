"""FreeCAD integration for CAD export.

Exports AFPM generator designs to STEP files for manufacturing.
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from neuroflux.core.config import ExternalToolConfig
from neuroflux.core.models import MachineGeometry, MagnetConfiguration


@dataclass
class STEPExportResult:
    """Result of STEP export operation."""
    success: bool
    step_path: Path | None = None
    message: str = ""


class FreeCADExporter:
    """Export AFPM designs to STEP format using FreeCAD."""

    def __init__(self, config: ExternalToolConfig | None = None) -> None:
        self._config = config or ExternalToolConfig.auto_detect()

    def is_available(self) -> bool:
        """Check if FreeCAD is available."""
        return self._config.freecad_available()

    def export_stator_step(
        self,
        geometry: MachineGeometry,
        output_path: str | Path,
        magnet_config: MagnetConfiguration | None = None,
    ) -> STEPExportResult:
        """Export stator assembly to STEP format.
        
        Args:
            geometry: Machine geometry parameters
            output_path: Path for output STEP file
            magnet_config: Optional magnet configuration for rotor
            
        Returns:
            STEPExportResult with success status and path
        """
        freecad_exe = self._config.get_freecad()
        if not freecad_exe:
            return STEPExportResult(
                success=False,
                message="FreeCAD not found. Set NEUROFLUX_FREECAD environment variable."
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate Python script for FreeCAD
        script = self._generate_stator_script(geometry, output_path, magnet_config)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = Path(f.name)

        try:
            # Run FreeCAD in console mode with script
            result = subprocess.run(
                [freecad_exe, "-c", str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0 and output_path.exists():
                return STEPExportResult(
                    success=True,
                    step_path=output_path,
                    message=f"Successfully exported to {output_path}"
                )
            else:
                return STEPExportResult(
                    success=False,
                    message=f"FreeCAD export failed: {result.stderr[-500:]}"
                )
        except subprocess.TimeoutExpired:
            return STEPExportResult(
                success=False,
                message="FreeCAD export timed out"
            )
        except Exception as e:
            return STEPExportResult(
                success=False,
                message=f"Export error: {e}"
            )
        finally:
            # Cleanup temp script
            script_path.unlink(missing_ok=True)

    def _generate_stator_script(
        self,
        geometry: MachineGeometry,
        output_path: Path,
        magnet_config: MagnetConfiguration | None,
    ) -> str:
        """Generate FreeCAD Python script for stator creation.
        
        Creates a parametric annular stator model.
        """
        # Convert dimensions
        r_out = geometry.D_out / 2.0
        r_in = r_out * geometry.k_D
        
        return f'''
import FreeCAD as App
import Part
import Mesh

# Create document
doc = App.newDocument("AFPM_Stator")

# Create outer cylinder (stator outer boundary)
outer_cyl = Part.makeCylinder(
    {r_out},
    {geometry.l_s},
    App.Vector(0, 0, -{geometry.l_s}/2)
)

# Create inner cylinder (to subtract for annular shape)
inner_cyl = Part.makeCylinder(
    {r_in},
    {geometry.l_s},
    App.Vector(0, 0, -{geometry.l_s}/2)
)

# Create annular stator by boolean cut
stator = outer_cyl.cut(inner_cyl)

# Create stator object in document
stator_obj = doc.addObject("Part::Feature", "Stator")
stator_obj.Shape = stator

# Save as STEP
import Import
Import.export([stator_obj], "{output_path}")

# Cleanup
doc.close()
App.closeDocument("AFPM_Stator")

print("STEP export completed: {output_path}")
'''

    def export_rotor_step(
        self,
        geometry: MachineGeometry,
        output_path: str | Path,
        magnet_config: MagnetConfiguration,
    ) -> STEPExportResult:
        """Export rotor with magnets to STEP format.
        
        Args:
            geometry: Machine geometry parameters
            output_path: Path for output STEP file
            magnet_config: Magnet configuration
            
        Returns:
            STEPExportResult with success status and path
        """
        freecad_exe = self._config.get_freecad()
        if not freecad_exe:
            return STEPExportResult(
                success=False,
                message="FreeCAD not found. Set NEUROFLUX_FREECAD environment variable."
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate Python script for FreeCAD
        script = self._generate_rotor_script(geometry, output_path, magnet_config)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = Path(f.name)

        try:
            result = subprocess.run(
                [freecad_exe, "-c", str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0 and output_path.exists():
                return STEPExportResult(
                    success=True,
                    step_path=output_path,
                    message=f"Successfully exported rotor to {output_path}"
                )
            else:
                return STEPExportResult(
                    success=False,
                    message=f"FreeCAD export failed: {result.stderr[-500:]}"
                )
        except subprocess.TimeoutExpired:
            return STEPExportResult(
                success=False,
                message="FreeCAD export timed out"
            )
        except Exception as e:
            return STEPExportResult(
                success=False,
                message=f"Export error: {e}"
            )
        finally:
            script_path.unlink(missing_ok=True)

    def _generate_rotor_script(
        self,
        geometry: MachineGeometry,
        output_path: Path,
        magnet_config: MagnetConfiguration,
    ) -> str:
        """Generate FreeCAD Python script for rotor creation."""
        r_out = geometry.D_out / 2.0
        r_in = r_out * geometry.k_D
        
        return f'''
import FreeCAD as App
import Part

# Create document
doc = App.newDocument("AFPM_Rotor")

# Create rotor back iron (annular disk)
outer_cyl = Part.makeCylinder(
    {r_out},
    {geometry.l_PM * 0.5},  # Back iron thickness is half magnet thickness
    App.Vector(0, 0, -{geometry.l_PM * 0.25})
)

inner_cyl = Part.makeCylinder(
    {r_in},
    {geometry.l_PM * 0.5},
    App.Vector(0, 0, -{geometry.l_PM * 0.25})
)

back_iron = outer_cyl.cut(inner_cyl)

# Create magnet blocks
magnet_width = {geometry.w_PM}
magnet_thickness = {geometry.l_PM}
pole_pairs = {geometry.p}

rotor_parts = [back_iron]

import math
for i in range(pole_pairs * 2):
    angle = i * 2 * math.pi / (pole_pairs * 2)
    r_magnet = ({r_out} + {r_in}) / 2
    x = r_magnet * math.cos(angle)
    y = r_magnet * math.sin(angle)
    
    # Create magnet block
    magnet = Part.makeBox(
        magnet_width,
        magnet_width,
        magnet_thickness,
        App.Vector(x - magnet_width/2, y - magnet_width/2, -magnet_thickness/2)
    )
    rotor_parts.append(magnet)

# Fuse all parts
rotor = rotor_parts[0]
for part in rotor_parts[1:]:
    rotor = rotor.fuse(part)

# Create rotor object
rotor_obj = doc.addObject("Part::Feature", "Rotor")
rotor_obj.Shape = rotor

# Export
import Import
Import.export([rotor_obj], "{output_path}")

# Cleanup
doc.close()
App.closeDocument("AFPM_Rotor")

print("Rotor STEP export completed: {output_path}")
'''
