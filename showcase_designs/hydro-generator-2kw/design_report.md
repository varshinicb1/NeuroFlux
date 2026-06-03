# NeuroFlux AFPM Generator Design: hydro-generator-2kw

            ## Use Case

            Low-speed permanent-magnet generator targeting 2000.0 W at
            100.0 rpm and 120.0 V.

            ## Selected Design

            - Candidate: NF-DSSR_slotted-25
            - Topology: DSSR_slotted
            - Outer diameter: 0.5520 m
            - Inner diameter: 0.3202 m
            - Pole count: 24
            - Slots: 72
            - Air gap: 0.0025 m
            - Magnet thickness: 0.0099 m
            - Turns per phase: 240

            ## Performance

            - Torque: 288.328 N m
            - Power: 2991.635 W
            - Back EMF RMS: 100.000 V
            - Efficiency: 0.991
            - Total losses: 27.725 W

            ## Phase 1: Thermal Screen

            - Status: pass
            - Winding temperature: 43.6 C
            - Magnet temperature: 40.8 C
            - Convective area: 0.4325 m2

            ## Phase 2: 3D Validation (Native FEA)

            - **Validation Status**: PASS
            - **Confidence**: HIGH CONFIDENCE
            - **3D Max Temperature**: 51.7 C
            - **3D Avg Temperature**: 51.0 C
            - **Hotspot Location**: r=0.2219 m, θ=326.2°, z=0.0331 m
            - **Thermal Margin to 180°C**: 128.3 C
            - **Solve Time**: 160 ms
            - **Node Count**: 4608
            - **VTK Output**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\validation\hydro-generator-2kw\thermal_fea3d\thermal_fea3d.vtk`

            ## Solver Handoffs Generated

            - **Elmer FEM**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\validation\hydro-generator-2kw\solver_handoffs\elmer_case`
- **Palace**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\validation\hydro-generator-2kw\solver_handoffs\palace_case`

            ## Artifact Index

            - Manifest: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\design_manifest.json`
            - 3D scene: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\scene3d.json`
            - Browser viewer: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\viewer.html`
            - Gmsh geometry: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\geometry.geo`
            - OpenSCAD assembly: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\assembly.scad`
            - STL inspection mesh: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\assembly.stl`
            - CAD index: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\cad_index.json`
            - Thermal JSON: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\thermal_analysis.json`
            - Parameter CSV: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\hydro-generator-2kw\parameters.csv`
