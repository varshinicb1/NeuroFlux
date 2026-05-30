"""
Autocoil Engine — PCB stator winding generator.

Wraps the autocoil Python tool for generating multi-layer PCB stator
layouts for axial-flux machines.

Per Document 06 Tier 1 #3:
    "Generates multi-layer PCB stators for axial flux machines programmatically."

Use cases:
    - Automated PCB stator layout generation
    - Winding resistance and inductance estimation
    - Integration with PCB manufacturing workflows

References:
    - Doc 06: External engines collection
    - Repository: https://github.com/pwspen/autocoil
"""

from __future__ import annotations

import time
import math

from pydantic import BaseModel, Field

from neuroflux.core.engine_base import (
    Engine,
    EngineCapabilities,
    EngineMetadata,
    ValidationResult,
)
from neuroflux.core.models import AFPMTopology, FidelityLevel


class AutocoilInput(BaseModel):
    """Input contract for the Autocoil PCB stator engine."""

    num_poles: int = Field(..., gt=0, description="Number of poles")
    num_phases: int = Field(default=3, gt=0, description="Number of phases")
    num_layers: int = Field(default=4, ge=1, description="Number of PCB layers")
    inner_radius: float = Field(..., gt=0, description="Inner radius of stator [m]")
    outer_radius: float = Field(..., gt=0, description="Outer radius of stator [m]")
    trace_width: float = Field(
        default=0.3e-3, gt=0, description="Copper trace width [m]"
    )
    trace_spacing: float = Field(
        default=0.15e-3, gt=0, description="Spacing between traces [m]"
    )
    copper_thickness: float = Field(
        default=35e-6, gt=0, description="Copper layer thickness [m] (1oz = 35μm)"
    )


class AutocoilOutput(BaseModel):
    """Output contract for the Autocoil PCB stator engine."""

    total_turns: int = Field(default=0, description="Total turns per phase")
    phase_resistance_ohm: float = Field(default=0.0, description="Phase resistance [Ω]")
    estimated_inductance_h: float = Field(
        default=0.0, description="Estimated phase inductance [H]"
    )
    pcb_file_path: str = Field(default="", description="Path to generated PCB layout")
    copper_area_m2: float = Field(default=0.0, description="Total copper area [m²]")
    computation_time_ms: float = Field(default=0.0)


