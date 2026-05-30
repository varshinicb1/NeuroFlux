"""
Custom exception hierarchy for NeuroFlux engines.

All engine-related errors derive from EngineError, enabling clean
error handling at the orchestration layer.
"""


class NeuroFluxError(Exception):
    """Base exception for all NeuroFlux errors."""

    pass


class EngineError(NeuroFluxError):
    """Base exception for engine execution errors.

    Raised when an engine fails during its run() method for reasons
    beyond input validation (solver failure, external tool crash, etc.).
    """

    def __init__(self, engine_name: str, message: str) -> None:
        self.engine_name = engine_name
        super().__init__(f"[{engine_name}] {message}")


class TopologyNotSupportedError(EngineError):
    """Raised when an engine does not support the requested topology.

    Each engine declares its supported topologies via get_capabilities().
    This error indicates a mismatch between the request and the engine.
    """

    def __init__(self, engine_name: str, topology: str) -> None:
        self.topology = topology
        super().__init__(engine_name, f"Topology '{topology}' is not supported")


class ConvergenceError(EngineError):
    """Raised when an iterative solver fails to converge.

    Common in non-linear magnetic circuit solvers when the saturation
    factor iteration does not stabilize within the allowed iterations.
    """

    def __init__(
        self, engine_name: str, iterations: int, residual: float, tolerance: float
    ) -> None:
        self.iterations = iterations
        self.residual = residual
        self.tolerance = tolerance
        super().__init__(
            engine_name,
            f"Failed to converge after {iterations} iterations "
            f"(residual={residual:.2e}, tolerance={tolerance:.2e})",
        )


class MaterialNotFoundError(NeuroFluxError):
    """Raised when a requested material grade is not in the database.

    The material database (neuroflux.core.materials) contains predefined
    grades. This error indicates the user specified an unknown grade.
    """

    def __init__(self, grade: str, material_type: str = "material") -> None:
        self.grade = grade
        self.material_type = material_type
        super().__init__(f"{material_type} grade '{grade}' not found in database")


class ExternalToolNotFoundError(EngineError):
    """Raised when a required external tool is not installed.

    Engine wrappers for FEMM, Elmer, PYLEECAN, etc. require those tools
    to be installed separately. This error provides a clear diagnostic.
    """

    def __init__(self, engine_name: str, tool_name: str, install_hint: str = "") -> None:
        self.tool_name = tool_name
        self.install_hint = install_hint
        msg = f"External tool '{tool_name}' is not installed or not found on PATH"
        if install_hint:
            msg += f". Install hint: {install_hint}"
        super().__init__(engine_name, msg)


class ValidationError(NeuroFluxError):
    """Raised when input validation fails.

    Contains structured information about which fields failed
    and why, enabling clean error reporting to the user.
    """

    def __init__(self, errors: list[dict]) -> None:
        self.errors = errors
        field_names = [e.get("field", "unknown") for e in errors]
        super().__init__(f"Validation failed for fields: {', '.join(field_names)}")
