"""
Input validation helpers for NeuroFlux engines.

Provides common validation checks that engines can reuse,
beyond what Pydantic field validators handle.
"""

from __future__ import annotations

from neuroflux.core.engine_base import ValidationResult
from neuroflux.core.models import (
    AFPMTopology,
    AnalyticalEngineInput,
    MachineGeometry,
)


def validate_geometry_physics(geometry: MachineGeometry) -> ValidationResult:
    """Validate that geometry is physically reasonable.

    Checks beyond Pydantic range validators — physics-based sanity checks.

    Args:
        geometry: Machine geometry to validate.

    Returns:
        ValidationResult with errors and warnings.
    """
    result = ValidationResult(is_valid=True)

    # Air-gap should be much smaller than outer radius
    if geometry.g > 0.05 * geometry.r_out:
        result.add_warning(
            f"Air-gap ({geometry.g*1000:.1f} mm) is >5% of outer radius "
            f"({geometry.r_out*1000:.1f} mm). This is unusually large."
        )

    # PM thickness should be reasonable relative to air-gap
    if geometry.l_PM < geometry.g:
        result.add_warning(
            f"PM thickness ({geometry.l_PM*1000:.1f} mm) is less than air-gap "
            f"({geometry.g*1000:.1f} mm). This may result in very low flux density."
        )

    # Magnet width should be less than pole pitch at mean radius
    r_mean = (geometry.r_out + geometry.r_in) / 2.0
    tau_p_mean = 3.14159 * r_mean / geometry.p
    if geometry.w_PM > tau_p_mean:
        result.add_error(
            "w_PM",
            f"Magnet width ({geometry.w_PM*1000:.1f} mm) exceeds pole pitch "
            f"({tau_p_mean*1000:.1f} mm) at mean radius."
        )

    # Slot count must be appropriate for the topology
    if geometry.topology in (AFPMTopology.SSDR_CORELESS, AFPMTopology.SSDR_CORELESS_HALBACH):
        if geometry.Q > 0:
            result.add_warning(
                f"Coreless topology '{geometry.topology.value}' typically has Q=0, "
                f"but Q={geometry.Q} was specified."
            )
    elif geometry.topology == AFPMTopology.DSSR_SLOTTED:
        if geometry.Q == 0:
            result.add_error(
                "Q",
                "Slotted DSSR topology requires Q > 0."
            )

    # k_D outside recommended range
    if geometry.k_D < 0.5 or geometry.k_D > 0.8:
        result.add_warning(
            f"Diameter ratio k_D={geometry.k_D:.2f} is outside the typical "
            f"practical range of 0.6–0.7 (Doc 12 §1.1). Optimal is ~0.58."
        )

    return result


def validate_analytical_input(input_data: AnalyticalEngineInput) -> ValidationResult:
    """Full validation of analytical engine input.

    Combines geometry physics checks with winding and material checks.

    Args:
        input_data: Complete analytical engine input.

    Returns:
        ValidationResult with all errors and warnings.
    """
    result = validate_geometry_physics(input_data.geometry)

    # Electrical frequency check
    freq = input_data.electrical_frequency
    if freq > 500:
        result.add_warning(
            f"Electrical frequency ({freq:.0f} Hz) is very high. "
            f"Loss models may be less accurate above ~400 Hz."
        )

    # Current density check
    j = input_data.winding.current_density
    if j > 10e6:
        result.add_warning(
            f"Current density ({j/1e6:.1f} A/mm²) is very high. "
            f"Thermal management will be critical."
        )

    return result
