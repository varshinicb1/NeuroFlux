"""
Loss modeling engine for AFPM machines.

Computes multi-physics loss components:
- Winding copper losses (DC + AC skin/proximity effects)
- Stator core iron losses (Steinmetz hysteresis, classical eddy, and excess losses)
- PM rotor eddy current losses
- Mechanical windage and friction losses

Equations trace to Document 12 §3.2.
"""

from __future__ import annotations

import math
from neuroflux.core.constants import PhysicalConstants
from neuroflux.core.models import AnalyticalEngineInput, OperatingPoint


class LossModelEvaluator:
    """
    Computes all electrical, magnetic, and mechanical losses in AFPM machines.
    """

    def __init__(self, config: AnalyticalEngineInput):
        self.config = config
        self.geom = config.geometry
        self.materials = config.materials

    def compute_copper_losses(self, op: OperatingPoint, r_dc: float) -> dict[str, float]:
        """
        Computes DC copper loss and AC high-frequency skin effect copper losses.
        """
        i_rms = op.I_rms
        f = (op.speed_rpm * (self.geom.p * 2)) / 120.0
        
        # DC loss (m phases)
        phases = 3.0
        p_dc = phases * (i_rms ** 2) * r_dc
        
        # AC Skin effect scaling factor (Dowells method approximation)
        # Skin depth: delta = sqrt(1 / (pi * f * mu * sigma))
        sigma_cu = 5.8e7  # Copper conductivity (S/m)
        mu0 = 4.0 * math.pi * 1e-7
        
        if f > 0:
            delta = math.sqrt(1.0 / (math.pi * f * mu0 * sigma_cu))
            d_wire = 1.0e-3  # wire diameter
            xi = d_wire / delta
            
            # Dowell's skin effect factor F_ac = xi * (sinh(2*xi) + sin(2*xi)) / (cosh(2*xi) - cos(2*xi))
            if xi < 0.1:
                f_ac = 1.0
            else:
                try:
                    f_ac = xi * (math.sinh(2*xi) + math.sin(2*xi)) / (math.cosh(2*xi) - math.cos(2*xi))
                except OverflowError:
                    f_ac = xi
        else:
            f_ac = 1.0
            
        p_ac = p_dc * (f_ac - 1.0)
        p_total = p_dc * f_ac
        
        return {
            "p_copper_dc": p_dc,
            "p_copper_ac": p_ac,
            "p_copper_total": p_total,
            "f_ac_factor": f_ac,
        }

    def compute_core_losses(self, op: OperatingPoint, b_peak: float) -> dict[str, float]:
        """
        Computes Steinmetz core losses in stator iron (hysteresis + eddy current + excess).
        Coefficients are per unit volume (W/m³).
        P_core = (C_h * f * B^α + C_e * f^2 * B^2 + C_exc * f^1.5 * B^1.5) * Volume
        """
        f = (op.speed_rpm * (self.geom.p * 2)) / 120.0
        if f <= 0 or b_peak <= 0:
            return {"p_hysteresis": 0.0, "p_eddy": 0.0, "p_excess": 0.0, "p_core_total": 0.0}
            
        # Standard electrical steel Steinmetz parameters from MaterialsConfig
        c_h = self.materials.k_hys
        x_h = self.materials.steinmetz_alpha
        c_e = self.materials.k_eddy
        c_exc = self.materials.k_exc
        
        # Volume of stator core back iron (m³)
        r_ext = self.geom.r_out
        r_int = self.geom.r_in
        h_yoke = self.geom.yoke_thickness if self.geom.yoke_thickness else 0.005
        
        volume = math.pi * (r_ext**2 - r_int**2) * h_yoke
        
        p_hyst = c_h * f * (b_peak ** x_h) * volume
        p_eddy = c_e * (f ** 2) * (b_peak ** 2) * volume
        p_exc = c_exc * (f ** 1.5) * (b_peak ** 1.5) * volume
        p_total = p_hyst + p_eddy + p_exc
        
        return {
            "p_hysteresis": p_hyst,
            "p_eddy": p_eddy,
            "p_excess": p_exc,
            "p_core_total": p_total,
        }

    def compute_rotor_losses(self, op: OperatingPoint, b_peak: float) -> float:
        """
        Estimate permanent magnet eddy current losses due to stator space harmonics.
        """
        f = (op.speed_rpm * (self.geom.p * 2)) / 120.0
        if f <= 0:
            return 0.0
            
        # Simplified magnet loss approximation: proportional to f^2 * B^2
        vol_pm = math.pi * (self.geom.r_out**2 - self.geom.r_in**2) * self.geom.l_PM * 0.7
        sigma_pm = 0.6e6  # NdFeB electrical conductivity (S/m)
        
        # Loss ~ (pi^2 / 6) * sigma * d^2 * f^2 * B^2 * Vol
        d_pm = 0.01  # magnet segment width (m)
        p_pm_loss = (math.pi**2 / 6.0) * sigma_pm * (d_pm**2) * (f**2) * ((0.05 * b_peak)**2) * vol_pm
        return p_pm_loss

    def compute_mechanical_losses(self, speed_rpm: float) -> dict[str, float]:
        """
        Computes bearing friction and aerodynamic windage/drag losses for double-rotor topologies.
        """
        omega = speed_rpm * (2.0 * math.pi / 60.0)
        
        # Bearing friction loss: P_bearing = T_bearing * omega
        # Simple heuristic bearing torque estimate
        mass_rotors = 15.0  # kg approximate rotor weight
        t_bearing = 0.005 * mass_rotors * 9.81 * 0.015  # T = mu * F * r_bearing
        p_bearing = t_bearing * omega
        
        # Windage loss (air friction drag on rotating disks):
        # P_windage = 0.5 * C_d * rho_air * omega^3 * (R_ext^5 - R_int^5)
        rho_air = 1.2  # kg/m^3
        c_d = 0.01     # drag coefficient for rotating disk
        r_ext = self.geom.r_out
        r_int = self.geom.r_in
        
        p_windage = 0.1 * c_d * rho_air * (omega ** 3) * (r_ext ** 5 - r_int ** 5)
        
        return {
            "p_bearing": p_bearing,
            "p_windage": p_windage,
            "p_mechanical_total": p_bearing + p_windage,
        }
