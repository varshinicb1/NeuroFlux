# NeuroFlux Engineering Intelligence Platform
## Mission: AlphaFold for Engineering Design - Initial AFPM Focus

**Principal Investigator Agent:** Grok (as Principal Research Scientist, Systems Engineer, Electrical Machine Expert, Patent Analyst, Computational Physicist, Autonomous Discovery Agent)

**Date:** 2026-05-30
**User Context:** Varshini (Vidyuthlabs / Parakram unification) - Bengaluru, India. Existing strengths in embedded systems, physics digital twins (EIS-RV), full-stack (Rust/Python/TS), hardware (KiCad, ESP32/STM32), AI agents, monorepo unification.

**Ultimate Vision:** An autonomous engineering discovery system that proposes, simulates, optimizes, validates, and helps patent novel electrical machine architectures (starting with AFPM generators), generalizable to motors, power electronics, sensors, energy systems, materials, and embedded control. One-click from high-level requirements (e.g., "direct-drive wind turbine generator 5kW, high efficiency, low cost, manufacturable in India") to simulation-validated, manufacturing-ready, patent-novel design + digital twin + control firmware.

This extends Parakram Studio vision with scientific computing and discovery layer, leveraging existing physics-informed digital twin work in EIS-RV / RĀMAN.

## Deliverables Status (This is v0.1 - Deep Investigation Phase 1)

1. **Repository Intelligence Report** - In progress (see 01_Repository_Intelligence_Report.md)
2. **AFPM State-of-the-Art Report** - Initial version below + detailed in 02_AFPM_State_of_the_Art_Report.md
3. **Patent Landscape Report** - To be generated (03_Patent_Landscape_Report.md)
4. **Simulation Ecosystem Report** - Initial (04_Simulation_Ecosystem_Report.md)
5. **Design Space Map** - Visual + tabular (05_Design_Space_Map.md)
6. **Knowledge Graph** - Foundational nodes/relations defined; implementation pending (06_Knowledge_Graph.md + graph files)
7. **White-Space Opportunity Report** - Core of discovery (07_White_Space_Opportunity_Report.md)
8. **Novel Invention Candidates** - 3-5 initial proposals with rationale (08_Novel_Invention_Candidates.md)
9. **NeuroFlux Architecture Proposal** - Detailed in 09_NeuroFlux_Architecture_Proposal.md
10. **Autonomous Engineering Discovery Roadmap** - Phased plan (10_Roadmap.md)

## Key Initial Findings from Tool-Assisted Investigation (Phase 1)

### AFPM Ecosystem Overview
AFPM machines excel in applications requiring high torque/power density and short axial length: direct-drive wind turbines, in-wheel EV motors, human-powered devices, aerospace, marine. Key advantage over RFPM: higher torque density for given volume in pancake form factor, simpler winding in some topologies, better cooling potential (larger surface).

**Major Topologies Identified (from reviews [web:1], [web:4], [web:6]):**
- **Single Stator Single Rotor (SSSR)**: Simple, but unbalanced axial force.
- **Double Stator Single Rotor (DSSR)**: Common for generators, better flux utilization, balanced forces.
- **Single Stator Double Rotor (SSDR / TORUS)**: Popular, yokeless options.
- **Yokeless and Segmented Armature (YASA)**: High performance, segmented stator teeth, reduced iron losses, modular.
- **Coreless / Air-cored**: No iron stator, lower losses, but larger airgap, lower power factor; good for high speed or low cogging.
- **Multi-stage / Multi-disc**: Stacked for higher power.
- Emerging: Bearingless AFPM, Magnetically Geared AFPM, Combined Radial-Axial flux, Halbach arrays, printed/segmented magnets, SMC (Soft Magnetic Composite) stators for 3D flux.

**Common Challenges (Repeated Bottlenecks):**
- Complex 3D flux paths and end-winding effects make 2D FEM insufficient; requires 3D FEM (computationally expensive).
- High axial forces in single-sided or unbalanced designs → structural challenges, bearing loads, rotor disc deflection.
- Thermal management: Magnets sensitive to temperature (demagnetization risk); concentrated windings + open slots increase rotor losses/harmonics.
- Manufacturing: Precise magnet placement/alignment, stator lamination or SMC pressing for axial flux is harder than radial; cost for prototypes.
- Cogging torque, torque ripple, vibration/noise in direct drive.
- Material costs (NdFeB magnets) and supply chain; interest in ferrite or rare-earth reduced designs.
- Optimization is multi-physics (EM + thermal + structural + acoustic) and multi-objective (efficiency, torque density, cost, manufacturability).

