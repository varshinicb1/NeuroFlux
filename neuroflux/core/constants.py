"""
Physical constants used across all NeuroFlux engines.

Centralizes all physical constants to avoid magic numbers and ensure
consistency across electromagnetic, thermal, and mechanical calculations.
"""

import math


class PhysicalConstants:
    """Standard physical constants for electromagnetic machine analysis."""

    # Permeability of free space [H/m]
    MU_0: float = 4.0 * math.pi * 1e-7

    # Permittivity of free space [F/m]
    EPSILON_0: float = 8.854187817e-12

    # Electrical conductivity of copper at 20°C [S/m]
    SIGMA_CU_20C: float = 5.96e7

    # Resistivity of copper at 20°C [Ω·m]
    RHO_CU_20C: float = 1.678e-8

    # Temperature coefficient of resistance for copper [1/K]
    ALPHA_CU: float = 0.00393

    # Density of copper [kg/m³]
    DENSITY_CU: float = 8960.0

    # Density of typical electrical steel (M600-50A) [kg/m³]
    DENSITY_STEEL: float = 7650.0

    # Density of NdFeB permanent magnets (typical) [kg/m³]
    DENSITY_NDFEB: float = 7500.0

    # Density of ferrite permanent magnets (typical) [kg/m³]
    DENSITY_FERRITE: float = 5000.0

    # Boltzmann constant [J/K]
    K_BOLTZMANN: float = 1.380649e-23

    # Stefan-Boltzmann constant [W/(m²·K⁴)]
    SIGMA_SB: float = 5.670374419e-8

    # Standard ambient temperature [°C]
    T_AMBIENT: float = 20.0

    # Thermal conductivity of air at ~20°C [W/(m·K)]
    K_AIR: float = 0.026

    # Thermal conductivity of copper [W/(m·K)]
    K_CU: float = 401.0

    # Thermal conductivity of electrical steel (typical) [W/(m·K)]
    K_STEEL: float = 30.0

    @staticmethod
    def copper_resistivity_at_temp(temp_c: float) -> float:
        """Calculate copper resistivity at a given temperature.

        Uses linear temperature coefficient model.

        Args:
            temp_c: Temperature in degrees Celsius.

        Returns:
            Resistivity in Ω·m at the given temperature.
        """
        return PhysicalConstants.RHO_CU_20C * (
            1.0 + PhysicalConstants.ALPHA_CU * (temp_c - PhysicalConstants.T_AMBIENT)
        )
