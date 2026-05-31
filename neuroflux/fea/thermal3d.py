"""3D thermal FEA-style solver for AFPM machine validation.

The solver builds a structured cylindrical annular mesh and solves steady-state
heat conduction with volumetric losses and convection to coolant/ambient
boundaries. It is deliberately compact and transparent so competition judges can
inspect the assumptions and reproduce the result without commercial software.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

from neuroflux.core.models import AFPMTopology


class ThermalFEA3DInput(BaseModel):
    """Input for the 3D annular AFPM thermal conduction solve."""

    name: str = Field(default="thermal_fea3d", min_length=1)
    outer_radius_m: float = Field(..., gt=0)
    inner_radius_m: float = Field(..., gt=0)
    axial_length_m: float = Field(..., gt=0)
    total_loss_w: float = Field(..., gt=0)
    copper_loss_fraction: float = Field(default=0.70, gt=0, lt=1)
    ambient_temp_c: float = Field(default=70.0)
    coolant_temp_c: float = Field(default=55.0)
    convection_w_per_m2k: float = Field(default=220.0, gt=0)
    conductivity_w_per_mk: float = Field(default=26.0, gt=0)
    topology: AFPMTopology = Field(default=AFPMTopology.DSSR_SLOTTED)
    radial_nodes: int = Field(default=16, ge=5, le=80)
    angular_nodes: int = Field(default=32, ge=8, le=160)
    axial_nodes: int = Field(default=9, ge=5, le=60)
    output_dir: str | Path = Field(default="fea_runs")


class ThermalFEA3DResult(BaseModel):
    """Result from a solved 3D thermal field."""

    converged: bool
    node_count: int
    max_temp_c: float
    min_temp_c: float
    average_temp_c: float
    coolant_temp_c: float
    hotspot_radius_m: float
    hotspot_angle_deg: float
    hotspot_z_m: float
    thermal_margin_to_180c: float
    solve_time_ms: float
    vtk_path: str
    summary_json_path: str
    confidence: str = "MEDIUM CONFIDENCE"


class ThermalFEA3DSolver:
    """Solve a structured 3D annular thermal model."""

    def solve(self, input_data: ThermalFEA3DInput) -> ThermalFEA3DResult:
        start = time.perf_counter()
        if input_data.inner_radius_m >= input_data.outer_radius_m:
            raise ValueError("inner_radius_m must be smaller than outer_radius_m")

        output_dir = Path(input_data.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        nr = input_data.radial_nodes
        nt = input_data.angular_nodes
        nz = input_data.axial_nodes
        node_count = nr * nt * nz
        dr = (input_data.outer_radius_m - input_data.inner_radius_m) / (nr - 1)
        dtheta = 2.0 * math.pi / nt
        dz = input_data.axial_length_m / (nz - 1)
        volume = math.pi * (
            input_data.outer_radius_m**2 - input_data.inner_radius_m**2
        ) * input_data.axial_length_m
        heat_source = input_data.total_loss_w / volume

        matrix = lil_matrix((node_count, node_count), dtype=float)
        rhs = np.zeros(node_count)

        for ir in range(nr):
            radius = input_data.inner_radius_m + ir * dr
            for it in range(nt):
                for iz in range(nz):
                    idx = self._idx(ir, it, iz, nt, nz)
                    diag = 0.0
                    cell_volume = max(radius, dr) * dr * dtheta * dz
                    rhs[idx] = heat_source * cell_volume

                    for jr, jt, jz, area, distance in self._neighbors(
                        ir,
                        it,
                        iz,
                        nr,
                        nt,
                        nz,
                        radius,
                        dr,
                        dtheta,
                        dz,
                    ):
                        conductance = input_data.conductivity_w_per_mk * area / distance
                        neighbor_idx = self._idx(jr, jt, jz, nt, nz)
                        matrix[idx, neighbor_idx] -= conductance
                        diag += conductance

                    boundary_area = self._boundary_area(
                        ir,
                        iz,
                        nr,
                        nz,
                        radius,
                        dr,
                        dtheta,
                        dz,
                    )
                    if boundary_area > 0.0:
                        convection = input_data.convection_w_per_m2k * boundary_area
                        boundary_temp = (
                            input_data.coolant_temp_c
                            if iz in (0, nz - 1)
                            else input_data.ambient_temp_c
                        )
                        diag += convection
                        rhs[idx] += convection * boundary_temp

                    matrix[idx, idx] = diag

        temperatures = np.asarray(spsolve(matrix.tocsr(), rhs), dtype=float)
        hotspot_index = int(np.argmax(temperatures))
        hotspot = self._coords(hotspot_index, input_data, nt, nz, dr, dtheta, dz)
        vtk_path = output_dir / "thermal_fea3d.vtk"
        summary_path = output_dir / "thermal_fea3d_summary.json"
        self._write_vtk(vtk_path, input_data, temperatures, dr, dtheta, dz)

        result = ThermalFEA3DResult(
            converged=bool(np.all(np.isfinite(temperatures))),
            node_count=node_count,
            max_temp_c=round(float(np.max(temperatures)), 6),
            min_temp_c=round(float(np.min(temperatures)), 6),
            average_temp_c=round(float(np.mean(temperatures)), 6),
            coolant_temp_c=input_data.coolant_temp_c,
            hotspot_radius_m=round(hotspot[0], 6),
            hotspot_angle_deg=round(math.degrees(hotspot[1]), 6),
            hotspot_z_m=round(hotspot[2], 6),
            thermal_margin_to_180c=round(180.0 - float(np.max(temperatures)), 6),
            solve_time_ms=round((time.perf_counter() - start) * 1000.0, 6),
            vtk_path=str(vtk_path.resolve()),
            summary_json_path=str(summary_path.resolve()),
        )
        summary_path.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return result

    def _neighbors(
        self,
        ir: int,
        it: int,
        iz: int,
        nr: int,
        nt: int,
        nz: int,
        radius: float,
        dr: float,
        dtheta: float,
        dz: float,
    ) -> list[tuple[int, int, int, float, float]]:
        neighbors: list[tuple[int, int, int, float, float]] = []
        radial_area = max(radius, dr) * dtheta * dz
        theta_area = dr * dz
        axial_area = max(radius, dr) * dr * dtheta
        if ir > 0:
            neighbors.append((ir - 1, it, iz, radial_area, dr))
        if ir < nr - 1:
            neighbors.append((ir + 1, it, iz, radial_area, dr))
        neighbors.append((ir, (it - 1) % nt, iz, theta_area, max(radius * dtheta, 1e-6)))
        neighbors.append((ir, (it + 1) % nt, iz, theta_area, max(radius * dtheta, 1e-6)))
        if iz > 0:
            neighbors.append((ir, it, iz - 1, axial_area, dz))
        if iz < nz - 1:
            neighbors.append((ir, it, iz + 1, axial_area, dz))
        return neighbors

    def _boundary_area(
        self,
        ir: int,
        iz: int,
        nr: int,
        nz: int,
        radius: float,
        dr: float,
        dtheta: float,
        dz: float,
    ) -> float:
        area = 0.0
        if ir in (0, nr - 1):
            area += max(radius, dr) * dtheta * dz
        if iz in (0, nz - 1):
            area += max(radius, dr) * dr * dtheta
        return area

    def _idx(self, ir: int, it: int, iz: int, nt: int, nz: int) -> int:
        return (ir * nt + it) * nz + iz

    def _coords(
        self,
        index: int,
        input_data: ThermalFEA3DInput,
        nt: int,
        nz: int,
        dr: float,
        dtheta: float,
        dz: float,
    ) -> tuple[float, float, float]:
        ir = index // (nt * nz)
        rem = index % (nt * nz)
        it = rem // nz
        iz = rem % nz
        radius = input_data.inner_radius_m + ir * dr
        theta = it * dtheta
        z = -input_data.axial_length_m / 2.0 + iz * dz
        return radius, theta, z

    def _write_vtk(
        self,
        path: Path,
        input_data: ThermalFEA3DInput,
        temperatures: np.ndarray,
        dr: float,
        dtheta: float,
        dz: float,
    ) -> None:
        points: list[tuple[float, float, float]] = []
        for ir in range(input_data.radial_nodes):
            radius = input_data.inner_radius_m + ir * dr
            for it in range(input_data.angular_nodes):
                theta = it * dtheta
                for iz in range(input_data.axial_nodes):
                    z = -input_data.axial_length_m / 2.0 + iz * dz
                    points.append((radius * math.cos(theta), radius * math.sin(theta), z))

        lines = [
            "# vtk DataFile Version 3.0",
            f"NeuroFlux 3D thermal FEA field: {input_data.name}",
            "ASCII",
            "DATASET POLYDATA",
            f"POINTS {len(points)} float",
        ]
        lines.extend(f"{x:.8f} {y:.8f} {z:.8f}" for x, y, z in points)
        lines.extend(
            [
                f"POINT_DATA {len(points)}",
                "SCALARS temperature_C float 1",
                "LOOKUP_TABLE default",
            ]
        )
        lines.extend(f"{value:.8f}" for value in temperatures)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
