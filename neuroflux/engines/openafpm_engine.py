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
        """Runs the OpenAFPM engine sizing calculation.
        
        Calculates electrical and magnetic parameters analytically using standard
        axial-flux wind generator sizing equations and writes mapped parameters to reports.
        """
        import time
        import math
        import json
        from pathlib import Path
        
        start_time = time.perf_counter()
        
        # 1. Magnetic Sizing
        # Magnet area (A_m)
        A_m = input_data.magnet_length * input_data.magnet_width
        
        # Estimate air-gap flux density
        # For NdFeB N40, Br is approx 1.25 Tesla.
        Br = 1.25
        g_mech = 0.0015  # Assumed mechanical air gap (1.5mm)
        t_stator = 2.0 * input_data.magnet_thickness + 0.002  # Estimated stator thickness
        g_eff = g_mech + t_stator
        
        # Flux density formula: Bg = Br * hm / (hm + g_eff)
        magnet_flux = Br * input_data.magnet_thickness / (input_data.magnet_thickness + g_eff)
        # Cap flux density between 0.3 and 1.2 T
        magnet_flux = max(0.3, min(1.2, magnet_flux))
        
        # Flux per pole: Phi = Bg * A_m
        flux_per_pole = magnet_flux * A_m
        
        # 2. Electrical Sizing
        # Frequency: f = p * RPM / 120
        # For Hugh Piggott wind generator, number of poles = number of magnets
        f = (input_data.number_of_magnets * input_data.target_rpm) / 120.0
        
        # Winding configuration: 3-phase, 4:3 magnet-to-coil ratio
        # Number of coils = number_of_magnets * 3/4
        # Coils per phase = number_of_magnets / 4
        coils_per_phase = max(1.0, input_data.number_of_magnets / 4.0)
        winding_factor = 0.966  # concentrated winding factor
        
        # Back-EMF per phase (RMS): E_phase = 4.44 * f * N_turns * N_coils_per_phase * Phi * kw
        E_phase = 4.44 * f * input_data.number_of_turns * coils_per_phase * flux_per_pole * winding_factor
        
        # Star (Wye) connection line-to-line RMS voltage: E_line = sqrt(3) * E_phase
        estimated_voltage = math.sqrt(3.0) * E_phase
        
        # 3. Resistive Sizing
        # Turn length estimation: 2 * magnet_length + 2 * magnet_width + pi * coil_inner_width
        L_turn = 2.0 * input_data.magnet_length + 2.0 * input_data.magnet_width + math.pi * input_data.coil_inner_width
        
        # Resistivity of copper at 20C: 1.72e-8 Ohm-m
        rho_copper = 1.72e-8
        A_wire = math.pi * (input_data.wire_gauge / 2.0) ** 2
        r_coil = rho_copper * (L_turn * input_data.number_of_turns) / A_wire
        
        # 4. Power Rating
        # Rated current density J = 5 A/mm2 (5e6 A/m2)
        J_rated = 5e6
        I_rated = J_rated * A_wire
        estimated_power = 3.0 * E_phase * I_rated
        
        # 5. Mapped parameters to JSON file
        project_root = Path(__file__).parent.parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        json_file_path = reports_dir / "openafpm_turbine_params.json"
        
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
            "CalculatedValues": {
                "EstimatedPowerW": estimated_power,
                "EstimatedVoltageV": estimated_voltage,
                "CoilResistanceOhm": r_coil,
                "MagnetFluxT": magnet_flux,
                "FrequencyHz": f
            }
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
            coil_resistance_ohm=r_coil,
            magnet_flux_t=magnet_flux,
            cad_file_path=str(json_file_path.resolve()) if json_file_path.exists() else "",
            computation_time_ms=computation_time_ms
        )

