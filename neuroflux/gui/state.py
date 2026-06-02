"""State management for GUI.

Tracks design sessions, progress, and results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from neuroflux.automation import AutomationResult


@dataclass
class DesignSession:
    """A single design automation session."""
    
    session_id: str
    name: str
    parameters: dict
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    current_stage: str = ""
    message: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    result: AutomationResult | None = None


class GUIState:
    """Global GUI state manager."""
    
    def __init__(self) -> None:
        self.sessions: dict[str, DesignSession] = {}
        self.current_session: DesignSession | None = None
    
    def add_session(self, session: DesignSession) -> None:
        """Add a new session."""
        self.sessions[session.session_id] = session
    
    def get_session(self, session_id: str) -> DesignSession | None:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def update_session_progress(
        self,
        session_id: str,
        progress: float,
        stage: str,
        message: str = "",
    ) -> None:
        """Update session progress."""
        session = self.sessions.get(session_id)
        if session:
            session.progress = progress
            session.current_stage = stage
            if message:
                session.message = message
