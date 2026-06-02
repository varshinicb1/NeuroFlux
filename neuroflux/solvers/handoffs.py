"""External solver deck generation for Elmer FEM and Palace."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from pydantic import BaseModel

from neuroflux.core.models import (
    MachineGeometry,
    MaterialProperties,
    OperatingPoint,
    WindingParameters,
)


class ExternalSolverHandoff(BaseModel):
    """Generated solver handoff metadata."""

    solver_name: str
    gui_tool: str | None = None
    case_dir: str
    geometry_geo_path: str
    mesh_path: str
    config_path: str
    run_command: str
    notes: list[str]

    @property
    def case_sif_path(self) -> str:
        return self.config_path


class ElmerHandoffBuilder:
    """Generate Elmer FEM multiphysics case files for ElmerSolver/ElmerGUI."""

    def __init__(self, output_root: str | Path = "solver_handoffs") -> None:
        self.output_root = Path(output_root)

    def build(
        self,
        geometry: MachineGeometry,
        materials: MaterialProperties,
        winding: WindingParameters,
        operating_point: OperatingPoint,
    ) -> ExternalSolverHandoff:
        case_dir = self.output_root / "elmer_case"
        case_dir.mkdir(parents=True, exist_ok=True)
        geo_path = case_dir / "geometry.geo"
        sif_path = case_dir / "case.sif"
        mesh_path = case_dir / "mesh"
        geo_path.write_text(self._geometry_geo(geometry), encoding="utf-8")
        sif_path.write_text(
            self._case_sif(geometry, materials, winding, operating_point),
            encoding="utf-8",
        )
        manifest = ExternalSolverHandoff(
            solver_name="Elmer FEM",
            gui_tool="ElmerGUI",
            case_dir=str(case_dir.resolve()),
            geometry_geo_path=str(geo_path.resolve()),
            mesh_path=str(mesh_path.resolve()),
            config_path=str(sif_path.resolve()),
            run_command="ElmerSolver case.sif",
            notes=[
                "Open geometry/mesh in ElmerGUI for GUI-based material, boundary, "
                "and solver review.",
                "Generate mesh with Gmsh/ElmerGrid before running ElmerSolver.",
                "This handoff is a solver deck; it does not claim Elmer was executed.",
            ],
        )
        (case_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return manifest

    def _geometry_geo(self, geometry: MachineGeometry) -> str:
        return dedent(
            f"""
            // NeuroFlux Elmer FEM AFPM handoff geometry
            SetFactory("OpenCASCADE");
            r_out = {geometry.r_out:.8f};
            r_in = {geometry.r_in:.8f};
            axial = {geometry.l_s:.8f};
            Cylinder(1) = {{0, 0, -axial/2, 0, 0, axial, r_out}};
            Cylinder(2) = {{0, 0, -axial/2, 0, 0, axial, r_in}};
            BooleanDifference{{ Volume{{1}}; Delete; }}{{ Volume{{2}}; Delete; }}
            machine_boundary[] = Boundary{{ Volume{{1}}; }};
            Physical Volume(1) = {{1}};
            Physical Surface(2) = {{machine_boundary[]}};
            Mesh.SaveAll = 1;
            Mesh.CharacteristicLengthMax = {max(geometry.g, geometry.active_length / 8.0):.8f};
            """
        ).lstrip()

    def _case_sif(
        self,
        geometry: MachineGeometry,
        materials: MaterialProperties,
        winding: WindingParameters,
        operating_point: OperatingPoint,
    ) -> str:
        current_density = winding.current_density
        frequency = geometry.p * operating_point.speed_rpm / 60.0
        return dedent(
            f"""
            Header
              CHECK KEYWORDS Warn
              Mesh DB "." "mesh"
              Include Path ""
              Results Directory "results"
            End

            Simulation
              Max Output Level = 5
              Coordinate System = Cartesian 3D
              Simulation Type = Steady State
              Steady State Max Iterations = 1
              Output Intervals = 1
              Solver Input File = case.sif
            End

            Constants
              Permittivity of Vacuum = 8.854187817e-12
              Permeability of Vacuum = 1.2566370614e-6
            End

            Body 1
              Name = "AFPM active domain"
              Equation = 1
              Material = 1
              Body Force = 1
            End

            Equation 1
              Active Solvers(2) = 1 2
            End

            Solver 1
              Equation = MagnetoDynamics
              Procedure = "MagnetoDynamics" "WhitneyAVSolver"
              Variable = A
              Variable DOFs = 3
              Fix Input Current Density = True
              Use Tree Gauge = True
              Linear System Solver = Iterative
              Linear System Iterative Method = BiCGStab
              Linear System Max Iterations = 1000
              Linear System Convergence Tolerance = 1.0e-8
            End

            Solver 2
              Equation = HeatSolve
              Procedure = "HeatSolve" "HeatSolver"
              Variable = Temperature
              Linear System Solver = Iterative
              Linear System Iterative Method = BiCGStab
              Linear System Max Iterations = 500
              Linear System Convergence Tolerance = 1.0e-8
            End

            Material 1
              Name = "Homogenized AFPM material"
              Relative Permeability = {materials.mu_r_steel_linear:.3f}
              Relative Permittivity = 1.0
              Heat Conductivity = 28.0
              Density = 7600.0
              Heat Capacity = 460.0
            End

            Body Force 1
              Current Density 1 = {current_density:.6e}
              Current Density 2 = 0.0
              Current Density 3 = 0.0
              Heat Source = {max(1.0, frequency * 25.0):.6f}
            End

            Boundary Condition 1
              Name = "outer magnetic and thermal reference"
              Target Boundaries(4) = 4 5 6 7
              AV {{e}} = 0.0
              Temperature = 338.15
            End
            """
        ).strip() + "\n"


class PalaceHandoffBuilder:
    """Generate Palace electromagnetics JSON configuration and manifest."""

    def __init__(self, output_root: str | Path = "solver_handoffs") -> None:
        self.output_root = Path(output_root)

    def build(
        self,
        geometry: MachineGeometry,
        materials: MaterialProperties,
        winding: WindingParameters,
        operating_point: OperatingPoint,
    ) -> ExternalSolverHandoff:
        case_dir = self.output_root / "palace_case"
        case_dir.mkdir(parents=True, exist_ok=True)
        geo_path = case_dir / "geometry.geo"
        mesh_path = case_dir / "geometry.msh"
        config_path = case_dir / "palace.json"
        geo_path.write_text(self._geometry_geo(geometry), encoding="utf-8")
        config_path.write_text(
            json.dumps(
                self._palace_config(geometry, materials, winding, operating_point),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        handoff = ExternalSolverHandoff(
            solver_name="Palace",
            gui_tool=None,
            case_dir=str(case_dir.resolve()),
            geometry_geo_path=str(geo_path.resolve()),
            mesh_path=str(mesh_path.resolve()),
            config_path=str(config_path.resolve()),
            run_command="palace palace.json",
            notes=[
                "Palace is a command-line 3D finite-element electromagnetics solver.",
                "Generate geometry.msh before execution, then run palace palace.json.",
                "Expected outputs include JSON metadata, CSV postprocessing, and VTK/PVD fields.",
            ],
        )
        (case_dir / "manifest.json").write_text(
            json.dumps(handoff.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return handoff

    def _geometry_geo(self, geometry: MachineGeometry) -> str:
        return dedent(
            f"""
            // NeuroFlux Palace electromagnetics mesh handoff
            SetFactory("OpenCASCADE");
            r_out = {geometry.r_out:.8f};
            r_in = {geometry.r_in:.8f};
            axial = {geometry.l_s:.8f};
            Cylinder(1) = {{0, 0, -axial/2, 0, 0, axial, r_out}};
            Cylinder(2) = {{0, 0, -axial/2, 0, 0, axial, r_in}};
            BooleanDifference{{ Volume{{1}}; Delete; }}{{ Volume{{2}}; Delete; }}
            Physical Volume("domain") = {{1}};
            """
        ).lstrip()

    def _palace_config(
        self,
        geometry: MachineGeometry,
        materials: MaterialProperties,
        winding: WindingParameters,
        operating_point: OperatingPoint,
    ) -> dict:
        frequency_hz = geometry.p * operating_point.speed_rpm / 60.0
        return {
            "Problem": {
                "Type": "Magnetostatic",
                "Verbose": 1,
            },
            "Model": {
                "Mesh": "geometry.msh",
                "L0": 1.0,
                "Refinement": 0,
            },
            "Domains": {
                "Materials": [
                    {
                        "Attributes": [1],
                        "Name": "homogenized_machine_domain",
                        "Permeability": 1.2566370614e-6 * materials.mu_r_steel_linear,
                        "Conductivity": 1.0 / materials.copper_resistivity_20c,
                    }
                ]
            },
            "Boundaries": {
                "PEC": {"Attributes": []},
                "Postprocessing": {"Surfaces": []},
            },
            "Solver": {
                "Order": 2,
                "Linear": {
                    "Type": "AMS",
                    "KSPType": "GMRES",
                    "Tol": 1.0e-8,
                    "MaxIts": 1000,
                },
            },
            "Postprocessing": {
                "Output": "postpro",
                "Fields": {"B": True, "H": True},
                "Metadata": {
                    "frequency_hz": frequency_hz,
                    "turns_per_phase": winding.turns_per_phase,
                },
            },
        }
