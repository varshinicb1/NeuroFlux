"""Tests for the unified AFPM generator design engine."""

from __future__ import annotations

import json

from neuroflux.core.models import AFPMTopology
from neuroflux.design import AFPMDesignEngine, AFPMGeneratorSpec
from neuroflux.lab.cli import main


def test_design_engine_writes_complete_design_package(tmp_path):
    engine = AFPMDesignEngine(output_root=tmp_path)
    spec = AFPMGeneratorSpec(
        name="low-speed-wind-250w",
        target_power_w=250.0,
        target_speed_rpm=600.0,
        target_voltage_v=48.0,
        max_outer_diameter_m=0.32,
        min_efficiency=0.50,
        topology=AFPMTopology.DSSR_SLOTTED,
        iterations=2,
        num_candidates=4,
        num_planes=5,
    )

    result = engine.design(spec)

    assert result.spec.name == "low-speed-wind-250w"
    assert result.best_candidate is not None
    assert result.best_candidate.analytical_result.power_w <= spec.target_power_w * 2.0
    assert result.thermal_analysis.max_winding_temp_c >= spec.ambient_temp_c
    assert result.thermal_analysis.status in {"pass", "warning", "fail"}
    assert result.rendering_scene.meshes
    assert result.rendering_scene.meshes[0].kind == "rotor_disk"
    assert result.design_package_dir.endswith("low-speed-wind-250w")

    expected_files = {
        "design_manifest.json",
        "design_report.md",
        "geometry.geo",
        "assembly.scad",
        "assembly.stl",
        "cad_index.json",
        "scene3d.json",
        "viewer.html",
        "thermal_analysis.json",
        "parameters.csv",
    }
    package_files = {path.name for path in tmp_path.joinpath("low-speed-wind-250w").iterdir()}
    assert expected_files.issubset(package_files)

    manifest = json.loads(
        tmp_path.joinpath("low-speed-wind-250w", "design_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["spec"]["target_power_w"] == 250.0
    assert manifest["best_candidate"]["candidate_id"]
    assert manifest["artifacts"]["viewer_html"].endswith("viewer.html")
    assert manifest["artifacts"]["assembly_scad"].endswith("assembly.scad")
    assert manifest["artifacts"]["assembly_stl"].endswith("assembly.stl")
    assert manifest["artifacts"]["cad_index_json"].endswith("cad_index.json")
    assert manifest["thermal_analysis"]["total_losses_w"] > 0

    cad_index = json.loads(
        tmp_path.joinpath("low-speed-wind-250w", "cad_index.json").read_text(encoding="utf-8")
    )
    assert cad_index["formats"]["openscad"].endswith("assembly.scad")
    assert cad_index["parts"][0]["name"] == "rotor_back_iron"


def test_design_engine_builds_use_case_defaults(tmp_path):
    engine = AFPMDesignEngine(output_root=tmp_path)

    result = engine.design_low_speed_250w_generator()

    assert result.spec.name == "low-speed-250w-afpm-generator"
    assert result.spec.target_speed_rpm == 600.0
    assert result.best_candidate is not None
    assert result.best_candidate.analytical_input.geometry.D_out <= result.spec.max_outer_diameter_m


def test_design_cli_writes_unified_design_manifest(tmp_path):
    exit_code = main(
        [
            "design",
            "--output",
            str(tmp_path),
            "--name",
            "cli-low-speed",
            "--iterations",
            "1",
            "--num-candidates",
            "2",
        ]
    )

    assert exit_code == 0
    assert tmp_path.joinpath("cli-low-speed", "design_manifest.json").exists()
