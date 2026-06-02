"""NeuroFlux Master Automation System.

World-class automated design pipeline with:
- Parallel execution of independent tasks
- Intelligent retry logic with exponential backoff
- Real-time progress tracking
- Automatic tool detection and configuration
- Comprehensive result aggregation
- Post-processing automation (visualization, CAD export)
"""

from neuroflux.automation.orchestrator import (
    MasterOrchestrator,
    AutomationConfig,
    AutomationResult,
    PipelineStage,
    StageStatus,
)
from neuroflux.automation.progress import ProgressTracker, ProgressReport
from neuroflux.automation.reporting import UnifiedReportGenerator, DesignPackage

__all__ = [
    "MasterOrchestrator",
    "AutomationConfig",
    "AutomationResult",
    "PipelineStage",
    "StageStatus",
    "ProgressTracker",
    "ProgressReport",
    "UnifiedReportGenerator",
    "DesignPackage",
]
