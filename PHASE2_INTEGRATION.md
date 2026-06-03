# Phase 2: 3D Validation Integration Guide

## Overview

Phase 2 integrates external FEM solvers (Elmer, Palace) with Gmsh meshing for full 3D multi-physics validation of AFPM generator designs.

## Architecture

```
Design Candidate → Gmsh Meshing → Solver Handoffs → External FEM → Results Aggregation
        ↓              ↓                ↓                ↓              ↓
   Geometry       .geo/.msh        .sif/.json      Elmer/Palace   ValidationReport
   Parameters     Mesh files       Case files      3D FEA solve   Confidence scoring
```

## Supported Solvers

### 1. Elmer FEM (Open Source)
- **Website**: https://www.elmerfem.org/
- **Use Cases**: Thermal, electromagnetic, structural multi-physics
- **Input**: `.sif` (Solver Input File), `.geo` (Gmsh geometry)
- **Output**: `.vtu` (VTK unstructured grid)

### 2. Palace (Open Source)
- **Repository**: https://github.com/awslabs/palace
- **Use Cases**: Large-scale electromagnetics, wave propagation
- **Input**: JSON configuration + Gmsh mesh
- **Output**: JSON results + VTK fields

### 3. Gmsh (Meshing)
- **Website**: https://gmsh.info/
- **Use Cases**: Geometry modeling, mesh generation
- **Input**: `.geo` (geometry script)
- **Output**: `.msh` (mesh file)

## Installation

### Windows

```powershell
# Elmer (via installer from elmerfem.org)
# Download and install ElmerFEM-Windows-CI-Release.exe

# Gmsh (via installer or conda)
conda install -c conda-forge gmsh

# FreeCAD (for CAD export)
# Download from freecad.org

# ParaView (for visualization)
# Download from paraview.org

# Palace (build from source - requires PETSc, SLEPc)
# See: https://github.com/awslabs/palace/blob/main/INSTALL.md
```

### Linux (Ubuntu/Debian)

```bash
# Elmer
sudo apt-get install elmerfem-csc

# Gmsh
sudo apt-get install gmsh

# FreeCAD
sudo apt-get install freecad

# ParaView
sudo apt-get install paraview

# Palace (build from source)
git clone https://github.com/awslabs/palace.git
cd palace && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

### macOS

```bash
# Using Homebrew
brew install elmerfem gmsh freecad paraview

# Palace requires manual build
```

## Configuration

### Environment Variables

```bash
# Windows
set NEUROFLUX_ELMER_SOLVER=C:\Program Files\ElmerFEM\bin\ElmerSolver.exe
set NEUROFLUX_ELMER_GUI=C:\Program Files\ElmerFEM\bin\ElmerGUI.exe
set NEUROFLUX_GMSH=C:\Program Files\gmsh\gmsh.exe
set NEUROFLUX_FREECAD=C:\Program Files\FreeCAD\bin\FreeCAD.exe
set NEUROFLUX_PARAVIEW=C:\Program Files\ParaView\bin\paraview.exe

# Linux/macOS
export NEUROFLUX_ELMER_SOLVER=/usr/bin/ElmerSolver
export NEUROFLUX_ELMER_GUI=/usr/bin/ElmerGUI
export NEUROFLUX_GMSH=/usr/bin/gmsh
export NEUROFLUX_FREECAD=/usr/bin/FreeCAD
export NEUROFLUX_PARAVIEW=/usr/bin/paraview
```

### Auto-Detection

NeuroFlux automatically detects installed tools in PATH:

```python
from neuroflux.core.config import ExternalToolConfig

tools = ExternalToolConfig.auto_detect()
tools.print_status()
```

## Usage

### Basic 3D Validation

```bash
# Run with external solvers enabled
python -m neuroflux.lab.cli design \
  --name my-design \
  --target-power-w 500 \
  --run-3d-validation \
  --run-external-solvers \
  --validation-refinement medium
```

### Automation with All Features

```bash
python -m neuroflux.lab.cli auto \
  --name full-validation \
  --target-power-w 1000 \
  --target-speed-rpm 800 \
  --run-external-solvers \
  --export-cad \
  --visualize \
  --parallel
```

### Python API

```python
from neuroflux.design.engine import AFPMGeneratorSpec
from neuroflux.validation import ValidationPipeline, ValidationSpec

# Create design with validation enabled
spec = AFPMGeneratorSpec(
    name="validated-design",
    target_power_w=500,
    run_3d_validation=True,
    run_external_solvers=True,
    validation_refinement="fine",
)

# Run validation pipeline
validation = ValidationSpec(
    name=spec.name,
    geometry=design.geometry,
    materials=design.materials,
    run_elmer_fea=True,
    run_palace=True,
    mesh_refinement="fine",
)

result = ValidationPipeline().run(validation)
print(f"Thermal max: {result.thermal.elmer_thermal_max_c}°C")
print(f"EM torque: {result.electromagnetic.elmer.torque_nm} Nm")
```

## Solver Handoffs

### Generated Files

Each design generates solver handoffs in `validation/<design_name>/solver_handoffs/`:

```
solver_handoffs/
├── elmer_case/
│   ├── case.sif          # Elmer solver input
│   ├── geometry.geo      # Gmsh geometry
│   └── manifest.json     # Metadata
└── palace_case/
    ├── palace.json       # Palace configuration
    ├── geometry.geo      # Gmsh geometry
    └── manifest.json     # Metadata
```

### Running Solvers Manually

```bash
# Elmer
cd validation/my-design/solver_handoffs/elmer_case
ElmerSolver case.sif

# Palace
cd validation/my-design/solver_handoffs/palace_case
palace palace.json
```

## Validation Report

The validation report includes:

- **Thermal Analysis**: Max winding/magnet temperatures, confidence level
- **EM Analysis**: Torque, losses, flux density, efficiency
- **Structural**: Stress, deformation (if enabled)
- **Mesh Statistics**: Element count, quality metrics
- **Solver Comparison**: Analytical vs FEA results

## Troubleshooting

### Solver Not Found

```bash
# Check if in PATH
which ElmerSolver
which gmsh

# Or set explicit path
export NEUROFLUX_ELMER_SOLVER=/path/to/ElmerSolver
```

### Mesh Generation Fails

- Check Gmsh installation: `gmsh -version`
- Verify geometry file syntax
- Try coarser refinement level

### Elmer Solver Errors

- Check `.sif` file syntax
- Verify material properties
- Review `elmeroutput.log` for details

### Palace Build Issues

- Ensure PETSc and SLEPc are installed
- Use MPI-enabled build for parallel solves
- Check https://github.com/awslabs/palace/issues for known issues

## Performance Benchmarks

| Solver | Mesh Size | Solve Time | Memory |
|--------|-----------|------------|--------|
| Analytical | N/A | 0.1s | 10MB |
| Native FEA3D | 10k elements | 2s | 100MB |
| Elmer (thermal) | 100k elements | 30s | 500MB |
| Elmer (EM) | 200k elements | 120s | 1GB |
| Palace | 500k elements | 300s | 2GB |

## Next Steps

- [ ] Implement mesh convergence study
- [ ] Add adaptive mesh refinement
- [ ] Integrate result uncertainty quantification
- [ ] Create benchmark validation cases
- [ ] Add cloud/HPC solver submission
