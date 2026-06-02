"""Web GUI server for NeuroFlux.

Modern Flask-based web interface with:
- Real-time WebSocket updates
- Interactive design forms
- Progress visualization
- 3D model viewer integration
- Results dashboard
"""

from __future__ import annotations

import json
import logging
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit

from neuroflux.automation import (
    MasterOrchestrator,
    AutomationConfig,
    AutomationResult,
)
from neuroflux.automation.progress import ProgressReport
from neuroflux.core.config import ExternalToolConfig
from neuroflux.design.engine import AFPMGeneratorSpec
from neuroflux.gui.state import GUIState, DesignSession

logger = logging.getLogger(__name__)


class GUIServer:
    """Web GUI server for NeuroFlux automation.
    
    Provides a modern web interface for:
    - Design parameter input
    - Real-time progress monitoring
    - Results visualization
    - Tool status checking
    - Historical design browser
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        output_root: str = "design_automation",
    ) -> None:
        self.host = host
        self.port = port
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        
        # Flask app
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static"),
        )
        self.app.config["SECRET_KEY"] = "neuroflux-gui-secret"
        
        # SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # State management
        self.state = GUIState()
        self._active_sessions: dict[str, DesignSession] = {}
        self._tool_config = ExternalToolConfig.auto_detect()
        
        # Setup routes
        self._setup_routes()
        self._setup_socket_events()
    
    def _setup_routes(self) -> None:
        """Setup HTTP routes."""
        
        @self.app.route("/")
        def index():
            """Main dashboard."""
            return render_template("index.html")
        
        @self.app.route("/design")
        def design_page():
            """Design form page."""
            return render_template("design.html")
        
        @self.app.route("/results/<session_id>")
        def results_page(session_id: str):
            """Results page for a design session."""
            return render_template("results.html", session_id=session_id)
        
        @self.app.route("/api/tool-status")
        def tool_status():
            """Get external tool status."""
            return jsonify({
                "elmer": {
                    "available": self._tool_config.elmer_available(),
                    "path": self._tool_config.get_elmer_solver(),
                },
                "freecad": {
                    "available": self._tool_config.freecad_available(),
                    "path": self._tool_config.get_freecad(),
                },
                "paraview": {
                    "available": self._tool_config.paraview_available(),
                    "path": self._tool_config.get_paraview(),
                },
                "gmsh": {
                    "available": self._tool_config.get_gmsh() is not None,
                    "path": self._tool_config.get_gmsh(),
                },
            })
        
        @self.app.route("/api/start-design", methods=["POST"])
        def start_design():
            """Start a new design automation."""
            data = request.json
            
            session_id = self._create_session(data)
            
            # Start automation in background thread
            thread = threading.Thread(
                target=self._run_automation,
                args=(session_id, data),
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "message": "Design automation started",
            })
        
        @self.app.route("/api/session/<session_id>/status")
        def session_status(session_id: str):
            """Get session status."""
            session = self._active_sessions.get(session_id)
            if not session:
                return jsonify({"error": "Session not found"}), 404
            
            return jsonify({
                "session_id": session_id,
                "status": session.status,
                "progress": session.progress,
                "current_stage": session.current_stage,
                "message": session.message,
                "started_at": session.started_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            })
        
        @self.app.route("/api/session/<session_id>/results")
        def session_results(session_id: str):
            """Get session results."""
            session = self._active_sessions.get(session_id)
            if not session:
                return jsonify({"error": "Session not found"}), 404
            
            if not session.result:
                return jsonify({"error": "Results not available yet"}), 404
            
            return jsonify(self._format_results(session.result))
        
        @self.app.route("/api/sessions")
        def list_sessions():
            """List all design sessions."""
            sessions = []
            for session_id, session in self._active_sessions.items():
                sessions.append({
                    "session_id": session_id,
                    "name": session.name,
                    "status": session.status,
                    "started_at": session.started_at.isoformat(),
                })
            return jsonify(sessions)
        
        @self.app.route("/api/designs")
        def list_designs():
            """List completed designs from output directory."""
            designs = []
            if self.output_root.exists():
                for design_dir in self.output_root.iterdir():
                    if design_dir.is_dir():
                        manifest = design_dir / "automation_report.json"
                        if manifest.exists():
                            designs.append({
                                "name": design_dir.name,
                                "path": str(design_dir),
                                "created": datetime.fromtimestamp(
                                    manifest.stat().st_mtime
                                ).isoformat(),
                            })
            return jsonify(designs)
    
    def _setup_socket_events(self) -> None:
        """Setup WebSocket events."""
        
        @self.socketio.on("connect")
        def handle_connect():
            """Client connected."""
            logger.info("Client connected")
            emit("connected", {"message": "Connected to NeuroFlux GUI"})
        
        @self.socketio.on("subscribe")
        def handle_subscribe(data):
            """Subscribe to session updates."""
            session_id = data.get("session_id")
            if session_id:
                emit("subscribed", {"session_id": session_id})
        
        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Client disconnected."""
            logger.info("Client disconnected")
    
    def _create_session(self, data: dict) -> str:
        """Create a new design session."""
        session_id = f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = DesignSession(
            session_id=session_id,
            name=data.get("name", "Untitled Design"),
            parameters=data,
        )
        self._active_sessions[session_id] = session
        return session_id
    
    def _run_automation(self, session_id: str, data: dict) -> None:
        """Run automation in background."""
        session = self._active_sessions[session_id]
        session.status = "running"
        
        try:
            # Build config
            config = AutomationConfig(
                output_root=str(self.output_root),
                run_external_solvers=data.get("run_external_solvers", False),
                run_visualization=data.get("visualize", False),
                run_cad_export=data.get("export_cad", False),
                validation_refinement=data.get("refinement", "medium"),
                enable_parallel=True,
                verbose=True,
            )
            
            # Build spec
            spec = AFPMGeneratorSpec(
                name=data.get("name", "auto-design"),
                target_power_w=data.get("target_power_w", 500.0),
                target_speed_rpm=data.get("target_speed_rpm", 800.0),
                target_voltage_v=data.get("target_voltage_v", 48.0),
                max_outer_diameter_m=data.get("max_diameter_m", 0.25),
                min_efficiency=data.get("min_efficiency", 0.60),
                run_3d_validation=True,
                run_external_solvers=data.get("run_external_solvers", False),
                validation_refinement=data.get("refinement", "medium"),
            )
            
            # Create orchestrator with progress callback
            orchestrator = MasterOrchestrator(config)
            
            # Run automation
            result = orchestrator.run(spec, run_id=session_id)
            
            # Update session
            session.result = result
            session.status = "completed" if result.success else "failed"
            session.completed_at = datetime.now()
            session.message = "Design completed successfully" if result.success else "Design failed"
            
            # Emit completion
            self.socketio.emit("design_complete", {
                "session_id": session_id,
                "success": result.success,
                "output_dir": str(result.output_directory) if result.output_directory else None,
            })
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            session.status = "failed"
            session.message = str(e)
            session.completed_at = datetime.now()
            
            self.socketio.emit("design_error", {
                "session_id": session_id,
                "error": str(e),
            })
    
    def _format_results(self, result: AutomationResult) -> dict:
        """Format automation results for API response."""
        design = result.design_result
        
        return {
            "success": result.success,
            "duration_seconds": result.duration_seconds,
            "stages": result.get_stage_summary(),
            "design": {
                "name": design.spec.name if design else None,
                "power_w": design.best_candidate.analytical_result.power_w if design and design.best_candidate else None,
                "torque_nm": design.best_candidate.analytical_result.torque_nm if design and design.best_candidate else None,
                "efficiency": design.best_candidate.analytical_result.efficiency if design and design.best_candidate else None,
                "diameter_m": design.best_candidate.analytical_input.geometry.D_out if design and design.best_candidate else None,
            } if design else None,
            "thermal": {
                "max_winding_temp": design.thermal_analysis.max_winding_temp_c if design else None,
                "max_magnet_temp": design.thermal_analysis.max_magnet_temp_c if design else None,
                "status": design.thermal_analysis.status if design else None,
            } if design else None,
            "validation": {
                "passed": design.validation_passed if design else None,
                "confidence": design.validation_result.thermal.confidence if design and design.validation_result else None,
            } if design else None,
            "output_directory": str(result.output_directory) if result.output_directory else None,
            "report_path": str(result.output_directory / "automation_report.md") if result.output_directory else None,
        }
    
    def run(self, open_browser: bool = True) -> None:
        """Run the GUI server."""
        url = f"http://{self.host}:{self.port}"
        
        logger.info(f"Starting NeuroFlux GUI at {url}")
        
        if open_browser:
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=False,
            use_reloader=False,
        )


def start_gui(
    host: str = "127.0.0.1",
    port: int = 8080,
    output_root: str = "design_automation",
    open_browser: bool = True,
) -> None:
    """Start the NeuroFlux GUI.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        output_root: Root directory for design outputs
        open_browser: Auto-open browser
    """
    server = GUIServer(
        host=host,
        port=port,
        output_root=output_root,
    )
    server.run(open_browser=open_browser)


if __name__ == "__main__":
    start_gui()
