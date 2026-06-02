"""
Grand Unified AFPM Matrix - State Definitions

All state variables for the 12-domain state-space model.
"""

import numpy as np
from dataclasses import dataclass, field
from enum import Enum, auto


class Domain(Enum):
    """All interacting domains in AFPM design."""
    ELECTROMAGNETIC = auto()
    THERMAL = auto()
    MECHANICAL = auto()
    STRUCTURAL = auto()
    MANUFACTURING = auto()
    FAULT = auto()
    RELIABILITY = auto()
    CERTIFICATION = auto()
    PATENT = auto()
    ECONOMIC = auto()
    CONTROL = auto()
    OPERATIONAL = auto()


@dataclass
class EMStates:
    """Electromagnetic state variables (17 states)."""
    B_air_gap: float = 0.0  # [T] Air gap flux density
    B_stator: float = 0.0   # [T] Stator flux density
    J_conductor: float = 0.0  # [A/m2] Current density
    E_back_emf: float = 0.0   # [V] Back EMF
    f_electrical: float = 0.0  # [Hz] Electrical frequency
    power_electromagnetic: float = 0.0  # [W]
    torque_electromagnetic: float = 0.0  # [Nm]
    power_factor: float = 0.0  # [-]
    efficiency_electromagnetic: float = 0.0  # [-]
    inductance_d: float = 0.0  # [H] D-axis inductance
    inductance_q: float = 0.0  # [H] Q-axis inductance
    resistance_phase: float = 0.0  # [Ohm]
    flux_linkage: float = 0.0  # [Wb]
    cogging_torque: float = 0.0  # [Nm]
    torque_ripple: float = 0.0  # [%]
    eddy_current_losses: float = 0.0  # [W]
    hysteresis_losses: float = 0.0  # [W]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.B_air_gap, self.B_stator, self.J_conductor,
            self.E_back_emf, self.f_electrical, self.power_electromagnetic,
            self.torque_electromagnetic, self.power_factor,
            self.efficiency_electromagnetic, self.inductance_d,
            self.inductance_q, self.resistance_phase, self.flux_linkage,
            self.cogging_torque, self.torque_ripple,
            self.eddy_current_losses, self.hysteresis_losses
        ])
    
    @classmethod
    def size(cls) -> int:
        return 17


@dataclass
class ThermalStates:
    """Thermal state variables (15 states)."""
    T_winding: float = 25.0  # [C] Winding temperature
    T_magnet: float = 25.0   # [C] Magnet temperature
    T_stator_core: float = 25.0  # [C] Stator core temp
    T_rotor: float = 25.0    # [C] Rotor temperature
    T_coolant_in: float = 25.0   # [C] Coolant inlet
    T_coolant_out: float = 25.0  # [C] Coolant outlet
    delta_T_winding: float = 0.0  # [K] Winding temp rise
    delta_T_magnet: float = 0.0   # [K] Magnet temp rise
    h_convection: float = 50.0    # [W/m2K] Convection coefficient
    thermal_resistance_jc: float = 0.0  # [K/W] Junction-case
    thermal_resistance_ca: float = 0.0  # [K/W] Case-ambient
    heat_flux_winding: float = 0.0  # [W/m2]
    heat_flux_magnets: float = 0.0  # [W/m2]
    thermal_time_constant: float = 0.0  # [s]
    cooling_power: float = 0.0  # [W] Cooling system power
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.T_winding, self.T_magnet, self.T_stator_core,
            self.T_rotor, self.T_coolant_in, self.T_coolant_out,
            self.delta_T_winding, self.delta_T_magnet,
            self.h_convection, self.thermal_resistance_jc,
            self.thermal_resistance_ca, self.heat_flux_winding,
            self.heat_flux_magnets, self.thermal_time_constant,
            self.cooling_power
        ])
    
    @classmethod
    def size(cls) -> int:
        return 15


