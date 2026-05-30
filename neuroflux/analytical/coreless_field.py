"""
Hague's analytical field solver for coreless AFPM machines.

Provides analytical solutions for magnetic field distributions in slotless/coreless
axial flux permanent magnet machines, based on Hague's mathematical framework (1984)
for permanent magnets bounded by high-permeability back iron.

Equations trace to Document 12 §2.3.
"""

from __future__ import annotations

import math
import numpy as np
from neuroflux.core.constants import PhysicalConstants
from neuroflux.core.models import AFPMTopology, AnalyticalEngineInput


class HagueCorelessSolver:
    """
    Implements Hague's analytical method for magnetic field distribution
    in coreless (slotless) AFPM machines.
    """

    def __init__(self, config: AnalyticalEngineInput):
        self.config = config
        self.geom = config.geometry
        self.materials = config.materials

    def compute_flux_density(
        self,
        r: float,
        theta: np.ndarray,
        z: float,
    ) -> dict[str, np.ndarray]:
        """
        Computes the axial (Bz) and azimuthal (Bt) components of magnetic flux density
        at radius r, angles theta, and axial position z.

        Args:
            r: Radial position (m)
            theta: Array of angular positions (rad)
            z: Axial position (m), where z=0 is the center of the airgap/stator

        Returns:
            Dictionary with 'Bz' and 'Bt' numpy arrays.
        """
        # Determine number of pole pairs
        p = self.geom.p
        
        # Magnetic properties
        br = self.materials.Br
        ur = self.materials.mu_r_PM
        
        # Dimensions
        g = self.geom.g             # Airgap thickness
        lm = self.geom.l_PM         # PM thickness
        
        # Mean radius calculations
        r_avg = (self.geom.r_out + self.geom.r_in) / 2.0
        
        # Active stator/rotor boundary dimensions
        h_stator = self.geom.winding_thickness if self.geom.winding_thickness else 0.01
        
        # Hague's harmonic formulation for slotless/coreless airgap fields
        # Harmonic order limit
        harmonics = range(1, 30, 2)  # Odd harmonics only
        
        bz = np.zeros_like(theta)
        bt = np.zeros_like(theta)
        
        # Pole pitch angle
        tau_p = math.pi / p
        # Magnet arc to pole pitch ratio
        alpha_p = 0.70  # Default magnet cover ratio if not specified
        
        for n in harmonics:
            # Fourier coefficient for PM magnetization
            an = (4.0 * br / (n * math.pi)) * math.sin(n * math.pi * alpha_p / 2.0)
            
            # Wavenumber at radius r
            kn = n * p / r
            
            # Hague boundary decay factor (simplified 2D cylindrical approximation at radius r)
            # Scaling with axial distance
            sinh_val = math.sinh(kn * lm)
            cosh_val = math.cosh(kn * (lm + g / 2.0))
            
            if cosh_val == 0:
                continue
                
            decay = sinh_val / cosh_val
            
            # Harmonic contribution
            bz_n = an * decay * np.cos(n * p * theta) * math.exp(-kn * abs(z))
            bt_n = an * decay * np.sin(n * p * theta) * math.exp(-kn * abs(z))
            
            bz += bz_n
            bt += bt_n
            
        return {"Bz": bz, "Bt": bt}

    def compute_no_load_loss(self, speed_rpm: float) -> float:
        """
        Computes no-load eddy current losses in winding copper due to Hague field.
        """
        # Frequency (Hz)
        f = (speed_rpm * (self.geom.p * 2)) / 120.0
        omega = 2.0 * math.pi * f
        
        # Estimate peak flux density in airgap
        r_avg = (self.geom.r_out + self.geom.r_in) / 2.0
        theta_test = np.array([0.0])
        fields = self.compute_flux_density(r_avg, theta_test, 0.0)
        bz_peak = float(np.max(np.abs(fields["Bz"])))
        
        # Copper volume (m^3)
        copper_vol = math.pi * (self.geom.r_out**2 - self.geom.r_in**2) * self.geom.g * 0.4
        
        # Eddy current loss factor in stator conductors
        sigma_cu = 5.8e7  # Copper conductivity (S/m)
        d_wire = 1.0e-3   # Equivalent wire diameter (m)
        
        # Loss formula: P = (1/32) * sigma * d^2 * omega^2 * B^2 * Vol
        eddy_loss = (1.0 / 32.0) * sigma_cu * (d_wire**2) * (omega**2) * (bz_peak**2) * copper_vol
        return eddy_loss
