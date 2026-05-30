# NeuroFlux Rust GUI

This is the desktop artifact dashboard for the autonomous AFPM lab.

The GUI deliberately reads `manifest.json` output from the Python lab instead of
owning physics state. That keeps the simulation backend reproducible and lets the
desktop layer evolve independently.

Run:

```bash
neuroflux-lab run --iterations 3 --output lab_runs
cargo run --manifest-path gui/neuroflux-gui/Cargo.toml -- lab_runs/<run-id>/manifest.json
```
