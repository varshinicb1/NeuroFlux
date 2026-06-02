"""Unified 3D validation pipeline for AFPM designs.

Phase 2 Implementation:
- Integrates Gmsh meshing
- Elmer FEM 3D multi-physics
- Palace electromagnetics
- Native Thermal FEA3D
- Analytical fallback chain

All existing solver modules are orchestrated here for a seamless
validation workflow from design → mesh → solve → report.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field

from neuroflux.core.models import (
    AFPMTopology,
    AnalyticalEngineInput,
    EngineResult,
    MachineGeometry,
    MaterialProperties,
    OperatingPoint,
    WindingParameters,
)
from neuroflux.engines.analytical_engine import AnalyticalEngine
from neuroflux.engines.elmer_engine import ElmerEngine, ElmerInput, ElmerOutput
from neuroflux.fea.thermal3d import ThermalFEA3DInput, ThermalFEA3DResult, ThermalFEA3DSolver
from neuroflux.solvers.handoffs import ElmerHandoffBuilder, ExternalSolverHandoff, PalaceHandoffBuilder


class ValidationSpec(BaseModel):
    """Specification for running 3D validation on a design candidate."""

    name: str = Field(default="validation_run", min_length=1)
    geometry: MachineGeometry
    materials: MaterialProperties
    winding: WindingParameters
    operating_point: OperatingPoint

    # Validation options
    run_analytical: bool = Field(default=True, description="Run Layer 1 analytical validation")
    run_thermal_fea3d: bool = Field(default=True, description="Run native 3D thermal FEA")
    run_elmer_fea: bool = Field(default=False, description="Run Elmer 3D FEM (if available)")
    run_palace: bool = Field(default=False, description="Run Palace EM solver (if available)")
    generate_handoffs: bool = Field(default=True, description="Generate solver handoff files")

    # Mesh settings
    mesh_refinement: str = Field(default="medium", pattern=r"^(coarse|medium|fine|very_fine)$")


class ThermalValidationResult(BaseModel):
    """Results from thermal validation stack."""

    native_fea3d: ThermalFEA3DResult | None = None
    elmer_thermal_max_c: float | None = None
    analytical_estimate_c: float | None = None
    confidence: str = "MEDIUM CONFIDENCE"


class EMValidationResult(BaseModel):
    """Results from electromagnetic validation stack."""

    analytical: EngineResult | None = None
    elmer: ElmerOutput | None = None
    palace_handoff: ExternalSolverHandoff | None = None


class ValidationResult(BaseModel):
    """Complete validation result from all solvers."""

    spec: ValidationSpec
    thermal: ThermalValidationResult
    electromagnetic: EMValidationResult
    solver_handoffs: list[ExternalSolverHandoff] = Field(default_factory=list)
    validation_time_ms: float
    output_dir: str
    passed: bool = True
    warnings: list[str] = Field(default_factory=list)


class ValidationPipeline:
    """Phase 2: Orchestrate 3D multi-physics validation for AFPM designs.

    This pipeline integrates all existing NeuroFlux solver modules:
    - AnalyticalEngine (Layer 1): Fast screening
    - ThermalFEA3DSolver (Native): 3D thermal analysis
    - ElmerEngine (Layer 3): Full 3D multi-physics (when available)
    - ElmerHandoffBuilder: Creates Elmer solver decks
    - PalaceHandoffBuilder: Creates Palace solver decks

    Usage:
        >>> pipeline = ValidationPipeline(output_root="validation_runs")
        >>> result = pipeline.run(ValidationSpec(
        ...     name="my_design",
        ...     geometry=machine_geometry,
        ...     materials=material_props,
        ...     winding=winding_params,
        ...     operating_point=op_point,
        ...     run_thermal_fea3d=True,
        ...     run_elmer_fea=False,  # Set True if Elmer installed
        ... ))
        >>> print(f"Max temp: {result.thermal.native_fea3d.max_temp_c:.1f} C")
    """

    def __init__(self, output_root: str | Path = "validation_runs") -> None:
        self.output_root = Path(output_root)
        self._analytical_engine = AnalyticalEngine()
        self._thermal_solver = ThermalFEA3DSolver()
        self._elmer_engine = ElmerEngine()

    def run(self, spec: ValidationSpec) -> ValidationResult:
        """Execute the full validation pipeline."""
        start_time = time.perf_counter()
        output_dir = self.output_root / self._slug(spec.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        warnings: list[str] = []
        solver_handoffs: list[ExternalSolverHandoff] = []

        # ─────────────────────────────────────────────────────────────────
        # Layer 1: Analytical Validation (Always runs)
        # ─────────────────────────────────────────────────────────────────
        em_result = EMValidationResult()
        if spec.run_analytical:
            analytical_input = AnalyticalEngineInput(
                geometry=spec.geometry,
                materials=spec.materials,
                winding=spec.winding,
                operating_point=spec.operating_point,
                num_planes=7 if spec.mesh_refinement == "medium" else 11,
            )
            em_result.analytical = self._analytical_engine.run(analytical_input)

        # ─────────────────────────────────────────────────────────────────
        # Native 3D Thermal FEA (SciPy-based)
        # ─────────────────────────────────────────────────────────────────
        thermal_result = ThermalValidationResult()
        if spec.run_thermal_fea3d and em_result.analytical:
            # Estimate losses from analytical result
            total_loss = em_result.analytical.total_losses_w
            thermal_input = ThermalFEA3DInput(
                name=spec.name,
                outer_radius_m=spec.geometry.r_out,
                inner_radius_m=spec.geometry.r_in,
                axial_length_m=spec.geometry.l_s,
                total_loss_w=total_loss,
                copper_loss_fraction=0.65,
                ambient_temp_c=spec.operating_point.ambient_temp,
                coolant_temp_c=spec.operating_point.ambient_temp + 15.0,
                convection_w_per_m2k=220.0,
                conductivity_w_per_mk=28.0,
                topology=spec.geometry.topology,
                radial_nodes=24 if spec.mesh_refinement == "fine" else 16,
                angular_nodes=48 if spec.mesh_refinement == "fine" else 32,
                axial_nodes=12 if spec.mesh_refinement == "fine" else 9,
                output_dir=output_dir / "thermal_fea3d",
            )
            thermal_result.native_fea3d = self._thermal_solver.solve(thermal_input)
            thermal_result.analytical_estimate_c = (
                spec.operating_point.ambient_temp + total_loss * 0.15
            )

        # ─────────────────────────────────────────────────────────────────
        # Layer 3: Elmer FEM (When available)
        # ─────────────────────────────────────────────────────────────────
        from neuroflux.core.config import ExternalToolConfig
        tool_config = ExternalToolConfig.auto_detect()
        elmer_available = tool_config.elmer_available()
        if spec.run_elmer_fea and elmer_available:
            elmer_input = ElmerInput(
                geometry=spec.geometry,
                materials=spec.materials,
                winding=spec.winding,
                operating_point=spec.operating_point,
                solver_type="magnetostatic",
                enable_thermal=True,
                mesh_order=2,
            )
            em_result.elmer = self._elmer_engine.run(elmer_input)
            if em_result.elmer:
                thermal_result.elmer_thermal_max_c = em_result.elmer.max_winding_temp
        elif spec.run_elmer_fea and not elmer_available:
            warnings.append(
                "ElmerSolver or Gmsh not found. Set NEUROFLUX_ELMER_SOLVER and "
                "NEUROFLUX_GMSH environment variables to enable Elmer FEA."
            )

        # ─────────────────────────────────────────────────────────────────
        # Generate Solver Handoffs (For external execution)
        # ─────────────────────────────────────────────────────────────────
        if spec.generate_handoffs:
            handoff_dir = output_dir / "solver_handoffs"
            
            # Create builders with correct output paths
            elmer_builder = ElmerHandoffBuilder(output_root=handoff_dir)
            palace_builder = PalaceHandoffBuilder(output_root=handoff_dir)
            
            # Elmer handoff
            elmer_handoff = elmer_builder.build(
                geometry=spec.geometry,
                materials=spec.materials,
                winding=spec.winding,
                operating_point=spec.operating_point,
            )
            solver_handoffs.append(elmer_handoff)

            # Palace handoff
            palace_handoff = palace_builder.build(
                geometry=spec.geometry,
                materials=spec.materials,
                winding=spec.winding,
                operating_point=spec.operating_point,
            )
            solver_handoffs.append(palace_handoff)
            em_result.palace_handoff = palace_handoff

        # ─────────────────────────────────────────────────────────────────
        # Confidence Assessment
        # ─────────────────────────────────────────────────────────────────
        if thermal_result.native_fea3d:
            max_temp = thermal_result.native_fea3d.max_temp_c
            if max_temp < 120:
                thermal_result.confidence = "HIGH CONFIDENCE"
            elif max_temp < 150:
                thermal_result.confidence = "MEDIUM CONFIDENCE"
            else:
                thermal_result.confidence = "LOW CONFIDENCE - Review cooling"
                warnings.append(f"High thermal stress: {max_temp:.1f} C peak temperature")

        # ─────────────────────────────────────────────────────────────────
        # Validation Pass/Fail
        # ─────────────────────────────────────────────────────────────────
        passed = True
        if thermal_result.native_fea3d and thermal_result.native_fea3d.max_temp_c > 180:
            passed = False
            warnings.append("FAIL: Maximum temperature exceeds 180°C safety limit")

        validation_time = (time.perf_counter() - start_time) * 1000.0

        result = ValidationResult(
            spec=spec,
            thermal=thermal_result,
            electromagnetic=em_result,
            solver_handoffs=solver_handoffs,
            validation_time_ms=validation_time,
            output_dir=str(output_dir.resolve()),
            passed=passed,
            warnings=warnings,
        )

        # Write validation report
        self._write_report(output_dir, result)
        return result

    def _write_report(self, output_dir: Path, result: ValidationResult) -> None:
        """Write validation summary report."""
        report_path = output_dir / "validation_report.json"
        report_path.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _slug(self, name: str) -> str:
        """Convert name to filesystem-safe slug."""
        chars = [char.lower() if char.isalnum() else "-" for char in name.strip()]
        slug = "".join(chars).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "validation"
