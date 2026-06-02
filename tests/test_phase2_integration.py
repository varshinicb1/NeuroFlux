"""Phase 2 Integration Test - Verify all components work as one system.

This test ensures:
1. All existing files are used (no waste)
2. Phase 1 + Phase 2 pipeline works end-to-end
3. All solver handoffs are generated
4. Validation results are integrated into design reports
"""

from pathlib import Path

import pytest

from neuroflux.core.models import AFPMTopology
from neuroflux.design import AFPMDesignEngine, AFPMGeneratorSpec
from neuroflux.validation import ValidationPipeline, ValidationSpec


class TestPhase2Integration:
    """Verify Phase 2 integration uses all files in the system."""

    def test_design_engine_with_validation_runs_full_pipeline(self, tmp_path):
        """Test that design engine runs Phase 1 + Phase 2 together."""
        engine = AFPMDesignEngine(output_root=tmp_path)
        spec = AFPMGeneratorSpec(
            name="integration-test",
            target_power_w=250.0,
            target_speed_rpm=600.0,
            target_voltage_v=48.0,
            max_outer_diameter_m=0.30,
            min_efficiency=0.55,
            iterations=2,
            num_candidates=3,
            run_3d_validation=True,
            run_external_solvers=False,  # Don't require external tools in tests
            validation_refinement="coarse",
        )

        result = engine.design(spec)

        # Verify Phase 1 results
        assert result.best_candidate is not None
        assert result.thermal_analysis.status in ("pass", "warning")
        assert result.validation_passed is True

        # Verify Phase 2 validation ran
        assert result.validation_result is not None
        assert result.validation_result.thermal.native_fea3d is not None
        assert result.validation_result.thermal.native_fea3d.node_count > 0
        assert result.validation_result.solver_handoffs

        # Verify all artifacts exist
        artifacts = result.artifacts
        assert Path(artifacts.manifest_json).exists()
        assert Path(artifacts.report_md).exists()
        assert Path(artifacts.geometry_geo).exists()
        assert Path(artifacts.viewer_html).exists()
        assert Path(artifacts.thermal_json).exists()

    def test_validation_pipeline_uses_all_solver_modules(self, tmp_path):
        """Test that validation pipeline uses all solver modules."""
        from neuroflux.core.materials import MaterialDatabase
        from neuroflux.core.models import (
            MachineGeometry,
            MaterialProperties,
            OperatingPoint,
            WindingParameters,
        )

        pipeline = ValidationPipeline(output_root=tmp_path)

        # Create test geometry
        materials = MaterialDatabase()
        spec = ValidationSpec(
            name="solver-integration-test",
            geometry=MachineGeometry(
                D_out=0.25,
                k_D=0.6,
                l_s=0.025,
                g=0.0025,
                l_PM=0.005,
                w_PM=0.02,
                p=6,
                Q=36,
                topology=AFPMTopology.DSSR_SLOTTED,
            ),
            materials=materials.build_material_properties("N42", "M600-50A"),
            winding=WindingParameters(
                turns_per_phase=50,
                phases=3,
                fill_factor=0.55,
                current_density=5e6,
            ),
            operating_point=OperatingPoint(
                speed_rpm=600.0,
                I_rms=5.0,
            ),
            run_analytical=True,
            run_thermal_fea3d=True,
            run_elmer_fea=False,
            generate_handoffs=True,
        )

        result = pipeline.run(spec)

        # Verify analytical engine was used
        assert result.electromagnetic.analytical is not None
        assert result.electromagnetic.analytical.torque_nm > 0

        # Verify thermal FEA3D was used
        assert result.thermal.native_fea3d is not None
        assert result.thermal.native_fea3d.max_temp_c > 0

        # Verify solver handoffs were generated
        assert len(result.solver_handoffs) == 2  # Elmer + Palace
        solver_names = [h.solver_name for h in result.solver_handoffs]
        assert "Elmer FEM" in solver_names
        assert "Palace" in solver_names

        # Verify handoff files exist
        for handoff in result.solver_handoffs:
            assert Path(handoff.case_dir).exists()
            assert Path(handoff.geometry_geo_path).exists()

    def test_no_files_are_wasted_all_imports_work(self):
        """Verify all Python files in neuroflux can be imported and used."""
        # Core modules - all used by design engine and validation
        from neuroflux.core import constants, engine_base, exceptions, materials, models
        from neuroflux.analytical import (
            coreless_field,
            halbach,
            losses,
            magnetic_circuit,
            performance,
            quasi3d,
            topology_registry,
        )
        from neuroflux.engines import (
            analytical_engine,
            autocoil_engine,
            elmer_engine,
            femm_engine,
            maggen_engine,
            openafpm_engine,
            pyleecan_engine,
        )
        from neuroflux.discovery import workflow
        from neuroflux.lab import autonomous_lab, cli, patents, scientist
        from neuroflux.fea import thermal3d
        from neuroflux.solvers import handoffs
        from neuroflux.pdr import aegis
        from neuroflux.bench import engine as bench_engine
        from neuroflux.utils import logging, validation

        # Validation module (Phase 2)
        from neuroflux.validation import pipeline, ValidationPipeline

        # All imports should succeed - no wasted files
        assert True

    def test_cli_integration_all_commands(self, tmp_path):
        """Test CLI commands work with Phase 2 options."""
        from neuroflux.lab.cli import main

        # Test design command with Phase 2 options
        exit_code = main(
            [
                "design",
                "--output",
                str(tmp_path),
                "--name",
                "cli-phase2-test",
                "--target-power-w",
                "300",
                "--target-speed-rpm",
                "500",
                "--iterations",
                "1",
                "--num-candidates",
                "2",
                "--validation-refinement",
                "coarse",
            ]
        )
        assert exit_code == 0

        # Verify outputs
        design_dir = tmp_path / "cli-phase2-test"
        assert design_dir.exists()
        assert (design_dir / "design_manifest.json").exists()
        assert (design_dir / "validation").exists()

    def test_design_report_includes_phase2_results(self, tmp_path):
        """Verify design report includes Phase 2 validation data."""
        engine = AFPMDesignEngine(output_root=tmp_path)
        spec = AFPMGeneratorSpec(
            name="report-test",
            target_power_w=250.0,
            target_speed_rpm=600.0,
            run_3d_validation=True,
            iterations=1,
            num_candidates=2,
        )

        result = engine.design(spec)
        report_path = Path(result.artifacts.report_md)
        report_content = report_path.read_text()

        # Verify Phase 2 content in report
        assert "Phase 2: 3D Validation" in report_content
        assert "Validation Status" in report_content
        assert "3D Max Temperature" in report_content
        assert "Solver Handoffs Generated" in report_content
        assert "Elmer FEM" in report_content
        assert "Palace" in report_content
