# Quasi-3D Analytical Engine — Python Architecture & Structure

**Document Type:** Implementation Blueprint  
**Version:** v1.0  
**Date:** May 30, 2026  
**Grounding:** Strictly based on equations and methods from Document 12 (AFPM Mathematical Foundation)

---

## 1. Purpose

This document defines a clean, modular, and extensible **Python architecture** for the **Layer 1 Fast Analytical / Quasi-3D Engine** in NeuroFlux.

The engine must:
- Support both **slotted** and **coreless** AFPM topologies.
- Implement quasi-3D modeling (multiple radial computation planes).
- Be fast enough for design space exploration and optimization loops (< 200 ms per evaluation target).
- Expose clean input/output contracts.
- Be grounded in the mathematical models from Document 12 (Parviainen + Hemeida style).

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Quasi3DAnalyticalEngine                    │
├──────────────────────────────────────────────────────────────┤
│  Topology Registry                                           │
│  Geometry Processor (Plane Division)                         │
│  Magnetic Model (MEC / Analytical per plane)                 │
│  Loss Calculator                                             │
│  Performance Aggregator                                      │
│  Thermal Estimator (optional lightweight)                    │
└──────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Composition over inheritance** where possible.
- Clear separation between geometry, electromagnetics, losses, and post-processing.
- Support for different topologies via strategy/plugin pattern.
- Strong typing and clear dataclasses for inputs/outputs.

---

## 3. Core Data Models (Dataclasses)

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np

@dataclass
class MachineGeometry:
    D_out: float          # Outer diameter [m]
    k_D: float            # Diameter ratio (r_in / r_out)
    l_s: float            # Axial length of stator stack [m]
    g: float              # Physical air-gap length [m]
    l_PM: float           # PM thickness [m]
    w_PM: float           # Magnet width at mean radius (or function)
    p: int                # Number of pole pairs
    Q: int                # Number of slots
    topology: str         # "DSSR_slotted", "SSDR_coreless", etc.

@dataclass
class MaterialProperties:
    Br: float             # Remanence [T]
    mu_r_PM: float        # Relative permeability of PM
    steel_grade: str      # e.g., "M600-50A"
    # Loss coefficients, thermal properties, etc.

@dataclass
class WindingParameters:
    turns_per_phase: int
    phases: int = 3
    fill_factor: float = 0.6
    current_density: float = 5e6   # A/m²

@dataclass
class OperatingPoint:
    speed_rpm: float
    I_rms: float
    ambient_temp: float = 40.0

@dataclass
class PlaneResult:
    r_mean: float
    B_g: float
    torque_contribution: float
    losses: Dict[str, float]

@dataclass
class EngineResult:
    torque: float
    back_emf_rms: float
    efficiency: float
    losses: Dict[str, float]
    max_flux_densities: Dict[str, float]
    plane_results: List[PlaneResult]
    computation_time_ms: float
```

---

## 4. Main Class Structure

```python
class Quasi3DAnalyticalEngine:
    def __init__(self, num_planes: int = 7):
        self.num_planes = num_planes
        self.topology_handlers = {
            "DSSR_slotted": self._handle_dssr_slotted,
            "SSDR_coreless": self._handle_ssdr_coreless,
            # Add more as needed
        }

    def evaluate(self, 
                 geometry: MachineGeometry,
                 materials: MaterialProperties,
                 winding: WindingParameters,
                 operating_point: OperatingPoint) -> EngineResult:
        """
        Main entry point. Returns full performance evaluation.
        """
        # 1. Generate computation planes
        planes = self._generate_planes(geometry)

        # 2. Select topology handler
        handler = self.topology_handlers.get(geometry.topology)
        if not handler:
            raise ValueError(f"Unsupported topology: {geometry.topology}")

        # 3. Compute per-plane results
        plane_results = []
        for plane in planes:
            result = handler(plane, geometry, materials, winding, operating_point)
            plane_results.append(result)

        # 4. Aggregate results
        return self._aggregate_results(plane_results, operating_point)

    def _generate_planes(self, geometry: MachineGeometry):
        """Divide machine into radial computation planes (quasi-3D)."""
        # Implementation based on Parviainen equations
        pass

    def _handle_dssr_slotted(self, plane, geometry, materials, winding, op):
        """Quasi-3D MEC + analytical calculations for slotted DSSR."""
        # Use reluctance network per plane
        # Calculate B_g, torque contribution, losses, etc.
        pass

    def _handle_ssdr_coreless(self, plane, geometry, materials, winding, op):
        """Analytical model for coreless (Hague / Fourier-Bessel style)."""
        pass

    def _aggregate_results(self, plane_results, operating_point):
        """Sum contributions across planes and compute global metrics."""
        pass
```

---

## 5. Key Internal Components

### 5.1 Geometry Processor
- Calculates `D_ave`, `τ_p`, and relative magnet width per plane.
- Handles variable magnet shape if `w_PM` is provided as a function of radius.

### 5.2 Magnetic Model (Per Plane)
- **Slotted**: Non-linear reluctance network (inspired by Parviainen + Hemeida 2019).
- **Coreless**: Analytical solution for air-gap field (Hague’s method or Fourier-Bessel series).

### 5.3 Loss Models
- Copper losses (slot + end-winding)
- Iron losses (using material-specific coefficients from Document 12)
- PM eddy current losses (especially important for coreless)

### 5.4 Performance Aggregator
- Total torque = sum of plane contributions
- Efficiency calculation
- Flux density reporting (teeth, yoke, air-gap)

---

## 6. Input / Output Contract (Clean Engine Interface)

**Input Example (JSON-like):**
```json
{
  "geometry": { "D_out": 0.52, "k_D": 0.6, ... },
  "materials": { "Br": 1.2, "steel_grade": "M600-50A" },
  "winding": { "turns_per_phase": 60, "current_density": 5e6 },
  "operating_point": { "speed_rpm": 300, "I_rms": 94 }
}
```

**Output:** `EngineResult` dataclass (as defined above).

This contract allows the engine to be called from optimization loops, surrogate trainers, or the digital twin ROM generator.

---

## 7. Extensibility Points

- Add new topologies by registering a new handler method.
- Swap magnetic solvers (MEC vs pure analytical) per topology.
- Add thermal estimator as an optional module.
- Support for Halbach arrays or different magnet shapes via geometry parameters.

---

## 8. Integration with NeuroFlux Stack

- **Layer 0 (Geometry Engine)** → Provides `MachineGeometry`
- **Layer 1 (This Engine)** → Fast evaluation
- **Surrogate Training** → Uses this engine to generate training data
- **Digital Twin ROM Generator** → Uses this engine + higher-fidelity data to create reduced-order models

---

## 9. Recommended Development Order

1. Implement `MachineGeometry` and plane generation.
2. Implement basic slotted DSSR handler with simplified MEC.
3. Add loss models and aggregation.
4. Add coreless handler.
5. Add unit tests against known cases from Parviainen thesis / literature.
6. Expose clean `evaluate()` interface.

---

**This structure provides a solid, grounded foundation for implementing the fast analytical engine in NeuroFlux.**

It is designed to be extended as more topologies and features (YASA, multi-stage, advanced thermal coupling, etc.) are added.

**End of Quasi-3D Analytical Engine Python Structure v1.0**