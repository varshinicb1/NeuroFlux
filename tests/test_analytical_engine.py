"""
Comprehensive unit tests for the NeuroFlux Analytical Engine.

Tests:
- Pydantic models & materials
- Quasi-3D plane generator
- MEC reluctance network solver
- Hague coreless field solver
- Halbach array field solver
- Multi-physics loss model evaluator
- Main AnalyticalEngine runner and validation
"""

from __future__ import annotations

import pytest
import numpy as np
from neuroflux.core.models import MachineGeometry, OperatingPoint, AnalyticalEngineInput, AFPMTopology, WindingParameters, MagnetConfiguration, MagnetType
from neuroflux.core.materials import MaterialDatabase
from neuroflux.analytical.quasi3d import generate_planes, compute_carter_coefficient
from neuroflux.analytical.magnetic_circuit import MagneticCircuitSolver, MECResult
from neuroflux.analytical.coreless_field import HagueCorelessSolver
from neuroflux.analytical.halbach import HalbachArraySolver
from neuroflux.analytical.losses import LossModelEvaluator
from neuroflux.engines.analytical_engine import AnalyticalEngine


@pytest.fixture
def sample_input():
    geom = MachineGeometry(
        D_out=0.30,
        k_D=0.6,
        l_s=0.05,
        g=0.003,
        l_PM=0.005,
        w_PM=0.02,
        p=8,
        Q=18,
        topology=AFPMTopology.DSSR_SLOTTED,
    )
    materials = MaterialDatabase().build_material_properties("N42", "M600-50A")
    winding = WindingParameters(
        turns_per_phase=100,
        phases=3,
        fill_factor=0.6,
        current_density=5e6,
    )
    op = OperatingPoint(speed_rpm=1500.0, I_rms=10.0)
    
    return AnalyticalEngineInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op,
        num_planes=5,
    )


def test_quasi3d_plane_generation(sample_input):
    """Verifies that generate_planes creates the requested planes with valid physical dimensions."""
    planes = generate_planes(sample_input.geometry, num_planes=5)
    assert len(planes) == 5
    for plane in planes:
        assert sample_input.geometry.r_in <= plane.r_mean <= sample_input.geometry.r_out
        assert plane.plane_width > 0


def test_mec_solver(sample_input):
    """Verifies non-linear MEC reluctance solver computations."""
    planes = generate_planes(sample_input.geometry, num_planes=5)
    solver = MagneticCircuitSolver()
    
    # Check solver execution
    mec_res = solver.solve_plane(planes[2], sample_input.geometry, sample_input.materials)
    assert isinstance(mec_res, MECResult)
    assert mec_res.B_g > 0.0
    assert mec_res.B_teeth > 0.0
    assert mec_res.B_yoke > 0.0
    assert mec_res.k_sat >= 1.0


def test_hague_coreless_field(sample_input):
    """Verifies Hague field solver for slotless/coreless stator machines."""
    geom = MachineGeometry(
        D_out=0.30,
        k_D=0.6,
        l_s=0.05,
        g=0.003,
        l_PM=0.005,
        w_PM=0.02,
        p=8,
        Q=0,
        topology=AFPMTopology.SSDR_CORELESS,
        winding_thickness=0.01,
    )
    materials = MaterialDatabase().build_material_properties("N42", "M600-50A")
    winding = WindingParameters(
        turns_per_phase=100,
        phases=3,
        fill_factor=0.6,
        current_density=5e6,
    )
    op = OperatingPoint(speed_rpm=1500.0, I_rms=10.0)
    
    inp = AnalyticalEngineInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op,
        num_planes=5,
    )
    
    solver = HagueCorelessSolver(inp)
    r_avg = (geom.r_out + geom.r_in) / 2.0
    theta = np.linspace(0, 2 * np.pi, 50)
    
    fields = solver.compute_flux_density(r_avg, theta, z=0.0)
    assert "Bz" in fields
    assert "Bt" in fields
    assert fields["Bz"].shape == (50,)


def test_halbach_array_field(sample_input):
    """Verifies Halbach array field modeling."""
    geom = MachineGeometry(
        D_out=0.30,
        k_D=0.6,
        l_s=0.05,
        g=0.003,
        l_PM=0.005,
        w_PM=0.02,
        p=8,
        Q=0,
        topology=AFPMTopology.SSDR_CORELESS_HALBACH,
        winding_thickness=0.01,
    )
    materials = MaterialDatabase().build_material_properties("N42", "M600-50A")
    winding = WindingParameters(
        turns_per_phase=100,
        phases=3,
        fill_factor=0.6,
        current_density=5e6,
    )
    op = OperatingPoint(speed_rpm=1500.0, I_rms=10.0)
    
    inp = AnalyticalEngineInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op,
        num_planes=5,
    )
    
    solver = HalbachArraySolver(inp)
    r_avg = (geom.r_out + geom.r_in) / 2.0
    theta = np.linspace(0, 2 * np.pi, 50)
    
    fields = solver.compute_airgap_field(r_avg, theta, z=0.0)
    assert "Bz" in fields
    assert fields["Bz"].shape == (50,)


def test_losses_evaluator(sample_input):
    """Verifies multi-physics loss model outputs."""
    evaluator = LossModelEvaluator(sample_input)
    
    # Copper losses
    copper = evaluator.compute_copper_losses(sample_input.operating_point, r_dc=0.05)
    assert copper["p_copper_dc"] > 0
    assert copper["p_copper_total"] >= copper["p_copper_dc"]
    
    # Core losses
    core = evaluator.compute_core_losses(sample_input.operating_point, b_peak=0.9)
    assert core["p_hysteresis"] > 0
    assert core["p_eddy"] > 0
    assert core["p_core_total"] > 0


def test_analytical_engine_run(sample_input):
    """Verifies end-to-end run execution of AnalyticalEngine."""
    engine = AnalyticalEngine()
    
    # Validate input
    val = engine.validate_input(sample_input)
    assert val.is_valid
    
    # Run simulation
    output = engine.run(sample_input)
    
    assert output.efficiency > 0.0
    assert output.torque_nm > 0.0
    assert output.computation_time_ms > 0.0
