# NeuroFlux Master Automation System

## World's Best AFPM Generator Design Tool

Complete end-to-end automation with parallel execution, intelligent retries, comprehensive reporting, and zero shortcuts.

---

## Features

### 🚀 Full Automation Pipeline
Single command runs the entire workflow:
1. **Design Discovery** - Autonomous lab finds optimal candidates
2. **Thermal Analysis** - Native 3D FEA with VTK output
3. **3D Validation** - Phase 2 multi-physics validation
4. **External Solvers** - Elmer FEM integration (optional)
5. **CAD Export** - STEP file generation via FreeCAD
6. **Visualization** - ParaView launch for results
7. **Unified Reporting** - Comprehensive markdown + JSON reports

### ⚡ Parallel Execution
- Independent stages run concurrently
- Configurable worker pool (default: 4 workers)
- Automatic dependency resolution
- Thread-safe progress tracking

### 🔄 Intelligent Retry Logic
- Exponential backoff (2^n seconds)
- Configurable max retries (default: 2)
- Per-stage retry tracking
- Graceful degradation on failure

### 📊 Real-Time Progress Tracking
- Live stage status updates
- ETA calculation based on historical data
- Weighted progress percentages
- Callback registration for custom UIs

### 📈 Comprehensive Reporting
- Executive summary with pass/fail assessment
- Stage-by-stage performance metrics
- Design performance vs. targets
- Thermal analysis results
- 3D validation confidence levels
- Tool utilization report
- Artifact inventory
- Next steps recommendations

---

## Usage

### Full Automation
```bash
# Complete pipeline with all features
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

### Quick Design
```bash
# Basic design without external tools
python -m neuroflux.lab.cli auto \
  --name quick-design \
  --target-power-w 250 \
  --output my_designs
```

### Individual Commands
```bash
# Check tool availability
python -m neuroflux.lab.cli tool-check --verbose

# Visualize existing design
python -m neuroflux.lab.cli visualize design_runs/my-design --type all