@dataclass
class MechanicalStates:
    """Mechanical state variables (15 states)."""
    omega_mech: float = 0.0    # [rad/s] Mechanical speed
    rpm: float = 0.0           # [rpm] Rotational speed
    torque_load: float = 0.0   # [Nm] Load torque
    torque_inertia: float = 0.0  # [Nm] Inertial torque
    tip_speed: float = 0.0     # [m/s] Rotor tip speed
    centrifugal_stress: float = 0.0  # [Pa]
    bearing_force_radial: float = 0.0  # [N]
    bearing_force_axial: float = 0.0   # [N]
    unbalance_force: float = 0.0  # [N]
    critical_speed_1: float = 0.0  # [rpm] First critical
    critical_speed_2: float = 0.0  # [rpm] Second critical
    vibration_displacement: float = 0.0  # [m]
    vibration_velocity: float = 0.0  # [m/s]
    vibration_acceleration: float = 0.0  # [m/s2]
    acoustic_noise: float = 0.0  # [dB]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.omega_mech, self.rpm, self.torque_load,
            self.torque_inertia, self.tip_speed, self.centrifugal_stress,
            self.bearing_force_radial, self.bearing_force_axial,
            self.unbalance_force, self.critical_speed_1,
            self.critical_speed_2, self.vibration_displacement,
            self.vibration_velocity, self.vibration_acceleration,
            self.acoustic_noise
        ])
    
    @classmethod
    def size(cls) -> int:
        return 15


@dataclass
class StructuralStates:
    """Structural state variables (16 states)."""
    stress_von_mises_stator: float = 0.0  # [Pa]
    stress_von_mises_rotor: float = 0.0   # [Pa]
    stress_von_mises_shaft: float = 0.0   # [Pa]
    deflection_stator: float = 0.0  # [m]
    deflection_rotor: float = 0.0   # [m]
    deflection_axial: float = 0.0   # [m] Axial deflection
    safety_factor_stator: float = 2.0
    safety_factor_rotor: float = 2.0
    safety_factor_shaft: float = 2.0
    fatigue_life_cycles: float = 1e9  # [cycles]
    fatigue_damage: float = 0.0  # [-] Cumulative damage
    resonance_frequency_1: float = 0.0  # [Hz]
    resonance_frequency_2: float = 0.0  # [Hz]
    stiffness_radial: float = 0.0  # [N/m]
    stiffness_axial: float = 0.0   # [N/m]
    stiffness_torsional: float = 0.0  # [Nm/rad]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.stress_von_mises_stator, self.stress_von_mises_rotor,
            self.stress_von_mises_shaft, self.deflection_stator,
            self.deflection_rotor, self.deflection_axial,
            self.safety_factor_stator, self.safety_factor_rotor,
            self.safety_factor_shaft, self.fatigue_life_cycles,
            self.fatigue_damage, self.resonance_frequency_1,
            self.resonance_frequency_2, self.stiffness_radial,
            self.stiffness_axial, self.stiffness_torsional
        ])
    
    @classmethod
    def size(cls) -> int:
        return 16


@dataclass
class ManufacturingStates:
    """Manufacturing state variables (14 states)."""
    tolerances_stackup: float = 0.0  # [m] Cumulative tolerance
    surface_finish_stator: float = 0.0  # [Ra] Surface roughness
    surface_finish_rotor: float = 0.0   # [Ra]
    winding_quality_factor: float = 1.0  # [-] 0-1
    magnet_placement_accuracy: float = 1.0  # [-] 0-1
    lamination_quality: float = 1.0  # [-] 0-1
    assembly_time_hours: float = 0.0  # [hours]
    rework_probability: float = 0.0  # [-]
    yield_rate: float = 0.95  # [-]
    inspectability_score: float = 0.5  # [-] 0-1
    automation_compatibility: float = 0.5  # [-] 0-1
    batch_size_optimal: float = 100.0  # [units]
    tooling_cost: float = 0.0  # [$]
    fixture_complexity: float = 0.0  # [-] 0-1
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.tolerances_stackup, self.surface_finish_stator,
            self.surface_finish_rotor, self.winding_quality_factor,
            self.magnet_placement_accuracy, self.lamination_quality,
            self.assembly_time_hours, self.rework_probability,
            self.yield_rate, self.inspectability_score,
            self.automation_compatibility, self.batch_size_optimal,
            self.tooling_cost, self.fixture_complexity
        ])
    
    @classmethod
    def size(cls) -> int:
        return 14


