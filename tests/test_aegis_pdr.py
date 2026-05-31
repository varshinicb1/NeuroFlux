"""Tests for the AEGIS-AFSG Preliminary Design Review package."""

from __future__ import annotations

import json

from neuroflux.pdr import AegisPDRGenerator, AegisPDRSpec


def test_aegis_pdr_generates_review_package_with_monte_carlo_and_artifacts(tmp_path):
    package = AegisPDRGenerator(output_root=tmp_path).generate(
        AegisPDRSpec(
            name="aegis-afsg-pdr",
            target_power_kw=25.0,
            target_speed_rpm=1200.0,
            dc_bus_voltage_v=540.0,
            monte_carlo_samples=750,
        )
    )

    output_dir = tmp_path / "aegis-afsg-pdr"
    expected = {
        "executive_summary.md",
        "trade_study.md",
        "novelty_report.md",
        "patentability_assessment.md",
        "electromagnetic_report.md",
        "thermal_report.md",
        "mechanical_report.md",
        "reliability_report.md",
        "fmea.csv",
        "monte_carlo_analysis.json",
        "certification_readiness_report.md",
        "manufacturing_report.md",
        "digital_twin_architecture.md",
        "risk_register.csv",
        "technology_readiness_roadmap.md",
        "design_manifest.json",
        "thermal_analysis.json",
        "geometry.geo",
        "assembly.scad",
        "assembly.stl",
        "cad_index.json",
        "parameters.csv",
        "viewer.html",
        "scene3d.json",
        "design_report.md",
    }

    assert package.top_candidate["architecture"] == "AEGIS-AFSG"
    assert package.top_candidate["major_objections_remaining"] == 0
    assert package.monte_carlo["samples"] == 750
    assert package.monte_carlo["failure_probability"] < 0.35
    assert package.thermal_fea["revised"]["thermal_margin_to_180c"] > 0
    assert expected.issubset({path.name for path in output_dir.iterdir()})
    assert (output_dir / "solver_handoffs" / "elmer_case" / "case.sif").exists()
    assert (output_dir / "solver_handoffs" / "palace_case" / "palace.json").exists()

    manifest = json.loads((output_dir / "design_manifest.json").read_text(encoding="utf-8"))
    assert manifest["concept"] == "AEGIS-AFSG"
    assert manifest["validation_status"]["thermal_fea"] == "completed"
    assert manifest["validation_status"]["elmer_handoff"] == "generated_not_executed"
    assert manifest["validation_status"]["palace_handoff"] == "generated_not_executed"
