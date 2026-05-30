"""
Analytical engine internals for the Quasi-3D Layer 1 engine.

Modules:
    quasi3d: Computation plane generation (Parviainen method)
    magnetic_circuit: MEC reluctance network solver (slotted)
    coreless_field: Hague's analytical field solver (coreless)
    halbach: Halbach array magnetization model
    losses: Copper, iron, PM eddy current loss models
    performance: Result aggregation and metric computation
    topology_registry: Topology dispatch (strategy pattern)
"""