# Export CAD from existing design
python -m neuroflux.lab.cli export-cad design_runs/my-design --component both -o output.step
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Discovery  │  │Thermal/FEA  │  │  3D Valid.  │  Sequential │
│  │   (req'd)   │→ │   (req'd)   │→ │   (req'd)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         ↓                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │Visualize    │  │  CAD Export │  │   Reporting │  Parallel   │
│  │(optional)   │  │ (optional)  │  │   (req'd)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
              Unified Report (JSON + Markdown)
```

---

## API Usage

### Python API
```python
from neuroflux.automation import (
    MasterOrchestrator,
    AutomationConfig,
)
from neuroflux.design.engine import AFPMGeneratorSpec

# Configure
config = AutomationConfig(
    run_external_solvers=True,
    run_cad_export=True,
    run_visualization=True,
    max_workers=8,
)

# Define spec
spec = AFPMGeneratorSpec(
    name="my-generator",
    target_power_w=500,
    target_speed_rpm=800,
    target_voltage_v=48,
    run_3d_validation=True,
)

# Run automation
orchestrator = MasterOrchestrator(config)
result = orchestrator.run(spec, run_id="my_run")

# Check results
print(f"Success: {result.success}")
print(f"Duration: {result.duration_seconds:.2f}s")
print(f"Output: {result.output_directory}")
print(f"Report: {result.output_directory / 'automation_report.md'}")

# Stage breakdown
for name, stage in result.stages.items():
    print(f"  {name}: {stage.status.name} ({stage.duration_ms:.0f}ms)")
```

---

## Configuration

### Environment Variables
```bash
# External tool paths (auto-detected if not set)
export NEUROFLUX_ELMER_SOLVER="/path/to/ElmerSolver"
export NEUROFLUX_ELMER_GUI="/path/to/ElmerGUI"
export NEUROFLUX_GMSH="/path/to/gmsh"
export NEUROFLUX_FREECAD="/path/to/FreeCAD"
export NEUROFLUX_PARAVIEW="/path/to/paraview"
```

### AutomationConfig Options
| Option | Default | Description |
|--------|---------|-------------|
| `max_workers` | 4 | Parallel execution workers |
| `enable_parallel` | True | Enable parallel stages |
| `retry_failed` | True | Retry failed stages |
| `max_retries` | 2 | Max retries per stage |
| `run_discovery` | True | Run design discovery |
| `run_thermal_analysis` | True | Run thermal analysis |
| `run_3d_validation` | True | Run 3D validation |
| `run_external_solvers` | False | Run Elmer/Palace |
| `run_visualization` | False | Auto-launch ParaView |
| `run_cad_export` | False | Export STEP files |
| `validation_refinement` | "medium" | Mesh refinement level |

---

## Output Structure

```
design_automation/
└── my-generator/
    ├── automation_report.md       # Human-readable report
    ├── automation_report.json     # Machine-readable report
    ├── design_manifest.json       # Design specification
    ├── design_report.md           # Design details
    ├── geometry.geo               # Gmsh geometry file
    ├── assembly.scad              # OpenSCAD assembly
    ├── assembly.stl               # Inspection mesh
    ├── viewer.html                # 3D web viewer
    ├── thermal_analysis.json      # Thermal results
    ├── parameters.csv             # Parameter table
    ├── scene3d.json               # 3D scene data
    ├── lab/                       # Autonomous lab outputs
    ├── validation/                # 3D validation results
    │   ├── thermal_fea3d/
    │   │   └── thermal_fea3d.vtk  # VTK thermal results
    │   └── solver_handoffs/
    │       └── elmer_case/        # Elmer input files
    └── cad_export/                # STEP files (if requested)
        ├── stator.step
        └── rotor.step
```

---

## Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Automation Tests Only
```bash
python -m pytest tests/test_automation.py -v
```

### Test Coverage
- **66 tests** covering all modules
- **23 automation-specific tests**
- Parallel execution tests
- Retry logic tests
- Progress tracking tests
- Report generation tests
- Error handling tests

---

## Performance

Typical execution times (coarse refinement):
| Stage | Duration |
|-------|----------|
| Discovery | 3-8s |
| Thermal Analysis | 1-2s |
| 3D Validation | 2-5s |
| External Solvers (Elmer) | 10-15s |
| CAD Export | 5-10s |
| **Total** | **15-40s** |

Parallel execution reduces total time by ~30% when visualization and CAD export are enabled.

---

## Error Handling

### Retry Strategy
1. First failure: Immediate retry
2. Second failure: Wait 2s, then retry
3. Third failure: Wait 4s, then retry
4. Final failure: Mark stage as FAILED, continue if possible

### Graceful Degradation
- External tools missing → Skip stage, warn user
- Discovery fails → Stop pipeline, report error
- Thermal analysis fails → Stop pipeline
- Validation fails → Continue but flag in report
- CAD export fails → Continue, note in report

---

## Tool Integration Status

| Tool | Detection | Integration | Status |
|------|-----------|-------------|--------|
| ElmerSolver | ✅ Auto | ✅ Full | Ready |
| ElmerGUI | ✅ Auto | ✅ Launch | Ready |
| Gmsh | ✅ Auto | ✅ Meshing | Ready |
| FreeCAD | ✅ Auto | ✅ STEP Export | Ready |
| ParaView | ✅ Auto | ✅ Visualization | Ready |

---

## Roadmap

### Completed ✅
- [x] Master orchestrator with parallel execution
- [x] Intelligent retry logic with exponential backoff
- [x] Real-time progress tracking with ETA
- [x] Comprehensive unified reporting (JSON + Markdown)
- [x] CAD export automation (FreeCAD)
- [x] Visualization automation (ParaView)
- [x] Full CLI integration
- [x] Complete test coverage (66 tests)

### Future Enhancements
- [ ] Palace solver integration
- [ ] Web-based progress dashboard
- [ ] Batch design optimization
- [ ] Cloud execution support
- [ ] Machine learning result prediction

---

## License

NeuroFlux - World's Best AFPM Generator Design Tool
© 2024 NeuroFlux Project
