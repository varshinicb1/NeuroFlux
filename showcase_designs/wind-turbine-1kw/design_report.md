# NeuroFlux AFPM Generator Design: wind-turbine-1kw

            ## Use Case

            Low-speed permanent-magnet generator targeting 1000.0 W at
            200.0 rpm and 48.0 V.

            ## Selected Design

            - Candidate: NF-DSSR_slotted-94
            - Topology: DSSR_slotted
            - Outer diameter: 0.3400 m
            - Inner diameter: 0.2244 m
            - Pole count: 20
            - Slots: 60
            - Air gap: 0.0025 m
            - Magnet thickness: 0.0061 m
            - Turns per phase: 156

            ## Performance

            - Torque: 73.237 N m
            - Power: 1497.103 W
            - Back EMF RMS: 100.000 V
            - Efficiency: 0.976
            - Total losses: 36.760 W

            ## Phase 1: Thermal Screen

            - Status: pass
            - Winding temperature: 54.0 C
            - Magnet temperature: 44.5 C
            - Convective area: 0.1461 m2

            ## Phase 2: 3D Validation (Native FEA)

            - **Validation Status**: PASS
            - **Confidence**: HIGH CONFIDENCE
            - **3D Max Temperature**: 51.6 C
            - **3D Avg Temperature**: 51.1 C
            - **Hotspot Location**: r=0.1392 m, θ=0.0°, z=-0.0204 m
            - **Thermal Margin to 180°C**: 128.4 C
            - **Solve Time**: 200 ms
            - **Node Count**: 4608
            - **VTK Output**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\validation\wind-turbine-1kw\thermal_fea3d\thermal_fea3d.vtk`

            ## Solver Handoffs Generated

            - **Elmer FEM**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\validation\wind-turbine-1kw\solver_handoffs\elmer_case`
- **Palace**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\validation\wind-turbine-1kw\solver_handoffs\palace_case`

            ## Artifact Index

            - Manifest: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\design_manifest.json`
            - 3D scene: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\scene3d.json`
            - Browser viewer: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\viewer.html`
            - Gmsh geometry: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\geometry.geo`
            - OpenSCAD assembly: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\assembly.scad`
            - STL inspection mesh: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\assembly.stl`
            - CAD index: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\cad_index.json`
            - Thermal JSON: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\thermal_analysis.json`
            - Parameter CSV: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\wind-turbine-1kw\parameters.csv`
