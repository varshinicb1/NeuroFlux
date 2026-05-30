"""
Material database for NeuroFlux.

Provides predefined material properties for common PM grades, steel grades,
and copper configurations used in AFPM machine design.

Data sources:
    - PM properties: Standard NdFeB/ferrite manufacturer datasheets
    - Steel properties: Parviainen (2005) for M600-50A coefficients (Doc 12 §3.2)
    - Copper: Standard handbook values

Usage:
    >>> from neuroflux.core.materials import MaterialDatabase
    >>> db = MaterialDatabase()
    >>> steel = db.get_steel("M600-50A")
    >>> pm = db.get_pm("N42")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from neuroflux.core.constants import PhysicalConstants
from neuroflux.core.exceptions import MaterialNotFoundError
from neuroflux.core.models import MaterialProperties


@dataclass(frozen=True)
class PMGrade:
    """Permanent magnet grade specification."""

    name: str
    Br: float  # Remanence [T] at 20°C
    Hcj: float  # Intrinsic coercivity [A/m]
    mu_r: float  # Relative permeability
    temp_coeff_br: float  # Temperature coefficient of Br [%/°C]
    max_operating_temp: float  # Maximum operating temperature [°C]
    density: float  # Density [kg/m³]


@dataclass(frozen=True)
class SteelGrade:
    """Electrical steel grade specification.

    Loss coefficients follow the Bertotti/Steinmetz model from Doc 12 §3.2:
        P_Fe = k_hys * f * B^α + k_eddy * (f*B)² + k_exc * (f*B)^1.5
    """

    name: str
    k_hys: float  # Hysteresis loss coefficient [W/m³]
    k_eddy: float  # Eddy current loss coefficient [W/m³]
    k_exc: float  # Excess loss coefficient [W/m³]
    alpha: float  # Steinmetz exponent
    B_sat: float  # Saturation flux density [T]
    mu_r_linear: float  # Relative permeability in linear region
    density: float  # Density [kg/m³]
    lamination_thickness: float  # Lamination thickness [m]


class MaterialDatabase:
    """Central database of material properties.

    Pre-loaded with common PM grades and steel grades.
    Extensible via add_pm() and add_steel() methods.
    """

    def __init__(self) -> None:
        self._pm_grades: dict[str, PMGrade] = {}
        self._steel_grades: dict[str, SteelGrade] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default material grades."""
        # ── NdFeB PM Grades ──
        # Standard sintered NdFeB grades at 20°C
        self.add_pm(PMGrade(
            name="N35",
            Br=1.17, Hcj=955e3, mu_r=1.05,
            temp_coeff_br=-0.12, max_operating_temp=80.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        self.add_pm(PMGrade(
            name="N38",
            Br=1.22, Hcj=955e3, mu_r=1.05,
            temp_coeff_br=-0.12, max_operating_temp=80.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        self.add_pm(PMGrade(
            name="N42",
            Br=1.28, Hcj=955e3, mu_r=1.05,
            temp_coeff_br=-0.12, max_operating_temp=80.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        self.add_pm(PMGrade(
            name="N45",
            Br=1.32, Hcj=876e3, mu_r=1.05,
            temp_coeff_br=-0.12, max_operating_temp=80.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        self.add_pm(PMGrade(
            name="N52",
            Br=1.43, Hcj=876e3, mu_r=1.05,
            temp_coeff_br=-0.12, max_operating_temp=80.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        # High-temperature NdFeB
        self.add_pm(PMGrade(
            name="N42SH",
            Br=1.28, Hcj=1592e3, mu_r=1.05,
            temp_coeff_br=-0.10, max_operating_temp=150.0,
            density=PhysicalConstants.DENSITY_NDFEB,
        ))
        # Ferrite
        self.add_pm(PMGrade(
            name="Y30BH",
            Br=0.38, Hcj=240e3, mu_r=1.1,
            temp_coeff_br=-0.20, max_operating_temp=250.0,
            density=PhysicalConstants.DENSITY_FERRITE,
        ))

        # ── Electrical Steel Grades ──
        # Coefficients based on Parviainen (2005) for M600-50A (Doc 12 §3.2)
        self.add_steel(SteelGrade(
            name="M600-50A",
            k_hys=143.0, k_eddy=0.53, k_exc=0.0,
            alpha=2.0, B_sat=1.8, mu_r_linear=5000.0,
            density=PhysicalConstants.DENSITY_STEEL,
            lamination_thickness=0.5e-3,
        ))
        # Lower loss grade for comparison
        self.add_steel(SteelGrade(
            name="M270-35A",
            k_hys=90.0, k_eddy=0.35, k_exc=0.0,
            alpha=2.0, B_sat=1.7, mu_r_linear=7000.0,
            density=7650.0,
            lamination_thickness=0.35e-3,
        ))
        # Higher loss / lower cost
        self.add_steel(SteelGrade(
            name="M800-65A",
            k_hys=200.0, k_eddy=0.75, k_exc=0.0,
            alpha=2.0, B_sat=1.85, mu_r_linear=4000.0,
            density=7700.0,
            lamination_thickness=0.65e-3,
        ))

    def add_pm(self, grade: PMGrade) -> None:
        """Register a PM grade in the database."""
        self._pm_grades[grade.name] = grade

    def add_steel(self, grade: SteelGrade) -> None:
        """Register a steel grade in the database."""
        self._steel_grades[grade.name] = grade

    def get_pm(self, name: str) -> PMGrade:
        """Look up a PM grade by name.

        Raises:
            MaterialNotFoundError: If the grade is not in the database.
        """
        if name not in self._pm_grades:
            available = ", ".join(sorted(self._pm_grades.keys()))
            raise MaterialNotFoundError(
                name, f"PM grade (available: {available})"
            )
        return self._pm_grades[name]

    def get_steel(self, name: str) -> SteelGrade:
        """Look up a steel grade by name.

        Raises:
            MaterialNotFoundError: If the grade is not in the database.
        """
        if name not in self._steel_grades:
            available = ", ".join(sorted(self._steel_grades.keys()))
            raise MaterialNotFoundError(
                name, f"Steel grade (available: {available})"
            )
        return self._steel_grades[name]

    def build_material_properties(
        self, pm_grade: str, steel_grade: str = "M600-50A"
    ) -> MaterialProperties:
        """Build a MaterialProperties model from grade names.

        Convenience method that looks up both PM and steel grades
        and constructs the unified MaterialProperties model.

        Args:
            pm_grade: PM grade name (e.g., "N42").
            steel_grade: Steel grade name (e.g., "M600-50A").

        Returns:
            MaterialProperties with all fields populated from the database.
        """
        pm = self.get_pm(pm_grade)
        steel = self.get_steel(steel_grade)
        return MaterialProperties(
            Br=pm.Br,
            mu_r_PM=pm.mu_r,
            Hcj=pm.Hcj,
            pm_temp_coeff=pm.temp_coeff_br,
            steel_grade=steel.name,
            k_hys=steel.k_hys,
            k_eddy=steel.k_eddy,
            k_exc=steel.k_exc,
            steinmetz_alpha=steel.alpha,
            B_sat=steel.B_sat,
            mu_r_steel_linear=steel.mu_r_linear,
        )

    def list_pm_grades(self) -> list[str]:
        """List all available PM grade names."""
        return sorted(self._pm_grades.keys())

    def list_steel_grades(self) -> list[str]:
        """List all available steel grade names."""
        return sorted(self._steel_grades.keys())
