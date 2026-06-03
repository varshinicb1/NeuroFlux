#!/usr/bin/env python3
"""Performance profiling script for NeuroFlux.

Profiles the discovery workflow and identifies optimization opportunities.
"""

import cProfile
import io
import pstats
import time
from contextlib import contextmanager
from pathlib import Path

from neuroflux.core.models import AFPMTopology
from neuroflux.discovery import DesignRequirements, DiscoveryWorkflow


@contextmanager
def timer(name: str):
    """Simple context manager for timing code blocks."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"  {name}: {elapsed:.3f}s")


def profile_discovery():
    """Profile the discovery workflow."""
    print("=" * 70)
    print("DISCOVERY WORKFLOW PROFILING")
    print("=" * 70)
    
    requirements = DesignRequirements(
        target_power_w=500.0,
        target_speed_rpm=600.0,
        target_voltage_v=48.0,
        max_outer_diameter_m=0.32,
        min_efficiency=0.50,
        topology=AFPMTopology.DSSR_SLOTTED,
        num_candidates=10,
        num_planes=7,
    )
    
    # Warm up
    print("\n[1/3] Warm-up run...")
    _ = DiscoveryWorkflow().run(requirements)
    
    # Profile with cProfile
    print("\n[2/3] Profiling with cProfile...")
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = DiscoveryWorkflow().run(requirements)
    
    profiler.disable()
    
    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)  # Top 30 functions
    print(s.getvalue())
    
    # Benchmark run
    print("\n[3/3] Benchmark runs...")
    times = []
    for i in range(3):
        start = time.perf_counter()
        _ = DiscoveryWorkflow().run(requirements)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.3f}s")
    
    avg_time = sum(times) / len(times)
    print(f"\n  Average: {avg_time:.3f}s")
    print(f"  Best: {min(times):.3f}s")
    print(f"  Worst: {max(times):.3f}s")
    print(f"  Candidates/sec: {requirements.num_candidates / avg_time:.1f}")


def profile_components():
    """Profile individual components."""
    print("\n" + "=" * 70)
    print("COMPONENT BREAKDOWN")
    print("=" * 70)
    
    from neuroflux.engines.analytical_engine import AnalyticalEngine
    from neuroflux.core.models import (
        AnalyticalEngineInput,
        MachineGeometry,
        MagnetConfiguration,
        MagnetType,
        OperatingPoint,
        WindingParameters,
    )
    
    # Create sample input
    geometry = MachineGeometry(
        outer_diameter_m=0.2,
        inner_diameter_m=0.1,
        axial_length_m=0.05,
        airgap_m=0.001,
        pole_pairs=8,
        slots_per_phase_per_pole=2,
    )
    
    magnet_config = MagnetConfiguration(
        magnet_type=MagnetType.NDFEB,
        grade="N42",
        thickness_m=0.005,
        pole_arc_ratio=0.8,
        is_halbach=False,
    )
    
    winding = WindingParameters(
        turns_per_coil=50,
        parallel_paths=1,
        wire_diameter_mm=1.0,
        fill_factor=0.6,
        winding_factor=0.95,
    )
    
    operating_point = OperatingPoint(
        speed_rpm=600.0,
        voltage_v=48.0,
        power_w=250.0,
        torque_nm=4.0,
        efficiency=0.85,
    )
    
    analytical_input = AnalyticalEngineInput(
        geometry=geometry,
        magnet_config=magnet_config,
        winding=winding,
        operating_point=operating_point,
        topology=AFPMTopology.DSSR_SLOTTED,
    )
    
    # Profile analytical engine
    print("\n[1/4] Analytical Engine...")
    engine = AnalyticalEngine()
    
    with timer("Single evaluation"):
        _ = engine.evaluate(analytical_input)
    
    # Profile multiple evaluations
    print("\n[2/4] Batch evaluation (100 runs)...")
    start = time.perf_counter()
    for _ in range(100):
        _ = engine.evaluate(analytical_input)
    elapsed = time.perf_counter() - start
    print(f"  Total: {elapsed:.3f}s")
    print(f"  Per evaluation: {elapsed/100*1000:.2f}ms")
    
    # Profile geometry operations
    print("\n[3/4] Geometry calculations...")
    from neuroflux.analytical.geometry import GeometryCalculator
    
    calc = GeometryCalculator()
    
    with timer("Volume calculations (1000 runs)"):
        for _ in range(1000):
            _ = calc.magnet_volume(geometry, magnet_config)
    
    # Profile thermal calculations
    print("\n[4/4] Thermal calculations...")
    from neuroflux.analytical.thermal import ThermalCalculator
    
    thermal = ThermalCalculator()
    
    with timer("Lumped thermal model (1000 runs)"):
        for _ in range(1000):
            _ = thermal.lumped_steady_state(
                losses_w=100.0,
                surface_area_m2=0.5,
                ambient_c=40.0,
                h_w_per_m2k=15.0,
            )


def suggest_optimizations():
    """Suggest optimization strategies."""
    print("\n" + "=" * 70)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 70)
    
    recommendations = [
        ("1. Vectorized Calculations",
         "Use NumPy vectorization for batch candidate evaluation",
         "Potential: 5-10x speedup for large batches"),
        
        ("2. Caching",
         "Cache geometry calculations and material properties",
         "Potential: 2-3x speedup for repeated evaluations"),
        
        ("3. Parallel Discovery",
         "Evaluate candidates in parallel using multiprocessing",
         "Potential: Near-linear scaling with CPU cores"),
        
        ("4. Surrogate Models",
         "Train ML surrogate for rapid screening",
         "Potential: 100x+ speedup for initial screening"),
        
        ("5. JIT Compilation",
         "Use Numba/JAX for hot numerical loops",
         "Potential: 10-50x speedup for thermal/EM calculations"),
        
        ("6. Reduced Fidelity",
         "Use coarser thermal models for initial screening",
         "Potential: 3-5x speedup, refine best candidates only"),
        
        ("7. Memory Preallocation",
         "Preallocate arrays for batch operations",
         "Potential: 20-30% reduction in GC overhead"),
    ]
    
    for title, desc, potential in recommendations:
        print(f"\n{title}")
        print(f"  Strategy: {desc}")
        print(f"  {potential}")


def main():
    """Run all profiling."""
    print("NeuroFlux Performance Profiler\n")
    
    try:
        profile_discovery()
    except Exception as e:
        print(f"Discovery profiling failed: {e}")
    
    try:
        profile_components()
    except Exception as e:
        print(f"Component profiling failed: {e}")
    
    suggest_optimizations()
    
    print("\n" + "=" * 70)
    print("PROFILING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