@dataclass
class FaultStates:
    """Fault state variables (15 states)."""
    fault_winding_short: float = 0.0  # [-] 0=none, 1=full short
    fault_winding_open: float = 0.0   # [-]
    fault_magnet_demag: float = 0.0   # [-]
    fault_bearing_wear: float = 0.0   # [-]
    fault_thermal_runaway: float = 0.0  # [-]
    fault_segment_isolation: float = 0.0  # Number of isolated segments
    fault_phase_loss: float = 0.0     # Number of lost phases
    fault_cooling_failure: float = 0.0  # [-]
    fault_sensor_failure: float = 0.0   # Number of failed sensors
    fault_severity_index: float = 0.0   # [0-1] Overall severity
    fault_containment_success: float = 1.0  # [-] 0-1
    degraded_power_available: float = 1.0   # [-] 0-1
    degraded_efficiency: float = 1.0        # [-] 0-1
    fault_detection_time: float = 0.0       # [s]
    fault_isolation_time: float = 0.0       # [s]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.fault_winding_short, self.fault_winding_open,
            self.fault_magnet_demag, self.fault_bearing_wear,
            self.fault_thermal_runaway, self.fault_segment_isolation,
            self.fault_phase_loss, self.fault_cooling_failure,
            self.fault_sensor_failure, self.fault_severity_index,
            self.fault_containment_success, self.degraded_power_available,
            self.degraded_efficiency, self.fault_detection_time,
            self.fault_isolation_time
        ])
    
    @classmethod
    def size(cls) -> int:
        return 15


@dataclass
class ReliabilityStates:
    """Reliability state variables (14 states)."""
    MTBF_hours: float = 10000.0  # [hours] Mean time between failures
    MTTR_hours: float = 2.0      # [hours] Mean time to repair
    availability: float = 0.999    # [-]
    failure_rate_lambda: float = 0.0  # [1/hours]
    weibull_beta: float = 1.0     # Shape parameter
    weibull_eta: float = 10000.0  # Scale parameter [hours]
    reliability_1000h: float = 0.95  # [-] Reliability at 1000h
    reliability_10000h: float = 0.90  # [-] Reliability at 10000h
    B10_life: float = 0.0  # [hours] 10% failure point
    B50_life: float = 0.0  # [hours] 50% failure point
    critical_components_count: float = 0.0
    redundancy_factor: float = 1.0  # [-] 1=no redundancy
    maintenance_interval: float = 2000.0  # [hours]
    health_index: float = 1.0  # [-] 0-1 overall health
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.MTBF_hours, self.MTTR_hours, self.availability,
            self.failure_rate_lambda, self.weibull_beta, self.weibull_eta,
            self.reliability_1000h, self.reliability_10000h,
            self.B10_life, self.B50_life, self.critical_components_count,
            self.redundancy_factor, self.maintenance_interval,
            self.health_index
        ])
    
    @classmethod
    def size(cls) -> int:
        return 14


