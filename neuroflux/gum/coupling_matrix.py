"""
Grand Unified AFPM Matrix - Coupling Matrix

Defines the Grand Coupling Matrix A where:
    x_dot = A @ x + B @ u + D @ d

Captures all known domain couplings with quantified strengths (0-10 scale).
"""

import numpy as np
from typing import List, Tuple, Dict
from .states import Domain


class GrandCouplingMatrix:
    """
    Grand Coupling Matrix (A) for state-space representation.
    Block matrix with sub-matrices for all domain interactions.
    """
    
    # Domain sizes (must match states.py)
    DOMAIN_SIZES = {
        Domain.ELECTROMAGNETIC: 17,
        Domain.THERMAL: 15,
        Domain.MECHANICAL: 15,
        Domain.STRUCTURAL: 16,
        Domain.MANUFACTURING: 14,
        Domain.FAULT: 15,
        Domain.RELIABILITY: 14,
        Domain.CERTIFICATION: 13,
        Domain.PATENT: 10,
        Domain.ECONOMIC: 13,
        Domain.CONTROL: 12,
        Domain.OPERATIONAL: 12,
    }
    
    def __init__(self):
        self.n_states = sum(self.DOMAIN_SIZES.values())
        self.A = np.zeros((self.n_states, self.n_states))
        self._build_coupling_matrix()
        self._normalize_matrix()
    
    def _get_domain_indices(self, domain: Domain) -> Tuple[int, int]:
        """Get start and end indices for a domain."""
        domains = list(Domain)
        start = sum([self.DOMAIN_SIZES[d] for d in domains[:domains.index(domain)]])
        end = start + self.DOMAIN_SIZES[domain]
        return start, end
    
    def _build_coupling_matrix(self):
        """Build all coupling sub-matrices with defined strengths."""
        couplings = self._define_all_couplings()
        
        for (from_domain, from_idx), (to_domain, to_idx), strength in couplings:
            from_start, _ = self._get_domain_indices(from_domain)
            to_start, _ = self._get_domain_indices(to_domain)
            
            global_from = from_start + from_idx
            global_to = to_start + to_idx
            
            if global_from < self.n_states and global_to < self.n_states:
                self.A[global_to, global_from] = strength
    
    def _normalize_matrix(self):
        """Normalize coupling strengths to 0-1 range."""
        max_val = np.max(np.abs(self.A))
        if max_val > 0:
            self.A = self.A / 10.0  # Scale from 0-10 to 0-1
    
    def _define_all_couplings(self) -> List[Tuple[Tuple[Domain, int], Tuple[Domain, int], float]]:
        """Define all inter-domain couplings with strengths (0-10)."""
        c = []
        
        # === ELECTROMAGNETIC DOMAIN COUPLINGS ===
        # EM -> Thermal (losses generate heat)
        c.extend([
            # Eddy losses (index 14) -> winding temp (index 0)
            ((Domain.ELECTROMAGNETIC, 14), (Domain.THERMAL, 0), 10),
            # Hysteresis losses (15) -> magnet temp (1)
            ((Domain.ELECTROMAGNETIC, 15), (Domain.THERMAL, 1), 10),
            # Copper losses -> stator temp (2)
            ((Domain.ELECTROMAGNETIC, 16), (Domain.THERMAL, 2), 8),
            # Power (5) -> heat flux winding (11)
            ((Domain.ELECTROMAGNETIC, 5), (Domain.THERMAL, 11), 7),
            # Efficiency (8) -> thermal margin inference
            ((Domain.ELECTROMAGNETIC, 8), (Domain.THERMAL, 6), 5),
        ])
        
        # EM -> Mechanical
        c.extend([
            # Torque (6) -> load torque (2)
            ((Domain.ELECTROMAGNETIC, 6), (Domain.MECHANICAL, 2), 10),
            # Electrical freq (4) -> rpm (1)
            ((Domain.ELECTROMAGNETIC, 4), (Domain.MECHANICAL, 1), 10),
            # Cogging torque (13) -> vibration (11)
            ((Domain.ELECTROMAGNETIC, 13), (Domain.MECHANICAL, 11), 6),
            # Torque ripple (14) -> vibration accel (13)
            ((Domain.ELECTROMAGNETIC, 14), (Domain.MECHANICAL, 13), 7),
        ])
        
        # EM -> Structural
        c.extend([
            # Flux density (0) -> stress (0)
            ((Domain.ELECTROMAGNETIC, 0), (Domain.STRUCTURAL, 0), 5),
            # Torque (6) -> deflection (4)
            ((Domain.ELECTROMAGNETIC, 6), (Domain.STRUCTURAL, 4), 7),
            # Back EMF (3) -> safety factor consideration
            ((Domain.ELECTROMAGNETIC, 3), (Domain.STRUCTURAL, 6), 3),
        ])
        
        # EM -> Fault
        c.extend([
            # High current density (2) -> winding short risk (0)
            ((Domain.ELECTROMAGNETIC, 2), (Domain.FAULT, 0), 8),
            # High flux -> demag risk (2)
            ((Domain.ELECTROMAGNETIC, 0), (Domain.FAULT, 2), 6),
            # High losses -> thermal runaway (4)
            ((Domain.ELECTROMAGNETIC, 16), (Domain.FAULT, 4), 7),
        ])
        
        # EM -> Certification
        c.extend([
            # Efficiency (8) -> DO160 score (0)
            ((Domain.ELECTROMAGNETIC, 8), (Domain.CERTIFICATION, 0), 8),
            # Power factor (7) -> EMC margin (4)
            ((Domain.ELECTROMAGNETIC, 7), (Domain.CERTIFICATION, 4), 6),
            # Torque ripple (14) -> vibration margin (6)
            ((Domain.ELECTROMAGNETIC, 14), (Domain.CERTIFICATION, 6), 7),
        ])
        
        # EM -> Reliability
        c.extend([
            # Efficiency (8) -> MTBF (0)
            ((Domain.ELECTROMAGNETIC, 8), (Domain.RELIABILITY, 0), 6),
            # Losses (16) -> health index (13)
            ((Domain.ELECTROMAGNETIC, 16), (Domain.RELIABILITY, 13), 7),
        ])
        
        # === THERMAL DOMAIN COUPLINGS ===
        # Thermal -> EM (temperature affects properties)
        c.extend([
            # Magnet temp (1) -> flux density (0) - demag risk
            ((Domain.THERMAL, 1), (Domain.ELECTROMAGNETIC, 0), 7),
            # Winding temp (0) -> resistance (11)
            ((Domain.THERMAL, 0), (Domain.ELECTROMAGNETIC, 11), 8),
            # Winding temp -> current density capability (2)
            ((Domain.THERMAL, 0), (Domain.ELECTROMAGNETIC, 2), 7),
        ])
        
        # Thermal -> Structural (thermal stress)
        c.extend([
            # Delta T winding (6) -> stress (0)
            ((Domain.THERMAL, 6), (Domain.STRUCTURAL, 0), 6),
            # Delta T magnet (7) -> rotor stress (1)
            ((Domain.THERMAL, 7), (Domain.STRUCTURAL, 1), 6),
            # Thermal time const (13) -> fatigue (10)
            ((Domain.THERMAL, 13), (Domain.STRUCTURAL, 10), 4),
        ])
        
        # Thermal -> Reliability
        c.extend([
            # Winding temp (0) -> MTBF (0)
            ((Domain.THERMAL, 0), (Domain.RELIABILITY, 0), 9),
            # Magnet temp (1) -> reliability 10000h (7)
            ((Domain.THERMAL, 1), (Domain.RELIABILITY, 7), 8),
            # Thermal time const (13) -> health (13)
            ((Domain.THERMAL, 13), (Domain.RELIABILITY, 13), 7),
        ])
        
        # Thermal -> Fault
        c.extend([
            # Winding temp (0) -> thermal runaway (4)
            ((Domain.THERMAL, 0), (Domain.FAULT, 4), 10),
            # Coolant temp rise -> cooling failure (7)
            ((Domain.THERMAL, 5), (Domain.FAULT, 7), 8),
        ])
        
        # Thermal -> Certification
        c.extend([
            # Temp margin -> DO160 score (0)
            ((Domain.THERMAL, 6), (Domain.CERTIFICATION, 5), 10),
            # Max temp -> ARP compliance (2)
            ((Domain.THERMAL, 0), (Domain.CERTIFICATION, 2), 7),
        ])
        
        # === MECHANICAL DOMAIN COUPLINGS ===
        # Mechanical -> Structural (loads)
        c.extend([
            # Torque load (2) -> stress (0)
            ((Domain.MECHANICAL, 2), (Domain.STRUCTURAL, 0), 10),
            # Centrifugal stress (5) -> stress (0)
            ((Domain.MECHANICAL, 5), (Domain.STRUCTURAL, 0), 10),
            # Tip speed (4) -> deflection (4)
            ((Domain.MECHANICAL, 4), (Domain.STRUCTURAL, 4), 8),
            # Bearing force (6,7) -> safety factor (8)
            ((Domain.MECHANICAL, 6), (Domain.STRUCTURAL, 7), 6),
        ])
        
        # Mechanical -> Thermal (friction heating)
        c.extend([
            # Bearing force radial (6) -> rotor temp (3)
            ((Domain.MECHANICAL, 6), (Domain.THERMAL, 3), 5),
            # Tip speed (4) -> windage heating
            ((Domain.MECHANICAL, 4), (Domain.THERMAL, 3), 4),
        ])
        
        # Mechanical -> Fault
        c.extend([
            # Vibration disp (11) -> bearing wear (3)
            ((Domain.MECHANICAL, 11), (Domain.FAULT, 3), 8),
            # Vibration accel (13) -> segment isolation (5)
            ((Domain.MECHANICAL, 13), (Domain.FAULT, 5), 6),
            # Critical speed proximity -> fault risk
            ((Domain.MECHANICAL, 1), (Domain.FAULT, 9), 7),
        ])
        
        # Mechanical -> Reliability
        c.extend([
            # Vibration (12) -> MTBF (0)
            ((Domain.MECHANICAL, 12), (Domain.RELIABILITY, 0), 8),
            # Tip speed (4) -> B10 life (8)
            ((Domain.MECHANICAL, 4), (Domain.RELIABILITY, 8), 7),
        ])
        
        # === STRUCTURAL DOMAIN COUPLINGS ===
        # Structural -> Manufacturing
        c.extend([
            # Safety factor (6) -> tolerances (0)
            ((Domain.STRUCTURAL, 6), (Domain.MANUFACTURING, 0), 7),
            # Deflection (4) -> winding quality (4)
            ((Domain.STRUCTURAL, 4), (Domain.MANUFACTURING, 4), 6),
            # Stress (0) -> lamination quality (5)
            ((Domain.STRUCTURAL, 0), (Domain.MANUFACTURING, 5), 5),
        ])
        
        # Structural -> Reliability
        c.extend([
            # Fatigue life (9) -> MTBF (0)
            ((Domain.STRUCTURAL, 9), (Domain.RELIABILITY, 0), 10),
            # Fatigue damage (10) -> health (13)
            ((Domain.STRUCTURAL, 10), (Domain.RELIABILITY, 13), 9),
            # Safety factor (6) -> reliability 1000h (6)
            ((Domain.STRUCTURAL, 6), (Domain.RELIABILITY, 6), 7),
        ])
        
        # Structural -> Certification
        c.extend([
            # Safety factors -> qualification risk (10)
            ((Domain.STRUCTURAL, 6), (Domain.CERTIFICATION, 10), 8),
            # Resonance freq (11) -> test coverage (8)
            ((Domain.STRUCTURAL, 11), (Domain.CERTIFICATION, 8), 6),
        ])
        
        # === MANUFACTURING DOMAIN COUPLINGS ===
        # Manufacturing -> EM
        c.extend([
            # Tolerances (0) -> air gap flux (0)
            ((Domain.MANUFACTURING, 0), (Domain.ELECTROMAGNETIC, 0), 7),
            # Winding quality (4) -> efficiency (8)
            ((Domain.MANUFACTURING, 4), (Domain.ELECTROMAGNETIC, 8), 6),
            # Magnet placement (5) -> cogging (13)
            ((Domain.MANUFACTURING, 5), (Domain.ELECTROMAGNETIC, 13), 8),
        ])
        
        # Manufacturing -> Reliability
        c.extend([
            # Yield rate (8) -> MTBF (0)
            ((Domain.MANUFACTURING, 8), (Domain.RELIABILITY, 0), 6),
            # Rework prob (7) -> health (13)
            ((Domain.MANUFACTURING, 7), (Domain.RELIABILITY, 13), 5),
        ])
        
        # Manufacturing -> Certification
        c.extend([
            # Inspectability (9) -> DO160 (0)
            ((Domain.MANUFACTURING, 9), (Domain.CERTIFICATION, 0), 7),
            # Documentation implicit in manufacturing quality
            ((Domain.MANUFACTURING, 4), (Domain.CERTIFICATION, 7), 5),
        ])
        
        # === FAULT DOMAIN COUPLINGS ===
        # Fault -> EM
        c.extend([
            # Winding short (0) -> copper losses (16)
            ((Domain.FAULT, 0), (Domain.ELECTROMAGNETIC, 16), 10),
            # Demag (2) -> flux density (0)
            ((Domain.FAULT, 2), (Domain.ELECTROMAGNETIC, 0), 10),
            # Phase loss (6) -> power (5)
            ((Domain.FAULT, 6), (Domain.ELECTROMAGNETIC, 5), 10),
        ])
        
        # Fault -> Thermal
        c.extend([
            # Winding short (0) -> winding temp (0)
            ((Domain.FAULT, 0), (Domain.THERMAL, 0), 10),
            # Cooling failure (7) -> coolant out (5)
            ((Domain.FAULT, 7), (Domain.THERMAL, 5), 10),
        ])
        
        # Fault -> Reliability
        c.extend([
            # Fault severity (9) -> MTBF (0)
            ((Domain.FAULT, 9), (Domain.RELIABILITY, 0), 9),
            # Degraded power (11) -> health (13)
            ((Domain.FAULT, 11), (Domain.RELIABILITY, 13), 8),
            # Fault containment (10) -> availability (2)
            ((Domain.FAULT, 10), (Domain.RELIABILITY, 2), 10),
        ])
        
        # Fault -> Certification
        c.extend([
            # Fault containment (10) -> ARP4761 (2)
            ((Domain.FAULT, 10), (Domain.CERTIFICATION, 2), 10),
            # Degraded efficiency (12) -> DAL level (9)
            ((Domain.FAULT, 12), (Domain.CERTIFICATION, 9), 7),
        ])
        
        # === RELIABILITY DOMAIN COUPLINGS ===
        # Reliability -> Economic
        c.extend([
            # MTBF (0) -> unit cost (0) - warranty cost
            ((Domain.RELIABILITY, 0), (Domain.ECONOMIC, 0), 6),
            # Availability (2) -> selling price (9)
            ((Domain.RELIABILITY, 2), (Domain.ECONOMIC, 9), 5),
            # Maintenance interval (12) -> LCOE (12)
            ((Domain.RELIABILITY, 12), (Domain.ECONOMIC, 12), 8),
        ])
        
        # Reliability -> Certification
        c.extend([
            # MTBF (0) -> ARP4754A (1)
            ((Domain.RELIABILITY, 0), (Domain.CERTIFICATION, 1), 8),
            # Reliability 10000h (7) -> qualification risk (10)
            ((Domain.RELIABILITY, 7), (Domain.CERTIFICATION, 10), 7),
        ])
        
        # === CERTIFICATION DOMAIN COUPLINGS ===
        # Certification -> Economic
        c.extend([
            # Cert cost (11) -> unit cost (0)
            ((Domain.CERTIFICATION, 11), (Domain.ECONOMIC, 0), 8),
            # Cert time (12) -> NRE (6)
            ((Domain.CERTIFICATION, 12), (Domain.ECONOMIC, 6), 7),
        ])
        
        # Certification -> Patent
        c.extend([
            # Documentation (7) -> invention disclosure (7)
            ((Domain.CERTIFICATION, 7), (Domain.PATENT, 7), 5),
        ])
        
        # === PATENT DOMAIN COUPLINGS ===
        # Patent -> Economic
        c.extend([
            # Novelty (0) -> selling price (9) - premium
            ((Domain.PATENT, 0), (Domain.ECONOMIC, 9), 6),
            # Patent risk (6) -> unit cost (0) - licensing
            ((Domain.PATENT, 6), (Domain.ECONOMIC, 0), 5),
        ])
        
        # === CONTROL DOMAIN COUPLINGS ===
        # Control -> EM
        c.extend([
            # Current bandwidth (0) -> torque ripple (14)
            ((Domain.CONTROL, 0), (Domain.ELECTROMAGNETIC, 14), 7),
            # Control latency (2) -> efficiency (8)
            ((Domain.CONTROL, 2), (Domain.ELECTROMAGNETIC, 8), 5),
        ])
        
        # Control -> Fault
        c.extend([
            # Sensor redundancy (11) -> fault detection (13)
            ((Domain.CONTROL, 11), (Domain.FAULT, 13), 9),
        ])
        
        # === OPERATIONAL DOMAIN COUPLINGS ===
        # Operational -> EM
        c.extend([
            # Power demand (9) -> power (5)
            ((Domain.OPERATIONAL, 9), (Domain.ELECTROMAGNETIC, 5), 10),
            # Speed demand (10) -> electrical freq (4)
            ((Domain.OPERATIONAL, 10), (Domain.ELECTROMAGNETIC, 4), 10),
        ])
        
        # Operational -> Thermal
        c.extend([
            # Ambient temp (2) -> winding temp (0)
            ((Domain.OPERATIONAL, 2), (Domain.THERMAL, 0), 8),
            # Altitude (3) -> convection (8)
            ((Domain.OPERATIONAL, 3), (Domain.THERMAL, 8), 7),
        ])
        
        # Operational -> Mechanical
        c.extend([
            # Speed demand (10) -> rpm (1)
            ((Domain.OPERATIONAL, 10), (Domain.MECHANICAL, 1), 10),
        ])
        
        # Operational -> Reliability
        c.extend([
            # Duty cycle (0) -> MTBF (0)
            ((Domain.OPERATIONAL, 0), (Domain.RELIABILITY, 0), 6),
            # Mission time (4) -> health (13)
            ((Domain.OPERATIONAL, 4), (Domain.RELIABILITY, 13), 7),
        ])
        
        # Operational -> Certification
        c.extend([
            # Altitude (3) -> DO160 (0)
            ((Domain.OPERATIONAL, 3), (Domain.CERTIFICATION, 0), 7),
        ])
        
        return c
    
    def get_submatrix(self, from_domain: Domain, to_domain: Domain) -> np.ndarray:
        """Extract a coupling submatrix A_{to,from}."""
        from_start, from_end = self._get_domain_indices(from_domain)
        to_start, to_end = self._get_domain_indices(to_domain)
        return self.A[to_start:to_end, from_start:from_end]
    
    def get_domain_coupling_strength(self, from_domain: Domain, to_domain: Domain) -> float:
        """Get overall coupling strength between two domains (0-1)."""
        submatrix = self.get_submatrix(from_domain, to_domain)
        return np.mean(np.abs(submatrix[submatrix != 0])) if np.any(submatrix != 0) else 0.0
    
    def export_to_json(self, filepath: str):
        """Export matrix to JSON for analysis."""
        import json
        data = {
            'n_states': int(self.n_states),
            'matrix_A': self.A.tolist(),
            'domain_sizes': {d.name: s for d, s in self.DOMAIN_SIZES.items()},
            'coupling_strengths': {}
        }
        
        # Calculate all domain-domain coupling strengths
        for from_d in Domain:
            for to_d in Domain:
                strength = self.get_domain_coupling_strength(from_d, to_d)
                if strength > 0:
                    key = f"{from_d.name}_to_{to_d.name}"
                    data['coupling_strengths'][key] = float(strength)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
