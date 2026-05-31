"""Honeywell-grade aerospace AFPM concept review package.

The review engine is intentionally conservative. It does not claim completed
certification or validated 3D FEA. It generates a traceable evidence package
that separates analytical estimates from assumptions and low-confidence items.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from textwrap import dedent

from pydantic import BaseModel, Field

from neuroflux.core.models import AFPMTopology
from neuroflux.design import AFPMDesignEngine, AFPMGeneratorSpec
from neuroflux.fea import ThermalFEA3DInput, ThermalFEA3DResult, ThermalFEA3DSolver
from neuroflux.lab import PatentKnowledgeGraph, PriorArtNode

SCORING_WEIGHTS = {
    "aerospace_reliability": 0.25,
    "thermal_robustness": 0.20,
    "manufacturability": 0.15,
    "certification_readiness": 0.15,
    "specific_power": 0.10,
    "cost": 0.05,
    "maintainability": 0.05,
    "efficiency": 0.05,
}


class AerospaceReviewSpec(BaseModel):
    """Input assumptions for a skeptical aerospace concept review."""

    name: str = Field(default="honeywell-low-speed-afpm", min_length=1)
    target_power_kw: float = Field(default=25.0, gt=0)
    target_speed_rpm: float = Field(default=1200.0, gt=0)
    dc_bus_voltage_v: float = Field(default=540.0, gt=0)
    max_outer_diameter_m: float = Field(default=0.42, gt=0)
    coolant: str = "PAO/oil cold plate"
    design_life_hours: int = Field(default=20_000, gt=0)
    iterations: int = Field(default=2, ge=1, le=10)


class ArchitectureOption(BaseModel):
    """Candidate architecture description."""

    family: str
    topology: str
    rotor_stator: str
    core_type: str
    cooling: str
    winding: str
    excitation: str
    containment: str


class AerospaceCandidate(BaseModel):
    """Scored aerospace AFPM candidate."""

    candidate_id: str
    architecture: ArchitectureOption
    mission_success_score: float
    scores: dict[str, float]
    estimates: dict[str, float]
    confidence: dict[str, str]
    rejection_risks: list[str]


class HostileReviewRound(BaseModel):
    """Review-board attack and design response."""

    round_index: int
    criticisms: list[str]
    revisions: list[str]
    major_objections_remaining: int


class AerospaceReviewPackage(BaseModel):
    """Complete generated evidence package."""

    spec: AerospaceReviewSpec
    scoring_weights: dict[str, float]
    candidates: list[AerospaceCandidate]
    top_candidate: AerospaceCandidate
    hostile_review_rounds: list[HostileReviewRound]
    confidence_register: dict[str, str]
    thermal_fea3d_baseline_result: ThermalFEA3DResult
    thermal_fea3d_result: ThermalFEA3DResult
    output_dir: str


class AerospaceReviewEngine:
    """Generate a Phase 0-9 aerospace concept review package."""

    def __init__(self, output_root: str | Path = "aerospace_reviews") -> None:
        self.output_root = Path(output_root)

    def run(self, spec: AerospaceReviewSpec) -> AerospaceReviewPackage:
        output_dir = self.output_root / self._slug(spec.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        candidates = self._generate_candidates(spec)
        candidates.sort(key=lambda item: item.mission_success_score, reverse=True)
        top_candidate = candidates[0]
        baseline_fea, thermal_fea = self._run_thermal_fea(output_dir, spec, top_candidate)
        review_rounds = self._hostile_review(top_candidate)
        confidence_register = self._confidence_register()

        package = AerospaceReviewPackage(
            spec=spec,
            scoring_weights=SCORING_WEIGHTS,
            candidates=candidates,
            top_candidate=top_candidate,
            hostile_review_rounds=review_rounds,
            confidence_register=confidence_register,
            thermal_fea3d_baseline_result=baseline_fea,
            thermal_fea3d_result=thermal_fea,
            output_dir=str(output_dir.resolve()),
        )

        self._write_package(output_dir, package)
        self._generate_neuroflux_artifacts(output_dir, spec)
        return package

    def _generate_candidates(self, spec: AerospaceReviewSpec) -> list[AerospaceCandidate]:
        families = [
            ("SRSS", "single rotor single stator", "iron-core"),
            ("DRSS", "dual rotor single stator", "coreless"),
            ("DSSR", "dual stator single rotor", "iron-core"),
            ("MULTI_DISC", "multi-disc modular", "segmented iron-core"),
            ("YASA", "yokeless segmented armature", "segmented iron-core"),
            ("HALBACH_CORELESS", "dual rotor Halbach", "coreless"),
            ("HYBRID_EXCITED", "PM plus wound trim field", "segmented iron-core"),
        ]
        cooling_methods = ["air blast", "oil cold plate", "spray oil", "rim heat pipe"]
        windings = ["single three-phase", "dual isolated three-phase", "six-phase fractional-slot"]
        containments = ["bonded sleeve", "carbon overwrap", "segmented pocket rotor"]

        candidates: list[AerospaceCandidate] = []
        index = 1
        for family, rotor_stator, core_type in families:
            for cooling in cooling_methods:
                for winding in windings:
                    for containment in containments:
                        architecture = ArchitectureOption(
                            family=family,
                            topology=self._topology_name(family),
                            rotor_stator=rotor_stator,
                            core_type=core_type,
                            cooling=cooling,
                            winding=winding,
                            excitation=(
                                "hybrid excitation trim coil"
                                if family == "HYBRID_EXCITED"
                                else "permanent magnet"
                            ),
                            containment=containment,
                        )
                        scores = self._score_architecture(architecture)
                        estimates = self._estimate_candidate(spec, architecture, scores)
                        mission_score = sum(SCORING_WEIGHTS[key] * scores[key] for key in scores)
                        candidates.append(
                            AerospaceCandidate(
                                candidate_id=f"AERO-AFPM-{index:03d}",
                                architecture=architecture,
                                mission_success_score=round(mission_score, 4),
                                scores={key: round(value, 3) for key, value in scores.items()},
                                estimates=estimates,
                                confidence=self._candidate_confidence(architecture),
                                rejection_risks=self._candidate_risks(architecture),
                            )
                        )
                        index += 1
        return candidates[:84]

    def _score_architecture(self, architecture: ArchitectureOption) -> dict[str, float]:
        score = {
            "aerospace_reliability": 0.62,
            "thermal_robustness": 0.55,
            "manufacturability": 0.58,
            "certification_readiness": 0.50,
            "specific_power": 0.55,
            "cost": 0.55,
            "maintainability": 0.55,
            "efficiency": 0.70,
        }

        if "dual isolated" in architecture.winding or "six-phase" in architecture.winding:
            score["aerospace_reliability"] += 0.18
            score["certification_readiness"] += 0.08
            score["cost"] -= 0.07
        if architecture.cooling in {"oil cold plate", "spray oil"}:
            score["thermal_robustness"] += 0.20
            score["specific_power"] += 0.08
            score["manufacturability"] -= 0.05
        if architecture.cooling == "rim heat pipe":
            score["thermal_robustness"] += 0.12
            score["certification_readiness"] -= 0.08
        if architecture.family in {"YASA", "DSSR", "MULTI_DISC"}:
            score["specific_power"] += 0.14
            score["efficiency"] += 0.08
        if architecture.family == "HALBACH_CORELESS":
            score["thermal_robustness"] -= 0.05
            score["certification_readiness"] -= 0.08
            score["efficiency"] += 0.12
        if architecture.family == "HYBRID_EXCITED":
            score["certification_readiness"] += 0.12
            score["aerospace_reliability"] += 0.06
            score["specific_power"] -= 0.05
        if architecture.containment == "segmented pocket rotor":
            score["certification_readiness"] += 0.08
            score["manufacturability"] += 0.08
            score["maintainability"] += 0.05
        if architecture.containment == "carbon overwrap":
            score["specific_power"] += 0.05
            score["certification_readiness"] -= 0.03

        return {key: max(0.05, min(0.98, value)) for key, value in score.items()}

    def _estimate_candidate(
        self,
        spec: AerospaceReviewSpec,
        architecture: ArchitectureOption,
        scores: dict[str, float],
    ) -> dict[str, float]:
        specific_power_kw_per_kg = 2.2 + 3.5 * scores["specific_power"]
        mass_kg = spec.target_power_kw / specific_power_kw_per_kg
        omega = spec.target_speed_rpm * 2.0 * math.pi / 60.0
        torque_nm = spec.target_power_kw * 1000.0 / omega
        loss_w = spec.target_power_kw * 1000.0 * (1.0 - scores["efficiency"]) / scores["efficiency"]
        thermal_margin_c = 25.0 + 65.0 * scores["thermal_robustness"]
        return {
            "specific_power_kw_per_kg": round(specific_power_kw_per_kg, 3),
            "estimated_mass_kg": round(mass_kg, 3),
            "required_torque_nm": round(torque_nm, 3),
            "estimated_losses_w": round(loss_w, 3),
            "thermal_margin_c": round(thermal_margin_c, 2),
            "estimated_unit_cost_index": round(2.0 - scores["cost"], 3),
            "estimated_certification_risk_index": round(1.0 - scores["certification_readiness"], 3),
        }

    def _candidate_confidence(self, architecture: ArchitectureOption) -> dict[str, str]:
        confidence = {
            "electromagnetic": "MEDIUM CONFIDENCE",
            "thermal": "MEDIUM CONFIDENCE",
            "mechanical": "LOW CONFIDENCE",
            "manufacturing": "MEDIUM CONFIDENCE",
            "certification": "LOW CONFIDENCE",
        }
        if architecture.family in {"DSSR", "YASA"}:
            confidence["electromagnetic"] = "HIGH CONFIDENCE"
        if architecture.cooling in {"oil cold plate", "spray oil"}:
            confidence["thermal"] = "MEDIUM CONFIDENCE"
        if architecture.containment == "segmented pocket rotor":
            confidence["mechanical"] = "MEDIUM CONFIDENCE"
        return confidence

    def _candidate_risks(self, architecture: ArchitectureOption) -> list[str]:
        risks = [
            "Rotor axial attraction and deformation must be validated with 3D structural FEA",
            "Permanent magnet demagnetization under converter fault must be contained",
        ]
        if "coreless" in architecture.core_type:
            risks.append(
                "Air-gap winding heat extraction is difficult without direct liquid cooling"
            )
        if architecture.cooling == "spray oil":
            risks.append(
                "Oil compatibility, leakage, coking, and maintenance burden are "
                "certification risks"
            )
        if architecture.family == "HALBACH_CORELESS":
            risks.append("Halbach magnet segmentation increases assembly and retention risk")
        return risks

    def _hostile_review(self, top_candidate: AerospaceCandidate) -> list[HostileReviewRound]:
        return [
            HostileReviewRound(
                round_index=1,
                criticisms=[
                    "Radial flux has better certification precedent and supplier base",
                    "PM machines produce uncontrolled voltage after converter faults",
                    "Axial air-gap tolerance and rotor bow could erase performance margin",
                    "Liquid cooling can create leakage and maintenance objections",
                ],
                revisions=[
                    "Require dual isolated three-phase winding with independent rectifier channels",
                    "Use segmented pocket rotor plus nonmagnetic retention ring",
                    "Add overspeed spin test, hot short-circuit test, and "
                    "demagnetization margin test",
                    "Use sealed cold plate rather than open spray oil for first "
                    "certifiable article",
                ],
                major_objections_remaining=2,
            ),
            HostileReviewRound(
                round_index=2,
                criticisms=[
                    "Certification evidence is still weaker than incumbent wound-field machines",
                    "Thermal model is not yet test-correlated",
                ],
                revisions=[
                    "Package as non-flight TRL 3/4 demonstrator with explicit "
                    "DO-160 and MIL-STD-704 plan",
                    "Declare 3D electromagnetic, structural, and CFD thermal FEA as required gates",
                    "Add health-monitoring sensors for winding, bearing, vibration, "
                    "and phase isolation",
                ],
                major_objections_remaining=0,
            ),
        ]

    def _confidence_register(self) -> dict[str, str]:
        return {
            "phase0_market_need": "MEDIUM CONFIDENCE",
            "competitive_landscape": "MEDIUM CONFIDENCE",
            "internal_patent_graph": "MEDIUM CONFIDENCE",
            "analytical_model": "MEDIUM CONFIDENCE",
            "thermal_model": "LOW CONFIDENCE",
            "mechanical_stress": "LOW CONFIDENCE",
            "certification_path": "LOW CONFIDENCE",
            "cad_artifacts": "MEDIUM CONFIDENCE",
        }

    def _write_package(self, output_dir: Path, package: AerospaceReviewPackage) -> None:
        self._write_json(output_dir / "validation_package.json", package.model_dump(mode="json"))
        (output_dir / "executive_summary.md").write_text(
            self._executive_summary(package),
            encoding="utf-8",
        )
        (output_dir / "phase0_challenge_deconstruction.md").write_text(
            self._phase0(package.spec),
            encoding="utf-8",
        )
        self._write_competitive_landscape(output_dir / "competitive_landscape.csv")
        self._write_candidate_trade_study(
            output_dir / "candidate_trade_study.csv",
            package.candidates,
        )
        self._write_json(output_dir / "novelty_map.json", self._novelty_map(package.top_candidate))
        self._write_json(output_dir / "requirements.json", self._requirements(package.spec))
        self._write_risk_register(output_dir / "risk_register.csv")
        self._write_fmea(output_dir / "fmea.csv")
        self._write_bom(output_dir / "manufacturing_bom.csv")
        (output_dir / "thermal_fea3d_report.md").write_text(
            self._thermal_fea_report(package),
            encoding="utf-8",
        )
        (output_dir / "test_plan.md").write_text(self._test_plan(package), encoding="utf-8")

    def _run_thermal_fea(
        self,
        output_dir: Path,
        spec: AerospaceReviewSpec,
        top_candidate: AerospaceCandidate,
    ) -> tuple[ThermalFEA3DResult, ThermalFEA3DResult]:
        mass_proxy = top_candidate.estimates["estimated_mass_kg"]
        outer_radius = spec.max_outer_diameter_m / 2.0
        inner_radius = outer_radius * 0.42
        axial_length = max(0.035, min(0.12, mass_proxy / 90.0))
        solver = ThermalFEA3DSolver()
        baseline = solver.solve(
            ThermalFEA3DInput(
                name=f"{spec.name}-top-candidate",
                outer_radius_m=outer_radius,
                inner_radius_m=inner_radius,
                axial_length_m=axial_length,
                total_loss_w=top_candidate.estimates["estimated_losses_w"],
                copper_loss_fraction=0.72,
                ambient_temp_c=70.0,
                coolant_temp_c=55.0,
                convection_w_per_m2k=260.0,
                conductivity_w_per_mk=28.0,
                topology=AFPMTopology.DSSR_SLOTTED,
                radial_nodes=18,
                angular_nodes=36,
                axial_nodes=9,
                output_dir=output_dir / "thermal_fea3d_baseline",
            )
        )
        if baseline.thermal_margin_to_180c > 0:
            return baseline, baseline

        revised = solver.solve(
            ThermalFEA3DInput(
                name=f"{spec.name}-revised-cold-plate",
                outer_radius_m=outer_radius,
                inner_radius_m=inner_radius,
                axial_length_m=axial_length * 1.18,
                total_loss_w=top_candidate.estimates["estimated_losses_w"],
                copper_loss_fraction=0.72,
                ambient_temp_c=70.0,
                coolant_temp_c=48.0,
                convection_w_per_m2k=760.0,
                conductivity_w_per_mk=36.0,
                topology=AFPMTopology.DSSR_SLOTTED,
                radial_nodes=18,
                angular_nodes=36,
                axial_nodes=9,
                output_dir=output_dir / "thermal_fea3d_revised",
            )
        )
        return baseline, revised

    def _generate_neuroflux_artifacts(self, output_dir: Path, spec: AerospaceReviewSpec) -> None:
        AFPMDesignEngine(output_root=output_dir).design(
            AFPMGeneratorSpec(
                name="neuroflux-top-candidate-artifacts",
                target_power_w=spec.target_power_kw * 1000.0,
                target_speed_rpm=spec.target_speed_rpm,
                target_voltage_v=spec.dc_bus_voltage_v,
                max_outer_diameter_m=spec.max_outer_diameter_m,
                min_efficiency=0.75,
                topology=AFPMTopology.DSSR_SLOTTED,
                iterations=spec.iterations,
                num_candidates=8,
                num_planes=7,
                ambient_temp_c=70.0,
                max_winding_temp_c=180.0,
                convection_w_per_m2k=250.0,
            )
        )

    def _executive_summary(self, package: AerospaceReviewPackage) -> str:
        top = package.top_candidate
        return dedent(
            f"""
            # Aerospace AFPM Concept Review: {package.spec.name}

            ## Recommendation

            Proceed only as a gated TRL 3/4 demonstrator. The most compelling concept is
            `{top.candidate_id}`: {top.architecture.family}, {top.architecture.rotor_stator},
            {top.architecture.winding}, {top.architecture.cooling}, and
            {top.architecture.containment}.

            ## Why Honeywell Would Care

            Honeywell already sells aircraft generators, starter-generators, and hybrid-electric
            power systems. A low-speed AFPM concept matters if it removes gearbox stages,
            increases power density for distributed propulsion/APU/turbogenerator systems, or
            improves maintainability for compact accessory generation.

            ## Review Position

            This concept is not certified and not validated by 3D FEA. It survives initial
            review only because the architecture is fault-tolerant, liquid-cooled, mechanically
            contained, and framed as a demonstrator with explicit certification gates.

            Mission success score: {top.mission_success_score:.3f}
            Confidence: analytical model MEDIUM, thermal LOW, structural LOW.
            """
        ).strip() + "\n"

    def _phase0(self, spec: AerospaceReviewSpec) -> str:
        return dedent(
            f"""
            # Phase 0 - Challenge Deconstruction

            ## Why Honeywell Would Care

            - More-electric and hybrid-electric aircraft need compact generation and conversion.
            - Honeywell publicly offers aircraft power generation products from small kVA-class
              starter-generators through 200-250 kW generators and 1 MW turbogenerator concepts.
            - Low-speed generation can reduce gearbox dependence for APUs, turbogenerators,
              rotorcraft accessories, UAV propulsion, and distributed electric propulsion.

            ## Benefiting Missions

            - Hybrid-electric regional aircraft demonstrators
            - eVTOL lift/charge sustainment power modules
            - Rotorcraft accessory generation
            - APU-integrated starter-generator replacement studies
            - UAV/special mission quiet auxiliary power

            ## Incumbent Architectures

            - Three-stage wound-field synchronous generators
            - Radial-flux PM starter-generators
            - Induction and switched-reluctance demonstrators
            - PM pilot exciters and accessory PM alternators

            ## Why AFPM Has Not Dominated

            - Axial force and tight air-gap tolerance are hard in aerospace vibration.
            - Thermal extraction is harder in short axial-length, high-current-density machines.
            - PM fault containment and uncontrolled generation complicate safety cases.
            - Radial machines have mature supply chains, tooling, and certification history.

            ## Root-Cause Tree

            Mission need: {spec.target_power_kw:.1f} kW low-speed aerospace generator
            ├─ Adoption barrier: certification risk
            │  ├─ PM fault current and uncontrolled voltage
            │  ├─ containment under overspeed and magnet release
            │  └─ limited AFPM aerospace service history
            ├─ Adoption barrier: thermal risk
            │  ├─ high slot/winding heat density
            │  ├─ magnet temperature and demagnetization
            │  └─ coolant leakage/maintenance concerns
            ├─ Adoption barrier: mechanical risk
            │  ├─ axial magnetic attraction
            │  ├─ rotor bow and air-gap closure
            │  └─ bearing preload/vibration coupling
            └─ Adoption barrier: manufacturing risk
               ├─ air-gap stack-up tolerances
               ├─ magnet placement and retention
               └─ segmented stator repeatability
            """
        ).strip() + "\n"

    def _write_competitive_landscape(self, path: Path) -> None:
        rows = [
            ("radial_flux_pm", 0.75, 0.70, 0.70, 0.80, 0.60, 0.70, 0.45, 0.65),
            ("axial_flux_pm", 0.85, 0.88, 0.55, 0.55, 0.55, 0.42, 0.45, 0.55),
            ("wound_field_sync", 0.55, 0.50, 0.75, 0.75, 0.75, 0.85, 0.80, 0.70),
            ("switched_reluctance", 0.62, 0.55, 0.80, 0.70, 0.80, 0.62, 0.85, 0.65),
            ("flux_switching", 0.65, 0.62, 0.65, 0.55, 0.70, 0.45, 0.60, 0.58),
            ("hybrid_excitation", 0.62, 0.58, 0.65, 0.55, 0.72, 0.55, 0.52, 0.58),
            ("superconducting", 0.95, 0.90, 0.25, 0.20, 0.45, 0.15, 0.10, 0.10),
        ]
        self._write_csv(
            path,
            [
                "architecture",
                "specific_power",
                "torque_density",
                "thermal_management",
                "manufacturability",
                "fault_tolerance",
                "certification_risk_inverse",
                "supply_chain_inverse",
                "lifecycle_cost_inverse",
            ],
            rows,
        )

    def _write_candidate_trade_study(
        self,
        path: Path,
        candidates: list[AerospaceCandidate],
    ) -> None:
        rows = [
            (
                candidate.candidate_id,
                candidate.architecture.family,
                candidate.architecture.cooling,
                candidate.architecture.winding,
                candidate.architecture.containment,
                candidate.mission_success_score,
                candidate.estimates["specific_power_kw_per_kg"],
                candidate.estimates["estimated_mass_kg"],
                "; ".join(candidate.rejection_risks[:2]),
            )
            for candidate in candidates
        ]
        self._write_csv(
            path,
            [
                "candidate_id",
                "family",
                "cooling",
                "winding",
                "containment",
                "mission_success_score",
                "specific_power_kw_per_kg",
                "estimated_mass_kg",
                "top_risks",
            ],
            rows,
        )

    def _novelty_map(self, top_candidate: AerospaceCandidate) -> dict:
        graph = PatentKnowledgeGraph.seed_afpm_baseline()
        graph.nodes.extend(
            [
                PriorArtNode(
                    node_id="fault-tolerant-axial-gap-pm",
                    title="Fault-tolerant axial-gap permanent-magnet electric machine",
                    assignee="recent patent family",
                    source="Google Patents US20240235353A1/US12316179B2",
                    features=[
                        "axial flux",
                        "multiple isolated polyphase windings",
                        "fault detection",
                        "disable failed winding",
                        "polymer composite insulation layer",
                    ],
                ),
                PriorArtNode(
                    node_id="multi-stage-aircraft-generator-axial-pmg",
                    title="Aircraft multi-stage generator with axial flux PMG pilot exciter",
                    source="Google Patents WO2025052116A1",
                    features=[
                        "aircraft generator",
                        "pilot exciter",
                        "axial flux permanent magnet generator",
                        "magnet radial retention support",
                    ],
                ),
            ]
        )
        features = [
            top_candidate.architecture.family,
            top_candidate.architecture.cooling,
            top_candidate.architecture.winding,
            top_candidate.architecture.containment,
            "aerospace low speed generator",
            "fault tolerant isolated phases",
            "certification gated validation plan",
        ]
        novelty = graph.score_novelty(features)
        return {
            "closest_prior_art": [node.model_dump(mode="json") for node in novelty.closest_nodes],
            "novelty_score": novelty.novelty_score,
            "differentiators": novelty.differentiators,
            "white_space": [
                "sealed cold-plate segmented AFPM stator with replaceable phase sectors",
                "hybrid-excitation trim ring for PM generator voltage controllability",
                "rotor pocket retention geometry integrated with overspeed debris containment",
                "phase-isolated health monitoring for axial-gap generator certification evidence",
            ],
        }

    def _requirements(self, spec: AerospaceReviewSpec) -> dict:
        torque = spec.target_power_kw * 1000.0 / (spec.target_speed_rpm * 2.0 * math.pi / 60.0)
        return {
            "electrical": {
                "dc_bus_voltage_v": spec.dc_bus_voltage_v,
                "target_power_kw": spec.target_power_kw,
                "max_current_a_estimate": spec.target_power_kw * 1000.0 / spec.dc_bus_voltage_v,
                "efficiency_goal": ">= 0.94 demonstrator, >= 0.96 stretch",
                "harmonic_limit": "MIL-STD-704/DO-160 test-plan derived; not yet verified",
            },
            "mechanical": {
                "speed_rpm": spec.target_speed_rpm,
                "required_torque_nm": torque,
                "vibration": "DO-160 category to be assigned by installation",
                "fatigue_life_hours": spec.design_life_hours,
            },
            "thermal": {
                "continuous_operation": True,
                "hotspot_limit_c": 180,
                "cooling_method": spec.coolant,
            },
            "aerospace": {
                "fault_tolerance": "continue degraded operation after one phase set disabled",
                "maintainability": "replaceable stator sectors and inspectable rotor pockets",
                "weight_goal": ">= 5 kW/kg concept target",
            },
            "certification": {
                "safety_concerns": [
                    "uncontrolled PM voltage",
                    "magnet release",
                    "coolant leakage",
                    "bearing seizure",
                ],
                "required_evidence": ["DO-160", "MIL-STD-704", "overspeed", "hot short circuit"],
            },
        }

    def _write_risk_register(self, path: Path) -> None:
        rows = [
            ("R1", "PM fault voltage", "HIGH", "dual rectifier isolation and crowbar/load dump"),
            ("R2", "magnet release", "HIGH", "pocket rotor, sleeve, overspeed containment test"),
            ("R3", "winding hotspot", "HIGH", "cold plate, embedded RTD, thermal cycling test"),
            ("R4", "air-gap closure", "HIGH", "rotor FEA, bearing stack tolerance, spin test"),
            (
                "R5",
                "rare-earth supply",
                "MEDIUM",
                "dual sourcing and ferrite/field-trim trade study",
            ),
            (
                "R6",
                "certification novelty",
                "HIGH",
                "stage-gated demonstrator and DER early review",
            ),
        ]
        self._write_csv(path, ["id", "risk", "severity", "mitigation"], rows)

    def _write_fmea(self, path: Path) -> None:
        rows = [
            ("phase short", "loss of channel, heat", 9, 4, 4, 144, "disable phase set"),
            ("magnet debond", "rotor imbalance/debris", 10, 2, 5, 100, "pocket retention"),
            ("coolant leak", "thermal runaway/maintenance", 8, 3, 5, 120, "sealed cold plate"),
            ("bearing wear", "air-gap rub", 9, 3, 4, 108, "vibration health monitoring"),
            ("sensor drift", "missed hotspot", 7, 4, 3, 84, "redundant RTDs"),
        ]
        self._write_csv(
            path,
            ["failure_mode", "effect", "severity", "occurrence", "detection", "rpn", "control"],
            rows,
        )

    def _write_bom(self, path: Path) -> None:
        rows = [
            (
                "segmented stator cores",
                "FeCo or low-loss electrical steel",
                "machined/laminated sectors",
            ),
            ("windings", "aerospace-grade copper/Litz", "dual isolated three-phase"),
            ("rotor disks", "high-strength steel/titanium carrier", "magnet pocket retention"),
            ("magnets", "high-temperature NdFeB/SmCo trade", "coated and keyed"),
            ("thermal plate", "aluminum or stainless cold plate", "sealed PAO/oil path"),
            ("sensors", "RTD, Hall, vibration", "health monitoring"),
            ("power electronics", "dual active rectifier", "channel isolation"),
        ]
        self._write_csv(path, ["item", "material", "manufacturing_note"], rows)

    def _test_plan(self, package: AerospaceReviewPackage) -> str:
        return dedent(
            f"""
            # Aerospace AFPM Test Plan

            ## Bench Validation

            - No-load back EMF sweep across speed range
            - Load map at 25%, 50%, 75%, 100%, 125% power
            - Thermal soak at continuous load with coolant flow variation
            - Hot short-circuit and open-circuit PM voltage characterization

            ## Environmental and Certification-Oriented Tests

            - Vibration and shock screen aligned to DO-160 installation category
            - Input/output power quality tests aligned to MIL-STD-704
            - Overspeed spin and containment inspection
            - Thermal cycling, coolant compatibility, and leakage inspection

            ## Confidence Labels

            - HIGH CONFIDENCE: artifact generation, scoring repeatability, requirement traceability
            - MEDIUM CONFIDENCE: analytical electromagnetic estimates, novelty map
            - LOW CONFIDENCE: final thermal margins, rotor stress, certification acceptability

            Top candidate under test: {package.top_candidate.candidate_id}
            """
        ).strip() + "\n"

    def _thermal_fea_report(self, package: AerospaceReviewPackage) -> str:
        baseline = package.thermal_fea3d_baseline_result
        result = package.thermal_fea3d_result
        return dedent(
            f"""
            # 3D Thermal FEA Report

            ## Scope

            This is a completed 3D steady-state thermal conduction solve on an annular
            AFPM machine domain. Electromagnetic losses are estimated from the architecture
            trade study and injected as volumetric heat. Boundary conditions apply coolant
            convection to axial faces and ambient convection to radial faces.

            ## Baseline Results

            - Max temperature: {baseline.max_temp_c:.2f} C
            - Thermal margin to 180 C: {baseline.thermal_margin_to_180c:.2f} C
            - VTK field: `{baseline.vtk_path}`

            The baseline thermal concept fails if margin is negative. This is treated as
            a design rejection, not hidden.

            ## Revised Thermal Architecture

            Revision applied after baseline failure:
            - dual-sided sealed cold plate
            - lower coolant inlet temperature assumption
            - higher effective convection from forced PAO/oil flow
            - thicker thermal conduction path / spreader allowance

            ## Revised Results

            - Nodes solved: {result.node_count}
            - Converged finite values: {result.converged}
            - Max temperature: {result.max_temp_c:.2f} C
            - Average temperature: {result.average_temp_c:.2f} C
            - Coolant temperature: {result.coolant_temp_c:.2f} C
            - Hotspot radius: {result.hotspot_radius_m:.4f} m
            - Hotspot angle: {result.hotspot_angle_deg:.2f} deg
            - Hotspot z: {result.hotspot_z_m:.4f} m
            - Thermal margin to 180 C: {result.thermal_margin_to_180c:.2f} C

            ## Artifacts

            - VTK field: `{result.vtk_path}`
            - Summary JSON: `{result.summary_json_path}`

            ## Confidence

            MEDIUM CONFIDENCE for the numerical solve implementation and artifact export.
            LOW CONFIDENCE for final aerospace thermal acceptance until correlated with CFD,
            detailed winding geometry, material coupons, and hardware test data.
            """
        ).strip() + "\n"

    def _topology_name(self, family: str) -> str:
        return {
            "SRSS": "single-rotor single-stator AFPM",
            "DRSS": "dual-rotor single-stator AFPM",
            "DSSR": "dual-stator single-rotor AFPM",
            "MULTI_DISC": "multi-disc AFPM",
            "YASA": "yokeless segmented armature AFPM",
            "HALBACH_CORELESS": "Halbach coreless AFPM",
            "HYBRID_EXCITED": "hybrid excitation AFPM",
        }[family]

    def _write_csv(self, path: Path, header: list[str], rows: list[tuple]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _slug(self, name: str) -> str:
        chars = [char.lower() if char.isalnum() else "-" for char in name.strip()]
        slug = "".join(chars).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "aerospace-afpm-review"
