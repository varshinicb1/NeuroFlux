"""Tests for the NeuroFlux Master Automation System."""

import pytest
import tempfile
from pathlib import Path

from neuroflux.automation import (
    MasterOrchestrator,
    AutomationConfig,
    AutomationResult,
    PipelineStage,
    StageStatus,
)
from neuroflux.automation.progress import ProgressTracker, ProgressReport, StageProgress
from neuroflux.automation.reporting import (
    UnifiedReportGenerator,
    DesignPackage,
    load_design_package,
)
from neuroflux.core.config import ExternalToolConfig
from neuroflux.design.engine import AFPMGeneratorSpec


def test_automation_config_defaults():
    """Test AutomationConfig default values."""
    config = AutomationConfig()
    
    assert config.max_workers == 4
    assert config.enable_parallel is True
    assert config.retry_failed is True
    assert config.max_retries == 2
    assert config.run_discovery is True
    assert config.run_thermal_analysis is True
    assert config.run_3d_validation is True
    assert config.run_external_solvers is False
    assert config.validation_refinement == "medium"


def test_automation_config_custom():
    """Test AutomationConfig with custom values."""
    config = AutomationConfig(
        max_workers=8,
        run_external_solvers=True,
        validation_refinement="fine",
    )
    
    assert config.max_workers == 8
    assert config.run_external_solvers is True
    assert config.validation_refinement == "fine"


def test_pipeline_stage_lifecycle():
    """Test PipelineStage state transitions."""
    stage = PipelineStage(name="test_stage")
    
    assert stage.status == StageStatus.PENDING
    assert stage.duration_ms == 0.0
    assert stage.is_success is False
    
    stage.status = StageStatus.RUNNING
    stage.start_time = 0.0
    stage.end_time = 1.0
    
    assert stage.status == StageStatus.RUNNING
    assert stage.duration_ms == 1000.0
    
    stage.status = StageStatus.COMPLETED
    assert stage.is_success is True


def test_orchestrator_initialization():
    """Test MasterOrchestrator initialization."""
    config = AutomationConfig()
    orchestrator = MasterOrchestrator(config)
    
    assert orchestrator.config == config
    assert orchestrator.tool_config is not None


def test_progress_tracker_initialization():
    """Test ProgressTracker initialization."""
    tracker = ProgressTracker()
    
    assert tracker._stages == {}
    assert len(tracker._callbacks) == 0


def test_progress_tracker_stage_lifecycle():
    """Test ProgressTracker stage lifecycle."""
    tracker = ProgressTracker()
    
    # Start stage
    tracker.start_stage("discovery", steps_total=5)
    assert "discovery" in tracker._stages
    assert tracker._stages["discovery"].steps_total == 5
    
    # Update stage
    tracker.update_stage("discovery", step="analyzing", steps_completed=2)
    assert tracker._stages["discovery"].current_step == "analyzing"
    assert tracker._stages["discovery"].steps_completed == 2
    
    # Complete stage
    tracker.complete_stage("discovery", duration_ms=1000.0)
    assert tracker._stages["discovery"].is_complete


def test_progress_report_generation():
    """Test ProgressReport generation."""
    tracker = ProgressTracker()
    tracker.start_stage("discovery", steps_total=5)
    tracker.update_stage("discovery", steps_completed=3)
    
    report = tracker.get_report()
    
    assert isinstance(report, ProgressReport)
    assert report.current_stage == "discovery"
    assert report.overall_percent > 0
    assert "discovery" in report.stages


def test_progress_report_to_dict():
    """Test ProgressReport serialization."""
    report = ProgressReport(
        overall_percent=50.0,
        current_stage="test",
        message="Testing",
    )
    
    d = report.to_dict()
    
    assert d["overall_percent"] == 50.0
    assert d["current_stage"] == "test"
    assert d["message"] == "Testing"
    assert "start_time" in d


def test_unified_report_generator_initialization():
    """Test UnifiedReportGenerator initialization."""
    generator = UnifiedReportGenerator()
    assert generator is not None


def test_step_export_result_dataclass():
    """Test STEPExportResult dataclass in automation context."""
    from neuroflux.cad import STEPExportResult
    
    result = STEPExportResult(
        success=True,
        step_path=Path("test.step"),
        message="Success",
    )
    
    assert result.success is True
    assert result.step_path == Path("test.step")
    assert result.message == "Success"


