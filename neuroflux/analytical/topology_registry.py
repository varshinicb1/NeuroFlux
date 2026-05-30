"""
Topology registry and solver dispatcher for NeuroFlux.

Decouples the machine topology selection (Slotted, Coreless, Halbach, etc.)
from the underlying numerical solvers. Allows new topologies to register
themselves and dispatch to their corresponding math engines.

Traceable to Document 12 §1.2.
"""

from __future__ import annotations

import math
import time
from typing import Callable

import numpy as np

from neuroflux.analytical.coreless_field import HagueCorelessSolver
from neuroflux.analytical.halbach import HalbachArraySolver
from neuroflux.analytical.losses import LossModelEvaluator
from neuroflux.analytical.magnetic_circuit import MagneticCircuitSolver
from neuroflux.analytical.quasi3d import generate_planes
from neuroflux.core.models import (
    AFPMTopology,
    AnalyticalEngineInput,
    EngineResult,
    FidelityLevel,
    OperatingPoint,
    PlaneResult,
)


class TopologyRegistry:
    """
    Main registry linking AFPMTopology choices to specialized solver execution paths.
    """

    _registry: dict[
        AFPMTopology,
        Callable[[AnalyticalEngineInput, OperatingPoint], EngineResult],
    ] = {}

    @classmethod
    def register(
        cls,
        topology: AFPMTopology,
        handler: Callable[[AnalyticalEngineInput, OperatingPoint], EngineResult],
    ) -> None:
        cls._registry[topology] = handler

    @classmethod
    def dispatch(
        cls,
        topology: AFPMTopology,
        config: AnalyticalEngineInput,
        op: OperatingPoint,
    ) -> EngineResult:
        if topology not in cls._registry:
            raise ValueError(
                f"Topology {topology} is not currently registered or supported by the "
                "Analytical Engine."
            )
        return cls._registry[topology](config, op)


# Define specialized solvers for each primary topology

def solve_dssr_slotted(config: AnalyticalEngineInput, op: OperatingPoint) -> EngineResult:
    """
    Solves Double Stator Single Rotor (DSSR) slotted iron topologies.
    Uses quasi-3D multi-plane non-linear MEC reluctance network.
    """
    start_time = time.perf_counter()

    # 1. Plane generation
    planes = generate_planes(config.geometry, num_planes=config.num_planes)

    # 2. Iterate planes and solve magnetic reluctance network
    torque_total = 0.0
    b_peak_max = 0.0
    plane_results = []

    solver = MagneticCircuitSolver()

    for i, plane in enumerate(planes):
        # Solve reluctance network
        mec_res = solver.solve_plane(plane, config.geometry, config.materials)
        b_peak_max = max(b_peak_max, mec_res.B_g)

        # Linear current density calculation: A = (2 * m * N * I) / (2 * pi * r)
        linear_current_density = (
            2.0
            * config.winding.phases
            * config.winding.turns_per_phase
            * op.I_rms
            / (2.0 * math.pi * plane.r_mean)
        )

        # Compute plane torque contribution
        t_plane = solver.compute_torque_contribution(
            mec_res,
            plane,
            config.geometry,
            linear_current_density,
        )
        torque_total += t_plane

        # Plane breakdown result
        plane_results.append(
            PlaneResult(
                plane_index=i,
                r_mean=plane.r_mean,
                tau_p=plane.tau_p,
                B_g=mec_res.B_g,
                torque_contribution=t_plane,
                losses={"copper": 10.0},  # Simple approximation
                flux_densities={"teeth": mec_res.B_teeth, "yoke": mec_res.B_yoke},
            )
        )

    # 3. Loss computation
    losses_eval = LossModelEvaluator(config)
    r_dc = 0.05
    copper_losses = losses_eval.compute_copper_losses(op, r_dc)
    core_losses = losses_eval.compute_core_losses(op, b_peak_max)
    rotor_pm_loss = losses_eval.compute_rotor_losses(op, b_peak_max)
    mech_losses = losses_eval.compute_mechanical_losses(op.speed_rpm)

    p_cu = copper_losses["p_copper_total"]
    p_fe = core_losses["p_core_total"]
    p_rotor = rotor_pm_loss
    p_mech = mech_losses["p_mechanical_total"]
    total_losses = p_cu + p_fe + p_rotor + p_mech

    # 4. Mechanical Power and efficiency
    omega = op.speed_rad_s
    p_shaft = torque_total * omega
    if p_shaft > 0:
        p_elec = p_shaft - total_losses
        efficiency = (p_elec / p_shaft) if p_elec > 0 else 0.0
    else:
        p_elec = 0.0
        efficiency = 0.0

    efficiency = max(0.0, min(1.0, efficiency))

    return EngineResult(
        torque_nm=torque_total,
        power_w=p_elec,
        back_emf_rms=100.0,  # EMF placeholder
        efficiency=efficiency,
        losses={
            "copper": p_cu,
            "core": p_fe,
            "rotor": p_rotor,
            "mechanical": p_mech,
        },
        total_losses_w=total_losses,
        max_flux_densities={"airgap": b_peak_max},
        plane_results=plane_results,
        computation_time_ms=(time.perf_counter() - start_time) * 1000.0,
        fidelity=FidelityLevel.ANALYTICAL,
        engine_name="Quasi3D_Analytical_Engine",
    )


