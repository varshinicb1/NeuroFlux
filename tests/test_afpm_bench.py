"""Tests for AFPM-Bench state-of-the-art intelligence engine."""

from __future__ import annotations

import json

from neuroflux.bench import AFPMBenchEngine


def test_afpm_bench_builds_database_rankings_radar_and_dashboard(tmp_path):
    result = AFPMBenchEngine(output_root=tmp_path).build()

    assert len(result.entries) >= 10
    assert result.aegis_percentiles["fault_tolerance"] >= 0.80
    assert result.aegis_percentiles["specific_power"] < 0.90
    assert result.ari_rankings[0]["architecture_id"]
    assert result.red_team_weaknesses
    assert result.blue_team_responses

    output_dir = tmp_path / "afpm_bench"
    expected = {
        "afpm_bench.json",
        "afpm_bench.csv",
        "ari_rankings.csv",
        "technology_radar.json",
        "patent_intelligence.json",
        "aegis_comparator.json",
        "red_team_weaknesses.md",
        "blue_team_responses.md",
        "dashboard.html",
        "confidence_heatmap.csv",
    }
    assert expected.issubset({path.name for path in output_dir.iterdir()})

    bench = json.loads((output_dir / "afpm_bench.json").read_text(encoding="utf-8"))
    yasa = next(
        entry for entry in bench["entries"] if entry["architecture_id"] == "YASA-59KWKG-2025"
    )
    assert yasa["specific_power_kw_per_kg"] == 59.0
    assert yasa["evidence_type"] == "Dyno Test"
    assert yasa["evidence_confidence"] == "MEDIUM"


def test_marketing_claims_do_not_receive_high_confidence(tmp_path):
    result = AFPMBenchEngine(output_root=tmp_path).build()

    marketing_entries = [
        entry for entry in result.entries if entry.evidence_type == "Marketing Claim"
    ]

    assert marketing_entries
    assert all(entry.evidence_confidence != "HIGH" for entry in marketing_entries)
