"""Tests for external high-fidelity solver handoff generation."""

from __future__ import annotations

import json

from neuroflux.core.materials import MaterialDatabase
from neuroflux.core.models import AFPMTopology, MachineGeometry, OperatingPoint, WindingParameters
from neuroflux.solvers import ElmerHandoffBuilder, PalaceHandoffBuilder


def _case():
    geometry = MachineGeometry(
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
    return {
        "geometry": geometry,
        "materials": MaterialDatabase().build_material_properties("N42", "M600-50A"),
        "winding": WindingParameters(
            turns_per_phase=100,
            phases=3,
            fill_factor=0.6,
            current_density=5e6,
        ),
        "operating_point": OperatingPoint(speed_rpm=1500.0, I_rms=10.0),
    }


def test_elmer_handoff_builder_writes_sif_geo_and_gui_metadata(tmp_path):
    handoff = ElmerHandoffBuilder(output_root=tmp_path).build(**_case())

    assert handoff.solver_name == "Elmer FEM"
    assert handoff.gui_tool == "ElmerGUI"
    assert handoff.case_sif_path.endswith("case.sif")
    assert handoff.geometry_geo_path.endswith("geometry.geo")
    assert handoff.run_command == "ElmerSolver case.sif"
    assert "HeatSolve" in (tmp_path / "elmer_case" / "case.sif").read_text(encoding="utf-8")


def test_palace_handoff_builder_writes_json_config_and_manifest(tmp_path):
    handoff = PalaceHandoffBuilder(output_root=tmp_path).build(**_case())

    assert handoff.solver_name == "Palace"
    assert handoff.run_command.endswith("palace.json")
    config = json.loads((tmp_path / "palace_case" / "palace.json").read_text(encoding="utf-8"))
    assert config["Problem"]["Type"] == "Magnetostatic"
    assert config["Model"]["Mesh"].endswith("geometry.msh")
    assert (tmp_path / "palace_case" / "manifest.json").exists()