@dataclass
class CertificationStates:
    """Certification state variables (13 states)."""
    DO160_compliance_score: float = 0.0  # [-] 0-1
    ARP4754A_compliance_score: float = 0.0  # [-]
    ARP4761_compliance_score: float = 0.0   # [-]
    DO254_compliance_score: float = 0.0     # [-]
    EMC_margin: float = 6.0  # [dB] EMC margin
    temperature_margin: float = 15.0  # [C] Temperature margin
    vibration_margin: float = 3.0     # [-] Safety factor on vibe
    documentation_completeness: float = 0.0  # [-] 0-1
    test_coverage: float = 0.0        # [-] 0-1
    DAL_level: float = 3.0  # Development Assurance Level (A=1, E=5)
    qualification_risk: float = 0.5   # [-] 0-1
    certification_cost_estimate: float = 0.0  # [$]
    certification_time_estimate: float = 0.0  # [months]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.DO160_compliance_score, self.ARP4754A_compliance_score,
            self.ARP4761_compliance_score, self.DO254_compliance_score,
            self.EMC_margin, self.temperature_margin,
            self.vibration_margin, self.documentation_completeness,
            self.test_coverage, self.DAL_level,
            self.qualification_risk, self.certification_cost_estimate,
            self.certification_time_estimate
        ])
    
    @classmethod
    def size(cls) -> int:
        return 13


@dataclass
class PatentStates:
    """Patent-space state variables (10 states)."""
    novelty_score: float = 0.0  # [-] 0-1
    prior_art_density: float = 0.5  # [-] 0-1 (1=high density)
    differentiation_index: float = 0.0  # [-]
    claim_strength: float = 0.0  # [-] 0-1
    patentability_likelihood: float = 0.0  # [-] 0-1
    freedom_to_operate: float = 0.5  # [-] 0-1
    patent_risk_level: float = 0.0   # [-] 0-1
    invention_disclosure_quality: float = 0.0  # [-]
    competitive_patent_count: float = 0.0  # Number of competitor patents
    whitespace_opportunity: float = 0.0  # [-] 0-1 unexplored space
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.novelty_score, self.prior_art_density,
            self.differentiation_index, self.claim_strength,
            self.patentability_likelihood, self.freedom_to_operate,
            self.patent_risk_level, self.invention_disclosure_quality,
            self.competitive_patent_count, self.whitespace_opportunity
        ])
    
    @classmethod
    def size(cls) -> int:
        return 10


@dataclass
class EconomicStates:
    """Economic state variables (13 states)."""
    unit_cost: float = 0.0  # [$]
    magnet_cost_fraction: float = 0.3  # [-]
    copper_cost_fraction: float = 0.2  # [-]
    steel_cost_fraction: float = 0.15  # [-]
    labor_cost_fraction: float = 0.25  # [-]
    overhead_cost_fraction: float = 0.1  # [-]
    NRE_cost: float = 0.0  # [$] Non-recurring engineering
    tooling_amortization: float = 0.0  # [$]
    recurring_cost_per_unit: float = 0.0  # [$]
    selling_price_estimate: float = 0.0  # [$]
    margin_percentage: float = 0.3  # [-]
    break_even_volume: float = 0.0  # [units]
    LCOE_cost: float = 0.0  # [$/kWh] Levelized cost
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.unit_cost, self.magnet_cost_fraction,
            self.copper_cost_fraction, self.steel_cost_fraction,
            self.labor_cost_fraction, self.overhead_cost_fraction,
            self.NRE_cost, self.tooling_amortization,
            self.recurring_cost_per_unit, self.selling_price_estimate,
            self.margin_percentage, self.break_even_volume,
            self.LCOE_cost
        ])
    
    @classmethod
    def size(cls) -> int:
        return 13


@dataclass
class ControlStates:
    """Control system state variables (12 states)."""
    bandwidth_current: float = 1000.0  # [Hz]
    bandwidth_speed: float = 100.0     # [Hz]
    control_latency: float = 0.001   # [s]
    sampling_frequency: float = 10000.0  # [Hz]
    PWM_frequency: float = 10000.0     # [Hz]
    position_resolution: float = 0.001   # [rad]
    current_ripple: float = 0.05       # [pu]
    torque_response_time: float = 0.01   # [s]
    speed_regulation: float = 0.001     # [pu]
    field_weakening_ratio: float = 2.0   # [-]
    control_mode: float = 0.0  # 0=torque, 1=speed, 2=position
    sensor_redundancy: float = 1.0  # Number of redundant sensors
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.bandwidth_current, self.bandwidth_speed,
            self.control_latency, self.sampling_frequency,
            self.PWM_frequency, self.position_resolution,
            self.current_ripple, self.torque_response_time,
            self.speed_regulation, self.field_weakening_ratio,
            self.control_mode, self.sensor_redundancy
        ])
    
    @classmethod
    def size(cls) -> int:
        return 12


