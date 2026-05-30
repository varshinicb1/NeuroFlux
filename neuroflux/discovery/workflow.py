"""End-to-end AFPM design discovery workflow.

This module provides the first production-oriented vertical slice of the
NeuroFlux vision: requirements -> candidate generation -> analytical physics
evaluation -> manufacturing/PCB estimates -> ranked design output.
"""

from __future__ import annotations

import math
import time

from pydantic import BaseModel, Field, model_validator

from neuroflux.core.materials import MaterialDatabase
from neuroflux.core.models import (
    AFPMTopology,
    AnalyticalEngineInput,
    EngineResult,
    MachineGeometry,
    MagnetConfiguration,
    MagnetType,
    OperatingPoint,
    WindingParameters,
)
from neuroflux.engines.analytical_engine import AnalyticalEngine
from neuroflux.engines.autocoil_engine import AutocoilEngine, AutocoilInput, AutocoilOutput
from neuroflux.engines.maggen_engine import MagGenEngine, MagGenInput, MagGenOutput
from neuroflux.engines.openafpm_engine import OpenAFPMEngine, OpenAFPMInput, OpenAFPMOutput


class DesignRequirements(BaseModel):
    """High-level AFPM generator requirements."""

    target_power_w: float = Field(..., gt=0)
    target_speed_rpm: float = Field(..., gt=0)
    target_voltage_v: float = Field(default=48.0, gt=0)
    max_outer_diameter_m: float = Field(..., gt=0)
    min_efficiency: float = Field(default=0.70, gt=0, lt=1)
    topology: AFPMTopology = Field(default=AFPMTopology.DSSR_SLOTTED)
    prefer_halbach: bool = Field(default=False)
    pm_grade: str = Field(default="N42")
    steel_grade: str = Field(default="M600-50A")
    num_candidates: int = Field(default=5, ge=1, le=20)
    num_planes: int = Field(default=7, ge=3, le=21)

    @model_validator(mode="after")
    def validate_topology_options(self) -> DesignRequirements:
        if self.prefer_halbach and self.topology != AFPMTopology.SSDR_CORELESS:
            raise ValueError("prefer_halbach is only supported for SSDR coreless designs")
        return self

    @property
    def required_torque_nm(self) -> float:
        omega = self.target_speed_rpm * 2.0 * math.pi / 60.0
        return self.target_power_w / omega


class DesignCandidate(BaseModel):
    """A generated and evaluated design candidate."""

    candidate_id: str
    analytical_input: AnalyticalEngineInput
    analytical_result: EngineResult
    openafpm_result: OpenAFPMOutput | None = None
    maggen_result: MagGenOutput | None = None
    autocoil_result: AutocoilOutput | None = None
    score: float
    meets_requirements: bool
    reasons: list[str] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    """Ranked output from a design discovery run."""

    requirements: DesignRequirements
    candidates: list[DesignCandidate]
    best_candidate: DesignCandidate | None
    computation_time_ms: float
    warnings: list[str] = Field(default_factory=list)