**Mathematical Foundations (First Principles - To be expanded with equations from papers):**
- Maxwell's equations in quasi-static form for low frequency.
- Magnetic circuit modeling for initial sizing (reluctance, MMF, flux).
- Sizing equations: Torque T ~ (π/4) * B * A * D² * L or adapted for axial (D_o³ - D_i³ factors for disc).
- Back-EMF, inductance calculation critical for control.
- Loss models: Copper (skin/proximity in high freq), iron (hysteresis + eddy, Bertotti or Steinmetz), magnet eddy (especially in coreless or high harmonic).
- Thermal: Lumped parameter or FEM, critical for continuous power.
- Structural: Centrifugal (high speed rotors), axial magnetic pull.

**From Repos (Initial):**
- **Eomys/pyleecan**: Mature, large Python framework for multiphysic design/optimization of electrical machines. GUI, many classes for machines, materials, simulations. Interfaces probably to FEMM or internal solvers. **Gap**: Search showed no explicit "axial flux" or AFPM classes in code (may be general or under development; needs deeper audit of Classes/Methods). Strong for radial, synchronous, induction; potential to extend for AFPM. Excellent for unified simulation workflows. Strengths: Community, documentation, optimization hooks. Weakness for this mission: Not AFPM-native out of box, Python-heavy (performance for large 3D?).
- **gbroques/openafpm-cad-core**: Practical FreeCAD-based CAD for AFPM wind turbine generators. Focus on manufacturable designs. Good for geometry generation and perhaps BOM. Complements simulation tools.
- **subatomicglue/maggen**: Hands-on C/OpenSCAD/web tools specifically for AFPM generator design, coil winding automation, production-ready CAD (plasma cut, 3D print, laser). Build notes and resources. Very aligned with "manufacturing-ready outputs". Small but focused and practical. Opportunity: Integrate its designer logic into parametric Python/CadQuery for NeuroFlux.
- **FEMM + automation (pyFEMM etc.)**: Ubiquitous for 2D magnetics. Many community scripts for optimization. Limitation: 2D primarily; AFPM often needs 3D or quasi-3D approximations.
- **Elmer FEM / Gmsh / GetDP / ONELAB**: Powerful open-source multi-physics FEM suite. Gmsh for meshing (Python API excellent for parametric), GetDP for weak form PDE solving (flexible for custom EM formulations), Elmer for coupled thermal/structural. **Key for automation**: Scriptable end-to-end. Steep curve but perfect for discovery pipeline. ONELAB for GUI/parameter studies.
- Other discovered: Various student theses repos, specific AFPM FEM scripts, but fragmented. No dominant "unified AFPM platform".

**Literature Highlights:**
- Multiple high-quality reviews 2022-2026 emphasize topology innovation, surrogate modeling / optimization (genetic algorithms, PSO, Bayesian), thermal management, additive manufacturing potential.
- PINNs and ML surrogates emerging for accelerating FEA in machine design.
- Digital twins for condition monitoring and control of AFPM generators in wind/EV.
- Validation often via prototype testing (back-to-back, dyno) + FEA correlation.

**Patent Trends (Initial Scan Direction):**
- Many on specific stator/rotor configurations (YASA-like segmented, coreless with specific winding), cooling (integrated channels, heat pipes), magnet retention/segmentation to reduce eddy, control algorithms for ripple reduction, manufacturing methods (SMC pressing, printed windings).
- White space likely in: AI-generated novel topologies validated for patentability, integrated sensor + embedded AI for self-optimizing machines, sustainable materials (ferrite + flux concentration), hybrid AFPM with integrated power conversion, topology optimization directly linked to manufacturability constraints (e.g., for Indian MSME production).

## Next Steps in Investigation (Deep Dive Plan)
1. Full recursive directory audit + key file reading for PYLEECAN (Classes for Machine, Simulation, Optimization; mathematical models in Methods).
2. Same for OpenAFPM (FreeCAD Python scripts for geometry), MAGGEN (OpenSCAD params, designer logic).
3. Deep dive Elmer/Gmsh/GetDP automation examples and Python bindings.
4. Targeted paper ingestion: Download/extract equations from key reviews and seminal AFPM papers (use browse or search for PDFs). Build equation database linked to implementations.
5. Google Patents / USPTO / EPO search for AFPM claims graphs. Identify blocking patents vs white space.
6. Build initial knowledge graph (nodes + relations) in JSON/GraphML or Neo4j-like (or simple networkx + viz).
7. Prototype small parametric AFPM geometry generator + mesh + basic analytical model in Python.
8. Identify integration points with Parakram (e.g., visual Blockly designer for machine topology → NeuroFlux backend; digital twin runtime on embedded; OTA for generator controllers).

This platform will challenge assumptions like "AFPM is just like RFPM but axial" by exploiting unique 3D flux, disc geometry for novel cooling/structural/integration, and AI to explore combinatorial topology space humans miss.

**Call to Action for Collaboration:** Provide access to specific papers/patents/repos, hardware specs for target use cases (e.g., your Parakram/EIS-RV related or new generator projects), or priorities (wind? EV? portable power?). We can push initial repo to your GitHub or new neuroflux org.

*Optimizing for depth over speed. This is foundation for months of autonomous discovery.*