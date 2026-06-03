# NeuroFlux AFPM Generator Design: ev-traction-5kw

            ## Use Case

            Low-speed permanent-magnet generator targeting 5000.0 W at
            3000.0 rpm and 400.0 V.

            ## Selected Design

            - Candidate: NF-DSSR_slotted-03
            - Topology: DSSR_slotted
            - Outer diameter: 0.2625 m
            - Inner diameter: 0.1522 m
            - Pole count: 16
            - Slots: 48
            - Air gap: 0.0025 m
            - Magnet thickness: 0.0047 m
            - Turns per phase: 108

            ## Performance

            - Torque: 16.929 N m
            - Power: 5270.434 W
            - Back EMF RMS: 100.000 V
            - Efficiency: 0.991
            - Total losses: 48.050 W

            ## Phase 1: Thermal Screen

            - Status: pass
            - Winding temperature: 67.3 C
            - Magnet temperature: 41.8 C
            - Convective area: 0.0978 m2

            ## Phase 2: 3D Validation (Native FEA)

            - **Validation Status**: PASS
            - **Confidence**: HIGH CONFIDENCE
            - **3D Max Temperature**: 53.3 C
            - **3D Avg Temperature**: 52.9 C
            - **Hotspot Location**: r=0.1018 m, θ=90.0°, z=0.0158 m
            - **Thermal Margin to 180°C**: 126.7 C
            - **Solve Time**: 174 ms
            - **Node Count**: 4608
            - **VTK Output**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\validation\ev-traction-5kw\thermal_fea3d\thermal_fea3d.vtk`

            ## Solver Handoffs Generated

            - **Elmer FEM**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\validation\ev-traction-5kw\solver_handoffs\elmer_case`
- **Palace**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\validation\ev-traction-5kw\solver_handoffs\palace_case`

            ## Artifact Index

            - Manifest: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\design_manifest.json`
            - 3D scene: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\scene3d.json`
            - Browser viewer: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\viewer.html`
            - Gmsh geometry: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\geometry.geo`
            - OpenSCAD assembly: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\assembly.scad`
            - STL inspection mesh: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\assembly.stl`
            - CAD index: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\cad_index.json`
            - Thermal JSON: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\thermal_analysis.json`
            - Parameter CSV: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\ev-traction-5kw\parameters.csv`
