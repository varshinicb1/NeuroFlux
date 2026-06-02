"""
OpenAFPM Engine — Wrapper for openafpm-cad-core (MagnAFPM).

Wraps the OpenAFPM parametric design tool and its MagnAFPM simulation
component for AFPM wind turbine generator design.

Per Document 06 Tier 1 #1:
    "Core of OpenAFPM. Contains MagnAFPM (parametric design + FEMM
     simulation for AFPM generators for wind). Excellent input/output potential."

Use cases:
    - Quick parametric AFPM generator designs
    - Wind turbine generator sizing
    - MagnAFPM-based FEMM simulation

References:
    - Doc 06: External engines collection
    - Repository: https://github.com/gbroques/openafpm-cad-core
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from neuroflux.core.engine_base import (
    Engine,
    EngineCapabilities,
    EngineMetadata,
    ValidationResult,
)
from neuroflux.core.models import AFPMTopology, FidelityLevel


class OpenAFPMInput(BaseModel):
    """Input contract for the OpenAFPM engine."""

    # OpenAFPM parametric inputs
    rotor_disk_radius: float = Field(..., gt=0, description="Rotor disk radius [m]")
    magnet_length: float = Field(..., gt=0, description="Magnet length [m]")
    magnet_width: float = Field(..., gt=0, description="Magnet width [m]")
    magnet_thickness: float = Field(..., gt=0, description="Magnet thickness [m]")
    number_of_magnets: int = Field(..., gt=0, description="Total number of magnets")
    coil_inner_width: float = Field(..., gt=0, description="Coil inner width [m]")
    coil_type: str = Field(default="rectangular", description="Coil shape type")
    wire_gauge: float = Field(default=1.0e-3, gt=0, description="Wire diameter [m]")
    number_of_turns: int = Field(default=100, gt=0, description="Turns per coil")
    target_rpm: float = Field(default=300.0, gt=0, description="Target RPM")


class OpenAFPMOutput(BaseModel):
    """Output contract for the OpenAFPM engine."""

    estimated_power_w: float = Field(default=0.0, description="Estimated power output [W]")
    estimated_voltage_v: float = Field(default=0.0, description="Estimated voltage [V]")
    coil_resistance_ohm: float = Field(default=0.0, description="Coil resistance [Ω]")
    magnet_flux_t: float = Field(default=0.0, description="Estimated magnet flux [T]")
    cad_file_path: str = Field(default="", description="Path to generated CAD file")
    computation_time_ms: float = Field(default=0.0)


class OpenAFPMEngine(Engine[OpenAFPMInput, OpenAFPMOutput]):
    """OpenAFPM parametric design engine.

    Wraps openafpm-cad-core for wind turbine AFPM generator design.
    """

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="OpenAFPM_Engine",
            version="0.1.0",
            description="Parametric AFPM generator design via OpenAFPM/MagnAFPM",
            fidelity_level=FidelityLevel.ANALYTICAL,
            typical_execution_time_ms=2000.0,
            requires_external_tool=True,
            external_tool_name="openafpm-cad-core",
        )

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supported_topologies=[AFPMTopology.SSDR_CORELESS],
            fidelity_level=FidelityLevel.ANALYTICAL,
            description="Parametric AFPM generator for wind turbines (coreless focus)",
        )

    def validate_input(self, input_data: OpenAFPMInput) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if input_data.rotor_disk_radius <= 0:
            result.add_error("rotor_disk_radius", "Rotor disk radius must be positive.")
        return result

    def run(self, input_data: OpenAFPMInput) -> OpenAFPMOutput:
        """Runs the OpenAFPM engine via openafpm-cad-core package.
        
        This is COMPULSORY - requires openafpm-cad-core to be installed.
        Uses actual MagnAFPM simulation and FreeCAD CAD generation.
        
        Raises:
            RuntimeError: If openafpm-cad-core is not installed.
        """
        import time
        import json
        from pathlib import Path
        
        start_time = time.perf_counter()
        
        # COMPULSORY: Check for openafpm-cad-core
        try:
            import openafpm_cad_core
        except ImportError as e:
            raise RuntimeError(
                "openafpm-cad-core is COMPULSORY but not installed.\n"
                "Install with: pip install git+https://github.com/gbroques/openafpm-cad-core.git\n"
                "Or clone and: pip install --editable ."
            ) from e
        
        # Prepare mapped parameters for openafpm-cad-core
        mapped_params = {
            "RotorDiskRadius": input_data.rotor_disk_radius,
            "RotorDiskInnerRadius": input_data.rotor_disk_radius - input_data.magnet_length,
            "MagnetLength": input_data.magnet_length,
            "MagnetWidth": input_data.magnet_width,
            "MagnetThickness": input_data.magnet_thickness,
            "MagnetMaterial": "NdFeB N40",
            "NumberMagnet": input_data.number_of_magnets,
            "CoilType": 1 if input_data.coil_type == "rectangular" else 3,
            "WireDiameter": input_data.wire_gauge,
            "TurnsPerCoil": input_data.number_of_turns,
            "TargetRPM": input_data.target_rpm,
        }
        
        # Call openafpm-cad-core to generate CAD and run MagnAFPM simulation
        # This requires FreeCAD to be installed and available
        try:
            # Import the core modules from openafpm-cad-core
            from openafpm_cad_core import create_cad_model, run_magnafpm_simulation
            
            # Create output directory
            output_dir = Path("design_runs") / "openafpm_output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate FreeCAD CAD model
            fcstd_path = output_dir / "turbine.fcstd"
            create_cad_model(mapped_params, str(fcstd_path))
            
            # Run MagnAFPM electromagnetic simulation
            sim_results = run_magnafpm_simulation(mapped_params)
            
            # Extract results
            estimated_power = sim_results.get("power_w", 0.0)
            estimated_voltage = sim_results.get("voltage_v", 0.0)
            coil_resistance = sim_results.get("resistance_ohm", 0.0)
            magnet_flux = sim_results.get("flux_density_t", 0.0)
            
        except Exception as e:
            # If openafpm-cad-core fails, raise error (no fallback)
            raise RuntimeError(
                f"openafpm-cad-core execution failed: {e}\n"
                "Ensure FreeCAD is installed and available in PATH."
            ) from e
        
        # Save mapped parameters for reference
        project_root = Path(__file__).parent.parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        json_file_path = reports_dir / "openafpm_turbine_params.json"
        
        mapped_params["CalculatedValues"] = {
            "EstimatedPowerW": estimated_power,
            "EstimatedVoltageV": estimated_voltage,
            "CoilResistanceOhm": coil_resistance,
            "MagnetFluxT": magnet_flux,
        }
        
        try:
            with open(json_file_path, "w") as f_out:
                json.dump(mapped_params, f_out, indent=4)
        except Exception:
            pass
        
        computation_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        return OpenAFPMOutput(
            estimated_power_w=estimated_power,
            estimated_voltage_v=estimated_voltage,
            coil_resistance_ohm=coil_resistance,
            magnet_flux_t=magnet_flux,
            cad_file_path=str(fcstd_path) if fcstd_path.exists() else "",
            computation_time_ms=computation_time_ms
        )

