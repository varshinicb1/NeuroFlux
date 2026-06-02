"""NeuroFlux Web-Based GUI.

Modern web interface for the AFPM generator design automation system.
Features:
- Real-time progress monitoring
- Interactive 3D visualization
- Design parameter forms
- Results dashboard
- Tool status indicators
"""

from neuroflux.gui.server import GUIServer, start_gui
from neuroflux.gui.state import GUIState, DesignSession

__all__ = ["GUIServer", "start_gui", "GUIState", "DesignSession"]
