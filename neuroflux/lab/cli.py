"""Command-line entry point for the NeuroFlux autonomous lab."""

from __future__ import annotations

import argparse
import sys

from neuroflux.aerospace import AerospaceReviewEngine, AerospaceReviewSpec
from neuroflux.bench import AFPMBenchEngine
from neuroflux.core.models import AFPMTopology
from neuroflux.design import AFPMDesignEngine, AFPMGeneratorSpec
from neuroflux.discovery import DesignRequirements
from neuroflux.lab.autonomous_lab import AutonomousLab, LabRunConfig
from neuroflux.pdr import AegisPDRGenerator, AegisPDRSpec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="neuroflux-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run autonomous AFPM design lab")
    run_parser.add_argument("--iterations", type=int, default=3)
    run_parser.add_argument("--output", default="lab_runs")
    run_parser.add_argument("--target-power-w", type=float, default=250.0)
    run_parser.add_argument("--target-speed-rpm", type=float, default=600.0)
    run_parser.add_argument("--target-voltage-v", type=float, default=48.0)
    run_parser.add_argument("--max-outer-diameter-m", type=float, default=0.32)
    run_parser.add_argument("--min-efficiency", type=float, default=0.50)
    run_parser.add_argument(
        "--topology",
        choices=[item.value for item in AFPMTopology],
        default=AFPMTopology.DSSR_SLOTTED.value,
    )
    run_parser.add_argument("--prefer-halbach", action="store_true")
    run_parser.add_argument("--num-candidates", type=int, default=4)
    run_parser.add_argument("--num-planes", type=int, default=5)

    design_parser = subparsers.add_parser(
        "design",
        help="produce a unified AFPM generator design package",
    )
    design_parser.add_argument("--output", default="design_runs")
    design_parser.add_argument("--name", default="low-speed-250w-afpm-generator")
    design_parser.add_argument("--target-power-w", type=float, default=250.0)
    design_parser.add_argument("--target-speed-rpm", type=float, default=600.0)
    design_parser.add_argument("--target-voltage-v", type=float, default=48.0)
    design_parser.add_argument("--max-outer-diameter-m", type=float, default=0.32)
    design_parser.add_argument("--min-efficiency", type=float, default=0.50)
    design_parser.add_argument("--ambient-temp-c", type=float, default=40.0)
    design_parser.add_argument("--max-winding-temp-c", type=float, default=120.0)
    design_parser.add_argument("--convection-w-per-m2k", type=float, default=18.0)
    design_parser.add_argument(
        "--topology",
        choices=[item.value for item in AFPMTopology],
        default=AFPMTopology.DSSR_SLOTTED.value,
    )
    design_parser.add_argument("--prefer-halbach", action="store_true")
    design_parser.add_argument("--iterations", type=int, default=3)
    design_parser.add_argument("--num-candidates", type=int, default=6)
    design_parser.add_argument("--num-planes", type=int, default=7)
    design_parser.add_argument("--no-3d-validation", action="store_true", help="Skip Phase 2 3D FEA validation")
    design_parser.add_argument("--run-external-solvers", action="store_true", help="Run Elmer/Palace if installed")
    design_parser.add_argument("--validation-refinement", choices=["coarse", "medium", "fine"], default="medium")

    aerospace_parser = subparsers.add_parser(
        "aerospace-review",
        help="generate Honeywell-grade aerospace AFPM review evidence package",
    )
    aerospace_parser.add_argument("--output", default="aerospace_reviews")
    aerospace_parser.add_argument("--name", default="honeywell-low-speed-afpm")
    aerospace_parser.add_argument("--target-power-kw", type=float, default=25.0)
    aerospace_parser.add_argument("--target-speed-rpm", type=float, default=1200.0)
    aerospace_parser.add_argument("--dc-bus-voltage-v", type=float, default=540.0)
    aerospace_parser.add_argument("--max-outer-diameter-m", type=float, default=0.42)
    aerospace_parser.add_argument("--coolant", default="PAO/oil cold plate")
    aerospace_parser.add_argument("--design-life-hours", type=int, default=20_000)
    aerospace_parser.add_argument("--iterations", type=int, default=2)

    pdr_parser = subparsers.add_parser(
        "aegis-pdr",
        help="generate AEGIS-AFSG Preliminary Design Review package",
    )
    pdr_parser.add_argument("--output", default="pdr_packages")
    pdr_parser.add_argument("--name", default="aegis-afsg-pdr")
    pdr_parser.add_argument("--target-power-kw", type=float, default=25.0)
    pdr_parser.add_argument("--target-speed-rpm", type=float, default=1200.0)
    pdr_parser.add_argument("--dc-bus-voltage-v", type=float, default=540.0)
    pdr_parser.add_argument("--max-outer-diameter-m", type=float, default=0.42)
    pdr_parser.add_argument("--coolant-temp-c", type=float, default=48.0)
    pdr_parser.add_argument("--monte-carlo-samples", type=int, default=2000)

    bench_parser = subparsers.add_parser(
        "afpm-bench",
        help="build AFPM-Bench state-of-the-art intelligence outputs",
    )
    bench_parser.add_argument("--output", default="bench_outputs")

    # GUI command
    gui_parser = subparsers.add_parser(
        "gui",
        help="launch web-based GUI",
    )
    gui_parser.add_argument("--host", default="127.0.0.1", help="host to bind to")
    gui_parser.add_argument("--port", type=int, default=8080, help="port to listen on")
    gui_parser.add_argument("--no-browser", action="store_true", help="don't auto-open browser")

    # Tool check command
    toolcheck_parser = subparsers.add_parser(
        "tool-check",
        help="check status of external tools (Elmer, Gmsh, FreeCAD, ParaView)",
    )
    toolcheck_parser.add_argument("--verbose", action="store_true", help="show detailed paths")

    # Visualization command
    viz_parser = subparsers.add_parser(
        "visualize",
        help="launch ParaView to visualize design results",
    )
    viz_parser.add_argument("design_dir", help="path to design run directory")
    viz_parser.add_argument("--type", choices=["thermal", "elmer", "all"], default="all",
                           help="type of results to visualize")

    # CAD export command
    cad_parser = subparsers.add_parser(
        "export-cad",
        help="export design to STEP format using FreeCAD",
    )
    cad_parser.add_argument("design_dir", help="path to design run directory")
    cad_parser.add_argument("--output", "-o", default="cad_export.step",
                           help="output STEP file path")
    cad_parser.add_argument("--component", choices=["stator", "rotor", "both"], default="both",
                           help="which component to export")

    # Full automation command
    auto_parser = subparsers.add_parser(
        "auto",
        help="full automation: design + validation + export + visualize",
    )
    auto_parser.add_argument("--name", default="auto-design",
                          help="design run name")
    auto_parser.add_argument("--target-power-w", type=float, default=500.0,
                            help="target power in watts")
    auto_parser.add_argument("--target-speed-rpm", type=float, default=800.0,
                            help="target speed in rpm")
    auto_parser.add_argument("--target-voltage-v", type=float, default=48.0,
                            help="target voltage in volts")
    auto_parser.add_argument("--max-diameter-m", type=float, default=0.25,
                            help="maximum outer diameter in meters")
    auto_parser.add_argument("--min-efficiency", type=float, default=0.60,
                            help="minimum efficiency")
    auto_parser.add_argument("--run-external-solvers", action="store_true",
                            help="run Elmer FEM if available")
    auto_parser.add_argument("--export-cad", action="store_true",
                            help="auto-export STEP files")
    auto_parser.add_argument("--visualize", action="store_true",
                            help="auto-launch ParaView")
    auto_parser.add_argument("--parallel", action="store_true", default=True,
                            help="enable parallel execution")
    auto_parser.add_argument("--output", "-o", default="design_automation",
                            help="output directory")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        requirements = DesignRequirements(
            target_power_w=args.target_power_w,
            target_speed_rpm=args.target_speed_rpm,
            target_voltage_v=args.target_voltage_v,
            max_outer_diameter_m=args.max_outer_diameter_m,
            min_efficiency=args.min_efficiency,
            topology=AFPMTopology(args.topology),
            prefer_halbach=args.prefer_halbach,
            num_candidates=args.num_candidates,
            num_planes=args.num_planes,
        )
        result = AutonomousLab(output_root=args.output).run(
            LabRunConfig(requirements=requirements, iterations=args.iterations)
        )
        print(result.manifest_path)
        return 0
    if args.command == "design":
        spec = AFPMGeneratorSpec(
            name=args.name,
            target_power_w=args.target_power_w,
            target_speed_rpm=args.target_speed_rpm,
            target_voltage_v=args.target_voltage_v,
            max_outer_diameter_m=args.max_outer_diameter_m,
            min_efficiency=args.min_efficiency,
            topology=AFPMTopology(args.topology),
            prefer_halbach=args.prefer_halbach,
            ambient_temp_c=args.ambient_temp_c,
            max_winding_temp_c=args.max_winding_temp_c,
            convection_w_per_m2k=args.convection_w_per_m2k,
            iterations=args.iterations,
            num_candidates=args.num_candidates,
            num_planes=args.num_planes,
            run_3d_validation=not args.no_3d_validation,
            run_external_solvers=args.run_external_solvers,
            validation_refinement=args.validation_refinement,
        )
        result = AFPMDesignEngine(output_root=args.output).design(spec)
        print(result.artifacts.manifest_json)
        if result.validation_result:
            print(f"Validation: {'PASS' if result.validation_passed else 'FAIL'}")
            if result.validation_result.thermal.native_fea3d:
                fea = result.validation_result.thermal.native_fea3d
                print(f"3D Max Temp: {fea.max_temp_c:.1f} C ({result.validation_result.thermal.confidence})")
        return 0
    if args.command == "aerospace-review":
        package = AerospaceReviewEngine(output_root=args.output).run(
            AerospaceReviewSpec(
                name=args.name,
                target_power_kw=args.target_power_kw,
                target_speed_rpm=args.target_speed_rpm,
                dc_bus_voltage_v=args.dc_bus_voltage_v,
                max_outer_diameter_m=args.max_outer_diameter_m,
                coolant=args.coolant,
                design_life_hours=args.design_life_hours,
                iterations=args.iterations,
            )
        )
        print(package.output_dir)
        return 0
    if args.command == "aegis-pdr":
        package = AegisPDRGenerator(output_root=args.output).generate(
            AegisPDRSpec(
                name=args.name,
                target_power_kw=args.target_power_kw,
                target_speed_rpm=args.target_speed_rpm,
                dc_bus_voltage_v=args.dc_bus_voltage_v,
                max_outer_diameter_m=args.max_outer_diameter_m,
                coolant_temp_c=args.coolant_temp_c,
                monte_carlo_samples=args.monte_carlo_samples,
            )
        )
        print(package.output_dir)
        return 0
    if args.command == "afpm-bench":
        result = AFPMBenchEngine(output_root=args.output).build()
        print(result.output_dir)
        return 0
    if args.command == "gui":
        from neuroflux.gui import start_gui
        print(f"═" * 70)
        print(f"NeuroFlux Web GUI")
        print(f"═" * 70)
        print(f"Starting server at http://{args.host}:{args.port}")
        print(f"Press Ctrl+C to stop")
        print(f"═" * 70)
        start_gui(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return 0
    if args.command == "tool-check":
        from neuroflux.core.config import ExternalToolConfig
        config = ExternalToolConfig.auto_detect()
        config.print_status()
        if args.verbose:
            print("\nDetailed paths:")
            print(f"  ElmerSolver: {config.get_elmer_solver() or 'N/A'}")
            print(f"  ElmerGUI: {config.get_elmer_gui() or 'N/A'}")
            print(f"  Gmsh: {config.get_gmsh() or 'N/A'}")
            print(f"  FreeCAD: {config.get_freecad() or 'N/A'}")
            print(f"  ParaView: {config.get_paraview() or 'N/A'}")
        # Return success if at least one tool is available
        if config.elmer_available() or config.freecad_available() or config.paraview_available():
            return 0
        return 1
    if args.command == "visualize":
        from pathlib import Path
        from neuroflux.visualization import ResultVisualizer
        
        design_dir = Path(args.design_dir)
        if not design_dir.exists():
            print(f"Error: Design directory not found: {design_dir}")
            return 1
        
        visualizer = ResultVisualizer()
        
        # Find validation directory
        validation_dirs = list(design_dir.glob("validation/*"))
        if validation_dirs:
            results = visualizer.visualize_validation_results(validation_dirs[0])
            print("Visualization launched:")
            for result_type, success in results.items():
                status = "✓" if success else "✗"
                print(f"  {status} {result_type}")
            if any(results.values()):
                return 0
            print("No visualization files found. Run design with --run-external-solvers first.")
            return 1
        else:
            print(f"No validation results found in {design_dir}")
            return 1
    if args.command == "export-cad":
        from pathlib import Path
        from neuroflux.cad import FreeCADExporter
        from neuroflux.core.config import ExternalToolConfig
        import json
        
        design_dir = Path(args.design_dir)
        if not design_dir.exists():
            print(f"Error: Design directory not found: {design_dir}")
            return 1
        
        # Load design manifest
        manifest_path = design_dir / "design_manifest.json"
        if not manifest_path.exists():
            print(f"Error: Design manifest not found: {manifest_path}")
            return 1
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check FreeCAD availability
        config = ExternalToolConfig.auto_detect()
        if not config.freecad_available():
            print("Error: FreeCAD not found. Set NEUROFLUX_FREECAD environment variable.")
            return 1
        
        exporter = FreeCADExporter(config)
        output_path = Path(args.output)
        
        print(f"Exporting {args.component} to STEP...")
        # Parse geometry from manifest (best_candidate.analytical_input.geometry)
        # Import locally to avoid shadowing global AFPMTopology
        from neuroflux.core.models import MachineGeometry as MG, MagnetConfiguration as MC, MagnetType as MT
        
        geo_data = manifest["best_candidate"]["analytical_input"]["geometry"]
        geometry = MG(
            D_out=geo_data["D_out"],
            k_D=geo_data["k_D"],
            l_s=geo_data["l_s"],
            g=geo_data["g"],
            l_PM=geo_data["l_PM"],
            w_PM=geo_data.get("w_PM", 0.03),
            p=geo_data["p"],
            Q=geo_data["Q"],
            topology=AFPMTopology(geo_data["topology"]),
        )
        
        if args.component in ["stator", "both"]:
            result = exporter.export_stator_step(geometry, output_path)
            if result.success:
                print(f"✓ Stator exported: {result.step_path}")
            else:
                print(f"✗ Stator export failed: {result.message}")
                return 1
        
        if args.component in ["rotor", "both"]:
            magnet_config = MC(
                grade=geo_data.get("magnet_grade", "N42"),
                type=MT.CONVENTIONAL,
            )
            rotor_path = output_path.parent / (output_path.stem + "_rotor.step")
            result = exporter.export_rotor_step(geometry, rotor_path, magnet_config)
            if result.success:
                print(f"✓ Rotor exported: {result.step_path}")
            else:
                print(f"✗ Rotor export failed: {result.message}")
                return 1
        
        return 0
    if args.command == "auto":
        from neuroflux.automation import (
            MasterOrchestrator,
            AutomationConfig,
        )
        # AFPMGeneratorSpec already imported at top of file
        
        # Build automation configuration
        auto_config = AutomationConfig(
            output_root=args.output,
            run_external_solvers=args.run_external_solvers,
            run_visualization=args.visualize,
            run_cad_export=args.export_cad,
            enable_parallel=args.parallel,
            verbose=True,
        )
        
        # Build design specification
        auto_spec = AFPMGeneratorSpec(
            name=args.name,
            target_power_w=args.target_power_w,
            target_speed_rpm=args.target_speed_rpm,
            target_voltage_v=args.target_voltage_v,
            max_outer_diameter_m=args.max_diameter_m,
            min_efficiency=args.min_efficiency,
            run_3d_validation=True,
            run_external_solvers=args.run_external_solvers,
        )
        
        # Run full automation
        print(f"═" * 70)
        print(f"NeuroFlux Full Automation Pipeline")
        print(f"═" * 70)
        print(f"Design: {args.name}")
        print(f"Target: {args.target_power_w}W @ {args.target_speed_rpm}rpm, {args.target_voltage_v}V")
        print(f"External Solvers: {'Yes' if args.run_external_solvers else 'No'}")
        print(f"CAD Export: {'Yes' if args.export_cad else 'No'}")
        print(f"Visualization: {'Yes' if args.visualize else 'No'}")
        print(f"Parallel: {'Yes' if args.parallel else 'No'}")
        print(f"═" * 70)
        
        orchestrator = MasterOrchestrator(auto_config)
        auto_result = orchestrator.run(auto_spec, run_id=args.name)
        
        # Final summary
        print(f"\n{'═' * 70}")
        if auto_result.success:
            print(f"✅ AUTOMATION COMPLETE")
        else:
            print(f"❌ AUTOMATION FAILED")
        print(f"{'═' * 70}")
        print(f"Duration: {auto_result.duration_seconds:.2f}s")
        print(f"Output: {auto_result.output_directory}")
        print(f"Report: {auto_result.output_directory / 'automation_report.md'}")
        
        return 0 if auto_result.success else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
