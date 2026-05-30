# NeuroFlux

**Engineering Intelligence Platform — AlphaFold for Electrical Machine Design**

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Research%20%26%20Platform%20Foundation-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Research](https://img.shields.io/badge/Focus-AFPM%20Generators%20%7C%20Multi--Physics%20%7C%20Generative%20Design-purple)

> An autonomous engineering discovery system that proposes, simulates, optimizes, validates, and helps patent novel electrical machine architectures — starting with **Axial Flux Permanent Magnet (AFPM) generators**.

**Generalizable to:** Motors • Power Electronics • Sensors • Energy Systems • Materials Discovery • Embedded Control

Part of the **Parakram Studio** / **Vidyuthlabs** ecosystem. Extends physics-informed digital twins (EIS-RV) and visual low-code design with deep scientific computing and AI-driven invention.

---

## Vision

Build the "AlphaFold for Engineering Design" — a system capable of:

- Understanding electrical machines at expert level (physics, simulation, manufacturing, patents)
- Generating novel, patentable architectures
- Running automated multi-physics simulation pipelines
- Optimizing across performance, cost, thermal, structural, and manufacturability
- Producing simulation-ready + manufacturing-ready outputs + digital twins
- One-click from high-level requirements to validated design

**Initial Domain:** AFPM generators (direct-drive wind, EV traction, portable power, etc.)

**Long-term:** Generalize the discovery engine across electrical machines, power electronics, and energy systems.

## Current Status (v0.1 — Engine + Discovery Foundation)

This repository contains the foundational research, analysis, architecture blueprints,
and an initial tested Python implementation of the NeuroFlux engine stack.

### Key Deliverables (Phase 1)

| # | Deliverable | Status | File |
|---|-------------|--------|------|
| 1 | Repository Intelligence Report (PYLEECAN focus) | ✅ | `reports/01_Deep_PYLEECAN_AFPM_Extension_Plan.md` |
| 2 | AFPM State-of-the-Art & Ecosystem | ✅ | `reports/00_Master_Index_and_Vision.md` |
| 3 | White-Space Opportunity Report | ✅ | `reports/07_White_Space_Opportunity_Report.md` |
| 4 | NeuroFlux Architecture Proposal | ✅ | `reports/09_NeuroFlux_Architecture_Proposal.md` |
| 5 | Layer 1 analytical engine + engine wrappers | ✅ | `neuroflux/` |
| 6 | Requirements-to-ranked-candidates discovery workflow | ✅ | `neuroflux/discovery/workflow.py` |

*Additional reports (Patent Landscape, Simulation Ecosystem, Knowledge Graph, Novel Inventions, Roadmap) will be added iteratively.*

## Repository Structure

```
NeuroFlux/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── neuroflux/
│   ├── analytical/      # Quasi-3D, MEC, coreless, Halbach, loss models
│   ├── core/            # Shared data models, materials, engine contracts
│   ├── discovery/       # End-to-end requirements -> ranked candidates workflow
│   ├── engines/         # Analytical, FEMM, Elmer, PYLEECAN, MagGen, OpenAFPM wrappers
│   └── utils/
├── reports/
│   ├── 00_Master_Index_and_Vision.md
│   ├── 01_Deep_PYLEECAN_AFPM_Extension_Plan.md
│   ├── 07_White_Space_Opportunity_Report.md
│   └── 09_NeuroFlux_Architecture_Proposal.md
├── tests/
└── external_repos/      # Optional external engines and reference repositories
```

## Getting Started (Research Use)

1. Clone the repo
   ```bash
   git clone https://github.com/varshinicb1/NeuroFlux.git
   cd NeuroFlux
   ```
2. Install in editable mode and run tests
   ```bash
   pip install -e ".[dev]"
   pytest
   ```
3. Run the first end-to-end discovery workflow
   ```python
   from neuroflux.core.models import AFPMTopology
   from neuroflux.discovery import DesignRequirements, DiscoveryWorkflow

   result = DiscoveryWorkflow().run(
       DesignRequirements(
           target_power_w=250.0,
           target_speed_rpm=600.0,
           target_voltage_v=48.0,
           max_outer_diameter_m=0.32,
           min_efficiency=0.50,
           topology=AFPMTopology.DSSR_SLOTTED,
           num_candidates=4,
       )
   )

   print(result.best_candidate.candidate_id)
   print(result.best_candidate.analytical_result.torque_nm)
   ```
4. Explore the reports in the `reports/` directory for deep analysis of:
   - PYLEECAN architecture and AFPM extension strategy
   - AFPM ecosystem, topologies, challenges, and mathematical foundations
   - White-space opportunities for novel invention
   - Full NeuroFlux system architecture (knowledge graph, agents, physics core, interfaces)

## Roadmap Highlights

- **Phase 1 (Current)**: Knowledge foundation, engine contracts, analytical engine, tested discovery workflow
- **Phase 2**: Parametric AFPM geometry + simulation pipeline prototype (Gmsh + Elmer/GetDP)
- **Phase 3**: Generative agents + patent graph integration
- **Phase 4**: NeuroFlux visual designer integration (Parakram extension) + digital twin runtime
- **Phase 5**: Generalization to motors, power electronics, and full energy systems

See individual reports for detailed phased plans.

## Collaboration & Contribution

This is an active research and platform development effort. Contributions, discussions, and collaborations are welcome — especially in:
- AFPM design, simulation, and manufacturing
- Physics-informed ML / PINNs for machines
- Patent analysis and IP strategy
- Hardware validation and digital twins
- Integration with embedded systems and edge AI

Please open an issue or start a discussion. For deeper involvement (e.g., specific use cases, hardware targets, or joint development), reach out directly.

**Process note**: We follow a rigorous audit-first, preserve-existing-work approach (inspired by agents.md discipline).

## Related Projects

- [Parakram_best](https://github.com/varshinicb1/parakram_best) — Unified embedded/IoT/AI platform (visual designer, agents, physics digital twins)
- [EIS-RV / RĀMAN Studio](https://github.com/varshinicb1) — Physics-informed digital twins for electrochemistry, batteries, and Raman
- PYLEECAN — Electrical machine simulation framework (target for AFPM extension)
- OpenAFPM & MAGGEN — Practical AFPM CAD and build tools

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

*Optimizing for depth over speed. Building what humanity has not yet fully explored in electrical machine design and autonomous engineering discovery.*

**Bengaluru, India • Vidyuthlabs / Parakram**