def solve_coreless(config: AnalyticalEngineInput, op: OperatingPoint) -> EngineResult:
    """
    Solves coreless/slotless stator structures using Hague's 3D analytical equations.
    """
    start_time = time.perf_counter()

    solver = HagueCorelessSolver(config)
    r_avg = (config.geometry.r_out + config.geometry.r_in) / 2.0
    theta = np.linspace(0, 2 * math.pi, 100)

    fields = solver.compute_flux_density(r_avg, theta, z=0.0)
    b_peak = float(np.max(np.abs(fields["Bz"])))

    losses_eval = LossModelEvaluator(config)
    r_dc = 0.04
    copper_losses = losses_eval.compute_copper_losses(op, r_dc)
    rotor_pm_loss = losses_eval.compute_rotor_losses(op, b_peak)
    mech_losses = losses_eval.compute_mechanical_losses(op.speed_rpm)

    p_cu = copper_losses["p_copper_total"]
    p_fe = 0.0
    p_rotor = rotor_pm_loss
    p_mech = mech_losses["p_mechanical_total"]
    total_losses = p_cu + p_fe + p_rotor + p_mech

    # Approximate torque under slotless conditions
    omega = op.speed_rad_s
    torque = 3.0 * 80.0 * op.I_rms / omega if omega > 0 else 0.0
    p_shaft = torque * omega
    p_elec = max(0.0, p_shaft - total_losses)
    efficiency = (p_elec / p_shaft) if p_shaft > 0 else 0.0

    return EngineResult(
        torque_nm=torque,
        power_w=p_elec,
        back_emf_rms=80.0,
        efficiency=max(0.0, min(1.0, efficiency)),
        losses={
            "copper": p_cu,
            "core": p_fe,
            "rotor": p_rotor,
            "mechanical": p_mech,
        },
        total_losses_w=total_losses,
        max_flux_densities={"airgap": b_peak},
        plane_results=[],
        computation_time_ms=(time.perf_counter() - start_time) * 1000.0,
        fidelity=FidelityLevel.ANALYTICAL,
        engine_name="Hague_Coreless_Engine",
    )


def solve_halbach(config: AnalyticalEngineInput, op: OperatingPoint) -> EngineResult:
    """
    Solves highly sinusoidal Halbach permanent magnet array structures.
    """
    start_time = time.perf_counter()

    solver = HalbachArraySolver(config)
    r_avg = (config.geometry.r_out + config.geometry.r_in) / 2.0
    theta = np.linspace(0, 2 * math.pi, 100)

    fields = solver.compute_airgap_field(r_avg, theta, z=0.0)
    b_peak = float(np.max(np.abs(fields["Bz"])))

    losses_eval = LossModelEvaluator(config)
    r_dc = 0.045
    copper_losses = losses_eval.compute_copper_losses(op, r_dc)
    rotor_pm_loss = losses_eval.compute_rotor_losses(op, b_peak)
    mech_losses = losses_eval.compute_mechanical_losses(op.speed_rpm)

    p_cu = copper_losses["p_copper_total"]
    p_fe = 0.0
    p_rotor = rotor_pm_loss
    p_mech = mech_losses["p_mechanical_total"]
    total_losses = p_cu + p_fe + p_rotor + p_mech

    omega = op.speed_rad_s
    torque = 3.0 * 90.0 * op.I_rms / omega if omega > 0 else 0.0
    p_shaft = torque * omega
    p_elec = max(0.0, p_shaft - total_losses)
    efficiency = (p_elec / p_shaft) if p_shaft > 0 else 0.0

    return EngineResult(
        torque_nm=torque,
        power_w=p_elec,
        back_emf_rms=90.0,
        efficiency=max(0.0, min(1.0, efficiency)),
        losses={
            "copper": p_cu,
            "core": p_fe,
            "rotor": p_rotor,
            "mechanical": p_mech,
        },
        total_losses_w=total_losses,
        max_flux_densities={"airgap": b_peak},
        plane_results=[],
        computation_time_ms=(time.perf_counter() - start_time) * 1000.0,
        fidelity=FidelityLevel.ANALYTICAL,
        engine_name="Halbach_Engine",
    )


# Register default topologies on startup
TopologyRegistry.register(AFPMTopology.DSSR_SLOTTED, solve_dssr_slotted)
TopologyRegistry.register(AFPMTopology.SSDR_CORELESS, solve_coreless)
TopologyRegistry.register(AFPMTopology.SSDR_CORELESS_HALBACH, solve_halbach)
