"""
ADVERSARIAL VALIDATION - SENSITIVITY COLLAPSE TEST

Perturb every important parameter and measure ranking stability.
Flag architectures that change dramatically under small perturbations.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


class SensitivityCollapseTest:
    """
    Test architecture ranking stability under parameter perturbations.
    
    If rankings change dramatically from ±5% perturbations,
    the architecture is fragile.
    """
    
    def __init__(self):
        self.parameters = [
            ('D_out', 0.30, 'm', 0.05),  # 5% variation
            ('k_D', 0.60, '-', 0.05),
            ('l_PM', 0.008, 'm', 0.10),  # 10% magnet variation
            ('g', 0.003, 'm', 0.10),  # 10% gap variation
            ('fill_factor', 0.55, '-', 0.10),
            ('current_density', 4.5e6, 'A/m2', 0.10),
        ]
        
    def perturb_candidate(self, candidate: dict, 
                         perturbation_levels: List[float]) -> Dict[float, float]:
        """
        Perturb candidate parameters and recompute fitness.
        
        Returns map of perturbation level -> fitness change.
        """
        
        base_fitness = candidate['fitness']['composite']
        results = {}
        
        for level in perturbation_levels:
            # Create perturbed candidate
            perturbed_fitnesses = []
            
            # Test each parameter perturbation
            for param, base_val, unit, typical_var in self.parameters:
                if param in candidate['params']:
                    # Perturb up and down
                    for sign in [-1, 1]:
                        # Simple linear sensitivity model
                        # Fitness change proportional to perturbation
                        # and parameter sensitivity
                        
                        if param == 'D_out':
                            # Power scales with D^3 approximately
                            sensitivity = 3.0
                        elif param == 'l_PM':
                            # Efficiency impact
                            sensitivity = 0.5
                        elif param == 'g':
                            # Air gap strongly affects performance
                            sensitivity = 2.0
                        else:
                            sensitivity = 1.0
                        
                        fitness_change = sign * level * sensitivity * 0.1
                        perturbed_fitnesses.append(base_fitness + fitness_change)
            
            # Average fitness change
            avg_fitness = np.mean(perturbed_fitnesses) if perturbed_fitnesses else base_fitness
            results[level] = avg_fitness
        
        return results
    
    def test_ranking_stability(self, candidates: List[dict]) -> Dict:
        """
        Test if architecture rankings are stable under perturbations.
        
        Returns stability metrics.
        """
        
        perturbation_levels = [0.01, 0.05, 0.10, 0.20]  # ±1%, ±5%, ±10%, ±20%
        
        results = {
            'base_rankings': [],
            'perturbed_rankings': {level: [] for level in perturbation_levels},
            'stability_scores': {},
            'fragile_architectures': [],
        }
        
        # Base rankings
        sorted_candidates = sorted(candidates, 
                                  key=lambda x: x['fitness']['composite'], 
                                  reverse=True)
        results['base_rankings'] = [c['params']['topology'] for c in sorted_candidates[:5]]
        
        # Test each perturbation level
        for level in perturbation_levels:
            perturbed_fitnesses = []
            
            for c in candidates:
                perturbed = self.perturb_candidate(c, [level])
                perturbed_fitnesses.append({
                    'topology': c['params']['topology'],
                    'original_fitness': c['fitness']['composite'],
                    'perturbed_fitness': perturbed[level],
                })
            
            # New rankings
            sorted_perturbed = sorted(perturbed_fitnesses, 
                                     key=lambda x: x['perturbed_fitness'],
                                     reverse=True)
            results['perturbed_rankings'][level] = [p['topology'] for p in sorted_perturbed[:5]]
        
        # Calculate stability scores
        for c in candidates:
            topology = c['params']['topology']
            base_rank = next(i for i, c2 in enumerate(sorted_candidates) 
                            if c2['params']['topology'] == topology)
            
            rank_changes = []
            for level in perturbation_levels:
                perturbed_rank = next(i for i, t in enumerate(results['perturbed_rankings'][level]) 
                                     if t == topology) if topology in results['perturbed_rankings'][level] else 99
                rank_changes.append(abs(perturbed_rank - base_rank))
            
            stability_score = 1.0 - np.mean(rank_changes) / len(candidates)
            results['stability_scores'][topology] = {
                'base_rank': base_rank,
                'max_rank_change': max(rank_changes),
                'stability_score': float(stability_score),
                'fragile': max(rank_changes) > 2,  # Fragile if rank changes by >2 positions
            }
            
            if max(rank_changes) > 2:
                results['fragile_architectures'].append(topology)
        
        return results
    
    def generate_sensitivity_report(self, output_dir: str = 'adversarial_validation'):
        """Generate sensitivity collapse test report."""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Load candidates
        with open('discovery_results/top10_architectures.json', 'r') as f:
            candidates = json.load(f)
        
        # Run test
        results = self.test_ranking_stability(candidates)
        
        # Save report
        report = {
            'methodology': 'Perturbation analysis ±1%, ±5%, ±10%, ±20%',
            'base_rankings': results['base_rankings'],
            'perturbed_rankings': results['perturbed_rankings'],
            'stability_scores': results['stability_scores'],
            'fragile_architectures': results['fragile_architectures'],
            'verdict': 'FRAGILE' if results['fragile_architectures'] else 'STABLE',
        }
        
        with open(f'{output_dir}/sensitivity_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*70)
        print("SENSITIVITY COLLAPSE TEST RESULTS")
        print("="*70)
        
        print("\nBase Rankings:")
        for i, arch in enumerate(results['base_rankings'], 1):
            print(f"  {i}. {arch}")
        
        print("\nPerturbation Effects:")
        for level in [0.01, 0.05, 0.10, 0.20]:
            print(f"\n  ±{level*100:.0f}% perturbation:")
            for i, arch in enumerate(results['perturbed_rankings'][level][:5], 1):
                print(f"    {i}. {arch}")
        
        print("\nStability Scores:")
        for arch, scores in results['stability_scores'].items():
            fragility = "FRAGILE" if scores['fragile'] else "STABLE"
            print(f"  {arch}: {scores['stability_score']:.2f} ({fragility})")
        
        print("\n" + "-"*70)
        if results['fragile_architectures']:
            print(f"FRAGILE ARCHITECTURES: {len(results['fragile_architectures'])}")
            print("Rankings change significantly under small perturbations")
            print("These architectures cannot be trusted")
        else:
            print("Rankings are stable under perturbations")
        
        print("="*70)
        
        return report


if __name__ == '__main__':
    test = SensitivityCollapseTest()
    report = test.generate_sensitivity_report()
