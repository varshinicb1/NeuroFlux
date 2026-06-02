"""
Grand Unified AFPM Model (GUM)

Canonical state-space representation of the complete AFPM design universe.

State equation:
    x_dot = A @ x + B @ u + D @ d

Output equation:
    y = C @ x

Where:
    x: 166-element state vector (12 domains)
    A: Grand Coupling Matrix (166x166)
    B: Control/Input Matrix (166 x n_inputs)
    D: Disturbance Matrix (166 x n_disturbances)
    u: Control inputs
    d: Disturbances
    y: Outputs
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .states import (
    GrandStateVector, Domain,
    EMStates, ThermalStates, MechanicalStates, StructuralStates,
    ManufacturingStates, FaultStates, ReliabilityStates,
    CertificationStates, PatentStates, EconomicStates,
    ControlStates, OperationalStates
)
from .coupling_matrix import GrandCouplingMatrix
from .matrices import (
    DependencyMatrix, FaultSurvivabilityMatrix,
    CertificationFeasibilityMatrix, PatentOpportunityMatrix,
    AerospaceSuitabilityMatrix, export_all_matrices
)


class GrandUnifiedAFPMModel:
    """
    Complete Grand Unified AFPM Model (GUM).
    
    The canonical mathematical representation of the AFPM design space.
    All simulations, optimizations, and analyses derive from this model.
    """
    
    def __init__(self):
        # State vector dimension
        self.n_states = GrandStateVector.total_size()
        
        # Domain sizes
        self.domain_sizes = GrandStateVector.get_domain_sizes()
        
        # Grand Coupling Matrix A (166x166)
        self.coupling = GrandCouplingMatrix()
        self.A = self.coupling.A
        
        # Input/Control Matrix B
        self.n_inputs = 10
        self.B = self._build_input_matrix()
        
        # Disturbance Matrix D
        self.n_disturbances = 8
        self.D = self._build_disturbance_matrix()
        
        # Output Matrix C
        self.n_outputs = 20
        self.C = self._build_output_matrix()
        
        # Assessment matrices
        self.dependency = None
        self.fault_survivability = None
        self.certification_feasibility = None
        self.patent_opportunity = None
        self.aerospace_suitability = None
        
        # Current state
        self.state = GrandStateVector()
        
        print(f"GUM Initialized: {self.n_states} states, {self.n_inputs} inputs, "
              f"{self.n_disturbances} disturbances, {self.n_outputs} outputs")
    
    def _build_input_matrix(self) -> np.ndarray:
        """Build control input matrix B."""
        B = np.zeros((self.n_states, self.n_inputs))
        
        # Define control inputs:
        # 0: Voltage command
        # 1: Current command
        # 2: Speed command
        # 3: Torque command
        # 4: Cooling flow rate
        # 5: PWM duty cycle
        # 6: Field weakening command
        # 7: Fault isolation trigger
        # 8: Segment enable/disable
        # 9: Control mode select
        
        # Map to EM domain states
        em_start = 0
        B[em_start + 3, 0] = 1.0    # Voltage -> back EMF
        B[em_start + 2, 1] = 1.0    # Current -> J_conductor
        B[em_start + 4, 2] = 1.0    # Speed -> f_electrical
        B[em_start + 6, 3] = 1.0    # Torque -> torque_EM
        
        # Map to Thermal domain
        th_start = 17
        B[th_start + 14, 4] = 1.0   # Cooling flow -> cooling_power
        
        # Map to Control domain
        ctrl_start = 154
        B[ctrl_start + 10, 9] = 1.0  # Mode select -> control_mode
        
        # Map to Fault domain
        fault_start = 80
        B[fault_start + 5, 7] = 1.0   # Isolation trigger -> segment_isolation
        B[fault_start + 6, 8] = 1.0   # Segment enable -> phase_loss
        
        return B
    
    def _build_disturbance_matrix(self) -> np.ndarray:
        """Build disturbance matrix D."""
        D = np.zeros((self.n_states, self.n_disturbances))
        
        # Disturbances:
        # 0: Ambient temperature change
        # 1: Altitude change
        # 2: Load torque disturbance
        # 3: Voltage sag
        # 4: Bearing wear rate
        # 5: Magnet degradation
        # 6: Cooling degradation
        # 7: Vibration input
        
        # Ambient temp -> thermal states
        th_start = 17
        D[th_start + 4, 0] = 1.0    # T_coolant_in
        D[th_start + 6, 0] = 0.5    # delta_T_winding
        
        # Altitude -> thermal (convection)
        D[th_start + 8, 1] = 1.0    # h_convection
        
        # Load torque -> mechanical
        mech_start = 32
        D[mech_start + 2, 2] = 1.0   # torque_load
        
        # Voltage sag -> EM
        em_start = 0
        D[em_start + 3, 3] = 1.0    # E_back_emf
        
        # Bearing wear -> fault
        fault_start = 80
        D[fault_start + 3, 4] = 1.0   # fault_bearing_wear
        
        # Magnet degradation -> fault
        D[fault_start + 2, 5] = 1.0   # fault_magnet_demag
        
        # Cooling degradation -> fault
        D[fault_start + 7, 6] = 1.0   # fault_cooling_failure
        
        # Vibration -> mechanical
        D[mech_start + 11, 7] = 1.0   # vibration_displacement
        
        return D
    
    def _build_output_matrix(self) -> np.ndarray:
        """Build output matrix C."""
        C = np.zeros((self.n_outputs, self.n_states))
        
        # Key outputs:
        # 0: Power output
        # 1: Efficiency
        # 2: Torque
        # 3: Winding temperature
        # 4: Magnet temperature
        # 5: Vibration level
        # 6: Stress level
        # 7: Fault severity
        # 8: Reliability index
        # 9: Certification score
        # 10: Patent potential
        # 11: Unit cost
        # 12: Overall fitness
        # 13: Power density
        # 14: Thermal margin
        # 15: Fault tolerance score
        # 16: Manufacturability
        # 17: Health index
        # 18: Degraded power available
        # 19: Tip speed
        
        # Map from state vector
        C[0, 5] = 1.0    # Power
        C[1, 8] = 1.0    # Efficiency
        C[2, 6] = 1.0    # Torque
        C[3, 17] = 1.0   # T_winding
        C[4, 18] = 1.0   # T_magnet
        C[5, 43] = 1.0   # vibration_displacement
        C[6, 47] = 1.0   # stress_von_mises_stator
        C[7, 89] = 1.0   # fault_severity_index
        C[8, 96] = 1.0   # MTBF (reliability proxy)
        C[9, 110] = 1.0  # DO160_compliance
        C[10, 123] = 1.0 # novelty_score
        C[11, 133] = 1.0 # unit_cost
        C[15, 86] = 1.0  # degraded_power_available
        C[17, 109] = 1.0 # health_index
        C[19, 35] = 1.0  # tip_speed
        
        # Derived outputs (combinations)
        # Power density = Power / (mass estimation)
        # C[13] will be computed dynamically
        
        return C
    
    def compute_outputs(self, state: Optional[GrandStateVector] = None) -> Dict[str, float]:
        """Compute output vector from current state."""
        if state is None:
            state = self.state
        
        x = state.to_array()
        y = self.C @ x
        
        # Compute derived outputs
        power = y[0]
        efficiency = y[1]
        mass_estimate = 45.0  # kg (simplified)
        power_density = power / mass_estimate if mass_estimate > 0 else 0
        
        # Thermal margin
        T_max = x[17]  # T_winding
        T_limit = 150.0
        thermal_margin = (T_limit - T_max) / T_limit if T_limit > 0 else 0
        
        # Overall fitness (simplified aerospace fitness)
        fitness = (
            0.30 * power_density / 5.0 +
            0.20 * thermal_margin +
            0.15 * y[15] +  # fault tolerance
            0.15 * x[74] +  # manufacturability
            0.10 * (1 - x[133] / 10000) +  # magnet cost reduction
            0.10 * y[9]   # certification
        )
        
        return {
            'power_W': float(y[0]),
            'efficiency': float(y[1]),
            'torque_Nm': float(y[2]),
            'T_winding_C': float(y[3]),
            'T_magnet_C': float(y[4]),
            'vibration_m': float(y[5]),
            'stress_Pa': float(y[6]),
            'fault_severity': float(y[7]),
            'reliability_index': float(y[8]),
            'certification_score': float(y[9]),
            'patent_potential': float(y[10]),
            'unit_cost_$': float(y[11]),
            'overall_fitness': float(fitness),
            'power_density_kW_kg': float(power_density),
            'thermal_margin': float(thermal_margin),
            'fault_tolerance_score': float(y[15]),
            'manufacturability': float(x[74]),
            'health_index': float(y[17]),
            'degraded_power_pct': float(y[18] * 100),
            'tip_speed_m_s': float(y[19]),
        }
    
    def step(self, u: np.ndarray, d: np.ndarray, dt: float = 0.001) -> GrandStateVector:
        """Simulate one time step of the state-space model."""
        x = self.state.to_array()
        
        # State update: x_dot = A @ x + B @ u + D @ d
        x_dot = self.A @ x + self.B @ u + self.D @ d
        
        # Euler integration
        x_new = x + x_dot * dt
        
        # Update state object (simplified - would need proper mapping)
        # For now, just update the internal state array
        self._update_state_from_array(x_new)
        
        return self.state
    
    def _update_state_from_array(self, x_array: np.ndarray):
        """Update state object from array representation."""
        # This would map array elements back to state fields
        # Simplified implementation
        pass
    
    def get_domain_coupling_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of coupling strengths between all domains."""
        summary = {}
        for from_d in Domain:
            summary[from_d.name] = {}
            for to_d in Domain:
                strength = self.coupling.get_domain_coupling_strength(from_d, to_d)
                if strength > 0.01:  # Only non-trivial couplings
                    summary[from_d.name][to_d.name] = float(strength)
        return summary
    
    def export_model(self, filepath: str):
        """Export complete GUM model to JSON."""
        data = {
            'model': {
                'n_states': self.n_states,
                'n_inputs': self.n_inputs,
                'n_disturbances': self.n_disturbances,
                'n_outputs': self.n_outputs,
                'domain_sizes': self.domain_sizes,
            },
            'matrices': {
                'A_shape': self.A.shape,
                'B_shape': self.B.shape,
                'D_shape': self.D.shape,
                'C_shape': self.C.shape,
                'A_sparse': self._matrix_to_sparse_dict(self.A),
            },
            'coupling_summary': self.get_domain_coupling_summary(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _matrix_to_sparse_dict(self, M: np.ndarray, threshold: float = 0.01) -> Dict:
        """Convert dense matrix to sparse dictionary representation."""
        sparse = {}
        rows, cols = np.where(np.abs(M) > threshold)
        for i, j in zip(rows, cols):
            sparse[f"{i},{j}"] = float(M[i, j])
        return sparse
    
    def build_assessment_matrices(self, output_dir: str = 'gum_results'):
        """Build and export all assessment matrices."""
        print("\nBuilding assessment matrices...")
        
        matrices = export_all_matrices(output_dir)
        
        self.dependency = matrices['dependency']
        self.fault_survivability = matrices['fault']
        self.certification_feasibility = matrices['certification']
        self.patent_opportunity = matrices['patent']
        self.aerospace_suitability = matrices['aerospace']
        
        print(f"Assessment matrices exported to {output_dir}/")
        
        # Print summary
        print("\n=== GUM ASSESSMENT SUMMARY ===")
        
        # Top patent opportunities
        top_patents = self.patent_opportunity.get_top_opportunities(3)
        print("\nTop Patent Opportunities:")
        for feature, score in top_patents:
            print(f"  {feature}: {score:.2f}")
        
        # Aerospace rankings
        rankings = self.aerospace_suitability.get_rankings()
        print("\nAerospace Suitability Rankings:")
        for arch, score in rankings:
            print(f"  {arch}: {score:.2f}")
        
        # Fault survivability
        print("\nFault Survivability (6-module system):")
        for fault in ['single_segment_failure', 'phase_a_loss', 'thermal_runaway']:
            score = self.fault_survivability.get_overall_survivability(fault)
            print(f"  {fault}: {score:.1f}/10")


def create_gum(output_dir: str = 'gum_results') -> GrandUnifiedAFPMModel:
    """Create and initialize the complete Grand Unified AFPM Model."""
    Path(output_dir).mkdir(exist_ok=True)
    
    print("="*70)
    print("GRAND UNIFIED AFPM MATRIX (GUM)")
    print("="*70)
    print("\nInitializing canonical state-space model...")
    
    # Create model
    gum = GrandUnifiedAFPMModel()
    
    # Export model matrices
    gum.export_model(f'{output_dir}/grand_unified_model.json')
    print(f"\nModel exported to {output_dir}/grand_unified_model.json")
    
    # Build assessment matrices
    gum.build_assessment_matrices(output_dir)
    
    # Compute baseline outputs
    outputs = gum.compute_outputs()
    
    print("\n" + "="*70)
    print("BASELINE OUTPUTS (Initialized State)")
    print("="*70)
    for key, value in outputs.items():
        print(f"  {key:25s}: {value:10.4f}")
    
    print("\n" + "="*70)
    print("GUM CONSTRUCTION COMPLETE")
    print("="*70)
    print(f"\nTotal state dimension: {gum.n_states}")
    print(f"Total coupling entries: {np.count_nonzero(gum.A)}")
    print(f"Domain coverage: 12 domains")
    print(f"\nAll artifacts saved to: {output_dir}/")
    
    return gum


if __name__ == '__main__':
    gum = create_gum()
