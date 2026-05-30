"""Command-line entry point for the NeuroFlux autonomous lab."""

from __future__ import annotations

import argparse

from neuroflux.core.models import AFPMTopology
from neuroflux.discovery import DesignRequirements
from neuroflux.lab.autonomous_lab import AutonomousLab, LabRunConfig


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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
