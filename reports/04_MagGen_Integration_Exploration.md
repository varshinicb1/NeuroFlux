# MagGen Integration Exploration Report
## Practical Manufacturing & Design Tools for Axial Flux Generators

**Repository:** https://github.com/subatomicglue/maggen  
**Explored:** 2026-05-30  
**Relevance to NeuroFlux:** High (Manufacturing + Design for Manufacturability)  
**Status:** Recommended for integration / reference layer

---

## 1. Executive Summary

**MagGen** is a practical, maker-oriented toolkit specifically built for **designing and fabricating Axial Flux Permanent Magnet (AFPM) generators**. 

While PYLEECAN excels at **physics simulation** (FEMM/Elmer), MagGen focuses on the **downstream manufacturing pipeline** — generating production-ready CAD, coil winding tools, molds, and even a physical coil winding robot.

This makes it highly complementary to NeuroFlux’s long-term vision of an autonomous engineering system that goes from **intent → validated design → manufacturing-ready outputs**.

**Key Value for NeuroFlux:**
- Parametric design tools tailored to AFPM topologies
- Strong emphasis on **design for manufacturability** (DFM)
- Coil winding automation concepts (reproducibility is critical for AFPM)
- Real-world build notes and engineering constraints

---

## 2. Repository Structure & Components

```
maggen/
├── designer/              # Core design tools
│   ├── maggen.scad        # Main 3D parametric model (OpenSCAD)
│   ├── index.html         # Live 2D web-based designer
│   ├── canvas.js / math.js / svg.js
│   └── examples/
├── coilbot/               # Coil winding robot hardware
│   ├── *.stl              # 3D printable parts
│   ├── *.scad             # Custom mechanical parts
│   ├── *.svg              # Laser-cut templates
│   └── README.md
├── build_notes/           # Engineering documentation
├── pics/
├── README.md
└── LICENSE
```

---

## 3. Detailed Component Analysis

### 3.1 MAGGEN:designer

**Location:** `designer/`

**Components:**
- **`maggen.scad`** (24k+ lines): The heart of the 3D parametric designer. Generates rotors, stators, coil winding tools, epoxy molds, plasma-cut iron discs, laser-cut parts, and 3D-printable components.
- **2D Web App** (`index.html` + supporting JS): Simple live parametric designer for quick 2D shapes. Useful for rapid iteration.
- Strong focus on **multiple manufacturing processes** in one tool (3D print, laser cut, plasma cut, etc.).

**Strengths:**
- Specifically built for AFPM generators (not generic CAD)
- Practical output formats for real fabrication
- OpenSCAD-based → scriptable and version-controllable

**Limitations:**
- Not integrated with modern simulation tools (no direct link to PYLEECAN/Elmer/FEMM)
- 2D web app is relatively basic
- OpenSCAD has known limitations for complex parametric geometry compared to CadQuery or build123d

**Integration Potential:** **High**  
Can serve as inspiration/reference for NeuroFlux’s manufacturing output layer. We can extract parametric logic or use it as a reference implementation for AFPM-specific DFM rules.

### 3.2 MAGGEN:coilbot

**Location:** `coilbot/`

A physical **coil winding robot** designed for reproducible production of magnetic coils used in AFPM machines.

**Contents:**
- 3D printable mechanical parts (STL files)
- OpenSCAD source for custom components (screw, shaft coupler, etc.)
- SVG templates for laser-cut enclosures
- Documentation and photos

**Why This Matters for NeuroFlux:**
Reproducibility of coil winding is one of the biggest practical challenges in AFPM generator manufacturing. Automated or semi-automated winding directly supports the goal of moving from simulation to **production-ready hardware**.

**Integration Potential:** **Medium-High**  
- Extract design principles and constraints for the manufacturing agent
- Use as reference when building NeuroFlux’s future "manufacturing recipe" generator
- Not recommended to directly integrate hardware control code (different domain), but the **mechanical design logic** is valuable

### 3.3 Build Notes

**Location:** `build_notes/`

Contains engineering notes, design guidelines, and lessons learned from building AFPM generators. This is "tribal knowledge" captured in documentation — extremely valuable for an autonomous system.

**Integration Potential:** **High**  
These notes should be ingested into NeuroFlux’s **Knowledge Graph** as manufacturing constraints, rules of thumb, and failure modes to avoid.

---

## 4. Strategic Value for NeuroFlux

| Area                        | MagGen Contribution                          | NeuroFlux Opportunity                     | Priority |
|----------------------------|----------------------------------------------|-------------------------------------------|----------|
| **Parametric Geometry**    | AFPM-specific OpenSCAD models                | Reference for AFPM geometry classes       | High     |
| **Design for Manufacturability** | Multi-process output (3D print, laser, plasma) | Manufacturing constraint engine           | High     |
| **Coil Winding**           | Physical coilbot + reproducibility focus     | Future manufacturing automation layer     | Medium   |
| **Engineering Knowledge**  | Build notes & practical constraints          | Knowledge Graph ingestion                 | High     |
| **Simulation Coupling**    | None (separate concern)                      | Opportunity to bridge simulation ↔ manufacturing | High     |

**Core Insight:**  
MagGen represents the **"last mile"** of the engineering pipeline that most simulation tools ignore. NeuroFlux should aim to close this gap.

---

## 5. Recommended Integration Approach (agents.md Compliant)

### 5.1 Do **NOT** do:
- Fork the entire MagGen repo into the main codebase
- Directly import OpenSCAD generation logic without audit
- Treat coilbot hardware control as part of the core simulation platform

### 5.2 Recommended Pattern:

1. **Clone for reference** (under `external_repos/maggen/`)
2. **Audit** the following files deeply:
   - `designer/maggen.scad`
   - `designer/README.md`
   - `coilbot/README.md`
   - Files in `build_notes/`
3. **Extract & Abstract**:
   - Manufacturing constraints and rules
   - Parametric relationships specific to AFPM
   - Coil geometry parameters
4. **Create thin adapters** in `neuroflux/manufacturing/`:
   - `dfm_rules.py` (inspired by MagGen)
   - `coil_geometry.py` (reference implementation)
5. **Ingest knowledge** into the NeuroFlux Knowledge Graph

### 5.3 Cloning Instructions (Safe)

```bash
mkdir -p external_repos
cd external_repos
git clone --depth 1 https://github.com/subatomicglue/maggen.git
```

Then follow the standard audit process before using any content.

---

## 6. Next Steps

1. Perform a **deeper code audit** of `designer/maggen.scad` (focus on AFPM parametric logic)
2. Extract key manufacturing constraints into a structured format for the Knowledge Graph
3. Evaluate whether to create a **CadQuery / build123d** re-implementation of the most useful MagGen geometry generators (cleaner Python integration)
4. Decide on long-term strategy: Reference-only vs. Active inspiration for NeuroFlux manufacturing module

---

**Conclusion:**

MagGen is one of the most relevant external repositories for the **manufacturing and DFM** aspects of NeuroFlux. While it is not a simulation tool, it fills a critical gap that pure physics platforms like PYLEECAN do not address. It should be treated as a **high-value reference and inspiration source** during the development of NeuroFlux’s geometry and manufacturing layers.

*Report generated following rigorous exploration and agents.md principles.*