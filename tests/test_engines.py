"""
Unit tests for the modular engine wrappers in NeuroFlux.
"""

from __future__ import annotations

import pytest
import os
from pathlib import Path

from neuroflux.core.models import MachineGeometry, OperatingPoint, AFPMTopology, WindingParameters
from neuroflux.core.materials import MaterialDatabase

from neuroflux.engines.autocoil_engine import AutocoilEngine, AutocoilInput
from neuroflux.engines.maggen_engine import MagGenEngine, MagGenInput
from neuroflux.engines.openafpm_engine import OpenAFPMEngine, OpenAFPMInput
from neuroflux.engines.femm_engine import FEMMEngine, FEMMInput
from neuroflux.engines.pyleecan_engine import PYLEECANEngine, PYLEECANInput
from neuroflux.engines.elmer_engine import ElmerEngine, ElmerInput


def test_autocoil_engine():
    engine = AutocoilEngine()
    inp = AutocoilInput(
        num_poles=16,
        num_phases=3,
        num_layers=4,
        inner_radius=0.015,
        outer_radius=0.060,
        trace_width=0.3e-3,
        trace_spacing=0.15e-3,
        copper_thickness=35e-6
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.total_turns > 0
    assert out.phase_resistance_ohm > 0
    assert out.estimated_inductance_h > 0
    assert out.copper_area_m2 > 0
    assert out.computation_time_ms > 0
    
    # Check that output PCB file was created (if fallback didn't empty it)
    if out.pcb_file_path:
        assert Path(out.pcb_file_path).exists()


def test_maggen_engine():
    engine = MagGenEngine()
    inp = MagGenInput(
        rotor_diameter=0.120,
        num_poles=8,
        num_coils=8,
        magnet_shape="rectangular",
        manufacturing_process="3d_print",
        output_format="stl"
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.computation_time_ms > 0
    assert len(out.dfm_warnings) > 0  # Should contain typical 3D print warnings
    assert out.rotor_file_path != ""


def test_openafpm_engine():
    engine = OpenAFPMEngine()
    inp = OpenAFPMInput(
        rotor_disk_radius=0.187,
        magnet_length=0.050,
        magnet_width=0.070,
        magnet_thickness=0.010,
        number_of_magnets=16,
        coil_inner_width=0.035,
        coil_type="triangular",
        wire_gauge=0.0015,
        number_of_turns=25,
        target_rpm=300.0
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.estimated_power_w > 0
    assert out.estimated_voltage_v > 0
    assert out.coil_resistance_ohm > 0
    assert out.magnet_flux_t > 0
    assert out.computation_time_ms > 0


def test_femm_engine_fallback():
    engine = FEMMEngine()
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
    
    inp = FEMMInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.torque_nm > 0
    assert out.back_emf_v > 0
    assert out.B_airgap_peak > 0
    assert out.copper_loss_w > 0
    assert out.computation_time_ms > 0


def test_pyleecan_engine_fallback():
    engine = PYLEECANEngine()
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
    
    inp = PYLEECANInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.torque_nm > 0
    assert out.back_emf_rms > 0
    assert len(out.flux_density_airgap) > 0
    assert out.computation_time_ms > 0


def test_elmer_engine_fallback():
    engine = ElmerEngine()
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
    
    inp = ElmerInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op
    )
    val = engine.validate_input(inp)
    assert val.is_valid
    
    out = engine.run(inp)
    assert out.torque_nm > 0
    assert out.axial_force_n > 0
    assert out.B_max > 0
    assert len(out.B_airgap_distribution) > 0
    assert out.computation_time_ms > 0
