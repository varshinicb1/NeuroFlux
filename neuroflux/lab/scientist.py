"""Deterministic digital scientist for AFPM lab iteration."""

from __future__ import annotations

from pydantic import BaseModel, Field

from neuroflux.discovery import DesignCandidate, DesignRequirements


class DesignCritique(BaseModel):
    """Scientific critique of a candidate and next experiment proposal."""

    verdict: str
    failure_modes: list[str] = Field(default_factory=list)
    validation_actions: list[str] = Field(default_factory=list)
    next_requirements: DesignRequirements


class DigitalScientist:
    """Critique designs and propose the next bounded experiment."""

    def critique(
        self,
        requirements: DesignRequirements,
        candidate: DesignCandidate,
        novelty_score: float,
    ) -> DesignCritique:
        result = candidate.analytical_result
        failure_modes: list[str] = []
        validation_actions = [
            "Correlate Layer 1 torque and flux against FEMM at mean radius.",
            "Run 3D Elmer validation before hardware release.",
            "Check magnet retention, rotor deflection, winding temperature, and "
            "assembly clearance.",
        ]

        if result.power_w < requirements.target_power_w:
            failure_modes.append("power_shortfall")
        if result.efficiency < requirements.min_efficiency:
            failure_modes.append("efficiency_shortfall")
        if novelty_score < 0.45:
            failure_modes.append("low_novelty_distance")
        if result.total_losses_w > result.power_w * 0.35:
            failure_modes.append("losses_too_high")
        if not candidate.meets_requirements:
            failure_modes.extend(candidate.reasons)

        verdict = "promote_to_validation" if not failure_modes else "iterate"
        next_requirements = self.propose_next_requirements(requirements, failure_modes)

        return DesignCritique(
            verdict=verdict,
            failure_modes=failure_modes,
            validation_actions=validation_actions,
            next_requirements=next_requirements,
        )

    def propose_next_requirements(
        self,
        requirements: DesignRequirements,
        failure_modes: list[str],
    ) -> DesignRequirements:
        data = requirements.model_dump()

        if "power_shortfall" in failure_modes:
            data["max_outer_diameter_m"] = min(
                requirements.max_outer_diameter_m * 1.05,
                requirements.max_outer_diameter_m + 0.05,
            )
            data["num_candidates"] = min(requirements.num_candidates + 2, 20)
        if "efficiency_shortfall" in failure_modes or "losses_too_high" in failure_modes:
            data["min_efficiency"] = max(0.35, requirements.min_efficiency - 0.03)
            data["num_planes"] = min(requirements.num_planes + 2, 21)
        if "low_novelty_distance" in failure_modes:
            data["prefer_halbach"] = (
                requirements.topology.value == "SSDR_coreless"
                or requirements.topology.value == "SSDR_coreless_halbach"
            )

        return DesignRequirements(**data)
