#!/usr/bin/env python3
"""
DISCOVERY RUNNER - Steps 2-8
Mission: Discover patentable AFPM aerospace starter-generator
"""

import json
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from neuroflux.engines.analytical_engine import AnalyticalEngine
from neuroflux.core.models import (
    AnalyticalEngineInput, MachineGeometry, WindingParameters,
    OperatingPoint, AFPMTopology, MaterialProperties
)
from neuroflux.core.materials import MaterialDatabase

# Configuration
mat_db = MaterialDatabase()
materials = mat_db.build_material_properties('N42', 'M600-50A')
engine = AnalyticalEngine()

# ============================================================
# STEP 2: SEARCH SPACE
# ============================================================
SEARCH_SPACE = {
    'D_out': [0.15, 0.20, 0.25, 0.30, 0.35],
    'k_D': [0.55, 0.60, 0.65, 0.70],
    'p': [4, 6, 8, 10, 12, 16],
    'Q': [6, 9, 12, 15, 18, 21],
    'l_PM': [0.005, 0.008, 0.010, 0.012],
    'g': [0.002, 0.003, 0.004, 0.005],
    'fill_factor': [0.50, 0.55, 0.60, 0.65],
    'current_density': [3.0e6, 4.0e6, 5.0e6, 6.0e6],
    'topology': [AFPMTopology.DSSR_SLOTTED, AFPMTopology.SSDR_CORELESS,
                 AFPMTopology.YASA],
    'modular_segments': [1, 2, 3, 4, 6],
    'magnet_segments': [1, 2, 3, 4],
}

# ============================================================
# STEP 3: CONSTRAINT FILTERS
# ============================================================
class ConstraintFilter:
    """Real-world constraint validation."""

    MAX_TEMP = 150
    MIN_EFFICIENCY = 0.90
    MAX_SPEED_RPM = 6000

    @staticmethod
    def check_electromagnetic(geom: MachineGeometry) -> Tuple[bool, str]:
        if geom.g < 0.001:
            return False, 'Air gap too small'
        if geom.l_PM / geom.g < 0.5:
            return False, 'Magnet/Pole gap ratio insufficient'
        if geom.p > geom.Q * 2:
            return False, 'Pole/slot combination impractical'
        return True, 'OK'

    @staticmethod
    def check_thermal(power_w: float, losses_w: float) -> Tuple[bool, str]:
        loss_ratio = losses_w / power_w if power_w > 0 else 1.0
        if loss_ratio > 0.15:
            return False, f'Loss ratio {loss_ratio:.1%} too high'
        return True, 'OK'

    @staticmethod
    def check_mechanical(D_out: float, rpm: float) -> Tuple[bool, str]:
        tip_speed = 3.14159 * D_out * rpm / 60
        if tip_speed > 250:
            return False, f'Tip speed {tip_speed:.0f} m/s exceeds limit'
        return True, 'OK'

    @staticmethod
    def check_manufacturing(geom: MachineGeometry) -> Tuple[bool, str]:
        if geom.Q > 0:
            slot_pitch = 3.14159 * geom.D_out * geom.k_D / geom.Q
            if slot_pitch < 0.005:
                return False, f'Slot pitch {slot_pitch*1000:.1f}mm too small'
        return True, 'OK'

    @classmethod
    def validate_all(cls, geom: MachineGeometry, power_w: float,
                     losses_w: float, rpm: float) -> Tuple[bool, List[str]]:
        failures = []
        checks = [
            cls.check_electromagnetic(geom),
            cls.check_thermal(power_w, losses_w),
            cls.check_mechanical(geom.D_out, rpm),
            cls.check_manufacturing(geom),
        ]
        for passed, msg in checks:
            if not passed:
                failures.append(msg)
        return len(failures) == 0, failures

# ============================================================
# STEP 4: FITNESS FUNCTION
# ============================================================
class AerospaceFitness:
    """Multi-objective aerospace fitness."""

    WEIGHTS = {
        'power_density': 0.30,
        'thermal_margin': 0.20,
        'fault_tolerance': 0.15,
        'manufacturability': 0.15,
        'magnet_reduction': 0.10,
        'certification': 0.10,
    }

    @staticmethod
    def calculate(result, geom: MachineGeometry, modular: int = 1) -> Dict[str, float]:
        # Power Density (kW/kg)
        volume = 3.14159 * (geom.D_out/2)**2 * geom.l_s * 2
        mass = volume * 8000
        power_density = (result.power_w / 1000) / mass if mass > 0 else 0

        # Thermal Margin
        loss_ratio = result.total_losses_w / result.power_w if result.power_w > 0 else 1.0
        thermal_margin = max(0, 1 - loss_ratio * 5)

        # Fault Tolerance
        fault_tolerance = min(1.0, modular / 6)

        # Manufacturability
        manu_score = max(0, 1 - geom.p / 20)

        # Magnet Reduction
        magnet_volume = geom.l_PM * geom.w_PM * geom.p * 2
        magnet_score = max(0, 1 - magnet_volume / 0.01)

        # Certification
        cert_score = 0.8 if geom.topology == AFPMTopology.DSSR_SLOTTED else 0.6

        return {
            'power_density': power_density,
            'thermal_margin': thermal_margin,
            'fault_tolerance': fault_tolerance,
            'manufacturability': manu_score,
            'magnet_reduction': magnet_score,
            'certification': cert_score,
            'composite': (
                0.30 * power_density / 5.0 +
                0.20 * thermal_margin +
                0.15 * fault_tolerance +
                0.15 * manu_score +
                0.10 * magnet_score +
                0.10 * cert_score
            )
        }

