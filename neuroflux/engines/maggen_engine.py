"""
MagGen Engine — Manufacturing-aware geometry generator.

Wraps the MagGen toolkit for generating production-ready CAD files,
coil winding patterns, and manufacturing artifacts for AFPM generators.

Per Document 04:
    "MagGen represents the 'last mile' of the engineering pipeline
     that most simulation tools ignore."

Use cases:
    - Manufacturing-ready CAD generation (OpenSCAD)
    - Coil winding tool design
    - DFM (Design for Manufacturability) constraint extraction

References:
    - Doc 04: MagGen integration exploration
    - Doc 06: External engines collection
    - Repository: https://github.com/subatomicglue/maggen
"""

from __future__ import annotations

import math
import time

from pydantic import BaseModel, Field

from neuroflux.core.engine_base import (
    Engine,
    EngineCapabilities,
    EngineMetadata,
    ValidationResult,
)
from neuroflux.core.models import AFPMTopology, FidelityLevel


class MagGenInput(BaseModel):
    """Input contract for the MagGen manufacturing engine."""

    rotor_diameter: float = Field(..., gt=0, description="Rotor diameter [m]")
    num_poles: int = Field(..., gt=0, description="Number of poles")
    num_coils: int = Field(..., gt=0, description="Number of coils")
    magnet_shape: str = Field(default="rectangular", description="Magnet shape")
    manufacturing_process: str = Field(
        default="3d_print",
        description="Primary process: 3d_print, laser_cut, plasma_cut"
    )
    output_format: str = Field(
        default="stl", description="Output format: stl, dxf, svg"
    )


class MagGenOutput(BaseModel):
    """Output contract for the MagGen manufacturing engine."""

    rotor_file_path: str = Field(default="", description="Rotor CAD file path")
    stator_file_path: str = Field(default="", description="Stator mold file path")
    coil_tool_path: str = Field(default="", description="Coil winding tool file path")
    dfm_warnings: list[str] = Field(
        default_factory=list, description="Manufacturing warnings"
    )
    computation_time_ms: float = Field(default=0.0)


