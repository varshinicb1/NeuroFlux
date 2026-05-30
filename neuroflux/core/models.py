"""
Shared data models for NeuroFlux engines.

All models use Pydantic v2 for strong validation, JSON serialization,
and schema generation. Models are grounded in Document 19 (Section 3)
and Document 12 (AFPM Mathematical Foundation).

Every engine's Input/Output contract is built from these shared models.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ──────────────────────────────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────────────────────────────


class AFPMTopology(str, Enum):
    """Supported AFPM machine topologies.

    Names follow standard literature conventions:
    - DSSR: Double-Stator Single-Rotor
    - SSDR: Single-Stator Double-Rotor
    - YASA: Yokeless And Segmented Armature
    """

    DSSR_SLOTTED = "DSSR_slotted"
    SSDR_CORELESS = "SSDR_coreless"
    SSDR_CORELESS_HALBACH = "SSDR_coreless_halbach"
    YASA = "YASA"
    TORUS_NN = "TORUS_NN"
    TORUS_NS = "TORUS_NS"


class MagnetType(str, Enum):
    """Permanent magnet arrangement types.

    Based on Document 21 Section 2.2 configurations.
    """

    CONVENTIONAL = "conventional"
    HALBACH_DISCRETE = "halbach_discrete"
    HALBACH_IDEAL = "halbach_ideal"


class FidelityLevel(str, Enum):
    """Simulation fidelity levels per Document 14."""

    ANALYTICAL = "analytical"  # Layer 1: ms per eval
    FEA_2D = "fea_2d"  # Layer 2: seconds per eval
    FEA_3D = "fea_3d"  # Layer 3: minutes to hours
    ROM = "rom"  # Layer 4: sub-ms (reduced order)


# ──────────────────────────────────────────────────────────────────────
# Input Models (Machine Definition)
# ──────────────────────────────────────────────────────────────────────


class MachineGeometry(BaseModel):
    """Parametric geometry of an AFPM machine.

    Grounded in Document 19 Section 3 and Document 12 Section 2.1.

    All dimensions are in SI units (meters).
    """

    D_out: float = Field(
        ..., gt=0, description="Outer diameter [m]"
    )
    k_D: float = Field(
        ..., gt=0, lt=1,
        description="Diameter ratio r_in/r_out. Optimal ≈ 0.58 (Doc 12 §1.1). Practical: 0.6–0.7"
    )
    l_s: float = Field(
        ..., gt=0, description="Axial length of stator stack [m]"
    )
    g: float = Field(
        ..., gt=0, description="Physical air-gap length (one side) [m]"
    )
    l_PM: float = Field(
        ..., gt=0, description="PM thickness in magnetization direction [m]"
    )
    w_PM: float = Field(
        ..., gt=0, description="Magnet width at mean radius [m]"
    )
    p: int = Field(
        ..., gt=0, description="Number of pole pairs"
    )
    Q: int = Field(
        ..., ge=0,
        description="Number of slots (0 for coreless/slotless topologies)"
    )
    topology: AFPMTopology = Field(
        ..., description="Machine topology identifier"
    )

    # Optional detailed geometry
    slot_depth: Optional[float] = Field(
        None, gt=0, description="Slot depth [m] (slotted topologies only)"
    )
    slot_opening: Optional[float] = Field(
        None, gt=0, description="Slot opening width [m]"
    )
    tooth_width: Optional[float] = Field(
        None, gt=0, description="Tooth width at air-gap [m]"
    )
    yoke_thickness: Optional[float] = Field(
        None, gt=0, description="Back-iron / yoke thickness [m]"
    )
    rotor_yoke_thickness: Optional[float] = Field(
        None, gt=0, description="Rotor back-iron thickness [m]"
    )
    winding_thickness: Optional[float] = Field(
        None, gt=0,
        description="Winding region axial thickness [m] (coreless topologies)"
    )

    @property
    def r_out(self) -> float:
        """Outer radius [m]."""
        return self.D_out / 2.0

    @property
    def r_in(self) -> float:
        """Inner radius [m]."""
        return self.r_out * self.k_D

    @property
    def D_in(self) -> float:
        """Inner diameter [m]."""
        return self.D_out * self.k_D

    @property
    def active_length(self) -> float:
        """Radial active length [m]."""
        return self.r_out - self.r_in

    @field_validator("k_D")
    @classmethod
    def validate_diameter_ratio(cls, v: float) -> float:
        """Warn if k_D is outside practical range (Doc 12 §1.1)."""
        if v < 0.4 or v > 0.85:
            # Still valid, but unusual — log warning in practice
            pass
        return v


class MaterialProperties(BaseModel):
    """Material properties for PM, steel, and copper.

    Loss coefficients from Document 12 Section 3.2 (Bertotti/Steinmetz).
    PM properties per standard NdFeB/ferrite datasheets.
    """

    # PM properties
    Br: float = Field(
        ..., gt=0, description="PM remanence [T]"
    )
    mu_r_PM: float = Field(
        default=1.05, gt=0,
        description="Relative permeability of PM material"
    )
    Hcj: float = Field(
        default=900e3, gt=0,
        description="Intrinsic coercivity [A/m]"
    )
    pm_temp_coeff: float = Field(
        default=-0.12,
        description="Temperature coefficient of Br [%/°C]"
    )

    # Steel properties (Bertotti/Steinmetz coefficients — Doc 12 §3.2)
    steel_grade: str = Field(
        default="M600-50A",
        description="Electrical steel grade identifier"
    )
    k_hys: float = Field(
        default=143.0, ge=0,
        description="Hysteresis loss coefficient [W/m³]"
    )
    k_eddy: float = Field(
        default=0.53, ge=0,
        description="Eddy current loss coefficient [W/m³]"
    )
    k_exc: float = Field(
        default=0.0, ge=0,
        description="Excess / anomalous loss coefficient [W/m³]"
    )
    steinmetz_alpha: float = Field(
        default=2.0, gt=0,
        description="Steinmetz exponent α for hysteresis"
    )

    # Steel saturation (simplified BH model)
    B_sat: float = Field(
        default=1.8, gt=0,
        description="Saturation flux density of steel [T]"
    )
    mu_r_steel_linear: float = Field(
        default=5000.0, gt=0,
        description="Relative permeability of steel in linear region"
    )

    # Copper
    copper_resistivity_20c: float = Field(
        default=1.678e-8, gt=0,
        description="Copper resistivity at 20°C [Ω·m]"
    )


class MagnetConfiguration(BaseModel):
    """Permanent magnet array configuration.

    Based on Document 21 Section 2.2 for Halbach arrays.
    """

    mag_type: MagnetType = Field(
        default=MagnetType.CONVENTIONAL,
        description="Magnet arrangement type"
    )
    segments_per_pole: int = Field(
        default=1, ge=1,
        description="Number of magnet segments per pole (for discrete Halbach)"
    )
    halbach_ratio: float = Field(
        default=1.0, gt=0, le=2.0,
        description="Halbach focusing ratio (1.0 = conventional)"
    )

    @model_validator(mode="after")
    def validate_halbach_config(self) -> MagnetConfiguration:
        """Validate Halbach-specific parameters."""
        if self.mag_type == MagnetType.CONVENTIONAL and self.segments_per_pole > 1:
            # Conventional magnets don't use multiple segments per pole
            pass  # Allow but it's unusual
        if self.mag_type in (MagnetType.HALBACH_DISCRETE, MagnetType.HALBACH_IDEAL):
            if self.segments_per_pole < 2:
                raise ValueError(
                    "Halbach arrays require at least 2 segments per pole"
                )
        return self


class WindingParameters(BaseModel):
    """Stator winding specification.

    Based on Document 19 Section 3.
    """

    turns_per_phase: int = Field(
        ..., gt=0, description="Total series turns per phase"
    )
    phases: int = Field(
        default=3, gt=0, description="Number of phases"
    )
    fill_factor: float = Field(
        default=0.6, gt=0, le=1.0,
        description="Slot fill factor (copper area / slot area)"
    )
    current_density: float = Field(
        default=5e6, gt=0,
        description="Current density [A/m²]"
    )
    coil_pitch: Optional[int] = Field(
        None, ge=1,
        description="Coil pitch in slot numbers (for distributed windings)"
    )
    parallel_paths: int = Field(
        default=1, ge=1,
        description="Number of parallel paths per phase"
    )
    conductor_diameter: Optional[float] = Field(
        None, gt=0,
        description="Individual conductor diameter [m] (for Litz wire / stranded)"
    )


class OperatingPoint(BaseModel):
    """Machine operating conditions.

    Based on Document 19 Section 3.
    """

    speed_rpm: float = Field(
        ..., gt=0, description="Rotational speed [rpm]"
    )
    I_rms: float = Field(
        ..., ge=0, description="Phase current RMS [A]"
    )
    ambient_temp: float = Field(
        default=40.0,
        description="Ambient temperature [°C]"
    )
    winding_temp: float = Field(
        default=80.0,
        description="Estimated winding temperature [°C]"
    )
    gamma_advance: float = Field(
        default=0.0,
        description="Current advance angle [electrical degrees]"
    )

    @property
    def speed_rad_s(self) -> float:
        """Mechanical angular velocity [rad/s]."""
        return self.speed_rpm * 2.0 * math.pi / 60.0

    @property
    def frequency_hz(self) -> float:
        """Electrical frequency [Hz]. Requires pole pairs (set externally)."""
        # Note: frequency depends on pole pairs, which is a geometry parameter.
        # This will be computed by the engine using p * speed_rpm / 60
        raise NotImplementedError(
            "Use engine.compute_frequency(operating_point, geometry) instead"
        )


# ──────────────────────────────────────────────────────────────────────
# Output Models
# ──────────────────────────────────────────────────────────────────────


class PlaneResult(BaseModel):
    """Results for a single quasi-3D computation plane.

    Based on Document 19 Section 3.
    """

    plane_index: int = Field(
        ..., ge=0, description="Index of the computation plane"
    )
    r_mean: float = Field(
        ..., gt=0, description="Mean radius of this plane [m]"
    )
    tau_p: float = Field(
        ..., gt=0, description="Pole pitch at this plane [m]"
    )
    B_g: float = Field(
        ..., ge=0, description="Air-gap flux density at this plane [T]"
    )
    torque_contribution: float = Field(
        ..., description="Torque contribution from this plane [N·m]"
    )
    emf_contribution: float = Field(
        default=0.0, description="Back-EMF contribution from this plane [V]"
    )
    losses: dict[str, float] = Field(
        default_factory=dict,
        description="Loss breakdown at this plane [W]: copper, iron, pm_eddy, etc."
    )
    flux_densities: dict[str, float] = Field(
        default_factory=dict,
        description="Flux density at key points [T]: teeth, yoke, air_gap"
    )


class EngineResult(BaseModel):
    """Complete engine evaluation output.

    Matches the output contract in Document 14 Section 4.
    This is the universal result format for all simulation engines.
    """

    # Primary performance metrics
    torque_nm: float = Field(
        ..., description="Electromagnetic torque [N·m]"
    )
    power_w: float = Field(
        ..., description="Output power [W]"
    )
    back_emf_rms: float = Field(
        ..., ge=0, description="Phase back-EMF RMS [V]"
    )
    efficiency: float = Field(
        ..., ge=0, le=1.0, description="Machine efficiency (0–1)"
    )

    # Loss breakdown [W]
    losses: dict[str, float] = Field(
        ...,
        description="Loss breakdown [W]: copper_w, iron_w, pm_eddy_w, windage_w, etc."
    )
    total_losses_w: float = Field(
        ..., ge=0, description="Total losses [W]"
    )

    # Flux densities [T]
    max_flux_densities: dict[str, float] = Field(
        default_factory=dict,
        description="Peak flux density at key points [T]: teeth, yoke, air_gap"
    )

    # Detailed per-plane results (for quasi-3D)
    plane_results: list[PlaneResult] = Field(
        default_factory=list,
        description="Per-plane results from quasi-3D analysis"
    )

    # Metadata
    computation_time_ms: float = Field(
        ..., ge=0, description="Wall-clock computation time [ms]"
    )
    fidelity: FidelityLevel = Field(
        ..., description="Fidelity level of this result"
    )
    engine_name: str = Field(
        ..., description="Name of the engine that produced this result"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings generated during computation"
    )

    @property
    def torque_density(self) -> float:
        """Torque per unit active volume [N·m/m³]. Requires geometry info."""
        # Placeholder — can be computed with geometry
        return 0.0


# ──────────────────────────────────────────────────────────────────────
# Compound Input Model (for Analytical Engine)
# ──────────────────────────────────────────────────────────────────────


class AnalyticalEngineInput(BaseModel):
    """Complete input for the Quasi-3D Analytical Engine.

    Bundles geometry, materials, winding, operating point, and
    magnet configuration into a single validated input.
    Matches the input contract in Document 14 Section 4.
    """

    geometry: MachineGeometry
    materials: MaterialProperties
    winding: WindingParameters
    operating_point: OperatingPoint
    magnet_config: MagnetConfiguration = Field(
        default_factory=MagnetConfiguration
    )
    num_planes: int = Field(
        default=7, ge=1, le=50,
        description="Number of quasi-3D computation planes (default 7 per Parviainen)"
    )

    @property
    def electrical_frequency(self) -> float:
        """Electrical frequency [Hz]."""
        return self.geometry.p * self.operating_point.speed_rpm / 60.0
