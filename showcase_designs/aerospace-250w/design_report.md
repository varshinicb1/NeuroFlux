# NeuroFlux AFPM Generator Design: aerospace-250w

            ## Use Case

            Low-speed permanent-magnet generator targeting 250.0 W at
            8000.0 rpm and 28.0 V.

            ## Selected Design

            - Candidate: NF-DSSR_slotted-01
            - Topology: DSSR_slotted
            - Outer diameter: 0.1103 m
            - Inner diameter: 0.0639 m
            - Pole count: 8
            - Slots: 24
            - Air gap: 0.0025 m
            - Magnet thickness: 0.0040 m
            - Turns per phase: 12

            ## Performance

            - Torque: 0.241 N m
            - Power: 179.776 W
            - Back EMF RMS: 100.000 V
            - Efficiency: 0.889
            - Total losses: 22.536 W

            ## Phase 1: Thermal Screen

            - Status: pass
            - Winding temperature: 112.6 C
            - Magnet temperature: 46.2 C
            - Convective area: 0.0173 m2

            ## Phase 2: 3D Validation (Native FEA)

            - **Validation Status**: PASS
            - **Confidence**: HIGH CONFIDENCE
            - **3D Max Temperature**: 56.6 C
            - **3D Avg Temperature**: 56.4 C
            - **Hotspot Location**: r=0.0443 m, θ=22.5°, z=0.0000 m
            - **Thermal Margin to 180°C**: 123.4 C
            - **Solve Time**: 187 ms
            - **Node Count**: 4608
            - **VTK Output**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\validation\aerospace-250w\thermal_fea3d\thermal_fea3d.vtk`

            ## Solver Handoffs Generated

            - **Elmer FEM**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\validation\aerospace-250w\solver_handoffs\elmer_case`
- **Palace**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\validation\aerospace-250w\solver_handoffs\palace_case`

            ## Artifact Index

            - Manifest: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\design_manifest.json`
            - 3D scene: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\scene3d.json`
            - Browser viewer: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\viewer.html`
            - Gmsh geometry: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\geometry.geo`
            - OpenSCAD assembly: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\assembly.scad`
            - STL inspection mesh: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\assembly.stl`
            - CAD index: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\cad_index.json`
            - Thermal JSON: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\thermal_analysis.json`
            - Parameter CSV: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\aerospace-250w\parameters.csv`
