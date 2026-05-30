# External Engines Collection for NeuroFlux
## High-Value Open Source Repositories as Modular Engines

**Focus:** Axial Flux Permanent Magnet (AFPM) Low-Speed Generators + Supporting Technologies  
**Philosophy:** Treat each repo as a specialized **engine** — well-defined inputs → useful outputs. NeuroFlux orchestrates them.

**Date:** 2026-05-30

---

## 1. Tier 1 – Highest Priority Engines (Start Here)

These have the strongest potential as first-class engines in NeuroFlux.

| # | Repository | Link | Type | Why It's a Good Engine | Recommended Integration |
|---|------------|------|------|------------------------|-------------------------|
| 1 | **gbroques/openafpm-cad-core** | https://github.com/gbroques/openafpm-cad-core | AFPM Design + FEMM Simulation | Core of OpenAFPM. Contains **MagnAFPM** (parametric design + FEMM simulation for AFPM generators for wind). Excellent input/output potential. | High priority. Wrap as `OpenAFPM_Engine`. Use for design generation + basic simulation. |
| 2 | **subatomicglue/maggen** | https://github.com/subatomicglue/maggen | AFPM CAD + Manufacturing | Parametric OpenSCAD designer for rotors, stators, coil tools, molds. Plus coilbot hardware. Strong DFM focus. | Wrap `maggen.scad` calls as engine. Extract manufacturing constraints. |
| 3 | **pwspen/autocoil** | https://github.com/pwspen/autocoil | PCB Stator Winding Generator | Generates multi-layer PCB stators for axial flux machines programmatically. | Clean Python engine. Direct integration or thin wrapper. |
| 4 | **dairykillsme/AxialFluxPCB** | https://github.com/dairykillsme/AxialFluxPCB | FEMM + PCB + Optimization | Working FEMM automation for axial flux + PCB stator + EMF calculation + optimization loop. | Extract patterns + wrap simulation functions as engine. |
| 5 | **ziteh/pcb-motor** | https://github.com/ziteh/pcb-motor | PCB Axial Flux Motor | PCB stator axial flux PMSM/BLDC motor designs (inspired by sabanekko3 and Carl Bugeja). | Hardware + geometry reference. Potential for PCB engine. |

---

## 2. Tier 2 – Strong Supporting Engines

| # | Repository | Link | Type | Value | Notes |
|---|------------|------|------|-------|-------|
| 6 | **offbyfour/Motor_Axial_Flux** | https://github.com/offbyfour/Motor_Axial_Flux | Open Source Axial Flux Motor | Full open source axial flux motor project (mechanical + possibly electrical). | Good for complete machine examples and validation cases. |
| 7 | **NickelKnock/Axial-Motor-Design-Calculator** | https://github.com/NickelKnock/Axial-Motor-Design-Calculator | Parametric Calculator | Works backwards from application requirements to design high-performance axial flux motors. | Excellent for early-stage requirement-to-geometry engine. |
| 8 | **dazzor/3dPrintedAxialFluxMotor** | https://github.com/dazzor/3dPrintedAxialFluxMotor | 3D Printed AF Motor | Practical 3D printed axial flux motor build with documentation. | Useful for manufacturing recipes and low-cost prototyping engine. |

---

## 3. Tier 3 – Niche / Reference Engines

- **gbroques/openafpm-cad-visualization** — https://github.com/gbroques/openafpm-cad-visualization  
  Visualization companion to openafpm-cad-core. Useful for output rendering engine.

- **sabanekko3/pcb_stator_v2** (and related Carl Bugeja inspired work) — Strong influence on many PCB stator projects. Reference for winding patterns.

- KiCad parametric PCB stator plugins (community efforts) — Potential future engine for automated PCB layout generation.

---

## 4. Recommended Engine Categories for NeuroFlux

| Category | Purpose | Example Engines | Priority |
|----------|---------|------------------|----------|
| **Electromagnetic Simulation** | Accurate field, EMF, torque, loss calculation | PYLEECAN (MagElmer), OpenAFPM (MagnAFPM + FEMM), AxialFluxPCB FEMM scripts | Very High |
| **Parametric Geometry / CAD** | Generate production-ready geometry | MagGen (OpenSCAD), NickelKnock Calculator, offbyfour designs | Very High |
| **PCB Stator Generation** | Automated winding layout for PCB stators | autocoil, ziteh/pcb-motor patterns, KiCad plugins | High |
| **Manufacturing & DFM** | Coil winding, molds, constraints, recipes | MagGen (coilbot + build notes), practical build repos | High |
| **Optimization** | Multi-objective design exploration | OptiAFPM concepts, custom loops around simulation engines | Medium-High |
| **Visualization & Validation** | 3D viewing, result interpretation | openafpm-cad-visualization, ParaView + VTU from Elmer | Medium |

---

## 5. Next Actions (Engine-Based Integration)

1. **Clone Tier 1 repos** into `external_repos/` as submodules or full clones.
2. **Audit priority order**:
   - First: `gbroques/openafpm-cad-core` (MagnAFPM logic)
   - Second: `subatomicglue/maggen`
   - Third: `pwspen/autocoil`
3. **Define Input/Output contracts** for the top 3–4 engines.
4. Create the first **Engine Wrapper** modules under `neuroflux/engines/`.
5. Start building the **Orchestrator** that can call multiple engines in sequence (e.g., Requirements → Geometry Engine → Simulation Engine → Manufacturing Engine).

---

**This collection focuses on repos that can realistically function as engines** rather than just code to copy. The goal is composability — NeuroFlux should be able to call these tools cleanly with parameters and receive structured outputs.

Would you like me to:
- Deep dive into any specific repo from this list (starting with `gbroques/openafpm-cad-core`)?
- Create the **Engine Architecture** document with input/output schemas?
- Prioritize and start wrapping the top engines?

Just say the word.