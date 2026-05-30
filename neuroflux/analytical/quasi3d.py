"""
Quasi-3D computation plane generation for AFPM machines.

Implements the Parviainen (2005) quasi-3D method where the axial-flux
machine is divided into N computation planes at different radii.
Each plane is "unrolled" into a linear machine equivalent for analysis.

Equations (from Document 12 §2.1 — Parviainen 2005):
    D_ave,i = D_out - (2i-1)/N * l_s          (average diameter of plane i)
    τ_p,i = π * D_ave,i / (2p)                (pole pitch at plane i)
    α_p,i = w_PM,i / τ_p,i                    (relative magnet width)

The quasi-3D approach captures radial variation of:
    - Pole pitch (increases with radius)
    - Magnet coverage ratio
    - Flux density
    - Torque density

This is the foundation used by both slotted (MEC) and coreless (Hague)
topology handlers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from neuroflux.core.models import MachineGeometry


@dataclass
class SlotGeometry:
    """Slot geometry at a specific computation plane.

    Computed from the machine geometry and the mean radius of the plane.
    Only populated for slotted topologies.
    """

    slot_pitch: float = 0.0  # Slot pitch at this radius [m]
    slot_opening_width: float = 0.0  # Slot opening [m]
    tooth_width: float = 0.0  # Tooth width at air-gap [m]
    slot_depth: float = 0.0  # Slot depth [m]
    slot_area: float = 0.0  # Cross-sectional area of one slot [m²]

    @property
    def slot_opening_ratio(self) -> float:
        """Ratio of slot opening to slot pitch."""
        if self.slot_pitch > 0:
            return self.slot_opening_width / self.slot_pitch
        return 0.0


@dataclass
class ComputationPlane:
    """A single quasi-3D computation plane.

    Represents a radial "slice" of the AFPM machine that is analyzed
    as an equivalent linear machine.

    Attributes:
        index: Plane index (0 to N-1)
        r_mean: Mean radius of this plane [m]
        D_ave: Average diameter of this plane [m]
        tau_p: Pole pitch at this plane [m]
        alpha_p: Relative magnet width at this plane
        plane_width: Radial width of this plane segment [m]
        circumference: Circumference at mean radius [m]
        slot_geometry: Slot geometry (slotted only)
    """

    index: int
    r_mean: float
    D_ave: float
    tau_p: float
    alpha_p: float
    plane_width: float
    circumference: float
    w_PM_at_plane: float  # Magnet width at this plane [m]
    slot_geometry: SlotGeometry = field(default_factory=SlotGeometry)

    @property
    def angular_extent(self) -> float:
        """Angular extent of one pole at this radius [rad]."""
        return self.tau_p / self.r_mean

    @property
    def area_per_pole(self) -> float:
        """Area per pole at this plane [m²]."""
        return self.tau_p * self.plane_width

    @property
    def magnet_area(self) -> float:
        """Magnet area per pole at this plane [m²]."""
        return self.w_PM_at_plane * self.plane_width


def generate_planes(
    geometry: MachineGeometry,
    num_planes: int = 7,
) -> list[ComputationPlane]:
    """Generate quasi-3D computation planes per Parviainen (2005).

    Divides the AFPM machine radially into N planes. Each plane
    is characterized by its mean radius and the corresponding
    pole pitch, magnet coverage, and slot geometry.

    Source: Document 12 §2.1 (Parviainen 2005, Chapter 2)
        D_ave,i = D_out - (2i-1)/N * l_s
        τ_p,i = π * D_ave,i / (2p)
        α_p,i = w_PM,i / τ_p,i

    Note: Parviainen's formula uses axial stator length l_s for the
    plane spacing. For the radial slicing in AFPM, we adapt this to
    divide between r_in and r_out.

    Args:
        geometry: Machine geometry specification.
        num_planes: Number of computation planes (default 7).

    Returns:
        List of ComputationPlane objects from inner to outer radius.
    """
    r_out = geometry.r_out
    r_in = geometry.r_in
    radial_length = r_out - r_in  # Total active radial length
    plane_width = radial_length / num_planes

    planes: list[ComputationPlane] = []

    for i in range(num_planes):
        # Mean radius of this plane (evenly spaced from inner to outer)
        r_mean = r_in + (i + 0.5) * plane_width
        D_ave = 2.0 * r_mean

        # Pole pitch at this plane (Doc 12 §2.1)
        tau_p = math.pi * D_ave / (2.0 * geometry.p)

        # Magnet width at this radius
        # If w_PM is given at mean machine radius, scale linearly with radius
        r_machine_mean = (r_out + r_in) / 2.0
        w_PM_at_plane = geometry.w_PM * (r_mean / r_machine_mean)

        # Relative magnet width (Doc 12 §2.1)
        alpha_p = w_PM_at_plane / tau_p if tau_p > 0 else 0.0
        alpha_p = min(alpha_p, 1.0)  # Cannot exceed pole pitch

        # Circumference at this radius
        circumference = 2.0 * math.pi * r_mean

        # Compute slot geometry (for slotted topologies)
        slot_geo = SlotGeometry()
        if geometry.Q > 0:
            slot_pitch = circumference / geometry.Q
            slot_opening = geometry.slot_opening if geometry.slot_opening else 0.4 * slot_pitch
            tooth_width = geometry.tooth_width if geometry.tooth_width else 0.6 * slot_pitch
            slot_depth = geometry.slot_depth if geometry.slot_depth else 0.02  # 20mm default

            slot_geo = SlotGeometry(
                slot_pitch=slot_pitch,
                slot_opening_width=min(slot_opening, slot_pitch),
                tooth_width=min(tooth_width, slot_pitch),
                slot_depth=slot_depth,
                slot_area=slot_depth * (slot_pitch - tooth_width),
            )

        plane = ComputationPlane(
            index=i,
            r_mean=r_mean,
            D_ave=D_ave,
            tau_p=tau_p,
            alpha_p=alpha_p,
            plane_width=plane_width,
            circumference=circumference,
            w_PM_at_plane=w_PM_at_plane,
            slot_geometry=slot_geo,
        )
        planes.append(plane)

    return planes


def compute_carter_coefficient(
    slot_opening: float,
    airgap: float,
    magnet_thickness: float,
    mu_r_pm: float = 1.05,
) -> float:
    """Compute Carter's coefficient for slotted machines.

    Carter's coefficient accounts for the increase in effective air-gap
    due to slot openings. The flux "fringes" at the slot opening edges,
    reducing the effective flux density.

    The effective air-gap becomes: g_eff = k_C * g

    Args:
        slot_opening: Slot opening width [m]
        airgap: Physical air-gap length [m]
        magnet_thickness: PM thickness [m]
        mu_r_pm: Relative permeability of PM

    Returns:
        Carter's coefficient k_C (always >= 1.0)
    """
    # Effective air-gap for Carter calculation includes PM thickness
    g_prime = airgap + magnet_thickness / mu_r_pm

    if slot_opening <= 0 or g_prime <= 0:
        return 1.0

    # Carter's coefficient formula
    gamma = slot_opening / g_prime
    # Standard formula: k_C = τ_s / (τ_s - γ * g')
    # where γ = (4/π) * [0.5*arctan(γ/2) - (1/γ)*ln(1 + (γ/2)²)]
    # Simplified approximation for moderate slot openings:
    beta = (gamma / 2.0) / math.sqrt(1.0 + (gamma / 2.0) ** 2)

    # This gives the reduction factor per slot pitch
    # Carter coefficient is typically applied via the slot pitch
    # For standalone use, return the basic form
    if beta <= 0:
        return 1.0

    # More accurate form
    sigma = (4.0 / math.pi) * (
        0.5 * math.atan(gamma / 2.0)
        - (1.0 / gamma) * math.log(1.0 + (gamma / 2.0) ** 2)
    )

    return 1.0 / (1.0 - sigma) if sigma < 1.0 else 2.0
