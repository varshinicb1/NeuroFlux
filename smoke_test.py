#!/usr/bin/env python3
"""Smoke test for NeuroFlux GUI and automation.

Run this to verify the system is working:
    python smoke_test.py
"""

import sys
import tempfile
from pathlib import Path

print("=" * 70)
print("NEUROFLUX SMOKE TEST")
print("=" * 70)

# Test 1: Import all modules
print("\n[1/5] Testing imports...")
try:
    from neuroflux.automation import MasterOrchestrator, AutomationConfig
    from neuroflux.design.engine import AFPMGeneratorSpec
    from neuroflux.gui.server import GUIServer
    from neuroflux.core.config import ExternalToolConfig
    print("  OK All imports successful")
except Exception as e:
    print(f"  FAIL Import error: {e}")
    sys.exit(1)

# Test 2: Create automation config
print("\n[2/5] Testing automation config...")
try:
    config = AutomationConfig(
        output_root=tempfile.mkdtemp(),
        run_external_solvers=False,
        run_visualization=False,
        run_cad_export=False,
    )
    print(f"  OK Config created (workers={config.max_workers})")
except Exception as e:
    print(f"  FAIL Config error: {e}")
    sys.exit(1)

# Test 3: Run mini automation
print("\n[3/5] Testing automation pipeline...")
try:
    orchestrator = MasterOrchestrator(config)
    spec = AFPMGeneratorSpec(
        name="smoke-test",
        target_power_w=100,
        target_speed_rpm=600,
        target_voltage_v=24,
        iterations=1,
        num_candidates=1,
    )
    result = orchestrator.run(spec, run_id="smoke_run")
    
    if result.stages["discovery"].is_success:
        print(f"  OK Discovery completed in {result.stages['discovery'].duration_ms:.0f}ms")
    else:
        print(f"  WARN Discovery did not complete")
        
    if result.design_result:
        print(f"  OK Design generated: {result.design_result.spec.name}")
    else:
        print(f"  WARN No design result")
except Exception as e:
    print(f"  FAIL Automation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check external tools (REQUIRED)
print("\n[4/5] Testing external tools (REQUIRED)...")
try:
    tool_config = ExternalToolConfig.auto_detect()
    tools = {
        "Elmer": tool_config.elmer_available(),
        "FreeCAD": tool_config.freecad_available(),
        "ParaView": tool_config.paraview_available(),
        "Gmsh": tool_config.get_gmsh() is not None,
    }
    
    all_available = True
    for name, available in tools.items():
        if available:
            print(f"  OK {name}")
        else:
            print(f"  FAIL {name} is REQUIRED but not found")
            all_available = False
    
    if not all_available:
        print("\n  ERROR: External tools are compulsory!")
        print("  Set environment variables:")
        print("    NEUROFLUX_ELMER_SOLVER")
        print("    NEUROFLUX_ELMER_GUI")
        print("    NEUROFLUX_GMSH")
        print("    NEUROFLUX_FREECAD")
        print("    NEUROFLUX_PARAVIEW")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL Tool config error: {e}")
    sys.exit(1)

# Test 5: Check GUI templates
print("\n[5/5] Testing GUI templates...")
try:
    template_dir = Path(__file__).parent / "neuroflux" / "gui" / "templates"
    required_templates = ["base.html", "index.html", "design.html"]
    
    for template in required_templates:
        template_path = template_dir / template
        if template_path.exists():
            print(f"  OK {template}")
        else:
            print(f"  FAIL {template} not found")
            sys.exit(1)
except Exception as e:
    print(f"  FAIL Template error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("SMOKE TEST PASSED")
print("=" * 70)
print("\nTo start the GUI, run:")
print("  python -m neuroflux.lab.cli gui --port 8080")
print("\nThen open http://127.0.0.1:8080 in your browser.")
