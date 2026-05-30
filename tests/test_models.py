"""
Unit tests for NeuroFlux models validation.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from neuroflux.core.models import MachineGeometry, OperatingPoint, AnalyticalEngineInput, AFPMTopology, WindingParameters
from neuroflux.core.materials import MaterialDatabase


def test_valid_geometry():
    """Verifies that a physically plausible geometry passes validation."""
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
    assert geom.r_out > geom.r_in
    assert geom.p > 0


def test_invalid_geometry_radii():
    """Verifies that negative or zero outer diameter fails validation."""
    with pytest.raises(ValidationError):
        MachineGeometry(
            D_out=-0.30,
            k_D=0.6,
            l_s=0.05,
            g=0.003,
            l_PM=0.005,
            w_PM=0.02,
            p=8,
            Q=18,
            topology=AFPMTopology.DSSR_SLOTTED,
        )


def test_engine_input_construction():
    """Verifies standard input creation with default materials."""
    materials = MaterialDatabase().build_material_properties("N42", "M600-50A")
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
    )
    
    assert inp.geometry.topology == AFPMTopology.DSSR_SLOTTED
    assert inp.operating_point.speed_rpm == 1500.0