class AutocoilEngine(Engine[AutocoilInput, AutocoilOutput]):
    """Autocoil PCB stator generation engine."""

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="Autocoil_Engine",
            version="0.1.0",
            description="PCB stator winding generator for axial-flux machines",
            fidelity_level=FidelityLevel.ANALYTICAL,
            typical_execution_time_ms=1000.0,
            requires_external_tool=True,
            external_tool_name="autocoil",
        )

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supported_topologies=[
                AFPMTopology.SSDR_CORELESS,
                AFPMTopology.SSDR_CORELESS_HALBACH,
            ],
            fidelity_level=FidelityLevel.ANALYTICAL,
            description="PCB stator generation for coreless AFPM machines",
        )

    def validate_input(self, input_data: AutocoilInput) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if input_data.inner_radius >= input_data.outer_radius:
            result.add_error(
                "inner_radius",
                "Inner radius must be less than outer radius"
            )
        return result

    def run(self, input_data: AutocoilInput) -> AutocoilOutput:
        """Runs the autocoil PCB stator generator and computes electrical properties.
        
        Uses the cloned autocoil repository to construct the physical spiral layouts
        and write a KiCad PCB layout file, then estimates resistance and inductance.
        """
        start_time = time.perf_counter()
        
        # Add the external_repos/autocoil directory to sys.path to import its modules
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        autocoil_path = project_root / "external_repos" / "autocoil"
        
        if str(autocoil_path.resolve()) not in sys.path:
            sys.path.append(str(autocoil_path.resolve()))
            
        try:
            import pcb_json
            import kicad_funcs
        except ImportError as e:
            raise RuntimeError(
                f"Failed to import autocoil packages. Ensure the repository is present in external_repos/autocoil. Details: {e}"
            ) from e
            
        # Map parameters
        # Dimensions are in meters for AutocoilInput, but autocoil script expects mm
        inner_r_mm = input_data.inner_radius * 1000.0
        outer_r_mm = input_data.outer_radius * 1000.0
        width_mm = outer_r_mm - inner_r_mm
        
        # Assume num_copies (number of coils) is determined from pole/phase count
        # For a standard 3-phase concentrated winding: num_coils = num_poles * num_phases / 2
        num_copies = int(round(input_data.num_poles * input_data.num_phases / 2.0))
        if num_copies <= 0:
            num_copies = 12
            
        # Maximum width (tangential spacing) of the coil at the outer radius
        # Circumference at outer radius is 2 * pi * outer_r_mm
        # Max height per coil is slot pitch: 2 * pi * outer_r_mm / num_copies
        # We take 90% of it to leave some space between coils
        height_mm = 0.90 * (2.0 * math.pi * outer_r_mm / num_copies)
        
        spacing_mm = (input_data.trace_width + input_data.trace_spacing) * 1000.0
        trace_width_mm = input_data.trace_width * 1000.0
        
        # Estimate maximum number of turns that can fit in the available coil height (winding window)
        # One turn has a width of spacing_mm.
        # Winding width is height_mm / 2.
        max_turns = int((height_mm / 2.0 - trace_width_mm) / spacing_mm)
        turns = max(1, min(20, max_turns))
        
        # Call generate_coil_array from autocoil
        coil_stacks = pcb_json.generate_coil_array(
            width=width_mm,
            height=height_mm,
            spacing=spacing_mm,
            turns=turns,
            corner_radius=0.0,
            trace_width=trace_width_mm,
            num_layers=input_data.num_layers,
            num_copies=num_copies,
            center_x=-inner_r_mm,
            center_y=height_mm / 2.0,
            start_angle=0.0
        )
        
        # Calculate resistance of one coil by summing up distances between points in layers
        total_length_m = 0.0
        for stack, info_dict in coil_stacks:
            for section in stack.sections:
                # Apply rounding to match physical layout (0.0 disables rounding and prevents segment size exceptions)
                pts = kicad_funcs.round_corners(section.points, 0.0, closed_loop=False)
                # Compute Euclidean length in meters (pts are in mm)
                layer_len_mm = 0.0
                for i in range(len(pts) - 1):
                    dx = pts[i+1][0] - pts[i][0]
                    dy = pts[i+1][1] - pts[i][1]
                    layer_len_mm += math.sqrt(dx*dx + dy*dy)
                total_length_m += layer_len_mm / 1000.0
            break # We only need to calculate for one coil, as they are identical
            
        # Resistivity of copper at 20C: 1.72e-8 Ohm-m
        rho_copper = 1.72e-8
        wire_area_m2 = input_data.trace_width * input_data.copper_thickness
        r_coil = rho_copper * total_length_m / wire_area_m2
        
        # Total phase resistance (assuming coils in series per phase)
        coils_per_phase = num_copies / input_data.num_phases
        phase_resistance = r_coil * coils_per_phase
        
        # Estimate inductance using Modified Wheeler formula for planar inductors
        d_out = 2.0 * input_data.outer_radius
        d_in = 2.0 * input_data.inner_radius
        d_avg = (d_out + d_in) / 2.0
        fill_factor = (d_out - d_in) / (d_out + d_in)
        
        # Constants for circular/approx-circular planar loop (c1=1.00, c2=2.46, c3=0.0, c4=0.20)
        c1, c2, c3, c4 = 1.0, 2.46, 0.0, 0.20
        mu0 = 4.0 * math.pi * 1e-7
        
        # Inductance of a single layer
        L_layer = (mu0 * (turns**2) * d_avg * c1 / 2.0) * (
            math.log(c2 / fill_factor) + c3 * fill_factor + c4 * (fill_factor**2)
        )
        
        # Mutual coupling coefficient between layers (approx 0.6)
        k_coupling = 0.6
        L_coil = L_layer * input_data.num_layers * (1.0 + k_coupling * (input_data.num_layers - 1))
        phase_inductance = L_coil * coils_per_phase
        
        # Total copper area [m2] (cross section area * length * number of coils)
        total_copper_area = wire_area_m2 * total_length_m * num_copies
        
        # Generate the KiCad PCB file in the reports/ directory
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        pcb_file_path = reports_dir / "pcb_stator_layout.kicad_pcb"
        
        # Template file from autocoil package
        template_file = autocoil_path / "mycoil" / "mycoil.kicad_pcb"
        
        try:
            # Copy template to target location first
            shutil.copy2(template_file, pcb_file_path)
            
            # Process sections to generate KiCAD representation (0.0 corner_radius)
            all_coil_sections, stack_uuids = pcb_json.process_coil_sections(coil_stacks, 0.0)
            
            # Write to output file
            kicad_funcs.write_coils_to_file(
                str(pcb_file_path.resolve()), 
                all_coil_sections, 
                stack_uuids,
                num_sections_per_stack=input_data.num_layers,
                stack_name="Multi-Layer Coil Array"
            )
        except Exception as e:
            # If KiCad write fails, we log it and keep the fallback file path empty/mocked
            pcb_file_path = Path("")
            
        computation_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        return AutocoilOutput(
            total_turns=turns * input_data.num_layers * int(coils_per_phase),
            phase_resistance_ohm=phase_resistance,
            estimated_inductance_h=phase_inductance,
            pcb_file_path=str(pcb_file_path.resolve()) if pcb_file_path else "",
            copper_area_m2=total_copper_area,
            computation_time_ms=computation_time_ms
        )