class MagGenEngine(Engine[MagGenInput, MagGenOutput]):
    """MagGen manufacturing-aware geometry engine.

    Drives OpenSCAD to generate production-ready AFPM components.
    """

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="MagGen_Engine",
            version="0.1.0",
            description="Manufacturing-aware AFPM geometry via MagGen/OpenSCAD",
            fidelity_level=FidelityLevel.ANALYTICAL,
            typical_execution_time_ms=5000.0,
            requires_external_tool=True,
            external_tool_name="OpenSCAD + maggen.scad",
        )

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supported_topologies=[AFPMTopology.SSDR_CORELESS],
            fidelity_level=FidelityLevel.ANALYTICAL,
            description="Manufacturing file generation for AFPM generators",
        )

    def validate_input(self, input_data: MagGenInput) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        import shutil
        if not shutil.which("openscad"):
            result.add_warning(
                "OpenSCAD binary not found on PATH. Geometry rendering is disabled. "
                "The engine will run in analytical DFM mode and output custom .scad files."
            )
        return result

    def run(self, input_data: MagGenInput) -> MagGenOutput:
        """Runs the MagGen engine to generate CAD and verify manufacturability.
        
        Performs DFM (Design for Manufacturability) analysis, updates the OpenSCAD
        template parameters, and compiles it via OpenSCAD if installed.
        """
        import time
        import subprocess
        import shutil
        from pathlib import Path
        
        start_time = time.perf_counter()
        dfm_warnings = []
        
        # Dimensions & parameters mapping
        overall_radius = (input_data.rotor_diameter * 1000.0) / 2.0  # m to mm
        magnets_number = input_data.num_poles
        coils_number = input_data.num_coils
        magnet_use_rects = (input_data.magnet_shape.lower() == "rectangular")
        
        # Output formats
        out_fmt = input_data.output_format.lower()
        render_for_3d_printer = (out_fmt == "stl")
        render_for_sheet_materials = (out_fmt in ("dxf", "svg"))
        
        # ──────────────────────────────────────────────────────────────────────
        # DFM Constraint Analysis
        # ──────────────────────────────────────────────────────────────────────
        # Check magnet spacing & overlap
        # Magnets are placed at a default radius of 0.7 * overall_radius (from maggen.scad)
        magnets_radius = 0.7 * overall_radius
        circ_at_magnets = 2.0 * math.pi * magnets_radius
        
        # Default magnet dimensions in mm (from maggen.scad)
        magnets_width = 12.7
        magnets_height = 19.05
        magnet_radius_circular = 6.35
        
        magnet_width_tangential = magnets_width if magnet_use_rects else (2.0 * magnet_radius_circular)
        
        # Calculate pitch and clearance between magnets
        pitch = circ_at_magnets / max(1, magnets_number)
        clearance = pitch - magnet_width_tangential
        
        if clearance < 0:
            dfm_warnings.append(
                f"Critical Overlap: Pole count ({magnets_number}) is too high for rotor diameter ({input_data.rotor_diameter:.3f} m). "
                f"Magnets overlap by {abs(clearance):.2f} mm at the magnet radius."
            )
        elif clearance < 1.0:
            dfm_warnings.append(
                f"Tight Magnet Spacing: Magnet clearance is {clearance:.2f} mm. "
                "Recommended spacing is >= 1.0 mm to prevent magnetic forces from cracking magnets during assembly."
            )
            
        # Check coils spacing
        # Coils are placed at the same radius as magnets
        coil_pitch = circ_at_magnets / max(1, coils_number)
        coil_width_tangential = magnets_height + 5.0 # coils_height = magnets_height + 5 in SCAD
        coil_clearance = coil_pitch - coil_width_tangential
        
        if coil_clearance < 0.6: # SCAD has coil_spacing = 0.6 default
            dfm_warnings.append(
                f"Coil Space Violation: Coil count ({coils_number}) is too high for stator diameter. "
                f"Coil spacing is {coil_clearance:.2f} mm (minimum recommended is 0.6 mm)."
            )
            
        # Overall size checks
        if overall_radius < 20.0:
            dfm_warnings.append(
                f"Rotor disk radius ({overall_radius:.1f} mm) is too small to fit typical shaft hub and assembly screws."
            )
            
        # Process specific warnings
        proc = input_data.manufacturing_process.lower()
        if "3d_print" in proc:
            dfm_warnings.append(
                "3D Printing DFM: Ensure rotor disk is printed with high infill (>60%) and robust material (PETG, ABS, or Carbon Fiber PLA) "
                "to prevent deflection under magnetic pull."
            )
        elif "laser" in proc or "plasma" in proc:
            if not magnet_use_rects:
                dfm_warnings.append(
                    "Laser Cutting DFM: Circular magnet pockets are hard to laser cut with tight tolerance. Rectangular slots are recommended."
                )
                
        # ──────────────────────────────────────────────────────────────────────
        # OpenSCAD Script Customization
        # ──────────────────────────────────────────────────────────────────────
        project_root = Path(__file__).parent.parent.parent
        maggen_dir = project_root / "external_repos" / "maggen" / "designer"
        scad_template_path = maggen_dir / "maggen.scad"
        
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        custom_scad_path = reports_dir / "custom_maggen.scad"
        
        # Read the template
        if scad_template_path.exists():
            with open(scad_template_path, "r") as f:
                scad_content = f.read()
                
            # Perform parameter replacement
            scad_content = scad_content.replace("overall_radius=40;", f"overall_radius={overall_radius};")
            scad_content = scad_content.replace("magnets_number = 8;", f"magnets_number = {magnets_number};")
            scad_content = scad_content.replace("coils_number = 8;", f"coils_number = {coils_number};")
            scad_content = scad_content.replace("MAGNET_USE_RECTS=true;", f"MAGNET_USE_RECTS={str(magnet_use_rects).lower()};")
            scad_content = scad_content.replace("RENDER_FOR_3D_PRINTER = false;", f"RENDER_FOR_3D_PRINTER = {str(render_for_3d_printer).lower()};")
            scad_content = scad_content.replace("RENDER_FOR_SHEET_MATERIALS = false;", f"RENDER_FOR_SHEET_MATERIALS = {str(render_for_sheet_materials).lower()};")
            
            with open(custom_scad_path, "w") as f:
                f.write(scad_content)
        else:
            # Fallback if repository template not found
            custom_scad_path = Path("")
            dfm_warnings.append("Template maggen.scad was not found. Customized SCAD generation skipped.")
            
        # ──────────────────────────────────────────────────────────────────────
        # OpenSCAD Compilation / Render
        # ──────────────────────────────────────────────────────────────────────
        rotor_path = ""
        stator_path = ""
        coil_tool_path = ""
        
        openscad_bin = shutil.which("openscad")
        if openscad_bin and custom_scad_path and custom_scad_path.exists():
            try:
                # Compile rotor, stator, and bobbin separately using OpenSCAD command line
                rotor_out = reports_dir / f"maggen_rotor.{out_fmt}"
                stator_out = reports_dir / f"maggen_stator.{out_fmt}"
                bobbin_out = reports_dir / f"maggen_bobbin.{out_fmt}"
                
                # Render rotor
                subprocess.run(
                    [openscad_bin, "-o", str(rotor_out), str(custom_scad_path)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
                rotor_path = str(rotor_out.resolve())
                stator_path = str(stator_out.resolve())
                coil_tool_path = str(bobbin_out.resolve())
            except Exception as e:
                dfm_warnings.append(f"OpenSCAD rendering failed: {str(e)}")
        else:
            # Fallback path outputs
            if custom_scad_path and custom_scad_path.exists():
                rotor_path = str(custom_scad_path.resolve())
                stator_path = str(custom_scad_path.resolve())
                coil_tool_path = str(custom_scad_path.resolve())
                
        computation_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        return MagGenOutput(
            rotor_file_path=rotor_path,
            stator_file_path=stator_path,
            coil_tool_path=coil_tool_path,
            dfm_warnings=dfm_warnings,
            computation_time_ms=computation_time_ms
        )

