"""Tests for the 3D thermal FEA solver."""

from __future__ import annotations

import json

from neuroflux.core.models import AFPMTopology
from neuroflux.fea import ThermalFEA3DInput, ThermalFEA3DSolver


def test_thermal_fea3d_solves_annular_machine_and_writes_artifacts(tmp_path):
    solver = ThermalFEA3DSolver()
    result = solver.solve(
        ThermalFEA3DInput(
            name="thermal-proof",
            outer_radius_m=0.18,
            inner_radius_m=0.07,
            axial_length_m=0.045,
            total_loss_w=450.0,
            copper_loss_fraction=0.72,
            ambient_temp_c=70.0,
            coolant_temp_c=55.0,
            convection_w_per_m2k=220.0,
            conductivity_w_per_mk=26.0,
            topology=AFPMTopology.DSSR_SLOTTED,
            radial_nodes=14,
            angular_nodes=24,
            axial_nodes=7,
            output_dir=tmp_path,
        )
    )

    assert result.node_count > 0
    assert result.converged is True
    assert result.max_temp_c > result.coolant_temp_c
    assert result.hotspot_radius_m >= 0.07
    assert result.hotspot_radius_m <= 0.18
    assert result.vtk_path.endswith("thermal_fea3d.vtk")
    assert result.summary_json_path.endswith("thermal_fea3d_summary.json")

    summary = json.loads((tmp_path / "thermal_fea3d_summary.json").read_text(encoding="utf-8"))
    assert summary["max_temp_c"] == result.max_temp_c
    assert (tmp_path / "thermal_fea3d.vtk").exists()
    assert "POINT_DATA" in (tmp_path / "thermal_fea3d.vtk").read_text(encoding="utf-8")
