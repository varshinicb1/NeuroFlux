"""
NeuroFlux — Autonomous Engineering Discovery System for AFPM Machines.

An engine-based, multi-fidelity simulation platform for Axial-Flux
Permanent Magnet (AFPM) machine design, optimization, and digital twins.

Architecture:
    Layer 0: Geometry Engine
    Layer 1: Fast Quasi-3D Analytical Engine
    Layer 2: 2D / Quasi-3D FEA Engine (FEMM)
    Layer 3: High-Fidelity 3D Multi-physics Engine (Elmer)
    Layer 4: Digital Twin + ROM Execution Layer
    Layer 5: Discovery / Optimization / Invention Layer

Every component exposes a clean input → output contract via the Engine protocol.
"""

__version__ = "0.1.0"
__author__ = "Varshini — Vidyuthlabs / Parakram"
