"""Command-line entry point for the NeuroFlux autonomous lab."""

from __future__ import annotations

import argparse

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
        )
        result = AFPMDesignEngine(output_root=args.output).design(spec)
        print(result.artifacts.manifest_json)
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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
