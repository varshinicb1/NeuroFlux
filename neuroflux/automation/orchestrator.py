"""Master orchestrator for fully automated AFPM design pipeline.

Executes all stages with intelligent parallelization, retry logic, and comprehensive logging.
"""

from __future__ import annotations

import concurrent.futures
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Callable, TypeVar

from pydantic import BaseModel, Field

from neuroflux.core.config import ExternalToolConfig
from neuroflux.design.engine import (
    AFPMDesignEngine,
    AFPMDesignResult,
    AFPMGeneratorSpec,
)
from neuroflux.visualization import ResultVisualizer
from neuroflux.cad import FreeCADExporter
from neuroflux.automation.progress import ProgressTracker

T = TypeVar("T")

logger = logging.getLogger(__name__)


class StageStatus(Enum):
    """Status of a pipeline stage."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class PipelineStage:
    """A single stage in the automation pipeline."""
    name: str
    status: StageStatus = StageStatus.PENDING
    start_time: float | None = None
    end_time: float | None = None
    error: str | None = None
    result: any = None
    retry_count: int = 0
    max_retries: int = 2

    @property
    def duration_ms(self) -> float:
        """Get stage duration in milliseconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.perf_counter()
        return (end - self.start_time) * 1000.0

    @property
    def is_success(self) -> bool:
        """Check if stage completed successfully."""
        return self.status == StageStatus.COMPLETED


class AutomationConfig(BaseModel):
    """Configuration for the automation pipeline."""
    
    # Execution control
    max_workers: int = Field(default=4, ge=1, le=16, description="Max parallel workers")
    enable_parallel: bool = Field(default=True, description="Enable parallel execution")
    retry_failed: bool = Field(default=True, description="Retry failed stages")
    max_retries: int = Field(default=2, ge=0, le=5, description="Max retries per stage")
    
    # Stage enablement
    run_discovery: bool = Field(default=True, description="Run design discovery")
    run_thermal_analysis: bool = Field(default=True, description="Run thermal analysis")
    run_3d_validation: bool = Field(default=True, description="Run 3D validation")
    run_external_solvers: bool = Field(default=False, description="Run Elmer/Palace if available")
    run_visualization: bool = Field(default=False, description="Auto-launch ParaView")
    run_cad_export: bool = Field(default=False, description="Export STEP files")
    
    # Quality settings
    validation_refinement: str = Field(default="medium", pattern=r"^(coarse|medium|fine)$")
    cad_export_components: list[str] = Field(default_factory=lambda: ["stator", "rotor"])
    
    # Output
    output_root: str = Field(default="design_automation")
    verbose: bool = Field(default=True, description="Verbose logging")
    
    model_config = {"extra": "forbid"}


@dataclass
class AutomationResult:
    """Complete result of an automation run."""
    success: bool
    design_result: AFPMDesignResult | None = None
    stages: dict[str, PipelineStage] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    total_duration_ms: float = 0.0
    tool_config: ExternalToolConfig | None = None
    output_directory: Path | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        return self.total_duration_ms / 1000.0
    
    def get_stage_summary(self) -> dict[str, any]:
        """Get summary of all stages."""
        return {
            name: {
                "status": stage.status.name,
                "duration_ms": stage.duration_ms,
                "retries": stage.retry_count,
                "error": stage.error,
            }
            for name, stage in self.stages.items()
        }


