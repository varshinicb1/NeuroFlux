# NeuroFlux Multi-Fidelity Simulation Stack Architecture

**Document Type:** Core Platform Architecture  
**Version:** v1.0  
**Date:** May 30, 2026

---

## 1. Vision & Philosophy

NeuroFlux aims to be an **autonomous engineering discovery system** ("AlphaFold for Engineering Design").

A critical requirement is a **multi-fidelity simulation stack** that can:

- Evaluate thousands of design candidates quickly (fast analytical layer).
- Provide high-accuracy validation when needed (higher-fidelity layers).
- Support optimization, surrogate modeling, and invention generation.
- Treat external tools (PYLEECAN, FEMM, Elmer, MagGen, etc.) as **clean engines** with well-defined inputs and outputs.

**Core Principle:**  
Never compromise on physics. Use the right fidelity at the right time. Fast models for exploration, accurate models for validation and final design.

---

## 2. Layered Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    NeuroFlux Simulation Stack                │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: System-Level / Digital Twin                        │
│           (Coupled EM + Thermal + Structural + Control)      │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: High-Fidelity 3D FEA                               │
│           (Full 3D electromagnetic + multi-physics)          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Medium-Fidelity 2D/Quasi-3D FEA                    │
│           (Fast 2D or quasi-3D finite element)               │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Fast Analytical / Quasi-3D Analytical Engine       │
│           (MEC + Analytical models — milliseconds per eval)  │
├─────────────────────────────────────────────────────────────┤
│  Layer 0: Geometry & Parameter Engine                        │
│           (Parametric generator for all supported topologies)│
└─────────────────────────────────────────────────────────────┘
```

Each layer can call lower layers and should expose clean **input → output contracts**.

---

## 3. Layer Descriptions & Recommended Engines

### Layer 0: Geometry & Parameter Engine
- **Purpose**: Generate consistent geometry, mesh parameters, and material definitions for any supported topology (slotted AFPM, coreless, YASA, multi-stage, etc.).
- **Recommended Tools**:
  - Parametric Python (CadQuery / OpenCascade)
  - Integration with `gbroques/openafpm-cad-core` concepts
  - Future: Link to MagGen-style manufacturing-aware generators

### Layer 1: Fast Analytical / Quasi-3D Analytical Engine (Primary Exploration Layer)
- **Purpose**: Millisecond-to-second evaluations for design space exploration and optimization.
- **Core Technologies**:
  - Quasi-3D Magnetic Equivalent Circuit (inspired by **Parviainen 2005** + **Hemeida 2019**)
  - Analytical air-gap field models (Hague’s solution, Fourier-Bessel for coreless)
  - Multi-slice torque, loss, and inductance calculation
- **Supported Topologies** (to be expanded):
  - Surface-mounted slotted AFPM (DSSR)
  - Coreless AFPM (SSDR and multi-stage)
  - YASA / segmented armature (future)
- **Output Contract**: Torque, back-EMF, losses, efficiency, flux densities, inductances, rough thermal estimates.

### Layer 2: Medium-Fidelity 2D / Quasi-3D FEA
- **Purpose**: Higher accuracy than pure analytical when needed (e.g., during optimization refinement).
- **Recommended Engines**:
  - **FEMM** + `pyfemm` automation (very fast for 2D magnetics)
  - Quasi-3D workflows in Elmer or GetDP
- **Use Cases**: Validation of Layer 1 results, detailed loss maps, cogging torque studies.

### Layer 3: High-Fidelity 3D FEA
- **Purpose**: Final validation and complex multi-physics studies.
- **Recommended Engines**:
  - **Elmer FEM** (excellent multi-physics coupling: EM + thermal + structural)
  - Commercial tools when needed (for comparison)
- **Use Cases**: 3D end-effects, thermal hotspots, structural deflection under load, full transient analysis.

### Layer 4: System-Level / Digital Twin
- **Purpose**: Coupled simulation of the complete system (machine + power electronics + control + thermal management).
- **Future Integration**:
  - Link to Parakram digital twin runtime
  - Real-time capable reduced-order models (ROM) derived from higher layers

---

## 4. Engine Interface Philosophy (Critical)

Every simulation component must behave like a **clean engine**:

**Example Contract (Layer 1 Analytical Engine):**

**Input:**
```json
{
  "topology": "DSSR_surface_mounted",
  "dimensions": { "D_out": 0.52, "k_D": 0.6, ... },
  "materials": { "PM_grade": "N42", "steel_grade": "M600-50A" },
  "winding": { "turns": 60, "phases": 3, ... },
  "operating_point": { "speed_rpm": 300, "current_rms": 94 }
}
```

**Output:**
```json
{
  "torque_nm": 1752.3,
  "back_emf_rms": 218.4,
  "efficiency": 0.916,
  "losses": { "copper_w": 4100, "iron_w": 420, ... },
  "max_flux_density": { "teeth": 1.81, "yoke": 1.16 },
  "computation_time_ms": 87
}
```

This philosophy allows:
- Easy swapping of engines
- Training of surrogate/ML models on top
- Clean orchestration and parallel evaluation

---

## 5. Fidelity Selection Strategy

| Phase                    | Recommended Layer | Reason |
|--------------------------|-------------------|--------|
| Design Space Exploration | Layer 1 (Analytical) | Speed — evaluate 10,000+ candidates |
| Optimization Loop        | Layer 1 + occasional Layer 2 | Balance speed and accuracy |
| Detailed Analysis        | Layer 2 / Layer 3 | When analytical assumptions break |
| Final Validation         | Layer 3 | Highest confidence before prototyping |
| Invention Discovery      | Layer 1 (broad) → Layer 3 (promising candidates) | Efficient discovery |

---

## 6. Implementation Roadmap (Autonomous Decision)

**Phase 1 (Current):**
- Implement robust **Layer 1 Quasi-3D Analytical Engine** (Python) based on Parviainen + Hemeida methods.
- Support both slotted and coreless AFPM.
- Define clean input/output contracts.

**Phase 2:**
- Build Layer 0 parametric geometry generator.
- Create automated comparison harness (Analytical vs FEMM vs Elmer).

**Phase 3:**
- Integrate surrogate modeling (ANN / Gaussian Process) trained on Layer 1 + Layer 2 data for ultra-fast evaluation.
- Add thermal and basic structural models into Layer 1.

**Phase 4:**
- Full multi-fidelity orchestration layer (decide which fidelity to run based on uncertainty or stage in optimization).

---

## 7. Connection to Existing Tools & Repos

| Tool / Repo              | Recommended Role in Stack          | Integration Type     |
|--------------------------|------------------------------------|----------------------|
| PYLEECAN                 | Strong candidate for Layer 2/3     | Python API / Engine  |
| FEMM + pyfemm            | Excellent Layer 2 engine           | Direct automation    |
| Elmer / Gmsh / GetDP     | Primary Layer 3 multi-physics      | Scripted workflows   |
| openafpm-cad-core        | Geometry inspiration for Layer 0   | Reference / partial integration |
| MagGen                   | Manufacturing-aware geometry       | Future Layer 0 extension |

---

## 8. Key Success Metrics for the Simulation Stack

- Layer 1 evaluation time < 200 ms per candidate (target).
- Analytical vs 3D FEA torque error < 5–8% on validation set.
- Clean, documented input/output contracts for every engine.
- Ability to automatically escalate from Layer 1 → Layer 3 when uncertainty is high.

---

**This document establishes the simulation philosophy for NeuroFlux.**

It will be updated as the platform evolves.

**End of Document v1.0**