class DiscoveryWorkflow:
    """Coordinate candidate generation and multi-engine evaluation."""

    def __init__(
        self,
        material_db: MaterialDatabase | None = None,
        analytical_engine: AnalyticalEngine | None = None,
        openafpm_engine: OpenAFPMEngine | None = None,
        maggen_engine: MagGenEngine | None = None,
        autocoil_engine: AutocoilEngine | None = None,
    ) -> None:
        self.material_db = material_db or MaterialDatabase()
        self.analytical_engine = analytical_engine or AnalyticalEngine()
        self.openafpm_engine = openafpm_engine or OpenAFPMEngine()
        self.maggen_engine = maggen_engine or MagGenEngine()
        self.autocoil_engine = autocoil_engine or AutocoilEngine()

    def run(self, requirements: DesignRequirements) -> DiscoveryResult:
        """Generate, evaluate, and rank AFPM candidates."""
        start = time.perf_counter()
        warnings: list[str] = []
        evaluated: list[DesignCandidate] = []

        for index, engine_input in enumerate(self._generate_inputs(requirements), start=1):
            if len(evaluated) >= requirements.num_candidates:
                break
            candidate_id = f"NF-{requirements.topology.value}-{index:02d}"
            try:
                analytical_result = self.analytical_engine.run(engine_input)
            except Exception as exc:
                warnings.append(f"{candidate_id}: analytical evaluation failed: {exc}")
                continue

            openafpm_result = None
            maggen_result = None
            autocoil_result = None

            if engine_input.geometry.topology in (
                AFPMTopology.SSDR_CORELESS,
                AFPMTopology.SSDR_CORELESS_HALBACH,
            ):
                openafpm_result = self._run_openafpm(engine_input, requirements)
                maggen_result = self._run_maggen(engine_input)
                autocoil_result = self._run_autocoil(engine_input)

            score, meets_requirements, reasons = self._score_candidate(
                requirements,
                analytical_result,
                maggen_result,
                autocoil_result,
            )

            evaluated.append(
                DesignCandidate(
                    candidate_id=candidate_id,
                    analytical_input=engine_input,
                    analytical_result=analytical_result,
                    openafpm_result=openafpm_result,
                    maggen_result=maggen_result,
                    autocoil_result=autocoil_result,
                    score=score,
                    meets_requirements=meets_requirements,
                    reasons=reasons,
                )
            )

        evaluated.sort(key=lambda candidate: candidate.score, reverse=True)
        return DiscoveryResult(
            requirements=requirements,
            candidates=evaluated,
            best_candidate=evaluated[0] if evaluated else None,
            computation_time_ms=(time.perf_counter() - start) * 1000.0,
            warnings=warnings,
        )

    def _generate_inputs(self, requirements: DesignRequirements) -> list[AnalyticalEngineInput]:
        materials = self.material_db.build_material_properties(
            requirements.pm_grade,
            requirements.steel_grade,
        )

        topology = (
            AFPMTopology.SSDR_CORELESS_HALBACH
            if requirements.prefer_halbach
            else requirements.topology
        )
        magnet_config = MagnetConfiguration(
            mag_type=(
                MagnetType.HALBACH_DISCRETE
                if requirements.prefer_halbach
                else MagnetType.CONVENTIONAL
            ),
            segments_per_pole=4 if requirements.prefer_halbach else 1,
            halbach_ratio=1.25 if requirements.prefer_halbach else 1.0,
        )

        inputs: list[AnalyticalEngineInput] = []
        max_diameter = requirements.max_outer_diameter_m
        diameter_factors = [1.0, 0.92, 0.84, 0.76, 0.68, 0.60]
        kd_values = [0.58, 0.62, 0.66, 0.70]
        pole_pairs_values = [4, 6, 8, 10, 12]

        for d_factor in diameter_factors:
            for k_d in kd_values:
                for pole_pairs in pole_pairs_values:
                    d_out = max_diameter * d_factor
                    r_out = d_out / 2.0
                    r_in = r_out * k_d
                    mean_radius = (r_out + r_in) / 2.0
                    pole_pitch_mean = math.pi * mean_radius / pole_pairs
                    q_slots = 0 if topology in (
                        AFPMTopology.SSDR_CORELESS,
                        AFPMTopology.SSDR_CORELESS_HALBACH,
                    ) else 3 * 2 * pole_pairs

                    current = self._estimate_current(requirements)
                    turns = self._estimate_turns(requirements, pole_pairs)

                    inputs.append(
                        AnalyticalEngineInput(
                            geometry=MachineGeometry(
                                D_out=d_out,
                                k_D=k_d,
                                l_s=max(0.012, min(0.08, d_out * 0.12)),
                                g=0.0025 if q_slots else 0.0035,
                                l_PM=max(0.004, min(0.012, d_out * 0.018)),
                                w_PM=0.72 * pole_pitch_mean,
                                p=pole_pairs,
                                Q=q_slots,
                                topology=topology,
                                slot_depth=0.025 if q_slots else None,
                                slot_opening=0.25 * pole_pitch_mean if q_slots else None,
                                tooth_width=0.42 * pole_pitch_mean if q_slots else None,
                                yoke_thickness=max(0.008, d_out * 0.035) if q_slots else None,
                                rotor_yoke_thickness=max(0.008, d_out * 0.035),
                                winding_thickness=0.010 if not q_slots else None,
                            ),
                            materials=materials,
                            winding=WindingParameters(
                                turns_per_phase=turns,
                                phases=3,
                                fill_factor=0.58 if q_slots else 0.46,
                                current_density=5e6,
                                parallel_paths=1,
                            ),
                            operating_point=OperatingPoint(
                                speed_rpm=requirements.target_speed_rpm,
                                I_rms=current,
                            ),
                            magnet_config=magnet_config,
                            num_planes=requirements.num_planes,
                        )
                    )

        return inputs

    def _estimate_current(self, requirements: DesignRequirements) -> float:
        apparent_power = requirements.target_power_w / max(requirements.min_efficiency, 0.1)
        return max(1.0, apparent_power / (math.sqrt(3.0) * requirements.target_voltage_v))

    def _estimate_turns(self, requirements: DesignRequirements, pole_pairs: int) -> int:
        electrical_frequency = pole_pairs * requirements.target_speed_rpm / 60.0
        volts_per_phase = requirements.target_voltage_v / math.sqrt(3.0)
        nominal_flux_wb = 0.0012
        turns = volts_per_phase / max(1e-6, 4.44 * electrical_frequency * nominal_flux_wb)
        return max(12, min(240, int(round(turns))))

    def _run_openafpm(
        self,
        engine_input: AnalyticalEngineInput,
        requirements: DesignRequirements,
    ) -> OpenAFPMOutput:
        geometry = engine_input.geometry
        return self.openafpm_engine.run(
            OpenAFPMInput(
                rotor_disk_radius=geometry.r_out,
                magnet_length=max(geometry.l_PM * 4.0, geometry.active_length * 0.35),
                magnet_width=geometry.w_PM,
                magnet_thickness=geometry.l_PM,
                number_of_magnets=geometry.p * 2,
                coil_inner_width=max(0.01, geometry.active_length * 0.25),
                coil_type="rectangular",
                wire_gauge=0.0012,
                number_of_turns=max(1, engine_input.winding.turns_per_phase // max(1, geometry.p)),
                target_rpm=requirements.target_speed_rpm,
            )
        )

    def _run_maggen(self, engine_input: AnalyticalEngineInput) -> MagGenOutput:
        geometry = engine_input.geometry
        return self.maggen_engine.run(
            MagGenInput(
                rotor_diameter=geometry.D_out,
                num_poles=geometry.p * 2,
                num_coils=max(3, int(geometry.p * 1.5)),
                magnet_shape="rectangular",
                manufacturing_process="3d_print",
                output_format="stl",
            )
        )

    def _run_autocoil(self, engine_input: AnalyticalEngineInput) -> AutocoilOutput:
        geometry = engine_input.geometry
        return self.autocoil_engine.run(
            AutocoilInput(
                num_poles=geometry.p * 2,
                num_phases=engine_input.winding.phases,
                num_layers=4,
                inner_radius=geometry.r_in,
                outer_radius=geometry.r_out,
            )
        )

    def _score_candidate(
        self,
        requirements: DesignRequirements,
        analytical_result: EngineResult,
        maggen_result: MagGenOutput | None,
        autocoil_result: AutocoilOutput | None,
    ) -> tuple[float, bool, list[str]]:
        torque_ratio = analytical_result.torque_nm / requirements.required_torque_nm
        power_ratio = analytical_result.power_w / requirements.target_power_w
        efficiency_ratio = analytical_result.efficiency / requirements.min_efficiency

        score = (
            0.40 * min(power_ratio, 1.5)
            + 0.35 * min(torque_ratio, 1.5)
            + 0.20 * min(efficiency_ratio, 1.3)
        )

        reasons: list[str] = []
        if analytical_result.power_w < requirements.target_power_w:
            reasons.append(
                "Power below target: "
                f"{analytical_result.power_w:.1f} W < {requirements.target_power_w:.1f} W"
            )
        if analytical_result.torque_nm < requirements.required_torque_nm:
            reasons.append(
                "Torque below target: "
                f"{analytical_result.torque_nm:.2f} N m < "
                f"{requirements.required_torque_nm:.2f} N m"
            )
        if analytical_result.efficiency < requirements.min_efficiency:
            reasons.append(
                "Efficiency below target: "
                f"{analytical_result.efficiency:.3f} < {requirements.min_efficiency:.3f}"
            )

        if maggen_result is not None:
            severe_dfm = [
                warning for warning in maggen_result.dfm_warnings
                if "Critical" in warning or "Violation" in warning
            ]
            if severe_dfm:
                score -= 0.20
                reasons.extend(severe_dfm)

        if autocoil_result is not None and autocoil_result.warnings:
            score -= 0.03

        meets_requirements = len(reasons) == 0
        return max(0.0, score), meets_requirements, reasons
