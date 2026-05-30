"""
Abstract Engine protocol — the non-negotiable contract for all NeuroFlux engines.

Every external tool (FEMM, Elmer, PYLEECAN, MagGen, etc.) and every
internal engine (Analytical, ROM) MUST implement this protocol.

Design philosophy (from core requirements):
    "Every external tool/repo must be treated as an Engine"
    - Clean input → output contract
    - No tight coupling
    - Swappable and testable in isolation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from neuroflux.core.models import AFPMTopology, FidelityLevel

# Generic type variables for engine input/output
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True)
class EngineCapabilities:
    """Declares what an engine can do.

    Used by the orchestrator to select appropriate engines for a given
    task and by validation to reject unsupported configurations early.
    """

    supported_topologies: list[AFPMTopology] = field(default_factory=list)
    fidelity_level: FidelityLevel = FidelityLevel.ANALYTICAL
    supports_thermal: bool = False
    supports_structural: bool = False
    supports_transient: bool = False
    max_recommended_poles: int = 100
    description: str = ""


@dataclass(frozen=True)
class EngineMetadata:
    """Static metadata about an engine.

    Provides identity, versioning, and performance characteristics
    for logging, orchestration, and result traceability.
    """

    name: str
    version: str
    description: str
    fidelity_level: FidelityLevel
    typical_execution_time_ms: float  # Expected time for a single run
    requires_external_tool: bool = False
    external_tool_name: str = ""


@dataclass
class ValidationResult:
    """Result of input validation.

    Engines validate inputs before running to provide early, clear
    feedback about configuration problems.
    """

    is_valid: bool
    errors: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, field_name: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append({"field": field_name, "message": message})
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a non-fatal validation warning."""
        self.warnings.append(message)


class Engine(ABC, Generic[InputT, OutputT]):
    """Abstract base class for all NeuroFlux engines.

    Every engine — whether wrapping an external tool (FEMM, Elmer, PYLEECAN)
    or implementing internal logic (Analytical, ROM) — must subclass this
    and implement the three core methods.

    The generic types InputT and OutputT define the engine's contract:
        - InputT: What the engine needs to perform a simulation
        - OutputT: What the engine produces as a result

    Example:
        >>> engine = Quasi3DAnalyticalEngine()
        >>> result = engine.run(analytical_input)
        >>> print(f"Torque: {result.torque_nm:.1f} N·m")

    Design Principles:
        1. Composition over inheritance — engines should be combinable
        2. Each engine testable in isolation
        3. Clean error handling with typed exceptions
        4. Proper logging for debugging and audit trails
    """

    @abstractmethod
    def get_metadata(self) -> EngineMetadata:
        """Return static metadata about this engine.

        Returns:
            EngineMetadata with name, version, fidelity, etc.
        """
        ...

    @abstractmethod
    def get_capabilities(self) -> EngineCapabilities:
        """Declare what this engine supports.

        Used by the orchestrator to select appropriate engines
        and by validation to reject unsupported configurations early.

        Returns:
            EngineCapabilities listing supported topologies and features.
        """
        ...

    @abstractmethod
    def validate_input(self, input_data: InputT) -> ValidationResult:
        """Validate input data before running.

        Should check:
        - Required fields are present and within valid ranges
        - Topology is supported
        - Material/geometry combinations are physically reasonable
        - External tools are available (if needed)

        Args:
            input_data: The input to validate.

        Returns:
            ValidationResult with is_valid flag, errors, and warnings.
        """
        ...

    @abstractmethod
    def run(self, input_data: InputT) -> OutputT:
        """Execute the engine simulation.

        This is the core method. It takes validated input and produces
        a complete output. Implementations should:
        - Call validate_input() internally (or assume pre-validated)
        - Time the execution
        - Handle errors gracefully with typed exceptions
        - Log key steps for debugging

        Args:
            input_data: Validated engine input.

        Returns:
            Engine output with all computed results.

        Raises:
            EngineError: On computation failure.
            TopologyNotSupportedError: If topology is not supported.
            ConvergenceError: If iterative solver fails to converge.
        """
        ...

    def run_safe(self, input_data: InputT) -> OutputT | ValidationResult:
        """Run with automatic input validation.

        Validates input first; returns ValidationResult if invalid,
        otherwise runs the engine and returns the output.

        Args:
            input_data: Engine input (may be invalid).

        Returns:
            OutputT on success, or ValidationResult on validation failure.
        """
        validation = self.validate_input(input_data)
        if not validation.is_valid:
            return validation
        return self.run(input_data)

    def __repr__(self) -> str:
        meta = self.get_metadata()
        return f"<{meta.name} v{meta.version} [{meta.fidelity_level.value}]>"
