# NeuroFlux AFPM Generator Design: portable-generator-500w

            ## Use Case

            Low-speed permanent-magnet generator targeting 500.0 W at
            1500.0 rpm and 12.0 V.

            ## Selected Design

            - Candidate: NF-DSSR_slotted-04
            - Topology: DSSR_slotted
            - Outer diameter: 0.1654 m
            - Inner diameter: 0.0959 m
            - Pole count: 20
            - Slots: 60
            - Air gap: 0.0025 m
            - Magnet thickness: 0.0040 m
            - Turns per phase: 12

            ## Performance

            - Torque: 3.155 N m
            - Power: 306.427 W
            - Back EMF RMS: 100.000 V
            - Efficiency: 0.618
            - Total losses: 189.150 W

            ## Phase 1: Thermal Screen

            - Status: fail
            - Winding temperature: 310.7 C
            - Magnet temperature: 131.4 C
            - Convective area: 0.0388 m2

            ## Phase 2: 3D Validation (Native FEA)

            - **Validation Status**: PASS
            - **Confidence**: HIGH CONFIDENCE
            - **3D Max Temperature**: 73.3 C
            - **3D Avg Temperature**: 72.4 C
            - **Hotspot Location**: r=0.0642 m, θ=225.0°, z=0.0000 m
            - **Thermal Margin to 180°C**: 106.7 C
            - **Solve Time**: 179 ms
            - **Node Count**: 4608
            - **VTK Output**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\validation\portable-generator-500w\thermal_fea3d\thermal_fea3d.vtk`

            ## Solver Handoffs Generated

            - **Elmer FEM**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\validation\portable-generator-500w\solver_handoffs\elmer_case`
- **Palace**: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\validation\portable-generator-500w\solver_handoffs\palace_case`

            ## Artifact Index

            - Manifest: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\design_manifest.json`
            - 3D scene: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\scene3d.json`
            - Browser viewer: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\viewer.html`
            - Gmsh geometry: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\geometry.geo`
            - OpenSCAD assembly: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\assembly.scad`
            - STL inspection mesh: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\assembly.stl`
            - CAD index: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\cad_index.json`
            - Thermal JSON: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\thermal_analysis.json`
            - Parameter CSV: `C:\Users\varsh\.codex\worktrees\a9d3\NeuroFlux\showcase_designs\portable-generator-500w\parameters.csv`
