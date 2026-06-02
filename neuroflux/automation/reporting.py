"""Unified reporting for complete automation results.

Generates comprehensive reports including:
- Executive summary
- Stage-by-stage breakdown
- Design performance metrics
- Validation results
- Artifact inventory
- Tool utilization report
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neuroflux.automation.orchestrator import AutomationResult


@dataclass
class DesignPackage:
    """Complete design package with all artifacts and metadata."""
    design_name: str
    output_directory: Path
    manifest_path: Path
    report_path: Path
    cad_files: list[Path] = field(default_factory=list)
    simulation_results: list[Path] = field(default_factory=list)
    visualization_files: list[Path] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "design_name": self.design_name,
            "output_directory": str(self.output_directory),
            "manifest": str(self.manifest_path),
            "report": str(self.report_path),
            "cad_files": [str(p) for p in self.cad_files],
            "simulation_results": [str(p) for p in self.simulation_results],
            "visualization_files": [str(p) for p in self.visualization_files],
            "generated_at": self.generated_at.isoformat(),
        }


class UnifiedReportGenerator:
    """Generate comprehensive unified reports from automation results."""
    
    def __init__(self) -> None:
        pass
    
    def generate(self, result: AutomationResult) -> Path:
        """Generate complete unified report.
        
        Args:
            result: Complete automation result
            
        Returns:
            Path to generated report
        """
        output_dir = result.output_directory or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / "automation_report.json"
        md_path = output_dir / "automation_report.md"
        
        # Generate JSON report
        json_report = self._generate_json_report(result)
        report_path.write_text(json.dumps(json_report, indent=2), encoding="utf-8")
        
        # Generate Markdown report
        md_report = self._generate_markdown_report(result)
        md_path.write_text(md_report, encoding="utf-8")
        
        return report_path
    
    def _generate_json_report(self, result: AutomationResult) -> dict:
        """Generate structured JSON report."""
        design = result.design_result
        
        return {
            "report_version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "automation": {
                "success": result.success,
                "duration_seconds": result.duration_seconds,
                "total_duration_ms": result.total_duration_ms,
                "stages": result.get_stage_summary(),
                "errors": result.errors,
                "warnings": result.warnings,
            },
            "tool_configuration": {
                "elmer_available": result.tool_config.elmer_available() if result.tool_config else False,
                "freecad_available": result.tool_config.freecad_available() if result.tool_config else False,
                "paraview_available": result.tool_config.paraview_available() if result.tool_config else False,
            },
            "design": {
                "name": design.spec.name if design else None,
                "target_power_w": design.spec.target_power_w if design else None,
                "target_speed_rpm": design.spec.target_speed_rpm if design else None,
                "target_voltage_v": design.spec.target_voltage_v if design else None,
                "max_outer_diameter_m": design.spec.max_outer_diameter_m if design else None,
                "achieved_efficiency": design.best_candidate.analytical_result.efficiency if design and design.best_candidate else None,
                "achieved_power_w": design.best_candidate.analytical_result.power_w if design and design.best_candidate else None,
                "achieved_torque_nm": design.best_candidate.analytical_result.torque_nm if design and design.best_candidate else None,
            } if design else None,
            "thermal_analysis": {
                "max_winding_temp_c": design.thermal_analysis.max_winding_temp_c if design else None,
                "max_magnet_temp_c": design.thermal_analysis.max_magnet_temp_c if design else None,
                "status": design.thermal_analysis.status if design else None,
            } if design else None,
            "validation": {
                "passed": design.validation_passed if design else None,
                "confidence": design.validation_result.thermal.confidence if design and design.validation_result else None,
                "max_temp_c": design.validation_result.thermal.native_fea3d.max_temp_c if design and design.validation_result and design.validation_result.thermal.native_fea3d else None,
            } if design else None,
            "artifacts": {
                "design_package_dir": str(design.design_package_dir) if design else None,
                "all_paths": {
                    k: str(v) for k, v in (design.artifacts.model_dump() if design else {}).items()
                },
            },
        }
    
    def _generate_markdown_report(self, result: AutomationResult) -> str:
        """Generate human-readable Markdown report."""
        design = result.design_result
        
        sections = [
            self._generate_header(result),
            self._generate_executive_summary(result),
            self._generate_stage_breakdown(result),
            self._generate_design_metrics(result),
            self._generate_thermal_analysis(result),
            self._generate_validation_results(result),
            self._generate_tool_report(result),
            self._generate_artifact_inventory(result),
            self._generate_next_steps(result),
        ]
        
        return "\n\n".join(sections)
    
    def _generate_header(self, result: AutomationResult) -> str:
        """Generate report header."""
        status_icon = "✅" if result.success else "❌"
        return dedent(f"""\
            # NeuroFlux Automation Report

            **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
            **Status**: {status_icon} {'SUCCESS' if result.success else 'FAILED'}  
            **Total Duration**: {result.duration_seconds:.2f} seconds  
            **Output Directory**: `{result.output_directory}`
            """)
    
    def _generate_executive_summary(self, result: AutomationResult) -> str:
        """Generate executive summary."""
        design = result.design_result
        
        if not design or not design.best_candidate:
            return "## Executive Summary\n\nNo design was generated."
        
        candidate = design.best_candidate
        spec = design.spec
        
        # Performance assessment
        power_ratio = candidate.analytical_result.power_w / spec.target_power_w
        efficiency = candidate.analytical_result.efficiency
        
        assessment = []
        if power_ratio >= 0.95:
            assessment.append("✅ Power target met")
        else:
            assessment.append(f"⚠️ Power at {power_ratio*100:.1f}% of target")
        
        if efficiency >= spec.min_efficiency:
            assessment.append(f"✅ Efficiency {efficiency:.1%} exceeds minimum {spec.min_efficiency:.1%}")
        else:
            assessment.append(f"❌ Efficiency {efficiency:.1%} below minimum {spec.min_efficiency:.1%}")
        
        return dedent(f"""\
            ## Executive Summary

            ### Design: {spec.name}

            | Metric | Target | Achieved | Status |
            |--------|--------|----------|--------|
            | Power | {spec.target_power_w:.0f} W | {candidate.analytical_result.power_w:.2f} W | {'✅' if power_ratio >= 0.95 else '⚠️'} |
            | Speed | {spec.target_speed_rpm:.0f} rpm | - | - |
            | Voltage | {spec.target_voltage_v:.0f} V | {candidate.analytical_result.back_emf_rms:.2f} V (BEMF) | {'✅' if candidate.analytical_result.back_emf_rms >= spec.target_voltage_v * 0.9 else '⚠️'} |
            | Efficiency | {spec.min_efficiency:.1%} | {efficiency:.2%} | {'✅' if efficiency >= spec.min_efficiency else '❌'} |
            | Outer Diameter | {spec.max_outer_diameter_m*1000:.0f} mm | {candidate.analytical_input.geometry.D_out*1000:.1f} mm | {'✅' if candidate.analytical_input.geometry.D_out <= spec.max_outer_diameter_m else '❌'} |

            ### Assessment

            {"\n".join(f"- {a}" for a in assessment)}

            ### Topology
            - **Type**: {candidate.analytical_input.geometry.topology.value}
            - **Pole Pairs**: {candidate.analytical_input.geometry.p}
            - **Slots**: {candidate.analytical_input.geometry.Q}
            - **Pole Pitch (mean)**: {(candidate.analytical_input.geometry.D_out/2 + candidate.analytical_input.geometry.D_out/2 * candidate.analytical_input.geometry.k_D) * 3.14159 / candidate.analytical_input.geometry.p * 1000:.2f} mm
            """)
    
    def _generate_stage_breakdown(self, result: AutomationResult) -> str:
        """Generate stage-by-stage breakdown."""
        rows = []
        for name, stage in result.stages.items():
            icon = "✅" if stage.is_success else "❌" if stage.status.name == "FAILED" else "⏭️"
            duration = f"{stage.duration_ms:.0f}ms"
            retries = f" ({stage.retry_count} retries)" if stage.retry_count > 0 else ""
            rows.append(f"| {icon} {name} | {stage.status.name} | {duration}{retries} |")
        
        return dedent(f"""\
            ## Pipeline Stage Breakdown

            | Stage | Status | Duration | Notes |
            |-------|--------|----------|-------|
            {"\n".join(rows)}
            """)
    
    def _generate_design_metrics(self, result: AutomationResult) -> str:
        """Generate detailed design metrics."""
        design = result.design_result
        if not design or not design.best_candidate:
            return ""
        
        r = design.best_candidate.analytical_result
        
        return dedent(f"""\
            ## Detailed Design Metrics

            ### Electromagnetic Performance
            | Parameter | Value | Unit |
            |-----------|-------|------|
            | Torque | {r.torque_nm:.4f} | Nm |
            | Power | {r.power_w:.2f} | W |
            | Back EMF (RMS) | {r.back_emf_rms:.2f} | V |
            | Efficiency | {r.efficiency:.3%} | - |
            | Frequency | {getattr(r, 'frequency_hz', 0):.2f} | Hz |

            ### Losses
            | Component | Value | Unit |
            |-----------|-------|------|
            | Copper Loss | {r.losses.get('copper_w', 0):.3f} | W |
            | Iron Loss | {r.losses.get('iron_w', 0):.3f} | W |
            | PM Eddy Loss | {r.losses.get('pm_eddy_w', 0):.3f} | W |
            | Total Losses | {r.total_losses_w:.3f} | W |

            ### Flux Densities
            | Location | B_max | Unit |
            |----------|-------|------|
            {"\n".join(f"| {k} | {v:.3f} | T |" for k, v in r.max_flux_densities.items())}
            """)
    
    def _generate_thermal_analysis(self, result: AutomationResult) -> str:
        """Generate thermal analysis section."""
        design = result.design_result
        if not design:
            return ""
        
        t = design.thermal_analysis
        
        return dedent(f"""\
            ## Thermal Analysis

            ### Operating Conditions
            | Parameter | Value | Unit |
            |-----------|-------|------|
            | Ambient Temperature | {t.ambient_temp_c:.1f} | °C |
            | Max Winding Temperature | {t.max_winding_temp_c:.1f} | °C |
            | Max Magnet Temperature | {t.max_magnet_temp_c:.1f} | °C |
            | Thermal Resistance | {t.thermal_resistance_k_per_w:.3f} | K/W |
            | Convective Area | {t.convective_area_m2:.6f} | m² |

            ### Status: {t.status}

            {"\n".join(f"- ⚠️ {w}" for w in t.warnings) if t.warnings else "- ✅ All thermal checks passed"}
            """)
    
    def _generate_validation_results(self, result: AutomationResult) -> str:
        """Generate validation results section."""
        design = result.design_result
        if not design or not design.validation_result:
            return "## 3D Validation\n\nValidation not run."
        
        v = design.validation_result
        
        sections = ["## 3D Validation Results\n"]
        
        # Overall status
        sections.append(f"**Status**: {'✅ PASS' if design.validation_passed else '❌ FAIL'}")
        sections.append(f"**Confidence**: {v.thermal.confidence}\n")
        
        # Native FEA results
        if v.thermal.native_fea3d:
            f = v.thermal.native_fea3d
            sections.append(dedent(f"""\
                ### Native 3D Thermal FEA
                | Metric | Value | Unit |
                |--------|-------|------|
                | Max Temperature | {f.max_temp_c:.1f} | °C |
                | Min Temperature | {f.min_temp_c:.1f} | °C |
                | Average Temperature | {f.average_temp_c:.1f} | °C |
                | Thermal Margin to 180°C | {f.thermal_margin_to_180c:.1f} | °C |
                | Hotspot Location | r={f.hotspot_radius_m:.4f}m, θ={f.hotspot_angle_deg:.1f}° | - |
                | Node Count | {f.node_count} | - |
                | Solve Time | {f.solve_time_ms:.0f} | ms |
                """))
        
        # Solver handoffs
        if v.solver_handoffs:
            sections.append("### Solver Handoffs Generated\n")
            for h in v.solver_handoffs:
                sections.append(f"- **{h.solver_name}**: `{h.case_dir}`")
        
        # Warnings
        if v.warnings:
            sections.append("\n### Warnings\n")
            for w in v.warnings:
                sections.append(f"- ⚠️ {w}")
        
        return "\n".join(sections)
    
    def _generate_tool_report(self, result: AutomationResult) -> str:
        """Generate tool utilization report."""
        tc = result.tool_config
        if not tc:
            return ""
        
        tools = [
            ("ElmerSolver", tc.elmer_available(), tc.get_elmer_solver() or "Not found"),
            ("ElmerGUI", tc.get_elmer_gui() is not None, tc.get_elmer_gui() or "Not found"),
            ("Gmsh", tc.get_gmsh() is not None, tc.get_gmsh() or "Not found"),
            ("FreeCAD", tc.freecad_available(), tc.get_freecad() or "Not found"),
            ("ParaView", tc.paraview_available(), tc.get_paraview() or "Not found"),
        ]
        
        rows = []
        for name, available, path in tools:
            icon = "✅" if available else "❌"
            rows.append(f"| {icon} {name} | {'Available' if available else 'Not Available'} | `{path}` |")
        
        return dedent(f"""\
            ## External Tool Status

            | Tool | Status | Path |
            |------|--------|------|
            {"\n".join(rows)}
            """)
    
    def _generate_artifact_inventory(self, result: AutomationResult) -> str:
        """Generate artifact inventory."""
        design = result.design_result
        if not design:
            return ""
        
        artifacts = design.artifacts
        
        return dedent(f"""\
            ## Artifact Inventory

            ### Core Design Files
            | Artifact | Path |
            |----------|------|
            | Design Manifest | `{artifacts.manifest_json}` |
            | Report | `{artifacts.report_md}` |
            | 3D Scene | `{artifacts.scene3d_json}` |
            | HTML Viewer | `{artifacts.viewer_html}` |

            ### CAD Files
            | Artifact | Path |
            |----------|------|
            | Gmsh Geometry | `{artifacts.geometry_geo}` |
            | OpenSCAD Assembly | `{artifacts.assembly_scad}` |
            | STL Mesh | `{artifacts.assembly_stl}` |
            | CAD Index | `{artifacts.cad_index_json}` |

            ### Analysis Files
            | Artifact | Path |
            |----------|------|
            | Thermal Analysis | `{artifacts.thermal_json}` |
            | Parameters CSV | `{artifacts.parameters_csv}` |
            | Lab Manifest | `{artifacts.lab_manifest_json}` |
            """)
    
    def _generate_next_steps(self, result: AutomationResult) -> str:
        """Generate next steps recommendations."""
        recommendations = []
        
        design = result.design_result
        tc = result.tool_config
        
        if design and design.validation_result:
            if design.validation_result.thermal.confidence != "HIGH":
                recommendations.append("- Consider running external solvers for higher confidence validation")
        
        if tc and not tc.elmer_available():
            recommendations.append("- Install Elmer FEM for advanced 3D electromagnetic analysis")
        
        if tc and not tc.freecad_available():
            recommendations.append("- Install FreeCAD for STEP file export to manufacturing")
        
        if not recommendations:
            recommendations.append("- Design is ready for prototyping")
            recommendations.append("- Export STEP files and send to manufacturer")
        
        return dedent(f"""\
            ## Recommended Next Steps

            {"\n".join(recommendations)}

            ---
            *Generated by NeuroFlux Automation v2.0*
            """)


def load_design_package(directory: Path | str) -> DesignPackage:
    """Load a design package from output directory.
    
    Args:
        directory: Path to design package directory
        
    Returns:
        DesignPackage with all artifacts
    """
    directory = Path(directory)
    
    # Load manifest
    manifest_path = directory / "design_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Design manifest not found: {manifest_path}")
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    design_name = manifest.get("spec", {}).get("name", "unknown")
    
    # Collect all artifacts
    cad_files = list(directory.glob("*.step")) + list(directory.glob("*.STEP"))
    cad_files.extend(directory.glob("cad_export/*.step"))
    
    sim_results = list((directory / "validation").rglob("*.vtk")) if (directory / "validation").exists() else []
    sim_results.extend((directory / "validation").rglob("*.vtu") if (directory / "validation").exists() else [])
    
    viz_files = list(directory.glob("*.html")) + list(directory.glob("viewer.html"))
    
    return DesignPackage(
        design_name=design_name,
        output_directory=directory,
        manifest_path=manifest_path,
        report_path=directory / "automation_report.md",
        cad_files=cad_files,
        simulation_results=sim_results,
        visualization_files=viz_files,
    )
