"""
Grand Unified AFPM Matrix (GUM)

Mathematical representation of the complete AFPM low-speed aerospace generator
design landscape. Canonical model for all simulations, optimizations, and analysis.

State-space representation:
    x_dot = A @ x + B @ u + D @ d
    y = C @ x

Where:
    x: 166-element state vector covering 12 domains:
       - Electromagnetic (17 states)
       - Thermal (15 states)
       - Mechanical (15 states)
       - Structural (16 states)
       - Manufacturing (14 states)
       - Fault (15 states)
       - Reliability (14 states)
       - Certification (13 states)
       - Patent (10 states)
       - Economic (13 states)
       - Control (12 states)
       - Operational (12 states)
    
    A: Grand Coupling Matrix (166x166) - captures all domain interactions
    B: Control/Input Matrix (166x10)
    D: Disturbance Matrix (166x8)
    C: Output Matrix (20x166)

Assessment Matrices:
    - Dependency Matrix: Parameter relationships (0-10 scale)
    - Fault Survivability Matrix: Performance under faults
    - Certification Feasibility Matrix: Certification metrics
    - Patent Opportunity Matrix: Novelty and patent potential
    - Aerospace Suitability Matrix: Aerospace requirement compliance

Usage:
    from neuroflux.gum import create_gum, GrandUnifiedAFPMModel
    
    # Create complete GUM
    gum = create_gum(output_dir='gum_results')
    
    # Access state-space matrices
    A = gum.A  # Grand Coupling Matrix
    B = gum.B  # Input Matrix
    outputs = gum.compute_outputs()
    
    # Access assessment matrices
    patent_scores = gum.patent_opportunity.get_top_opportunities(3)
    aerospace_rankings = gum.aerospace_suitability.get_rankings()
"""

from .states import (
    Domain,
    GrandStateVector,
    EMStates, ThermalStates, MechanicalStates, StructuralStates,
    ManufacturingStates, FaultStates, ReliabilityStates,
    CertificationStates, PatentStates, EconomicStates,
    ControlStates, OperationalStates,
)

from .coupling_matrix import GrandCouplingMatrix

from .matrices import (
    DependencyMatrix,
    FaultSurvivabilityMatrix,
    CertificationFeasibilityMatrix,
    PatentOpportunityMatrix,
    AerospaceSuitabilityMatrix,
    export_all_matrices,
)

from .grand_unified_model import GrandUnifiedAFPMModel, create_gum

__all__ = [
    # Main model
    'GrandUnifiedAFPMModel',
    'create_gum',
    
    # Domains
    'Domain',
    'GrandStateVector',
    
    # State classes
    'EMStates',
    'ThermalStates',
    'MechanicalStates',
    'StructuralStates',
    'ManufacturingStates',
    'FaultStates',
    'ReliabilityStates',
    'CertificationStates',
    'PatentStates',
    'EconomicStates',
    'ControlStates',
    'OperationalStates',
    
    # Matrices
    'GrandCouplingMatrix',
    'DependencyMatrix',
    'FaultSurvivabilityMatrix',
    'CertificationFeasibilityMatrix',
    'PatentOpportunityMatrix',
    'AerospaceSuitabilityMatrix',
    'export_all_matrices',
]

__version__ = '1.0.0'