# ============================================================
# CANDIDATE EVALUATION
# ============================================================
def evaluate_candidate(params: Dict) -> Optional[Dict]:
    """Evaluate single candidate with hypotheses."""

    geom = MachineGeometry(
        D_out=params['D_out'],
        k_D=params['k_D'],
        l_s=0.040,
        g=params['g'],
        l_PM=params['l_PM'],
        w_PM=0.025,
        p=params['p'],
        Q=params['Q'],
        topology=params['topology']
    )

    winding = WindingParameters(
        turns_per_phase=100,
        phases=3,
        fill_factor=params['fill_factor'],
        current_density=params['current_density']
    )

    op = OperatingPoint(speed_rpm=1800, I_rms=15.0)

    inp = AnalyticalEngineInput(
        geometry=geom,
        materials=materials,
        winding=winding,
        operating_point=op,
        num_planes=5
    )

    try:
        result = engine.run(inp)
    except Exception as e:
        return None

    # Constraints
    passed, failures = ConstraintFilter.validate_all(
        geom, result.power_w, result.total_losses_w, op.speed_rpm
    )
    if not passed:
        return None

    # Fitness
    fitness = AerospaceFitness.calculate(
        result, geom, modular=params.get('modular_segments', 1)
    )

    if fitness['composite'] < 0.3:
        return None

    # Hypothesis 5: Modular degradation
    n_modules = params.get('modular_segments', 1)
    degraded = []
    for failed in range(min(4, n_modules + 1)):
        remaining = max(1, n_modules - failed)
        ratio = remaining / n_modules if n_modules > 1 else 1.0
        degraded.append({'failed': failed, 'ratio': ratio})

    # Hypothesis 6: Magnet segmentation
    n_mag_segments = params.get('magnet_segments', 1)
    eddy_reduction = 1 - (0.15 * (n_mag_segments - 1) / 3)

    # Hypothesis 7: Thermal estimate
    max_temp = 70 + result.total_losses_w / 50

    return {
        'valid': True,
        'params': {
            'D_out': params['D_out'],
            'k_D': params['k_D'],
            'p': params['p'],
            'Q': params['Q'],
            'l_PM': params['l_PM'],
            'g': params['g'],
            'topology': str(params['topology']),
            'modular_segments': n_modules,
            'magnet_segments': n_mag_segments,
        },
        'power_w': result.power_w,
        'torque_nm': result.torque_nm,
        'efficiency': result.efficiency,
        'losses_w': result.total_losses_w,
        'fitness': fitness,
        'modular_degradation': degraded,
        'eddy_reduction': eddy_reduction,
        'thermal_c': max_temp,
    }

# ============================================================
# STEP 8: OPTIMIZATION
# ============================================================
def run_discovery(n_candidates: int = 100) -> List[Dict]:
    """Run discovery search."""
    print(f'Running {n_candidates} candidate evaluations...')

    candidates = []
    for i in range(n_candidates):
        params = {
            'D_out': random.choice(SEARCH_SPACE['D_out']),
            'k_D': random.choice(SEARCH_SPACE['k_D']),
            'p': random.choice(SEARCH_SPACE['p']),
            'Q': random.choice([s for s in SEARCH_SPACE['Q'] if s % 3 == 0]),
            'l_PM': random.choice(SEARCH_SPACE['l_PM']),
            'g': random.choice(SEARCH_SPACE['g']),
            'fill_factor': random.choice(SEARCH_SPACE['fill_factor']),
            'current_density': random.choice(SEARCH_SPACE['current_density']),
            'topology': random.choice(SEARCH_SPACE['topology']),
            'modular_segments': random.choice(SEARCH_SPACE['modular_segments']),
            'magnet_segments': random.choice(SEARCH_SPACE['magnet_segments']),
        }

        result = evaluate_candidate(params)
        if result:
            candidates.append(result)

        if (i + 1) % 20 == 0:
            print(f'  {i+1}/{n_candidates}, {len(candidates)} valid')

    candidates.sort(key=lambda x: x['fitness']['composite'], reverse=True)
    return candidates

if __name__ == '__main__':
    print('='*70)
    print('STEP 2-8: DISCOVERY RUNNER')
    print('='*70)

    results = run_discovery(n_candidates=100)

    print(f'\nFound {len(results)} valid candidates')
    if results:
        print(f'Best fitness: {results[0]["fitness"]["composite"]:.3f}')
        print(f'Best power density: {results[0]["fitness"]["power_density"]:.2f} kW/kg')
        print(f'Best candidate: {results[0]["params"]}')

    # Save
    Path('discovery_results').mkdir(exist_ok=True)
    with open('discovery_results/candidates.json', 'w') as f:
        json.dump(results[:20], f, indent=2)
    print('\nSaved to: discovery_results/candidates.json')
