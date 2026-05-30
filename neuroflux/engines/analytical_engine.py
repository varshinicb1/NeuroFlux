"""
Main Layer 1 Analytical Engine wrapper for NeuroFlux.

Exposes a unified, lightning-fast (<15ms) analytical evaluation pipeline
for multi-plane Quasi-3D/MEC slotted DSSR, coreless Hague, and Halbach
AFPM machines.

Fully conforms to the Engine protocol.
"""

from __future__ import annotations

import time
from neuroflux.core.engine_base import Engine, ValidationResult, EngineMetadata, EngineCapabilities
from neuroflux.core.models import AnalyticalEngineInput, EngineResult, AFPMTopology, FidelityLevel
from neuroflux.core.exceptions import EngineError
from neuroflux.analytical.topology_registry import TopologyRegistry
from neuroflux.utils.validation import validate_analytical_input


class AnalyticalEngine(Engine[AnalyticalEngineInput, EngineResult]):
    """
    Main Analytical simulation engine conforming to the NeuroFlux Engine contract.
    """

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="Quasi3DAnalyticalEngine",
            version="1.0.0",
            description="Layer 1 Quasi-3D MEC and coreless Hague physics solver",
            fidelity_level=FidelityLevel.ANALYTICAL,
            typical_execution_time_ms=12.5,
            requires_external_tool=False,
        )

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supported_topologies=[
                AFPMTopology.DSSR_SLOTTED,
                AFPMTopology.SSDR_CORELESS,
                AFPMTopology.SSDR_CORELESS_HALBACH,
            ],
            fidelity_level=FidelityLevel.ANALYTICAL,
            supports_thermal=False,
            supports_structural=False,
            supports_transient=False,
            max_recommended_poles=80,
            description="Ultra-fast magnetic equivalent circuit and analytical field mapping",
        )

    def validate_input(self, input_data: AnalyticalEngineInput) -> ValidationResult:
        """
        Validates physics and constraints before launching computations.
        """
        return validate_analytical_input(input_data)

    def run(self, input_data: AnalyticalEngineInput) -> EngineResult:
        """
        Executes the analytical solvers based on the chosen topology.
        """
        # Step 1: Pre-validation
        val_res = self.validate_input(input_data)
        if not val_res.is_valid:
            error_details = ", ".join([f"{e.get('field', 'general')}: {e.get('message', '')}" for e in val_res.errors])
            raise EngineError(
                "Quasi3DAnalyticalEngine",
                f"Input failed physical validation: {error_details}"
            )

        # Step 2: Fetch topology dispatcher
        topology = input_data.geometry.topology
        op = input_data.operating_point
        
        try:
            # Step 3: Run registered solver pipeline
            output = TopologyRegistry.dispatch(topology, input_data, op)
            return output
        except Exception as e:
            raise EngineError("Quasi3DAnalyticalEngine", f"Analytical engine solver execution failed: {str(e)}") from e
