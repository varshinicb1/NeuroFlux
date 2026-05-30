"""
Magnetic Equivalent Circuit (MEC) solver for slotted AFPM machines.

Implements a non-linear reluctance network per computation plane
for surface-mounted PM machines with slotted stators (DSSR topology).

Equations (from Document 12 §2.2 — Parviainen 2005 + Hemeida 2019):
    Reluctance:        ℛ_i = l_i / (μ₀ μ_r S_i)
    PM MMF:            F_PM = B_r * l_PM / (μ₀ * μ_r,PM)
    Saturation factor: k_sat = (Θ_agap + Θ_t + Θ_y + Θ_rotor) / (0.5 * Θ_agap)
    Effective air-gap: g_eff = k_sat * k_C * g

The solver iterates to find the saturation factor, updating iron
permeabilities based on the computed flux densities at each step.

Key features:
    - Iterative saturation handling via BH-curve lookup
    - Carter coefficient for slot opening effect
    - Per-plane solution (feeds into quasi-3D aggregation)
    - Hemeida 2019 improvements for radial variation efficiency
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from neuroflux.analytical.quasi3d import ComputationPlane, compute_carter_coefficient
from neuroflux.core.constants import PhysicalConstants
from neuroflux.core.exceptions import ConvergenceError
from neuroflux.core.models import MachineGeometry, MaterialProperties
from neuroflux.utils.logging import get_logger

logger = get_logger(__name__)

MU_0 = PhysicalConstants.MU_0


@dataclass
class ReluctanceElement:
    """A single reluctance element in the magnetic circuit.

    Represents a section of the magnetic path (air-gap, tooth, yoke, PM, rotor).

    Attributes:
        name: Descriptive name (e.g., "airgap", "tooth", "yoke")
        length: Magnetic path length [m]
        area: Cross-sectional area perpendicular to flux [m²]
        mu_r: Relative permeability (updated during iteration)
    """

    name: str
    length: float
    area: float
    mu_r: float = 1.0  # Default for air

    @property
    def reluctance(self) -> float:
        """Compute reluctance ℛ = l / (μ₀ μ_r S).

        Source: Document 12 §2.2
        """
        return self.length / (MU_0 * self.mu_r * self.area)

    @property
    def permeance(self) -> float:
        """Compute permeance (inverse of reluctance)."""
        r = self.reluctance
        return 1.0 / r if r > 0 else float("inf")


@dataclass
class MECResult:
    """Result from the MEC solver for a single computation plane.

    Contains all electromagnetic quantities computed from the
    reluctance network solution.
    """

    B_g: float = 0.0  # Air-gap flux density [T]
    B_teeth: float = 0.0  # Tooth flux density [T]
    B_yoke: float = 0.0  # Yoke (back-iron) flux density [T]
    B_rotor_yoke: float = 0.0  # Rotor yoke flux density [T]
    phi_main: float = 0.0  # Main flux per pole [Wb]
    k_sat: float = 1.0  # Saturation factor
    k_carter: float = 1.0  # Carter's coefficient
    g_eff: float = 0.0  # Effective air-gap [m]
    F_PM: float = 0.0  # PM MMF [A·turns]
    iterations: int = 0  # Number of iterations to converge
    converged: bool = True


class MagneticCircuitSolver:
    """Non-linear MEC solver for slotted AFPM machines.

    Builds a reluctance network for one computation plane and solves
    iteratively to handle iron saturation.

    The magnetic circuit for a surface-mounted PM machine per pole:

        F_PM → ℛ_PM → ℛ_gap → ℛ_tooth → ℛ_yoke → (return path)
                               ↑
                          ℛ_leakage

    Source: Document 12 §2.2, Parviainen 2005 Chapter 2.2.1

    Args:
        max_iterations: Maximum iterations for saturation convergence.
        tolerance: Convergence tolerance for saturation factor.
    """

    def __init__(
        self,
        max_iterations: int = 50,
        tolerance: float = 1e-4,
    ) -> None:
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def solve_plane(
        self,
        plane: ComputationPlane,
        geometry: MachineGeometry,
        materials: MaterialProperties,
    ) -> MECResult:
        """Solve the magnetic circuit for a single computation plane.

        Iteratively adjusts iron permeabilities based on computed
        flux densities until the saturation factor converges.

        Args:
            plane: Computation plane with geometry at specific radius.
            geometry: Full machine geometry.
            materials: Material properties (PM, steel).

        Returns:
            MECResult with flux densities, saturation factor, etc.

        Raises:
            ConvergenceError: If saturation factor doesn't converge.
        """
        result = MECResult()

        # ── Step 1: Compute PM MMF (Doc 12 §2.2) ──
        # F_PM = B_r * l_PM / (μ₀ * μ_r,PM)
        F_PM = materials.Br * geometry.l_PM / (MU_0 * materials.mu_r_PM)
        result.F_PM = F_PM

        # ── Step 2: Carter coefficient (account for slot openings) ──
        if plane.slot_geometry.slot_opening_width > 0:
            k_carter = compute_carter_coefficient(
                slot_opening=plane.slot_geometry.slot_opening_width,
                airgap=geometry.g,
                magnet_thickness=geometry.l_PM,
                mu_r_pm=materials.mu_r_PM,
            )
        else:
            k_carter = 1.0
        result.k_carter = k_carter

        # ── Step 3: Build reluctance elements ──
        # Areas for each section
        A_gap = plane.tau_p * plane.plane_width * plane.alpha_p  # Pole area
        A_pm = A_gap  # PM area same as pole area (surface mounted)

        # Tooth area (sum of all teeth under one pole)
        if geometry.Q > 0:
            teeth_per_pole = geometry.Q / (2 * geometry.p)
            tooth_width = plane.slot_geometry.tooth_width
            A_tooth = teeth_per_pole * tooth_width * plane.plane_width
        else:
            A_tooth = A_gap
            teeth_per_pole = 1

        # Yoke area
        yoke_thickness = geometry.yoke_thickness if geometry.yoke_thickness else 0.01
        A_yoke = yoke_thickness * plane.plane_width

        # Rotor yoke area
        rotor_yoke_thickness = (
            geometry.rotor_yoke_thickness if geometry.rotor_yoke_thickness else 0.01
        )
        A_rotor_yoke = rotor_yoke_thickness * plane.plane_width

        # Build reluctance elements
        R_pm = ReluctanceElement(
            name="PM",
            length=geometry.l_PM,
            area=A_pm,
            mu_r=materials.mu_r_PM,
        )
        R_gap = ReluctanceElement(
            name="air_gap",
            length=geometry.g,
            area=A_gap,
            mu_r=1.0,
        )

        slot_depth = plane.slot_geometry.slot_depth if plane.slot_geometry.slot_depth > 0 else 0.02
        R_tooth = ReluctanceElement(
            name="tooth",
            length=slot_depth,
            area=A_tooth,
            mu_r=materials.mu_r_steel_linear,
        )

        # Yoke path length ~ half pole pitch
        yoke_path_length = plane.tau_p / 2.0
        R_yoke = ReluctanceElement(
            name="yoke",
            length=yoke_path_length,
            area=A_yoke,
            mu_r=materials.mu_r_steel_linear,
        )

        R_rotor = ReluctanceElement(
            name="rotor_yoke",
            length=plane.tau_p / 2.0,
            area=A_rotor_yoke,
            mu_r=materials.mu_r_steel_linear,
        )

        # ── Step 4: Iterative solution with saturation ──
        k_sat = 1.0
        k_sat_prev = 0.0
        converged = False

        for iteration in range(self.max_iterations):
            # Effective air-gap (Doc 12 §2.2)
            g_eff = k_sat * k_carter * geometry.g + geometry.l_PM / materials.mu_r_PM
            result.g_eff = g_eff

            # Total reluctance of the main flux path (series circuit)
            R_total = (
                R_pm.reluctance
                + R_gap.reluctance * k_carter
                + R_tooth.reluctance
                + R_yoke.reluctance
                + R_rotor.reluctance
            )

            # Main flux per pole: Φ = F_PM / ℛ_total
            phi_main = F_PM / R_total if R_total > 0 else 0.0
            result.phi_main = phi_main

            # Flux densities in each section
            B_g = phi_main / A_gap if A_gap > 0 else 0.0
            B_teeth = phi_main / A_tooth if A_tooth > 0 else 0.0
            B_yoke = phi_main / (2.0 * A_yoke) if A_yoke > 0 else 0.0
            B_rotor = phi_main / (2.0 * A_rotor_yoke) if A_rotor_yoke > 0 else 0.0

            # Update iron permeabilities based on flux densities
            R_tooth.mu_r = self._get_mu_r_from_B(B_teeth, materials)
            R_yoke.mu_r = self._get_mu_r_from_B(B_yoke, materials)
            R_rotor.mu_r = self._get_mu_r_from_B(B_rotor, materials)

            # Compute MMF drops
            theta_gap = B_g * g_eff / MU_0 if MU_0 > 0 else 0.0
            theta_tooth = phi_main * R_tooth.reluctance
            theta_yoke = phi_main * R_yoke.reluctance
            theta_rotor = phi_main * R_rotor.reluctance

            # Saturation factor (Doc 12 §2.2)
            # k_sat = (Θ_agap + Θ_t + Θ_y + Θ_rotor) / (0.5 * Θ_agap)
            if theta_gap > 0:
                k_sat_new = (
                    theta_gap + theta_tooth + theta_yoke + theta_rotor
                ) / (0.5 * theta_gap)
            else:
                k_sat_new = 1.0

            # Clamp to reasonable range
            k_sat_new = max(1.0, min(k_sat_new, 5.0))

            # Check convergence
            if abs(k_sat_new - k_sat) < self.tolerance:
                converged = True
                k_sat = k_sat_new
                break

            k_sat = k_sat_new

        if not converged:
            raise ConvergenceError(
                engine_name="MagneticCircuitSolver",
                iterations=self.max_iterations,
                residual=abs(k_sat - k_sat_prev),
                tolerance=self.tolerance,
            )

        # Store final results
        result.B_g = B_g
        result.B_teeth = B_teeth
        result.B_yoke = B_yoke
        result.B_rotor_yoke = B_rotor
        result.k_sat = k_sat
        result.iterations = iteration + 1
        result.converged = converged

        return result

    def _get_mu_r_from_B(
        self,
        B: float,
        materials: MaterialProperties,
    ) -> float:
        """Estimate relative permeability from flux density.

        Uses a simplified analytical BH-curve model. For flux densities
        below saturation, uses the linear permeability. Near and above
        saturation, permeability drops sharply.

        This is a simplified approach. For higher accuracy, use
        measured BH-curve data with interpolation.

        Args:
            B: Flux density [T]
            materials: Material properties with saturation data.

        Returns:
            Estimated relative permeability μ_r.
        """
        B_sat = materials.B_sat
        mu_r_linear = materials.mu_r_steel_linear

        if B <= 0:
            return mu_r_linear

        # Simplified saturation model
        # Smooth transition using a modified Langevin-like function
        B_ratio = abs(B) / B_sat

        if B_ratio < 0.7:
            # Linear region
            return mu_r_linear
        elif B_ratio < 1.0:
            # Transition region (knee of BH curve)
            # Linearly interpolate between mu_r_linear and a reduced value
            transition = (B_ratio - 0.7) / 0.3
            mu_r_reduced = mu_r_linear * 0.1  # Reduced near saturation
            return mu_r_linear * (1.0 - transition) + mu_r_reduced * transition
        else:
            # Deep saturation — permeability drops drastically
            return max(mu_r_linear * 0.01, 10.0)

    def compute_torque_contribution(
        self,
        mec_result: MECResult,
        plane: ComputationPlane,
        geometry: MachineGeometry,
        linear_current_density: float,
    ) -> float:
        """Compute electromagnetic torque contribution from one plane.

        Uses the simplified torque equation from Document 12 §1.1:
            dT_em = 2π r · A_in · B_max · r · dr

        For the discrete plane, this becomes:
            T_plane = 2π · r_mean · A · B_g · r_mean · Δr · 2p · α_p

        Where A is the linear current density and the factor accounts
        for the number of poles and magnet coverage.

        Args:
            mec_result: Solved MEC result for this plane.
            plane: Computation plane geometry.
            geometry: Machine geometry.
            linear_current_density: Linear current density A [A/m].

        Returns:
            Torque contribution from this plane [N·m].
        """
        # Torque contribution per plane (adapted from Doc 12 §1.1)
        # T = B_g * A * r² * Δr * 2π * α_p
        torque = (
            mec_result.B_g
            * linear_current_density
            * plane.r_mean ** 2
            * plane.plane_width
            * 2.0
            * math.pi
            * plane.alpha_p
        )

        return torque