@dataclass
class OperationalStates:
    """Operational state variables (12 states)."""
    duty_cycle: float = 0.8  # [-]
    load_profile_factor: float = 0.7  # [-]
    ambient_temperature: float = 25.0  # [C]
    altitude: float = 0.0  # [m]
    mission_time: float = 0.0  # [hours]
    cycles_completed: float = 0.0  # [-]
    degradation_factor: float = 1.0  # [-] 1.0=new
    maintenance_due: float = 0.0  # [hours] Time to maintenance
    diagnostic_flags: float = 0.0  # Bitfield
    power_demand: float = 0.0  # [W]
    speed_demand: float = 0.0  # [rpm]
    efficiency_demand: float = 0.95  # [-]
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.duty_cycle, self.load_profile_factor,
            self.ambient_temperature, self.altitude,
            self.mission_time, self.cycles_completed,
            self.degradation_factor, self.maintenance_due,
            self.diagnostic_flags, self.power_demand,
            self.speed_demand, self.efficiency_demand
        ])
    
    @classmethod
    def size(cls) -> int:
        return 12


@dataclass
class GrandStateVector:
    """Complete state vector for AFPM design space (166 states total)."""
    em: EMStates = field(default_factory=EMStates)
    thermal: ThermalStates = field(default_factory=ThermalStates)
    mechanical: MechanicalStates = field(default_factory=MechanicalStates)
    structural: StructuralStates = field(default_factory=StructuralStates)
    manufacturing: ManufacturingStates = field(default_factory=ManufacturingStates)
    fault: FaultStates = field(default_factory=FaultStates)
    reliability: ReliabilityStates = field(default_factory=ReliabilityStates)
    certification: CertificationStates = field(default_factory=CertificationStates)
    patent: PatentStates = field(default_factory=PatentStates)
    economic: EconomicStates = field(default_factory=EconomicStates)
    control: ControlStates = field(default_factory=ControlStates)
    operational: OperationalStates = field(default_factory=OperationalStates)
    
    def to_array(self) -> np.ndarray:
        """Convert to full state vector (166 elements)."""
        return np.concatenate([
            self.em.to_array(), self.thermal.to_array(),
            self.mechanical.to_array(), self.structural.to_array(),
            self.manufacturing.to_array(), self.fault.to_array(),
            self.reliability.to_array(), self.certification.to_array(),
            self.patent.to_array(), self.economic.to_array(),
            self.control.to_array(), self.operational.to_array()
        ])
    
    @classmethod
    def total_size(cls) -> int:
        return (
            EMStates.size() + ThermalStates.size() + MechanicalStates.size() +
            StructuralStates.size() + ManufacturingStates.size() + FaultStates.size() +
            ReliabilityStates.size() + CertificationStates.size() + PatentStates.size() +
            EconomicStates.size() + ControlStates.size() + OperationalStates.size()
        )
    
    @classmethod
    def get_domain_sizes(cls) -> dict:
        """Get sizes of all domains."""
        return {
            'EM': EMStates.size(),
            'Thermal': ThermalStates.size(),
            'Mechanical': MechanicalStates.size(),
            'Structural': StructuralStates.size(),
            'Manufacturing': ManufacturingStates.size(),
            'Fault': FaultStates.size(),
            'Reliability': ReliabilityStates.size(),
            'Certification': CertificationStates.size(),
            'Patent': PatentStates.size(),
            'Economic': EconomicStates.size(),
            'Control': ControlStates.size(),
            'Operational': OperationalStates.size(),
            'TOTAL': cls.total_size()
        }
