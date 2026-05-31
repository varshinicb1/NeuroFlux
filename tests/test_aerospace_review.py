"""Tests for the Honeywell-grade aerospace AFPM review package."""

from __future__ import annotations

import json

from neuroflux.aerospace import AerospaceReviewEngine, AerospaceReviewSpec


def test_aerospace_review_generates_50_candidates_and_evidence_package(tmp_path):
    engine = AerospaceReviewEngine(output_root=tmp_path)

    package = engine.run(
        AerospaceReviewSpec(
            name="honeywell-low-speed-afpm",
            target_power_kw=25.0,
            target_speed_rpm=1200.0,
            iterations=2,
        )
    )

    assert len(package.candidates) >= 50
    assert abs(sum(package.scoring_weights.values()) - 1.0) < 1e-9
    assert package.top_candidate.mission_success_score > 0.0
    assert package.top_candidate.architecture.family
    assert package.hostile_review_rounds[-1].major_objections_remaining == 0
    assert package.confidence_register["analytical_model"] in {
        "HIGH CONFIDENCE",
        "MEDIUM CONFIDENCE",
        "LOW CONFIDENCE",
    }

    output_dir = tmp_path / "honeywell-low-speed-afpm"
    expected = {
        "executive_summary.md",
        "phase0_challenge_deconstruction.md",
        "competitive_landscape.csv",
        "candidate_trade_study.csv",
        "novelty_map.json",
        "requirements.json",
        "risk_register.csv",
        "fmea.csv",
        "manufacturing_bom.csv",
        "test_plan.md",
        "thermal_fea3d_report.md",
        "validation_package.json",
    }
    assert expected.issubset({path.name for path in output_dir.iterdir()})
    assert (output_dir / "thermal_fea3d_baseline" / "thermal_fea3d.vtk").exists()
    assert (output_dir / "thermal_fea3d_revised" / "thermal_fea3d.vtk").exists()

    validation = json.loads((output_dir / "validation_package.json").read_text(encoding="utf-8"))
    assert validation["thermal_fea3d_result"]["max_temp_c"] > 0
    assert validation["thermal_fea3d_result"]["thermal_margin_to_180c"] > 0
    assert (
        validation["top_candidate"]["mission_success_score"]
        == package.top_candidate.mission_success_score
    )
