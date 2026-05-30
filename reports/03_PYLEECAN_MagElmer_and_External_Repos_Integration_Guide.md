# PYLEECAN MagElmer & External Repos Integration Guide
## For NeuroFlux AFPM Low-Speed Generator Development

**Version:** 0.1  
**Date:** 2026-05-30  
**Context:** NeuroFlux Engineering Intelligence Platform – AFPM Low-Speed Generator focus  
**Audience:** AI Agents + Human Engineers working under `agents.md` discipline

---

## 1. Executive Summary

This document provides a **rigorous integration guide** for using **PYLEECAN** (especially `MagElmer`) and selected high-value external repositories as the foundation for NeuroFlux’s physics simulation and geometry capabilities for **Axial-Flux Permanent-Magnet Low-Speed Generators**.

**Core Principle (agents.md):**  
Audit → Categorize → Understand → Integrate (do not delete or break existing work). Prefer extension, subclassing, and thin adapters over forking or heavy modification.

**Key Repositories Identified:**

| Repository | Type | Value for NeuroFlux | Recommendation |
|------------|------|---------------------|----------------|
| [Eomys/pyleecan](https://github.com/Eomys/pyleecan) | Core Framework | Mature multi-physics platform with `MagElmer` | **Primary target** – Extend for AFPM |
| [dairykillsme/AxialFluxPCB](https://github.com/dairykillsme/AxialFluxPCB) | FEMM + PCB + Optimization | Working FEMM automation + PCB stator generation + EMF calculation | High – Study patterns, extract ideas |
| [pwspen/autocoil](https://github.com/pwspen/autocoil) | Python PCB Stator Generator | Programmatic multi-layer PCB stator generation | High – Strong candidate for integration |
| [subatomicglue/maggen](https://github.com/subatomicglue/maggen) | Manufacturing Tools | Practical AFPM design + fabrication knowledge | Medium-High – Reference for manufacturing constraints |
| Others (see Section 4) | Various | Niche value | Study case-by-case |

---

## 2. PYLEECAN `MagElmer` Deep Analysis

### 2.1 Location & Structure

- **Main Class**: `pyleecan/Classes/MagElmer.py` (~34k lines)
- **Supporting Classes**:
  - `pyleecan/Classes/Elmer.py`
  - `pyleecan/Classes/OutMagElmer.py`
  - `pyleecan/Classes/ElmerResults.py` + `ElmerResultsVTU.py`
  - `pyleecan/Classes/StructElmer.py` (for multi-physics coupling)
- **Methods**: Located under `pyleecan/Methods/Simulation/MagElmer/`

### 2.2 How `MagElmer` Works (High-Level Flow)

1. **Geometry** → Uses PYLEECAN’s existing `build_geometry()` system (mostly radial-oriented)
2. **Meshing** → Gmsh (via `MeshMat` or direct calls) → `.geo` / `.msh`
3. **Solver Input** → Generates Elmer `.sif` files
4. **Execution** → `ElmerGrid` + `ElmerSolver`
5. **Results** → Reads VTU files → Populates `OutMagElmer`

### 2.3 Strengths

- Clean integration with PYLEECAN’s `Simulation`, `VarOpti`, and output hierarchy
- Supports multi-physics (can couple with structural solver)
- Modern output format (VTU / ParaView)
- Part of a mature, actively maintained framework

### 2.4 Limitations for AFPM Low-Speed Generators

- Geometry system is heavily biased toward **radial-flux** machines
- Limited native **3D** support for disc-type geometries
- No built-in **axial force** calculation (critical for AFPM)
- Post-processing is not optimized for axial flux phenomena (end effects, disc magnet eddy currents, etc.)
- 3D meshing and solver setup is less mature than the 2D path

### 2.5 Strategic Recommendation

**Do not fork PYLEECAN.**  
Instead:
- Create new AFPM-specific geometry classes (or extend existing ones with an `is_axial` flag / new topology classes)
- Extend `MagElmer` with AFPM-specific methods (`comp_axial_force`, AFPM post-processing, 3D mesh strategies)
- Add new `MachineAFPM_*` classes following PYLEECAN’s generator pattern
- Keep all changes **additive** and upstream-contributable

---

## 3. Recommended Integration Architecture

```
NeuroFlux / parakram_best
├── neuroflux/
│   ├── simulation/
│   │   ├── pyleecan_adapter/          # Thin wrappers + extensions
│   │   ├── afpm_geometry/             # New AFPM parametric geometry
│   │   ├── elmer_3d/                  # Custom 3D Elmer workflows
│   │   └── femm_reference/            # Extracted patterns from external repos
│   ├── manufacturing/
│   │   └── maggen_reference/          # Manufacturing constraints & ideas
│   └── knowledge_graph/               # Nodes for repos, papers, methods
└── docs/
    └── reports/                       # This and other analysis documents
```

**Rule for Agents:**
- Never modify core PYLEECAN files directly in the first pass.
- Create **adapter / extension modules** that import from PYLEECAN.
- Document every decision in the knowledge graph or decision log.

---

## 4. Key External Repositories & Source Links

### Tier 1 – High Priority (Study & Extract)

| Repo | Link | Why Useful | Agent Action |
|------|------|------------|--------------|
| **dairykillsme/AxialFluxPCB** | https://github.com/dairykillsme/AxialFluxPCB | Working FEMM automation for axial flux + PCB stator + EMF calculation + optimization | Deep audit `Alternator.py` and `Alternator2DSimulation.py`. Extract patterns for geometry + simulation loop. |
| **pwspen/autocoil** | https://github.com/pwspen/autocoil | Python code that generates multi-layer PCB stators for axial flux motors | High priority for NeuroFlux geometry agent. Study how it parametrizes windings. |
| **subatomicglue/maggen** | https://github.com/subatomicglue/maggen | Practical manufacturing tools, coil winding automation ideas, multi-process fabrication notes | Reference for manufacturing constraints in optimization. |

### Tier 2 – Useful References

- [sabanekko3/pcb_stator_v2](https://github.com/sabanekko3/pcb_stator_v2) – Influential PCB stator work
- [Eomys/pyleecan](https://github.com/Eomys/pyleecan) – Core framework (primary)
- [gbroques/openafpm-cad-core](https://github.com/gbroques/openafpm-cad-core) – FreeCAD-based AFPM CAD

---

## 5. Instructions for AI Agents (agents.md Compliant)

### 5.1 Cloning Repositories

**Never clone directly into the main working tree without approval.**

Recommended safe pattern:

```bash
# Create a dedicated external_repos directory (do not put inside src/)
mkdir -p /path/to/neuroflux/external_repos
cd /path/to/neuroflux/external_repos

# Clone with depth limit for speed (you can deepen later)
git clone --depth 1 https://github.com/Eomys/pyleecan.git
git clone --depth 1 https://github.com/dairykillsme/AxialFluxPCB.git
git clone --depth 1 https://github.com/pwspen/autocoil.git
git clone --depth 1 https://github.com/subatomicglue/maggen.git
```

### 5.2 Audit Process (Mandatory)

Before using any code from these repos, every agent **must**:

1. Read the full `README.md`
2. Explore the directory tree
3. Identify the core files related to geometry / simulation / manufacturing
4. Read and understand the key implementation files
5. Document findings in `neuroflux/knowledge_graph/` or a decision log
6. **Never delete or overwrite** any existing PYLEECAN or NeuroFlux code without explicit approval

### 5.3 How to Use as Modules (Recommended Patterns)

**Preferred Approach: Thin Adapters + Extraction**

Do **not** import large external codebases directly into production paths.

Instead:

```python
# Example: neuroflux/simulation/femm_reference/afpm_femm_patterns.py

"""
Extracted and adapted patterns from dairkillsme/AxialFluxPCB
Original source: https://github.com/dairykillsme/AxialFluxPCB
License: [check original repo]
"""

import femm
from typing import Dict

def create_afpm_femm_model(params: Dict):
    """Adapted from Alternator.py simulate() method"""
    femm.openfemm()
    # ... your cleaned/adapted implementation ...
    femm.closefemm()
```

**Alternative (when appropriate):**  
Add the external repo as a **git submodule** under `external_repos/` with clear documentation.

### 5.4 Contribution Back Strategy

After validation:
- Prepare clean, well-documented improvements
- Open issues or PRs to the original repositories where beneficial
- Credit original authors in NeuroFlux code and documentation

---

## 6. Immediate Recommended Actions

1. **Clone** the four Tier-1 repositories following the instructions above.
2. **Audit** `dairykillsme/AxialFluxPCB` first (highest immediate value).
3. **Audit** PYLEECAN’s `MagElmer.py` and related Elmer files.
4. Create the first **AFPM geometry adapter** module.
5. Update the NeuroFlux Knowledge Graph with findings.

---

**This document should be treated as living.** Update it as new understanding is gained.

*Built following the rigorous audit-first, preserve-existing-work philosophy.*