class MasterOrchestrator:
    """World-class automation orchestrator for AFPM generator design.
    
    Features:
    - Intelligent parallel execution of independent stages
    - Exponential backoff retry logic for failed operations
    - Real-time progress tracking with detailed logging
    - Automatic tool detection and configuration
    - Comprehensive error handling and recovery
    - Post-processing automation (visualization, CAD export)
    """
    
    def __init__(self, config: AutomationConfig | None = None) -> None:
        self.config = config or AutomationConfig()
        self.tracker = ProgressTracker()
        self.tool_config = ExternalToolConfig.auto_detect()
        self._executor: concurrent.futures.ThreadPoolExecutor | None = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if self.config.verbose else logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def run(
        self,
        spec: AFPMGeneratorSpec | None = None,
        run_id: str | None = None,
    ) -> AutomationResult:
        """Execute complete automated design pipeline.
        
        Args:
            spec: Design specification (uses defaults if None)
            run_id: Optional run identifier
            
        Returns:
            Complete automation result with all stages
        """
        run_id = run_id or f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        spec = spec or AFPMGeneratorSpec(name=run_id)
        
        logger.info(f"═" * 70)
        logger.info(f"Starting NeuroFlux Master Automation: {run_id}")
        logger.info(f"═" * 70)
        
        # Validate external tools (only if they will be used)
        self._validate_external_tools()
        
        result = AutomationResult(
            success=False,
            tool_config=self.tool_config,
            output_directory=Path(self.config.output_root) / run_id,
        )
        
        start_time = time.perf_counter()
        
        try:
            # Initialize stages
            self._initialize_stages(result)
            
            # Phase 1: Design Discovery (required, sequential)
            self._execute_stage(result, "discovery", self._run_discovery, spec)
            if not result.stages["discovery"].is_success:
                raise RuntimeError("Design discovery failed - cannot continue")
            
            design_result = result.stages["discovery"].result
            result.design_result = design_result
            
            # Phase 2: Parallel post-processing (optional, parallel)
            parallel_tasks = []
            
            if self.config.run_visualization and self.tool_config.paraview_available():
                parallel_tasks.append(
                    ("visualization", self._run_visualization, design_result)
                )
            
            if self.config.run_cad_export and self.tool_config.freecad_available():
                parallel_tasks.append(
                    ("cad_export", self._run_cad_export, design_result)
                )
            
            # Execute parallel tasks
            if parallel_tasks and self.config.enable_parallel:
                self._execute_parallel_stages(result, parallel_tasks)
            else:
                # Sequential execution
                for name, func, arg in parallel_tasks:
                    self._execute_stage(result, name, func, arg)
            
            # Generate unified report
            self._execute_stage(result, "reporting", self._generate_report, result)
            
            result.success = all(
                s.is_success or s.status == StageStatus.SKIPPED
                for s in result.stages.values()
            )
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            result.errors.append(str(e))
            result.errors.extend(traceback.format_exc().split("\n"))
        
        finally:
            result.end_time = datetime.now()
            result.total_duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Cleanup
            if self._executor:
                self._executor.shutdown(wait=True)
            
            # Log summary
            self._log_summary(result)
        
        return result
    
    def _initialize_stages(self, result: AutomationResult) -> None:
        """Initialize all pipeline stages."""
        stages = [
            "discovery",
            "visualization",
            "cad_export",
            "reporting",
        ]
        
        for stage_name in stages:
            result.stages[stage_name] = PipelineStage(name=stage_name)
    
    def _validate_external_tools(self) -> None:
        """Validate that required external tools are available.
        
        Only checks tools that will actually be used based on configuration.
        Core functionality (discovery, thermal analysis) works without external tools.
        
        Raises:
            RuntimeError: If any required tool for enabled features is not available.
        """
        missing_tools = []
        warnings = []
        
        # Check Elmer only if external solvers are enabled
        if self.config.run_external_solvers:
            if not self.tool_config.elmer_available():
                missing_tools.append("ElmerSolver/ElmerGUI")
        else:
            if not self.tool_config.elmer_available():
                warnings.append("Elmer not found (skipping external solver stage)")
        
        # Check Gmsh only if external solvers are enabled
        if self.config.run_external_solvers:
            if self.tool_config.get_gmsh() is None:
                missing_tools.append("Gmsh")
        else:
            if self.tool_config.get_gmsh() is None:
                warnings.append("Gmsh not found (using internal meshing)")
        
        # Check FreeCAD only if CAD export is enabled
        if self.config.run_cad_export:
            if not self.tool_config.freecad_available():
                missing_tools.append("FreeCAD")
        else:
            if not self.tool_config.freecad_available():
                warnings.append("FreeCAD not found (skipping CAD export)")
        
        # Check ParaView only if visualization is enabled
        if self.config.run_visualization:
            if not self.tool_config.paraview_available():
                missing_tools.append("ParaView")
        else:
            if not self.tool_config.paraview_available():
                warnings.append("ParaView not found (skipping visualization)")
        
        # Log warnings for optional tools
        for warning in warnings:
            logger.warning(f"⚠ {warning}")
        
        # Only fail if required tools for enabled features are missing
        if missing_tools:
            error_msg = (
                f"Required external tools for enabled features are missing: {', '.join(missing_tools)}\n"
                f"Set environment variables or disable these features:\n"
                f"  NEUROFLUX_ELMER_SOLVER=<path to ElmerSolver.exe>\n"
                f"  NEUROFLUX_ELMER_GUI=<path to ElmerGUI.exe>\n"
                f"  NEUROFLUX_GMSH=<path to gmsh.exe>\n"
                f"  NEUROFLUX_FREECAD=<path to FreeCAD.exe>\n"
                f"  NEUROFLUX_PARAVIEW=<path to ParaView.exe>\n"
                f"Or run with: --no-external-solvers --no-cad-export --no-visualization"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("✓ External tools validated (core functionality ready)")
    
    def _execute_stage(
        self,
        result: AutomationResult,
        stage_name: str,
        func: Callable[[any], T],
        arg: any,
    ) -> None:
        """Execute a single stage with retry logic."""
        stage = result.stages[stage_name]
        stage.status = StageStatus.RUNNING
        stage.start_time = time.perf_counter()
        
        logger.info(f"▶ Stage '{stage_name}' started")
        
        max_retries = self.config.max_retries if self.config.retry_failed else 0
        
        for attempt in range(max_retries + 1):
            try:
                stage.result = func(arg)
                stage.status = StageStatus.COMPLETED
                stage.end_time = time.perf_counter()
                logger.info(f"✓ Stage '{stage_name}' completed ({stage.duration_ms:.0f}ms)")
                return
                
            except Exception as e:
                stage.retry_count = attempt
                stage.error = str(e)
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"⚠ Stage '{stage_name}' failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    stage.status = StageStatus.FAILED
                    stage.end_time = time.perf_counter()
                    logger.error(f"✗ Stage '{stage_name}' failed after {attempt + 1} attempts: {e}")
                    raise
    
    def _execute_parallel_stages(
        self,
        result: AutomationResult,
        tasks: list[tuple[str, Callable, any]],
    ) -> None:
        """Execute multiple stages in parallel."""
        logger.info(f"▶ Executing {len(tasks)} stages in parallel")
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            
            # Submit all tasks
            futures = {}
            for name, func, arg in tasks:
                stage = result.stages[name]
                stage.status = StageStatus.RUNNING
                stage.start_time = time.perf_counter()
                
                future = executor.submit(self._run_stage_with_error_handling, func, arg)
                futures[future] = name
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                stage = result.stages[name]
                
                try:
                    stage.result = future.result()
                    stage.status = StageStatus.COMPLETED
                    logger.info(f"✓ Parallel stage '{name}' completed")
                except Exception as e:
                    stage.status = StageStatus.FAILED
                    stage.error = str(e)
                    logger.error(f"✗ Parallel stage '{name}' failed: {e}")
                finally:
                    stage.end_time = time.perf_counter()
    
    def _run_stage_with_error_handling(self, func: Callable[[any], T], arg: any) -> T:
        """Run a stage function with error handling for thread pool."""
        return func(arg)
    
    def _run_discovery(self, spec: AFPMGeneratorSpec) -> AFPMDesignResult:
        """Execute design discovery stage."""
        # Update spec with automation config
        spec.run_3d_validation = self.config.run_3d_validation
        spec.run_external_solvers = self.config.run_external_solvers
        spec.validation_refinement = self.config.validation_refinement
        
        engine = AFPMDesignEngine(output_root=self.config.output_root)
        return engine.design(spec)
    
    def _run_visualization(self, design_result: AFPMDesignResult) -> dict[str, bool]:
        """Execute visualization stage."""
        visualizer = ResultVisualizer(self.tool_config)
        
        design_dir = Path(design_result.design_package_dir)
        results = visualizer.visualize_design_run(design_dir)
        
        launched = [k for k, v in results.items() if v]
        if launched:
            logger.info(f"✓ Launched ParaView for: {', '.join(launched)}")
        
        return results
    
    def _run_cad_export(self, design_result: AFPMDesignResult) -> dict[str, any]:
        """Execute CAD export stage."""
        exporter = FreeCADExporter(self.tool_config)
        geometry = design_result.best_candidate.analytical_input.geometry
        
        output_dir = Path(design_result.design_package_dir) / "cad_export"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        if "stator" in self.config.cad_export_components:
            stator_path = output_dir / "stator.step"
            results["stator"] = exporter.export_stator_step(geometry, stator_path)
        
        if "rotor" in self.config.cad_export_components:
            from neuroflux.core.models import MagnetConfiguration
            rotor_path = output_dir / "rotor.step"
            magnet_config = MagnetConfiguration(
                grade="N42",
                type="conventional",
            )
            results["rotor"] = exporter.export_rotor_step(geometry, rotor_path, magnet_config)
        
        successful = [k for k, v in results.items() if v.success]
        if successful:
            logger.info(f"✓ Exported CAD for: {', '.join(successful)}")
        
        return results
    
    def _generate_report(self, result: AutomationResult) -> Path:
        """Generate unified automation report."""
        from neuroflux.automation.reporting import UnifiedReportGenerator
        
        generator = UnifiedReportGenerator()
        report_path = generator.generate(result)
        
        logger.info(f"✓ Generated unified report: {report_path}")
        return report_path
    
    def _log_summary(self, result: AutomationResult) -> None:
        """Log final automation summary."""
        logger.info(f"═" * 70)
        logger.info(f"Automation Complete: {'SUCCESS' if result.success else 'FAILED'}")
        logger.info(f"═" * 70)
        logger.info(f"Total Duration: {result.duration_seconds:.2f}s")
        logger.info(f"Output Directory: {result.output_directory}")
        
        # Stage summary
        logger.info("Stage Summary:")
        for name, stage in result.stages.items():
            status_icon = "✓" if stage.is_success else "✗" if stage.status == StageStatus.FAILED else "○"
            logger.info(f"  {status_icon} {name}: {stage.status.name} ({stage.duration_ms:.0f}ms)")
        
        if result.errors:
            logger.error(f"Errors: {len(result.errors)}")
        
        if result.warnings:
            logger.warning(f"Warnings: {len(result.warnings)}")
