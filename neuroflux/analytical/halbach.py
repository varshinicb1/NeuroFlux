"""
Halbach array field solver for AFPM machines.

Calculates magnetization patterns, orientation vectors, and airgap flux density
harmonics for Halbach permanent magnet configurations in AFPM designs.

Equations trace to Document 12 §2.4.
"""

from __future__ import annotations

import math
import numpy as np
from neuroflux.core.models import AnalyticalEngineInput


class HalbachArraySolver:
    """
    Implements analytical formulations for Halbach magnet arrays in AFPM machines.
    """

    def __init__(self, config: AnalyticalEngineInput):
        self.config = config
        self.geom = config.geometry
        self.materials = config.materials

    def compute_magnetization_vector(self, theta: float) -> tuple[float, float, float]:
        """
        Computes the magnetization vector (Mr, Mt, Mz) at a given angular coordinate theta.
        
        For a classical 2D Halbach array (4 segments per pole pair):
        - Mz (axial) is sinusoidal or square-shifted axial magnetization
        - Mt (tangential) is shifted by 90 degrees to concentrate flux on one side
        """
        p = self.geom.p
        br = self.materials.Br
        m_amp = br / PhysicalConstants_mu0_approx()
        
        # Fundamental electrical angle
        elec_angle = p * theta
        
        # Ideal Halbach magnetization vector components
        mr = 0.0  # Purely axial-tangential for AFPM
        mt = m_amp * math.cos(elec_angle)
        mz = m_amp * math.sin(elec_angle)
        
        return mr, mt, mz

    def compute_airgap_field(self, r: float, theta: np.ndarray, z: float) -> dict[str, np.ndarray]:
        """
        Computes Halbach field components.
        Halbach arrays concentrate flux on the airgap side and virtually cancel it on the back-iron side.
        """
        p = self.geom.p
        br = self.materials.Br
        g = self.geom.g
        lm = self.geom.l_PM
        
        # Ideal Halbach enhancement factor (1 + exp(-k * lm))
        bz = np.zeros_like(theta)
        bt = np.zeros_like(theta)
        
        # Calculate fundamental wavelength at radius r
        tau_p = (2.0 * math.pi * r) / (2.0 * p)
        k1 = math.pi / tau_p
        
        # Fundamental component (Halbach is highly sinusoidal, harmonics are negligible)
        bz_peak = br * (1.0 - math.exp(-k1 * lm)) * math.exp(-k1 * abs(z))
        
        # Re-enforce directionality
        bz = bz_peak * np.sin(p * theta)
        bt = bz_peak * np.cos(p * theta)
        
        return {"Bz": bz, "Bt": bt}


def PhysicalConstants_mu0_approx() -> float:
    return 4.0 * math.pi * 1e-7
