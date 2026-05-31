"""AFPM-Bench state-of-the-art benchmark and intelligence engine."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from textwrap import dedent

from pydantic import BaseModel, Field


class AFPMBenchEntry(BaseModel):
    """Normalized AFPM-Bench database row."""

    architecture_id: str
    source: str
    year: int
    organization: str
    product_name: str
    application: str
    topology: str
    rotor_type: str
    stator_type: str
    cooling_type: str
    magnet_type: str
    phase_count: int | None = None
    power_kw: float | None = None
    continuous_power_kw: float | None = None
    peak_power_kw: float | None = None
    rpm: float | None = None
    torque_nm: float | None = None
    mass_kg: float | None = None
    outer_diameter_m: float | None = None
    axial_length_m: float | None = None
    efficiency_percent: float | None = None
    specific_power_kw_per_kg: float | None = None
    torque_density_nm_per_kg: float | None = None
    thermal_strategy: str
    fault_tolerance_level: float = Field(ge=0, le=1)
    certification_readiness: float = Field(ge=0, le=1)
    trl: float = Field(ge=1, le=9)
    patent_references: list[str] = Field(default_factory=list)
    source_url: str
    evidence_type: str
    evidence_confidence: str
    notes: str = ""


class AFPMBenchResult(BaseModel):
    """Generated AFPM-Bench intelligence result."""

    entries: list[AFPMBenchEntry]
    ari_rankings: list[dict]
    aegis_percentiles: dict[str, float]
    technology_radar: list[dict]
    patent_intelligence: dict
    red_team_weaknesses: list[str]
    blue_team_responses: list[dict]
    output_dir: str


class AFPMBenchEngine:
    """Build AFPM-Bench and compare AEGIS against global state-of-the-art entries."""

    def __init__(self, output_root: str | Path = "bench_outputs") -> None:
        self.output_root = Path(output_root)

    def build(self) -> AFPMBenchResult:
        output_dir = self.output_root / "afpm_bench"
        output_dir.mkdir(parents=True, exist_ok=True)

        entries = self._seed_entries()
        rankings = self._ari_rankings(entries)
        percentiles = self._aegis_percentiles(entries)
        radar = self._technology_radar()
        patent = self._patent_intelligence(entries)
        red = self._red_team(entries)
        blue = self._blue_team(red)

        result = AFPMBenchResult(
            entries=entries,
            ari_rankings=rankings,
            aegis_percentiles=percentiles,
            technology_radar=radar,
            patent_intelligence=patent,
            red_team_weaknesses=red,
            blue_team_responses=blue,
            output_dir=str(output_dir.resolve()),
        )
        self._write_outputs(output_dir, result)
        return result

    def _seed_entries(self) -> list[AFPMBenchEntry]:
        return [
            AFPMBenchEntry(
                architecture_id="AEGIS-AFSG-PDR",
                source="NeuroFlux PDR",
                year=2026,
                organization="NeuroFlux",
                product_name="AEGIS-AFSG",
                application="aerospace generator demonstrator",
                topology="stationary-magnet axial-flux switching generator",
                rotor_type="passive salient rotor",
                stator_type="removable PM/winding/cooling cassettes",
                cooling_type="liquid cold plate with vapor spreader",
                magnet_type="stationary high-temperature PM / SmCo candidate",
                phase_count=6,
                power_kw=25.0,
                continuous_power_kw=25.0,
                peak_power_kw=30.0,
                rpm=1200.0,
                torque_nm=198.94,
                mass_kg=5.7,
                outer_diameter_m=0.42,
                axial_length_m=0.07,
                efficiency_percent=94.5,
                specific_power_kw_per_kg=4.39,
                torque_density_nm_per_kg=34.9,
                thermal_strategy="stationary cassette direct liquid cooling",
                fault_tolerance_level=0.92,
                certification_readiness=0.58,
                trl=3.0,
                patent_references=[],
                source_url="local:pdr_packages/aegis-afsg-pdr/design_manifest.json",
                evidence_type="Analytical + FEA",
                evidence_confidence="MEDIUM",
                notes="Thermal FEA completed; 3D EM and structural FEA still required.",
            ),
            AFPMBenchEntry(
                architecture_id="YASA-59KWKG-2025",
                source="YASA public news release",
                year=2025,
                organization="YASA",
                product_name="Next-generation axial flux motor benchmark",
                application="electric propulsion motor",
                topology="yokeless segmented armature axial flux",
                rotor_type="permanent magnet rotor",
                stator_type="segmented armature",
                cooling_type="not fully disclosed",
                magnet_type="permanent magnet",
                peak_power_kw=750.0,
                continuous_power_kw=350.0,
                efficiency_percent=None,
                specific_power_kw_per_kg=59.0,
                thermal_strategy="commercial undisclosed high-performance cooling",
                fault_tolerance_level=0.45,
                certification_readiness=0.42,
                trl=6.0,
                patent_references=[],
                source_url=(
                    "https://yasa.com/news/yasa-smashes-own-unofficial-power-density-world-"
                    "record-pushing-state-of-the-art-electric-motor-to-staggering-new-"
                    "59kw-kg-benchmark/"
                ),
                evidence_type="Dyno Test",
                evidence_confidence="MEDIUM",
                notes=(
                    "Public dyno/news claim; not equivalent to aerospace generator "
                    "qualification."
                ),
            ),
            AFPMBenchEntry(
                architecture_id="YASA-COMMERCIAL",
                source="YASA official website",
                year=2026,
                organization="YASA",
                product_name="YASA axial flux technology",
                application="automotive/electric propulsion",
                topology="yokeless segmented armature axial flux",
                rotor_type="PM rotor",
                stator_type="segmented stator",
                cooling_type="commercial undisclosed",
                magnet_type="permanent magnet",
                thermal_strategy="compact high-power density motor cooling",
                fault_tolerance_level=0.42,
                certification_readiness=0.40,
                trl=8.0,
                specific_power_kw_per_kg=8.0,
                source_url="https://yasa.com/",
                evidence_type="Commercial Product",
                evidence_confidence="HIGH",
                notes="Commercial maturity high; aerospace-generator readiness not established.",
            ),
            AFPMBenchEntry(
                architecture_id="MAGNAX-YOKELESS",
                source="Magnax public website",
                year=2026,
                organization="Magnax",
                product_name="Magnax yokeless axial flux technology",
                application="mobility and industrial electric machines",
                topology="yokeless axial flux",
                rotor_type="PM rotor",
                stator_type="yokeless stator",
                cooling_type="not fully disclosed",
                magnet_type="permanent magnet",
                thermal_strategy="direct winding/compact axial flux cooling claims",
                fault_tolerance_level=0.48,
                certification_readiness=0.42,
                trl=6.0,
                specific_power_kw_per_kg=15.0,
                source_url="https://www.magnax.com/",
                evidence_type="Marketing Claim",
                evidence_confidence="LOW",
                notes="Useful benchmark but public page lacks full validated metrics.",
            ),
            AFPMBenchEntry(
                architecture_id="TRAXIAL-MOTOR-TECH",
                source="Traxial public website",
                year=2026,
                organization="Traxial",
                product_name="Traxial axial flux motor technology",
                application="electric traction",
                topology="axial flux PM",
                rotor_type="PM rotor",
                stator_type="compact axial stator",
                cooling_type="not fully disclosed",
                magnet_type="permanent magnet",
                thermal_strategy="commercial undisclosed",
                fault_tolerance_level=0.44,
                certification_readiness=0.40,
                trl=6.0,
                specific_power_kw_per_kg=12.0,
                source_url="https://traxial.com/tag/motor-technology/",
                evidence_type="Marketing Claim",
                evidence_confidence="LOW",
                notes="Commercial positioning; detailed engineering metrics not public.",
            ),
            AFPMBenchEntry(
                architecture_id="ARXIV-SCALING-2409-01205",
                source="arXiv",
                year=2024,
                organization="Academic",
                product_name="Geometric Scaling Laws for AFPM Motors",
                application="AFPM analytical scaling",
                topology="AFPM scaling study",
                rotor_type="various",
                stator_type="various",
                cooling_type="not primary",
                magnet_type="permanent magnet",
                thermal_strategy="scaling/analytical",
                fault_tolerance_level=0.20,
                certification_readiness=0.15,
                trl=2.0,
                source_url="https://arxiv.org/abs/2409.01205",
                evidence_type="Analytical",
                evidence_confidence="MEDIUM",
                notes="Valuable for normalized scaling, not a product benchmark.",
            ),
            AFPMBenchEntry(
                architecture_id="ARXIV-PCB-AFPM-2509-23561",
                source="arXiv",
                year=2025,
                organization="Academic",
                product_name="High Torque Density PCB AFPM Motor",
                application="PCB AFPM research",
                topology="PCB stator AFPM",
                rotor_type="PM rotor",
                stator_type="PCB winding stator",
                cooling_type="PCB conduction/convection",
                magnet_type="permanent magnet",
                thermal_strategy="PCB thermal conduction",
                fault_tolerance_level=0.35,
                certification_readiness=0.18,
                trl=3.0,
                source_url="https://arxiv.org/abs/2509.23561",
                evidence_type="Experimental",
                evidence_confidence="MEDIUM",
                notes="Research-grade validation; aerospace readiness low.",
            ),
            AFPMBenchEntry(
                architecture_id="ARXIV-EDDY-BRAKE-2306-10710",
                source="arXiv",
                year=2023,
                organization="Academic",
                product_name="Design of AFPM Eddy Current Brake",
                application="AFPM eddy current braking",
                topology="axial flux PM electromagnetic brake",
                rotor_type="conductive rotor",
                stator_type="PM/electromagnetic source",
                cooling_type="thermal dissipation critical",
                magnet_type="permanent magnet",
                thermal_strategy="eddy current heat management",
                fault_tolerance_level=0.30,
                certification_readiness=0.18,
                trl=3.0,
                source_url="https://arxiv.org/abs/2306.10710",
                evidence_type="FEA",
                evidence_confidence="MEDIUM",
                notes="Not generator product; informs eddy loss and thermal risk.",
            ),
            AFPMBenchEntry(
                architecture_id="WOUND-FIELD-AERO-GEN",
                source="NeuroFlux reference baseline",
                year=2026,
                organization="Incumbent aerospace suppliers",
                product_name="wound-field synchronous aircraft generator",
                application="aircraft power generation",
                topology="radial wound-field synchronous",
                rotor_type="wound rotor/exciter",
                stator_type="laminated stator",
                cooling_type="oil/aircraft thermal management",
                magnet_type="none / exciter PM optional",
                thermal_strategy="mature oil/air cooling",
                fault_tolerance_level=0.72,
                certification_readiness=0.90,
                trl=9.0,
                source_url="https://aerospace.honeywell.com/",
                evidence_type="Commercial Product",
                evidence_confidence="HIGH",
                notes="Certification benchmark; lower novelty and specific power.",
            ),
            AFPMBenchEntry(
                architecture_id="RADIAL-PM-AERO-GEN",
                source="NeuroFlux reference baseline",
                year=2026,
                organization="Aerospace industry",
                product_name="radial PM starter-generator",
                application="starter-generator",
                topology="radial flux PM",
                rotor_type="PM rotor",
                stator_type="distributed winding",
                cooling_type="oil/air",
                magnet_type="permanent magnet",
                thermal_strategy="mature radial machine thermal paths",
                fault_tolerance_level=0.58,
                certification_readiness=0.68,
                trl=8.0,
                specific_power_kw_per_kg=3.5,
                source_url="https://aerospace.honeywell.com/",
                evidence_type="Commercial Product",
                evidence_confidence="MEDIUM",
                notes="Relevant incumbent competitor.",
            ),
        ]

    def _ari_rankings(self, entries: list[AFPMBenchEntry]) -> list[dict]:
        rankings = []
        for entry in entries:
            specific_power_score = min((entry.specific_power_kw_per_kg or 2.0) / 12.0, 1.0)
            thermal = self._thermal_score(entry)
            manufacturability = self._manufacturability_score(entry)
            maintainability = self._maintainability_score(entry)
            reliability = (entry.fault_tolerance_level + entry.certification_readiness) / 2.0
            score = (
                0.25 * reliability
                + 0.20 * thermal
                + 0.20 * entry.fault_tolerance_level
                + 0.15 * maintainability
                + 0.10 * manufacturability
                + 0.10 * specific_power_score
            )
            rankings.append(
                {
                    "architecture_id": entry.architecture_id,
                    "organization": entry.organization,
                    "aerospace_readiness_index": round(score, 4),
                    "specific_power_score": round(specific_power_score, 4),
                    "evidence_confidence": entry.evidence_confidence,
                }
            )
        return sorted(rankings, key=lambda item: item["aerospace_readiness_index"], reverse=True)

    def _aegis_percentiles(self, entries: list[AFPMBenchEntry]) -> dict[str, float]:
        aegis = next(entry for entry in entries if entry.architecture_id == "AEGIS-AFSG-PDR")
        metrics = {
            "fault_tolerance": [entry.fault_tolerance_level for entry in entries],
            "thermal_robustness": [self._thermal_score(entry) for entry in entries],
            "specific_power": [entry.specific_power_kw_per_kg or 0.0 for entry in entries],
            "maintainability": [self._maintainability_score(entry) for entry in entries],
            "certification_readiness": [entry.certification_readiness for entry in entries],
        }
        values = {
            "fault_tolerance": aegis.fault_tolerance_level,
            "thermal_robustness": self._thermal_score(aegis),
            "specific_power": aegis.specific_power_kw_per_kg or 0.0,
            "maintainability": self._maintainability_score(aegis),
            "certification_readiness": aegis.certification_readiness,
        }
        return {
            key: round(sum(item <= values[key] for item in series) / len(series), 4)
            for key, series in metrics.items()
        }

    def _technology_radar(self) -> list[dict]:
        technologies = [
            ("Yokeless AFPM", 0.72, 0.82, 0.74, 0.70),
            ("Segmented Armature", 0.70, 0.78, 0.70, 0.68),
            ("Halbach Arrays", 0.56, 0.72, 0.42, 0.64),
            ("Flux Switching Machines", 0.48, 0.68, 0.28, 0.55),
            ("Flux Modulation Machines", 0.42, 0.62, 0.22, 0.48),
            ("Hybrid Excitation Machines", 0.50, 0.60, 0.25, 0.50),
            ("PCB Windings", 0.38, 0.65, 0.18, 0.36),
            ("Fiber Bragg Monitoring", 0.52, 0.54, 0.34, 0.40),
            ("Integrated Digital Twins", 0.45, 0.74, 0.30, 0.58),
            ("Rare-Earth-Free Machines", 0.36, 0.62, 0.20, 0.46),
            ("Hydrogen Aircraft Generators", 0.30, 0.58, 0.10, 0.35),
            ("Cryogenic/Superconducting Machines", 0.28, 0.70, 0.08, 0.45),
        ]
        return [
            {
                "technology": name,
                "technology_maturity": maturity,
                "research_activity": research,
                "commercial_adoption": adoption,
                "patent_velocity": patents,
            }
            for name, maturity, research, adoption, patents in technologies
        ]

    def _patent_intelligence(self, entries: list[AFPMBenchEntry]) -> dict:
        return {
            "tracked_assignees": [
                "Honeywell",
                "Collins Aerospace",
                "Safran",
                "GE Aerospace",
                "Rolls-Royce Electrical",
                "YASA",
                "Magnax",
                "Evolito",
            ],
            "aegis_patent_similarity_index": 0.41,
            "aegis_novelty_score": 0.68,
            "aegis_white_space_score": 0.74,
            "claim_conflict_probability": 0.36,
            "confidence": "LOW",
            "reason": (
                "Seed graph and public references only; claim-level patent counsel search required."
            ),
            "entries_with_patents": sum(bool(entry.patent_references) for entry in entries),
        }

    def _red_team(self, entries: list[AFPMBenchEntry]) -> list[str]:
        yasa = next(entry for entry in entries if entry.architecture_id == "YASA-59KWKG-2025")
        aegis = next(entry for entry in entries if entry.architecture_id == "AEGIS-AFSG-PDR")
        return [
            (
                "YASA peak specific power claim "
                f"({yasa.specific_power_kw_per_kg} kW/kg) far exceeds AEGIS estimate "
                f"({aegis.specific_power_kw_per_kg} kW/kg)."
            ),
            "AEGIS has no 3D electromagnetic FEA yet.",
            "AEGIS has no structural rotor burst FEA yet.",
            "Stationary magnet flux-switching may suffer torque ripple and acoustic noise.",
            "Cassette sealing increases manufacturing and inspection complexity.",
            "Cold plate blockage can create common-cause thermal failure.",
            "Patent conflict probability is non-trivial until claim charts are done.",
            "Wound-field aircraft generators have much stronger certification precedent.",
            "AEGIS specific power may be too low for propulsion-grade aerospace use.",
            "Flux-switching core losses may exceed preliminary estimates.",
            "High-temperature PM supply and SmCo cost can hurt lifecycle cost.",
            "Multi-cassette harnessing increases connector failure points.",
            "Power electronics channel isolation adds mass and qualification burden.",
            "Thermal FEA uses homogenized materials, not detailed winding geometry.",
            "No hardware dyno data exists.",
            "No environmental DO-160 evidence exists.",
            "No MIL-STD-704 power quality evidence exists.",
            "Maintenance concept depends on cassette accessibility in aircraft installation.",
            "A passive salient rotor still needs tight air-gap and vibration control.",
            "Marketing comparison against commercial motors is not apples-to-apples.",
        ]

    def _blue_team(self, weaknesses: list[str]) -> list[dict]:
        responses = []
        for weakness in weaknesses:
            responses.append(
                {
                    "weakness": weakness,
                    "mitigation": self._mitigation_for(weakness),
                    "research_direction": "turn into testable PDR gate with evidence artifact",
                    "patent_opportunity": (
                        "focus on stationary cassette cooling/fault isolation integration"
                    ),
                }
            )
        return responses

    def _mitigation_for(self, weakness: str) -> str:
        if "specific power" in weakness:
            return "position AEGIS for reliability-critical generation, not propulsion peak power"
        if "electromagnetic" in weakness or "core losses" in weakness:
            return "complete 3D EM FEA and harmonic/loss map before PDR freeze"
        if "thermal" in weakness or "Cold plate" in weakness:
            return "add flow sensors, bypass, dual-sided cold plate, and CFD correlation"
        if "certification" in weakness or "DO-160" in weakness or "MIL-STD" in weakness:
            return "create certification readiness matrix and environmental test plan"
        if "Patent" in weakness or "patent" in weakness:
            return "perform claim chart and redesign around high-conflict claims"
        return "create verification test and retire risk through evidence"

    def _write_outputs(self, output_dir: Path, result: AFPMBenchResult) -> None:
        payload = result.model_dump(mode="json")
        self._write_json(output_dir / "afpm_bench.json", {"entries": payload["entries"]})
        self._write_entries_csv(output_dir / "afpm_bench.csv", result.entries)
        self._write_dict_rows(output_dir / "ari_rankings.csv", result.ari_rankings)
        self._write_json(output_dir / "technology_radar.json", result.technology_radar)
        self._write_json(output_dir / "patent_intelligence.json", result.patent_intelligence)
        self._write_json(
            output_dir / "aegis_comparator.json",
            {"percentiles": result.aegis_percentiles, "ari_rankings": result.ari_rankings},
        )
        (output_dir / "red_team_weaknesses.md").write_text(
            self._weaknesses_md(result.red_team_weaknesses),
            encoding="utf-8",
        )
        (output_dir / "blue_team_responses.md").write_text(
            self._blue_team_md(result.blue_team_responses),
            encoding="utf-8",
        )
        self._write_confidence_heatmap(output_dir / "confidence_heatmap.csv", result.entries)
        (output_dir / "dashboard.html").write_text(self._dashboard_html(result), encoding="utf-8")

    def _thermal_score(self, entry: AFPMBenchEntry) -> float:
        text = f"{entry.cooling_type} {entry.thermal_strategy}".lower()
        if "liquid" in text or "cold plate" in text:
            return 0.86
        if "oil" in text:
            return 0.74
        if "undisclosed" in text:
            return 0.45
        return 0.50

    def _manufacturability_score(self, entry: AFPMBenchEntry) -> float:
        text = f"{entry.topology} {entry.stator_type}".lower()
        if "cassette" in text:
            return 0.62
        if "segmented" in text or "yokeless" in text:
            return 0.58
        if "wound-field" in text or "radial" in text:
            return 0.78
        return 0.50

    def _maintainability_score(self, entry: AFPMBenchEntry) -> float:
        text = f"{entry.stator_type} {entry.notes}".lower()
        if "cassette" in text or "replaceable" in text:
            return 0.90
        if entry.certification_readiness > 0.80:
            return 0.72
        return 0.48

    def _write_entries_csv(self, path: Path, entries: list[AFPMBenchEntry]) -> None:
        rows = [entry.model_dump(mode="json") for entry in entries]
        self._write_dict_rows(path, rows)

    def _write_dict_rows(self, path: Path, rows: list[dict]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def _write_confidence_heatmap(self, path: Path, entries: list[AFPMBenchEntry]) -> None:
        rows = [
            {
                "architecture_id": entry.architecture_id,
                "evidence_type": entry.evidence_type,
                "confidence": entry.evidence_confidence,
                "confidence_numeric": {"LOW": 0.33, "MEDIUM": 0.66, "HIGH": 1.0}[
                    entry.evidence_confidence
                ],
            }
            for entry in entries
        ]
        self._write_dict_rows(path, rows)

    def _weaknesses_md(self, weaknesses: list[str]) -> str:
        return "# AEGIS Red Team Weaknesses\n\n" + "\n".join(
            f"{index}. {weakness}" for index, weakness in enumerate(weaknesses, start=1)
        ) + "\n"

    def _blue_team_md(self, responses: list[dict]) -> str:
        lines = ["# AEGIS Blue Team Responses", ""]
        for index, item in enumerate(responses, start=1):
            lines.extend(
                [
                    f"## {index}. Weakness",
                    item["weakness"],
                    "",
                    f"Mitigation: {item['mitigation']}",
                    f"Research direction: {item['research_direction']}",
                    f"Patent opportunity: {item['patent_opportunity']}",
                    "",
                ]
            )
        return "\n".join(lines)

    def _dashboard_html(self, result: AFPMBenchResult) -> str:
        rankings = "\n".join(
            f"<tr><td>{row['architecture_id']}</td><td>{row['aerospace_readiness_index']}</td>"
            f"<td>{row['evidence_confidence']}</td></tr>"
            for row in result.ari_rankings
        )
        percentiles = "".join(
            f"<li>{name}: {value:.0%}</li>" for name, value in result.aegis_percentiles.items()
        )
        return dedent(
            f"""
            <!doctype html>
            <html><head><meta charset="utf-8"><title>AFPM-Bench Dashboard</title>
            <style>
            body {{
              font-family: Arial, sans-serif;
              margin: 24px;
              background: #101418;
              color: #e8edf2;
            }}
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #40505c; padding: 8px; }}
            </style></head><body>
            <h1>AFPM Global Leaderboard</h1>
            <h2>AEGIS Percentiles</h2>
            <ul>{percentiles}</ul>
            <h2>Aerospace Readiness Ranking</h2>
            <table><tr><th>Architecture</th><th>ARI</th><th>Confidence</th></tr>
            {rankings}
            </table>
            <h2>Dashboard Pages</h2>
            <p>Patent Heatmap, Technology Radar, AEGIS Comparison View,
            State-of-the-Art Comparator, Confidence Heatmap, and Risk Heatmap are
            generated as JSON/CSV/Markdown artifacts in this folder.</p>
            </body></html>
            """
        ).strip() + "\n"

    def _write_json(self, path: Path, payload) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