def test_automation_result_summary():
    """Test AutomationResult get_stage_summary method."""
    result = AutomationResult(success=True)
    
    # Add stages
    result.stages["discovery"] = PipelineStage(
        name="discovery",
        status=StageStatus.COMPLETED,
    )
    result.stages["discovery"].start_time = 0.0
    result.stages["discovery"].end_time = 1.0
    
    summary = result.get_stage_summary()
    
    assert "discovery" in summary
    assert summary["discovery"]["status"] == "COMPLETED"
    assert summary["discovery"]["duration_ms"] == 1000.0


def test_orchestrator_run_without_external_tools(monkeypatch):
    """Test orchestrator runs with mocked external tools."""
    config = AutomationConfig(
        run_external_solvers=False,
        run_visualization=False,
        run_cad_export=False,
        output_root=tempfile.mkdtemp(),
    )
    
    orchestrator = MasterOrchestrator(config)
    
    # Mock external tool validation to always pass
    monkeypatch.setattr(orchestrator, "_validate_external_tools", lambda: None)
    
    spec = AFPMGeneratorSpec(
        name="test_orchestrator",
        target_power_w=100,
        target_speed_rpm=600,
        target_voltage_v=24,
        iterations=1,
        num_candidates=1,
    )
    
    result = orchestrator.run(spec, run_id="test_run")
    
    # Should complete discovery at minimum
    assert result.stages["discovery"].is_success
    assert result.design_result is not None


def test_orchestrator_handles_edge_case_parameters(monkeypatch):
    """Test orchestrator handles edge case parameters gracefully."""
    config = AutomationConfig(
        run_discovery=True,
        output_root=tempfile.mkdtemp(),
    )
    
    orchestrator = MasterOrchestrator(config)
    
    # Mock external tool validation to always pass
    monkeypatch.setattr(orchestrator, "_validate_external_tools", lambda: None)
    
    # Use extreme parameters - engine should handle gracefully
    spec = AFPMGeneratorSpec(
        name="test_edge",
        target_power_w=1000000,  # Very high
        target_speed_rpm=1,
        target_voltage_v=1000000,
        max_outer_diameter_m=0.01,  # Very small
        iterations=1,
        num_candidates=1,
    )
    
    result = orchestrator.run(spec, run_id="test_edge_run")
    
    # Should complete without crashing (success depends on engine robustness)
    assert result is not None
    assert "discovery" in result.stages


def test_progress_tracker_callbacks():
    """Test ProgressTracker callback mechanism."""
    tracker = ProgressTracker()
    
    received_reports = []
    
    def callback(report):
        received_reports.append(report)
    
    tracker.register_callback(callback)
    
    # Trigger update
    tracker.start_stage("test")
    
    assert len(received_reports) > 0


def test_design_package_to_dict():
    """Test DesignPackage serialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg = DesignPackage(
            design_name="test_design",
            output_directory=Path(tmpdir),
            manifest_path=Path(tmpdir) / "manifest.json",
            report_path=Path(tmpdir) / "report.md",
        )
        
        d = pkg.to_dict()
        
        assert d["design_name"] == "test_design"
        assert "output_directory" in d
        assert "manifest" in d
        assert "report" in d


@pytest.mark.parametrize("stage_status", [
    StageStatus.PENDING,
    StageStatus.RUNNING,
    StageStatus.COMPLETED,
    StageStatus.FAILED,
    StageStatus.SKIPPED,
])
def test_stage_status_variations(stage_status):
    """Test all StageStatus enum values."""
    stage = PipelineStage(name="test", status=stage_status)
    assert stage.status == stage_status


def test_automation_config_validation():
    """Test AutomationConfig validation constraints."""
    # Valid values should work
    config = AutomationConfig(max_workers=8, max_retries=3)
    assert config.max_workers == 8
    assert config.max_retries == 3


def test_orchestrator_stage_weights():
    """Test orchestrator has proper stage weights configured."""
    config = AutomationConfig()
    orchestrator = MasterOrchestrator(config)
    
    # Check that stage weights are defined
    assert "discovery" in orchestrator.tracker._stage_weights
    assert orchestrator.tracker._stage_weights["discovery"] > 0


def test_report_generation_with_minimal_result():
    """Test report generation with minimal AutomationResult."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = AutomationResult(
            success=True,
            output_directory=Path(tmpdir),
        )
        
        generator = UnifiedReportGenerator()
        report_path = generator.generate(result)
        
        assert report_path.exists()
        assert report_path.suffix == ".json"
        
        # Check markdown report was also generated
        md_path = report_path.parent / "automation_report.md"
        assert md_path.exists()
