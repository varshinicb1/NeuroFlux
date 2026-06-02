"""End-to-end tests for the NeuroFlux discovery workflow."""

from __future__ import annotations

from neuroflux.core.models import AFPMTopology
from neuroflux.discovery import DesignRequirements, DiscoveryWorkflow


def test_discovery_workflow_generates_ranked_slotted_candidates():
    workflow = DiscoveryWorkflow()
    requirements = DesignRequirements(
        target_power_w=250.0,
        target_speed_rpm=600.0,
        target_voltage_v=48.0,
        max_outer_diameter_m=0.32,
        min_efficiency=0.50,
        topology=AFPMTopology.DSSR_SLOTTED,
        num_candidates=4,
        num_planes=5,
    )

    result = workflow.run(requirements)

    assert result.best_candidate is not None
    assert len(result.candidates) == 4
    assert result.candidates == sorted(result.candidates, key=lambda item: item.score, reverse=True)
    assert result.best_candidate.analytical_result.torque_nm > 0
    assert result.best_candidate.analytical_result.power_w >= 0
    assert result.best_candidate.analytical_input.geometry.topology == AFPMTopology.DSSR_SLOTTED


def test_discovery_workflow_runs_coreless_manufacturing_engines():
    import pytest
    workflow = DiscoveryWorkflow()
    requirements = DesignRequirements(
        target_power_w=120.0,
        target_speed_rpm=900.0,
        target_voltage_v=24.0,
        max_outer_diameter_m=0.18,
        min_efficiency=0.40,
        topology=AFPMTopology.SSDR_CORELESS,
        prefer_halbach=True,
        num_candidates=2,
        num_planes=5,
    )

    result = workflow.run(requirements)

    assert result.best_candidate is not None
    assert len(result.candidates) == 2
    best = result.best_candidate
    assert best.analytical_input.geometry.topology == AFPMTopology.SSDR_CORELESS_HALBACH
    
    # Check if OpenAFPM is available (compulsory but external)
    try:
        import openafpm_cad_core
        has_openafpm = True
    except ImportError:
        has_openafpm = False
    
    if has_openafpm:
        assert best.openafpm_result is not None
        assert best.openafpm_result.estimated_power_w > 0
    else:
        # Should have warning about missing OpenAFPM
        assert any("OpenAFPM not available" in w for w in result.warnings)
    
    assert best.maggen_result is not None
    assert best.maggen_result.rotor_file_path != ""
    assert best.autocoil_result is not None
    assert best.autocoil_result.total_turns > 0
