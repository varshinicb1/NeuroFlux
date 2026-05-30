"""Tests for the autonomous AFPM lab loop."""

from __future__ import annotations

import json

from neuroflux.core.models import AFPMTopology
from neuroflux.discovery import DesignRequirements
from neuroflux.lab import AutonomousLab, LabRunConfig, PatentKnowledgeGraph
from neuroflux.lab.cli import main


def _requirements() -> DesignRequirements:
    return DesignRequirements(
        target_power_w=180.0,
        target_speed_rpm=600.0,
        target_voltage_v=48.0,
        max_outer_diameter_m=0.28,
        min_efficiency=0.45,
        topology=AFPMTopology.DSSR_SLOTTED,
        num_candidates=3,
        num_planes=5,
    )


def test_patent_graph_scores_candidate_features():
    graph = PatentKnowledgeGraph.seed_afpm_baseline()

    score = graph.score_novelty(
        [
            "DSSR slotted axial flux generator",
            "manufacturing DFM checked",
            "embedded sensor thermal digital twin",
        ]
    )

    assert 0.0 <= score.novelty_score <= 1.0
    assert score.closest_nodes
    assert "embedded" in score.differentiators


def test_autonomous_lab_writes_manifest_and_iteration_artifacts(tmp_path):
    lab = AutonomousLab(output_root=tmp_path)

    result = lab.run(
        LabRunConfig(
            requirements=_requirements(),
            iterations=2,
            run_id="test-run",
        )
    )

    run_dir = tmp_path / "test-run"
    assert result.best_candidate is not None
    assert len(result.iterations) == 2
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "summary.md").exists()
    assert (run_dir / "iteration_001.json").exists()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "test-run"
    assert manifest["best_candidate"]["candidate_id"]


def test_lab_cli_runs_and_writes_manifest(tmp_path):
    exit_code = main(
        [
            "run",
            "--iterations",
            "1",
            "--output",
            str(tmp_path),
            "--target-power-w",
            "120",
            "--num-candidates",
            "2",
        ]
    )

    assert exit_code == 0
    manifests = list(tmp_path.glob("*/manifest.json"))
    assert len(manifests) == 1
