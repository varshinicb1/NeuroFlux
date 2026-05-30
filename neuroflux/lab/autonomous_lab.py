"""Autonomous AFPM design lab with durable experiment artifacts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from neuroflux.discovery import DesignCandidate, DesignRequirements, DiscoveryWorkflow
from neuroflux.lab.patents import NoveltyScore, PatentKnowledgeGraph
from neuroflux.lab.scientist import DesignCritique, DigitalScientist


class LabRunConfig(BaseModel):
    """Configuration for an autonomous lab run."""

    requirements: DesignRequirements
    iterations: int = Field(default=3, ge=1, le=200)
    run_id: str | None = None
    stop_on_valid_candidate: bool = False


class LabIteration(BaseModel):
    """One autonomous lab iteration."""

    index: int
    requirements: DesignRequirements
    best_candidate: DesignCandidate
    novelty: NoveltyScore
    critique: DesignCritique
    artifact_path: str


class LabRunResult(BaseModel):
    """Complete autonomous lab run result."""

    run_id: str
    iterations: list[LabIteration]
    best_candidate: DesignCandidate | None
    manifest_path: str
    summary_path: str
    computation_time_ms: float


class AutonomousLab:
    """Run repeated design-discovery experiments and write lab artifacts."""

    def __init__(
        self,
        output_root: str | Path = "lab_runs",
        discovery_workflow: DiscoveryWorkflow | None = None,
        patent_graph: PatentKnowledgeGraph | None = None,
        scientist: DigitalScientist | None = None,
    ) -> None:
        self.output_root = Path(output_root)
        self.discovery_workflow = discovery_workflow or DiscoveryWorkflow()
        self.patent_graph = patent_graph or PatentKnowledgeGraph.seed_afpm_baseline()
        self.scientist = scientist or DigitalScientist()

    def run(self, config: LabRunConfig) -> LabRunResult:
        start = time.perf_counter()
        run_id = config.run_id or f"nf-lab-{uuid4().hex[:10]}"
        run_dir = self.output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        current_requirements = config.requirements
        iterations: list[LabIteration] = []
        best_candidate: DesignCandidate | None = None

        for index in range(1, config.iterations + 1):
            discovery = self.discovery_workflow.run(current_requirements)
            if discovery.best_candidate is None:
                raise RuntimeError("Discovery workflow produced no candidates")

            candidate = discovery.best_candidate
            novelty = self.patent_graph.score_novelty(self._candidate_features(candidate))
            critique = self.scientist.critique(
                current_requirements,
                candidate,
                novelty.novelty_score,
            )

            artifact_file = run_dir / f"iteration_{index:03d}.json"
            iteration = LabIteration(
                index=index,
                requirements=current_requirements,
                best_candidate=candidate,
                novelty=novelty,
                critique=critique,
                artifact_path=str(artifact_file.resolve()),
            )
            self._write_json(artifact_file, iteration.model_dump(mode="json"))
            iterations.append(iteration)

            if best_candidate is None or candidate.score > best_candidate.score:
                best_candidate = candidate

            current_requirements = critique.next_requirements
            if config.stop_on_valid_candidate and critique.verdict == "promote_to_validation":
                break

        manifest_path = run_dir / "manifest.json"
        summary_path = run_dir / "summary.md"
        result = LabRunResult(
            run_id=run_id,
            iterations=iterations,
            best_candidate=best_candidate,
            manifest_path=str(manifest_path.resolve()),
            summary_path=str(summary_path.resolve()),
            computation_time_ms=(time.perf_counter() - start) * 1000.0,
        )
        self._write_json(manifest_path, result.model_dump(mode="json"))
        summary_path.write_text(self._render_summary(result), encoding="utf-8")
        return result

    def _candidate_features(self, candidate: DesignCandidate) -> list[str]:
        geometry = candidate.analytical_input.geometry
        features = [
            geometry.topology.value,
            f"{geometry.p * 2} pole",
            f"kD {geometry.k_D:.2f}",
            f"outer diameter {geometry.D_out:.3f} m",
            f"airgap {geometry.g:.4f} m",
        ]
        if geometry.Q == 0:
            features.append("coreless stator")
        else:
            features.append(f"{geometry.Q} slot stator")
        if "HALBACH" in geometry.topology.name:
            features.append("halbach permanent magnet array")
        if candidate.maggen_result is not None:
            features.append("manufacturing DFM checked")
        if candidate.autocoil_result is not None:
            features.append("PCB winding estimate")
        return features

    def _render_summary(self, result: LabRunResult) -> str:
        lines = [
            f"# NeuroFlux Autonomous Lab Run {result.run_id}",
            "",
            f"Iterations: {len(result.iterations)}",
            f"Runtime: {result.computation_time_ms:.1f} ms",
            "",
        ]
        if result.best_candidate is not None:
            best = result.best_candidate
            lines.extend(
                [
                    "## Best Candidate",
                    "",
                    f"- ID: {best.candidate_id}",
                    f"- Score: {best.score:.3f}",
                    f"- Torque: {best.analytical_result.torque_nm:.3f} N m",
                    f"- Power: {best.analytical_result.power_w:.3f} W",
                    f"- Efficiency: {best.analytical_result.efficiency:.3f}",
                    "",
                ]
            )
        lines.append("## Iterations")
        lines.append("")
        for iteration in result.iterations:
            candidate = iteration.best_candidate
            lines.extend(
                [
                    f"### Iteration {iteration.index}",
                    "",
                    f"- Candidate: {candidate.candidate_id}",
                    f"- Verdict: {iteration.critique.verdict}",
                    f"- Novelty: {iteration.novelty.novelty_score:.3f}",
                    f"- Artifact: `{iteration.artifact_path}`",
                    "",
                ]
            )
        return "\n".join(lines)

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
