"""Real-time progress tracking for automation pipeline.

Provides detailed progress reporting with ETA calculations and stage breakdowns.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


@dataclass
class StageProgress:
    """Progress information for a single stage."""
    name: str
    percent_complete: float = 0.0
    current_step: str = ""
    steps_total: int = 0
    steps_completed: int = 0
    eta_seconds: float | None = None
    start_time: float | None = None
    
    @property
    def is_complete(self) -> bool:
        return self.percent_complete >= 100.0
    
    @property
    def elapsed_seconds(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.perf_counter() - self.start_time


@dataclass
class ProgressReport:
    """Complete progress report for the automation pipeline."""
    overall_percent: float = 0.0
    current_stage: str = ""
    stages: dict[str, StageProgress] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    eta_completion: datetime | None = None
    message: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "overall_percent": self.overall_percent,
            "current_stage": self.current_stage,
            "start_time": self.start_time.isoformat(),
            "eta_completion": self.eta_completion.isoformat() if self.eta_completion else None,
            "message": self.message,
            "stages": {
                name: {
                    "percent": stage.percent_complete,
                    "step": stage.current_step,
                    "steps_completed": stage.steps_completed,
                    "steps_total": stage.steps_total,
                    "eta_seconds": stage.eta_seconds,
                }
                for name, stage in self.stages.items()
            },
        }


class ProgressTracker:
    """Track and report progress of automation pipeline.
    
    Provides real-time updates with ETA calculations based on historical
    stage durations and current execution speed.
    """
    
    def __init__(self) -> None:
        self._stages: dict[str, StageProgress] = {}
        self._start_time = time.perf_counter()
        self._callbacks: list[Callable[[ProgressReport], None]] = []
        self._stage_weights: dict[str, float] = {
            "discovery": 0.50,
            "thermal_analysis": 0.15,
            "3d_validation": 0.20,
            "visualization": 0.05,
            "cad_export": 0.05,
            "reporting": 0.05,
        }
        self._historical_durations: dict[str, float] = {}
    
    def register_callback(self, callback: Callable[[ProgressReport], None]) -> None:
        """Register a callback to receive progress updates."""
        self._callbacks.append(callback)
    
    def start_stage(self, stage_name: str, steps_total: int = 1) -> None:
        """Mark a stage as started."""
        self._stages[stage_name] = StageProgress(
            name=stage_name,
            steps_total=steps_total,
            start_time=time.perf_counter(),
        )
        self._notify()
    
    def update_stage(
        self,
        stage_name: str,
        step: str | None = None,
        steps_completed: int | None = None,
        percent: float | None = None,
    ) -> None:
        """Update progress for a stage."""
        if stage_name not in self._stages:
            return
        
        stage = self._stages[stage_name]
        
        if step is not None:
            stage.current_step = step
        
        if steps_completed is not None:
            stage.steps_completed = steps_completed
            if stage.steps_total > 0:
                stage.percent_complete = (steps_completed / stage.steps_total) * 100.0
        
        if percent is not None:
            stage.percent_complete = percent
        
        # Calculate ETA based on progress rate
        if stage.percent_complete > 0 and stage.percent_complete < 100:
            elapsed = stage.elapsed_seconds
            estimated_total = elapsed / (stage.percent_complete / 100.0)
            stage.eta_seconds = estimated_total - elapsed
        
        self._notify()
    
    def complete_stage(self, stage_name: str, duration_ms: float | None = None) -> None:
        """Mark a stage as complete."""
        if stage_name in self._stages:
            self._stages[stage_name].percent_complete = 100.0
            
            # Record historical duration for future ETA estimates
            if duration_ms is not None:
                self._historical_durations[stage_name] = duration_ms
        
        self._notify()
    
    def get_report(self) -> ProgressReport:
        """Generate current progress report."""
        # Calculate overall percentage using stage weights
        total_weight = 0.0
        weighted_progress = 0.0
        
        for stage_name, stage in self._stages.items():
            weight = self._stage_weights.get(stage_name, 0.1)
            total_weight += weight
            weighted_progress += (stage.percent_complete / 100.0) * weight
        
        overall_percent = (weighted_progress / total_weight * 100.0) if total_weight > 0 else 0.0
        
        # Determine current stage (last started but not complete)
        current_stage = ""
        for name, stage in self._stages.items():
            if not stage.is_complete:
                current_stage = name
                break
        
        # Calculate ETA
        eta_completion = None
        if overall_percent > 0 and overall_percent < 100:
            elapsed = time.perf_counter() - self._start_time
            estimated_total = elapsed / (overall_percent / 100.0)
            remaining = estimated_total - elapsed
            eta_completion = datetime.now() + timedelta(seconds=remaining)
        
        return ProgressReport(
            overall_percent=min(overall_percent, 100.0),
            current_stage=current_stage,
            stages=dict(self._stages),
            start_time=datetime.fromtimestamp(self._start_time),
            eta_completion=eta_completion,
        )
    
    def _notify(self) -> None:
        """Notify all registered callbacks."""
        report = self.get_report()
        for callback in self._callbacks:
            try:
                callback(report)
            except Exception:
                pass  # Don't let callbacks break the pipeline


class ConsoleProgressDisplay:
    """Display progress updates to console with live updating."""
    
    def __init__(self, tracker: ProgressTracker) -> None:
        self.tracker = tracker
        self._last_lines = 0
        tracker.register_callback(self._on_update)
    
    def _on_update(self, report: ProgressReport) -> None:
        """Handle progress update."""
        # Simple console output (can be enhanced with curses/rich for live updates)
        if report.current_stage:
            stage = report.stages.get(report.current_stage)
            if stage:
                print(
                    f"\r[{report.overall_percent:5.1f}%] {report.current_stage}: "
                    f"{stage.current_step} ({stage.steps_completed}/{stage.steps_total})",
                    end="",
                    flush=True,
                )
        
        if report.overall_percent >= 100.0:
            print()  # New line when complete
