# NeuroFlux ⚡

**Engineering Intelligence Platform — AlphaFold for Electrical Machine Design**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Research%20%26%20Platform%20Foundation-orange)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-66%20passing-brightgreen)]()
[![Code](https://img.shields.io/badge/Code-64%20modules-informational)]()
[![Reports](https://img.shields.io/badge/Reports-23%20docs-blueviolet)]()
[![Research](https://img.shields.io/badge/Focus-AFPM%20Generators%20%7C%20Multi--Physics%20%7C%20Generative%20Design-purple)]()
[![Made with Love](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20in%20Bengaluru-red)](https://vidyuthlabs.com)

> 🚀 An autonomous engineering discovery system that proposes, simulates, optimizes, validates, and helps patent novel electrical machine architectures — starting with **Axial Flux Permanent Magnet (AFPM) generators**.

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

---

## Current Status (v0.1 — Unified Design Engine Foundation)

This repository contains the foundational research, analysis, architecture blueprints,
and a tested Python + Rust implementation of the first NeuroFlux design stack.

### Key Deliverables (Phase 1)

| # | Deliverable | Status | File |
|---|-------------|--------|------|
| 1 | Repository Intelligence Report (PYLEECAN focus) | ✅ | `reports/01_Deep_PYLEECAN_AFPM_Extension_Plan.md` |
| 2 | AFPM State-of-the-Art & Ecosystem | ✅ | `reports/00_Master_Index_and_Vision.md` |
| 3 | White-Space Opportunity Report | ✅ | `reports/07_White_Space_Opportunity_Report.md` |
| 4 | NeuroFlux Architecture Proposal | ✅ | `reports/09_NeuroFlux_Architecture_Proposal.md` |
| 5 | Layer 1 analytical engine + engine wrappers | ✅ | `neuroflux/` |
| 6 | Requirements-to-ranked-candidates discovery workflow | ✅ | `neuroflux/discovery/workflow.py` |
| 7 | Unified AFPM generator design engine + artifacts | ✅ | `neuroflux/design/engine.py` |
| 8 | Autonomous lab loop with seeded patent knowledge graph | ✅ | `neuroflux/lab/` |
| 9 | Rust desktop dashboard for lab/design manifests | ✅ | `gui/neuroflux-gui/` |
| 10 | **Master Automation System** | ✅ | `neuroflux/automation/` |
| 11 | **CAD Export (STEP)** | ✅ | `neuroflux/cad/` |
| 12 | **3D Visualization (ParaView)** | ✅ | `neuroflux/visualization/` |
| 13 | **Validation Pipeline** | ✅ | `neuroflux/validation/` |
| 14 | **Grand Unified Model** | ✅ | `neuroflux/gum/` |

---

## ✨ Features

### Master Automation System
- **Parallel Execution** — Independent stages run concurrently with configurable workers
- **Intelligent Retry Logic** — Exponential backoff with graceful degradation
- **Real-Time Progress Tracking** — Live stage status with ETA calculation
- **Comprehensive Reporting** — Unified JSON + Markdown reports
- **Tool Integration** — Auto-detection for Elmer, Gmsh, FreeCAD, ParaView

### Design & Discovery
- **End-to-End Workflow** — Requirements → Candidates → Ranked Designs
- **Multi-Physics Analysis** — Analytical, thermal, and 3D FEA validation
- **Multiple Topologies** — DSSR, SSDR, slotted and coreless variants
- **Patent-Aware** — Prior art scoring and novelty assessment

### CAD & Visualization
- **STEP Export** — Manufacturing-ready CAD files via FreeCAD
- **3D Viewer** — Three.js browser-based design inspection
- **VTK Output** — ParaView-compatible thermal analysis results
- **SCAD Assembly** — OpenSCAD-based geometry generation

### GUI & Interfaces
- **Rust Dashboard** — Native egui desktop application
- **Python Web GUI** — Flask-based browser interface
- **CLI Tools** — Complete command-line interface

---

## Repository Structure

```
NeuroFlux/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── AUTOMATION.md          # Master automation system docs
├── smoke_test.py          # Quick validation script
├── neuroflux/
│   ├── analytical/        # Quasi-3D, MEC, coreless, Halbach, loss models
│   ├── automation/        # Master orchestrator, parallel execution
│   ├── cad/               # FreeCAD STEP export
│   ├── core/              # Shared data models, materials, engine contracts
│   ├── design/            # Single-input AFPM generator design package engine
│   ├── discovery/         # End-to-end requirements → ranked candidates workflow
│   ├── engines/           # Analytical, FEMM, Elmer, PYLEECAN, MagGen, OpenAFPM wrappers
│   ├── gum/               # Grand Unified Model for cross-domain modeling
│   ├── lab/               # Autonomous iteration loop, scientist, patent graph
│   ├── validation/        # 3D validation pipeline
│   ├── visualization/     # ParaView integration
│   └── utils/
├── gui/
│   └── neuroflux-gui/     # Rust egui dashboard for lab/design manifests
├── tests/                 # 66+ tests covering all modules
├── reports/               # 23 research & architecture documents
├── evidence_acquisition/  # Mission analysis and architecture synthesis
├── design_automation/     # Generated design outputs
└── external_repos/        # Optional external engines and reference repositories
```

---

## 🚀 Getting Started (Research Use)

### 1. Clone the Repository

```bash
git clone https://github.com/varshinicb1/NeuroFlux.git
cd NeuroFlux
```

### 2. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest -v
```

### 4. Run the Unified AFPM Generator Design Engine

```bash
python -m neuroflux.lab.cli design \
  --output design_runs \
  --name low-speed-250w-afpm-generator \
  --target-power-w 250 \
  --target-speed-rpm 600 \
  --target-voltage-v 48 \
  --max-outer-diameter-m 0.32 \
  --min-efficiency 0.50 \
  --iterations 3 \
  --num-candidates 6 \
  --num-planes 7
```

This writes a complete design package:
- `design_manifest.json`: unified machine-readable output
- `design_report.md`: human-readable engineering report
- `geometry.geo`: Gmsh/OpenCASCADE geometry handoff
- `scene3d.json`: deterministic 3D scene model
- `viewer.html`: Three.js browser viewer for the 3D scene
- `thermal_analysis.json`: lumped steady-state thermal screen
- `parameters.csv`: manufacturing/design parameter table

### 5. Run the Full Automation Pipeline

```bash
python -m neuroflux.lab.cli auto \
  --name my-generator \
  --target-power-w 500 \
  --target-speed-rpm 800 \
  --target-voltage-v 48 \
  --max-diameter-m 0.25 \
  --min-efficiency 0.60 \
  --run-external-solvers \
  --export-cad \
  --visualize \
  --parallel \
  --output design_automation
```

### 6. Run the Rust Desktop Dashboard

```bash
cargo run --manifest-path gui/neuroflux-gui/Cargo.toml -- \
  design_runs/low-speed-250w-afpm-generator/design_manifest.json
```

### 7. Run the Web GUI

```bash
python -m neuroflux.gui.server --port 5000
```

### 8. Run the Lower-Level Discovery Workflow from Python

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

### 9. Explore the Reports

Check the `reports/` directory for deep analysis:
- PYLEECAN architecture and AFPM extension strategy
- AFPM ecosystem, topologies, challenges, and mathematical foundations
- White-space opportunities for novel invention
- Full NeuroFlux system architecture (knowledge graph, agents, physics core, interfaces)

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Discovery  │  │Thermal/FEA  │  │  3D Valid.  │  Sequential │
│  │   (req'd)   │→ │   (req'd)   │→ │   (req'd)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         ↓                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │Visualize    │  │  CAD Export │  │   Reporting │  Parallel    │
│  │(optional)   │  │ (optional)  │  │   (req'd)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
              Unified Report (JSON + Markdown)
```

---

## 🛠️ Tool Integration Status

| Tool | Detection | Integration | Status |
|------|-----------|-------------|--------|
| ElmerSolver | ✅ Auto | ✅ Full | Ready |
| ElmerGUI | ✅ Auto | ✅ Launch | Ready |
| Gmsh | ✅ Auto | ✅ Meshing | Ready |
| FreeCAD | ✅ Auto | ✅ STEP Export | Ready |
| ParaView | ✅ Auto | ✅ Visualization | Ready |
| FEMM | ✅ Auto | ✅ 2D FEA | Ready |

---

## 📈 Roadmap Highlights

- **Phase 1 (Current)**: Knowledge foundation, engine contracts, analytical engine, tested discovery workflow, unified design package engine, master automation system, CAD export, visualization
- **Phase 2**: External-solver-backed Gmsh + Elmer/GetDP 3D validation pipeline
- **Phase 3**: Live patent ingestion, retrieval-backed novelty scoring, and richer design-space exploration
- **Phase 4**: NeuroFlux visual designer integration (Parakram extension) + digital twin runtime
- **Phase 5**: Generalization to motors, power electronics, and full energy systems

See individual reports for detailed phased plans.

---

## 🤝 Collaboration & Contribution

This is an active research and platform development effort. Contributions, discussions, and collaborations are welcome — especially in:
- AFPM design, simulation, and manufacturing
- Physics-informed ML / PINNs for machines
- Patent analysis and IP strategy
- Hardware validation and digital twins
- Integration with embedded systems and edge AI

Please open an issue or start a discussion. For deeper involvement (e.g., specific use cases, hardware targets, or joint development), reach out directly.

**Process note**: We follow a rigorous audit-first, preserve-existing-work approach (inspired by agents.md discipline).

---

## 📚 Related Projects

- [Parakram_best](https://github.com/varshinicb1/parakram_best) — Unified embedded/IoT/AI platform (visual designer, agents, physics digital twins)
- [EIS-RV / RĀMAN Studio](https://github.com/varshinicb1) — Physics-informed digital twins for electrochemistry, batteries, and Raman
- PYLEECAN — Electrical machine simulation framework (target for AFPM extension)
- OpenAFPM & MAGGEN — Practical AFPM CAD and build tools

---

## 📝 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

*Optimizing for depth over speed. Building what humanity has not yet fully explored in electrical machine design and autonomous engineering discovery.*

**Bengaluru, India • Vidyuthlabs / Parakram**
