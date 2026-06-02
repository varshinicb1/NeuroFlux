"""
Aerospace Requirements Database for AFPM Generator Design.

Collects and structures:
- Certification requirements (FAA, EASA, DO-160, ARP4754, ARP4761, DO-254, DO-178C)
- Industry benchmarks (Honeywell, GE, Rolls-Royce, Pratt & Whitney)
- Existing product specifications
- Patent disclosures
- Public program targets

All requirements include:
- source: Origin of requirement
- value: Numerical or categorical value
- confidence: HIGH/MEDIUM/LOW
- citation: Specific document/reference
- requirement_type: CONFIRMED/INFERRED/ASSUMED
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path
import json


class RequirementType(Enum):
    """Classification of requirement confidence."""
    CONFIRMED = "confirmed"      # Directly from published document
    INFERRED = "inferred"        # Derived from multiple sources
    ASSUMED = "assumed"          # Engineering assumption with rationale


class ConfidenceLevel(Enum):
    """Confidence in requirement value."""
    HIGH = "high"      # Multiple authoritative sources
    MEDIUM = "medium"   # Some evidence
    LOW = "low"         # Single source or speculation


@dataclass
class Requirement:
    """Single aerospace requirement with full traceability."""
    
    parameter: str                          # Parameter name (e.g., "Power", "RPM")
    value: str                              # Value or range
    unit: str                               # Unit of measurement
    
    # Source tracking
    source: str                             # Primary source (e.g., "DO-160G", "Honeywell Patent US12345")
    section: Optional[str] = None           # Section/clause reference
    citation: Optional[str] = None          # Full citation text
    
    # Confidence
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    requirement_type: RequirementType = RequirementType.INFERRED
    
    # Context
    category: str = "general"               # Certification/Benchmark/Environmental/Performance
    notes: Optional[str] = None            # Additional context
    
    # Traceability
    related_requirements: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


@dataclass  
class CertificationRequirement:
    """DO-160, ARP, DO-xxx certification requirements."""
    
    # Required fields first
    standard: str                           # DO-160G, ARP4754A, etc.
    section: str                            # Section number
    test_category: str                      # Temperature, Vibration, EMI, etc.
    test_condition: str                     # Specific test condition
    parameter: str
    value_range: str                        # "-40°C to +70°C"
    unit: str
    source_document: str
    
    # Optional fields with defaults
    subsection: Optional[str] = None      # Subsection
    severity_level: str = "E"                # DO-160 severity level (A/B/C/D/E)
    page_clause: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    notes: Optional[str] = None


@dataclass
class ProductBenchmark:
    """Existing aerospace generator product specifications."""
    
    # Required fields first
    manufacturer: str                      # Honeywell, GE, Safran, etc.
    product_name: str                      # Starter-generator model
    source: str                            # Product datasheet, brochure
    
    # Optional specifications
    product_family: Optional[str] = None   # Series name
    power_kw: Optional[float] = None
    voltage_v: Optional[float] = None
    rpm: Optional[float] = None
    weight_kg: Optional[float] = None
    efficiency_pct: Optional[float] = None
    
    # Operating conditions
    cooling_type: Optional[str] = None     # Air, Oil, Liquid
    max_temp_c: Optional[float] = None
    altitude_ft: Optional[float] = None
    
    # Source details
    url: Optional[str] = None
    year: Optional[int] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Notes
    notes: Optional[str] = None


@dataclass
class PatentDisclosure:
    """Patent-based performance targets."""
    
    # Required fields
    patent_number: str                     # US12345678
    title: str
    assignee: str                          # Honeywell International Inc.
    technology_area: str                   # "AFPM Generator", "Starter-Generator"
    
    # Optional fields
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    
    # Claims relevant to AFPM
    claimed_parameters: dict = field(default_factory=dict)
    # Example: {"power_density": "5 kW/kg", "efficiency": "98.5%"}
    
    # Source
    url: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Context
    notes: Optional[str] = None


class AerospaceRequirementsDB:
    """Central database for all aerospace requirements."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("aerospace_requirements/db.json")
        
        # Collections
        self.certification_requirements: list[CertificationRequirement] = []
        self.product_benchmarks: list[ProductBenchmark] = []
        self.patent_disclosures: list[PatentDisclosure] = []
        self.performance_targets: list[Requirement] = []
        
        # Summary table
        self.requirements_matrix: dict = {}  # parameter -> {min, target, stretch, source}
    
    def add_certification_requirement(self, req: CertificationRequirement) -> None:
        """Add DO-160, ARP, or other certification requirement."""
        self.certification_requirements.append(req)
    
    def add_product_benchmark(self, bench: ProductBenchmark) -> None:
        """Add existing product specification."""
        self.product_benchmarks.append(bench)
    
    def add_patent_disclosure(self, patent: PatentDisclosure) -> None:
        """Add patent-based target."""
        self.patent_disclosures.append(patent)
    
    def add_performance_target(self, req: Requirement) -> None:
        """Add performance target with full traceability."""
        self.performance_targets.append(req)
        self._update_requirements_matrix(req)
    
    def _update_requirements_matrix(self, req: Requirement) -> None:
        """Update the summary requirements matrix."""
        param = req.parameter
        if param not in self.requirements_matrix:
            self.requirements_matrix[param] = {
                "minimum": None,
                "target": None,
                "stretch": None,
                "unit": req.unit,
                "sources": [],
                "confidence": req.confidence.value,
                "type": req.requirement_type.value
            }
        
        self.requirements_matrix[param]["sources"].append({
            "value": req.value,
            "source": req.source,
            "confidence": req.confidence.value
        })
    
    def get_requirements_table(self) -> dict:
        """Generate the requirements traceability table."""
        return {
            "parameters": self.requirements_matrix,
            "certification_count": len(self.certification_requirements),
            "benchmark_count": len(self.product_benchmarks),
            "patent_count": len(self.patent_disclosures),
        }
    
    def export_markdown(self, output_path: Path) -> None:
        """Export requirements as markdown report."""
        lines = [
            "# Aerospace AFPM Generator Requirements Database",
            "",
            "## Executive Summary",
            f"- **Certification Requirements**: {len(self.certification_requirements)}",
            f"- **Product Benchmarks**: {len(self.product_benchmarks)}",
            f"- **Patent Disclosures**: {len(self.patent_disclosures)}",
            f"- **Performance Targets**: {len(self.performance_targets)}",
            "",
            "## Requirements Traceability Matrix",
            "",
            "| Parameter | Minimum | Target | Stretch Goal | Unit | Confidence | Type | Sources |",
            "|-----------|---------|--------|--------------|------|------------|------|---------|",
        ]
        
        for param, data in self.requirements_matrix.items():
            sources = ", ".join([s["source"] for s in data["sources"][:2]])
            lines.append(
                f"| {param} | {data['minimum'] or '?'} | {data['target'] or '?'} | "
                f"{data['stretch'] or '?'} | {data['unit']} | {data['confidence']} | "
                f"{data['type']} | {sources} |"
            )
        
        lines.extend([
            "",
            "## Certification Requirements",
            "",
        ])
        
        for req in self.certification_requirements:
            lines.append(f"### {req.standard} - {req.test_category}")
            lines.append(f"- **Section**: {req.section}")
            lines.append(f"- **Parameter**: {req.parameter}")
            lines.append(f"- **Requirement**: {req.value_range} {req.unit}")
            lines.append(f"- **Severity Level**: {req.severity_level}")
            lines.append(f"- **Source**: {req.source_document}")
            lines.append("")
        
        lines.extend([
            "## Product Benchmarks",
            "",
            "| Manufacturer | Product | Power (kW) | Weight (kg) | Efficiency (%) | Source |",
            "|--------------|---------|------------|-------------|----------------|--------|",
        ])
        
        for bench in self.product_benchmarks:
            lines.append(
                f"| {bench.manufacturer} | {bench.product_name} | "
                f"{bench.power_kw or '?'} | {bench.weight_kg or '?'} | "
                f"{bench.efficiency_pct or '?'} | {bench.source} |"
            )
        
        output_path.write_text("\n".join(lines), encoding="utf-8")
    
    def save(self) -> None:
        """Save database to JSON."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "certification_requirements": [
                {
                    "standard": r.standard,
                    "section": r.section,
                    "test_category": r.test_category,
                    "parameter": r.parameter,
                    "value_range": r.value_range,
                    "unit": r.unit,
                    "severity_level": r.severity_level,
                    "source": r.source_document,
                }
                for r in self.certification_requirements
            ],
            "product_benchmarks": [
                {
                    "manufacturer": b.manufacturer,
                    "product": b.product_name,
                    "power_kw": b.power_kw,
                    "weight_kg": b.weight_kg,
                    "efficiency_pct": b.efficiency_pct,
                    "source": b.source,
                }
                for b in self.product_benchmarks
            ],
            "requirements_matrix": self.requirements_matrix,
        }
        
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)


def initialize_do160_requirements() -> list[CertificationRequirement]:
    """Initialize DO-160G environmental requirements for generators."""
    
    reqs = []
    
    # Temperature (Section 4)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="4",
        test_category="Temperature",
        test_condition="Operating Low",
        parameter="Operating Temperature Low",
        value_range="-40°C",
        unit="°C",
        source_document="DO-160G Section 4",
        subsection="4.5",
        severity_level="E",
        page_clause="Table 4-1",
        confidence=ConfidenceLevel.HIGH,
        notes="Category E: Extended temperature range for turbine engine equipment"
    ))
    
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="4",
        test_category="Temperature",
        test_condition="Operating High",
        parameter="Operating Temperature High",
        value_range="+70°C",
        unit="°C",
        source_document="DO-160G Section 4",
        subsection="4.5",
        severity_level="E",
        page_clause="Table 4-1",
        confidence=ConfidenceLevel.HIGH,
        notes="Category E: Extended temperature range"
    ))
    
    # Altitude (Section 5)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="5",
        test_category="Altitude",
        test_condition="Maximum Operating",
        parameter="Operating Altitude",
        value_range="55,000",
        unit="ft",
        source_document="DO-160G Section 5",
        severity_level="E",
        page_clause="Table 5-1",
        confidence=ConfidenceLevel.HIGH,
        notes="Category E: Standard aircraft altitude"
    ))
    
    # Vibration (Section 8)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="8",
        test_category="Vibration",
        test_condition="Sine Vibration",
        parameter="Vibration Level",
        value_range="10g (5-2000 Hz)",
        unit="g",
        source_document="DO-160G Section 8",
        severity_level="E",
        page_clause="Curves E",
        confidence=ConfidenceLevel.HIGH,
        notes="Category E: Turbine engine zone equipment"
    ))
    
    # Shock (Section 7)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="7",
        test_category="Shock",
        test_condition="Operating Shock",
        parameter="Shock Level",
        value_range="20g (11ms half-sine)",
        unit="g",
        source_document="DO-160G Section 7",
        severity_level="E",
        page_clause="Table 7-2",
        confidence=ConfidenceLevel.HIGH,
        notes="Category E: Equipment in engine nacelle"
    ))
    
    # Humidity (Section 6)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="6",
        test_category="Humidity",
        test_condition="High Humidity",
        parameter="Humidity Resistance",
        value_range="95% RH at 50°C",
        unit="% RH",
        source_document="DO-160G Section 6",
        severity_level="E",
        page_clause="Standard test",
        confidence=ConfidenceLevel.HIGH,
        notes="Tropical environment simulation"
    ))
    
    # EMI/EMC (Section 21 & 22)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="21",
        test_category="RF Emission",
        test_condition="Conducted and Radiated",
        parameter="EMI Emissions",
        value_range="Category M",
        unit="-",
        source_document="DO-160G Section 21",
        severity_level="M",
        page_clause="Table 21-4",
        confidence=ConfidenceLevel.HIGH,
        notes="Category M: Equipment in areas with sensitive equipment"
    ))
    
    # Lightning (Section 22)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="22",
        test_category="Lightning Induced",
        test_condition="Transient Susceptibility",
        parameter="Lightning Protection",
        value_range="Level 3 (300V/150A)",
        unit="V/A",
        source_document="DO-160G Section 22",
        severity_level="A3J3L3",
        page_clause="Table 22-2",
        confidence=ConfidenceLevel.HIGH,
        notes="Level 3: Equipment with critical functions"
    ))
    
    # Power Transients (Section 16)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="16",
        test_category="Power Input",
        test_condition="Voltage Transients",
        parameter="DC Power Bus Transients",
        value_range="28V nominal, 80V spike",
        unit="V",
        source_document="DO-160G Section 16",
        severity_level="B",
        page_clause="Table 16-3",
        confidence=ConfidenceLevel.HIGH,
        notes="Category B: 28V DC aircraft power"
    ))
    
    # Flammability (Section 26)
    reqs.append(CertificationRequirement(
        standard="DO-160G",
        section="26",
        test_category="Fire Resistance",
        test_condition="Flammability",
        parameter="Flammability Rating",
        value_range="Self-extinguishing within 15s",
        unit="s",
        source_document="DO-160G Section 26",
        severity_level="-",
        page_clause="60s flame test",
        confidence=ConfidenceLevel.HIGH,
        notes="Materials must be fire-resistant"
    ))
    
    return reqs


def initialize_arp_requirements() -> list[CertificationRequirement]:
    """Initialize ARP4754 and ARP4761 process requirements."""
    
    reqs = []
    
    # ARP4754A - Development Process Requirements
    reqs.append(CertificationRequirement(
        standard="ARP4754A",
        section="3.0",
        test_category="Development Process",
        test_condition="System Development",
        parameter="Development Assurance Level",
        value_range="A, B, C, D, E",
        unit="-",
        source_document="ARP4754A Guidelines",
        severity_level="DAL-A",
        page_clause="Section 3",
        confidence=ConfidenceLevel.HIGH,
        notes="DAL-A: Catastrophic failure must be extremely improbable. Generator control is typically DAL-B or DAL-C."
    ))
    
    reqs.append(CertificationRequirement(
        standard="ARP4754A",
        section="4.0",
        test_category="Validation Process",
        test_condition="Requirements Validation",
        parameter="Validation Coverage",
        value_range="100% of requirements",
        unit="%",
        source_document="ARP4754A Guidelines",
        severity_level="Required",
        page_clause="Section 4",
        confidence=ConfidenceLevel.HIGH,
        notes="All requirements must be validated through review, analysis, or test."
    ))
    
    # ARP4761 - Safety Assessment
    reqs.append(CertificationRequirement(
        standard="ARP4761",
        section="3.2",
        test_category="Safety Assessment",
        test_condition="Functional Hazard Assessment",
        parameter="FHA Coverage",
        value_range="All functions",
        unit="-",
        source_document="ARP4761 Guidelines",
        severity_level="Required",
        page_clause="Section 3.2",
        confidence=ConfidenceLevel.HIGH,
        notes="Functional Hazard Assessment must identify all potential failure conditions."
    ))
    
    reqs.append(CertificationRequirement(
        standard="ARP4761",
        section="4.0",
        test_category="Safety Assessment",
        test_condition="Fault Tree Analysis",
        parameter="Single Fault Tolerance",
        value_range="No single failure",
        unit="-",
        source_document="ARP4761 Guidelines",
        severity_level="Required",
        page_clause="Section 4",
        confidence=ConfidenceLevel.HIGH,
        notes="Hazardous and catastrophic failure conditions must be single-fault tolerant."
    ))
    
    reqs.append(CertificationRequirement(
        standard="ARP4761",
        section="5.0",
        test_category="Safety Assessment",
        test_condition="Failure Modes and Effects Analysis",
        parameter="FMEA Coverage",
        value_range="All components",
        unit="-",
        source_document="ARP4761 Guidelines",
        severity_level="Required",
        page_clause="Section 5",
        confidence=ConfidenceLevel.HIGH,
        notes="Failure Modes and Effects Analysis for all electrical and mechanical components."
    ))
    
    # DO-254 - Airborne Electronic Hardware
    reqs.append(CertificationRequirement(
        standard="DO-254",
        section="2.0",
        test_category="Hardware Design",
        test_condition="Design Assurance",
        parameter="Design Assurance Level",
        value_range="A, B, C, D, E",
        unit="-",
        source_document="DO-254 Guidelines",
        severity_level="Level A",
        page_clause="Section 2",
        confidence=ConfidenceLevel.HIGH,
        notes="Generator control electronics typically Level B or C."
    ))
    
    reqs.append(CertificationRequirement(
        standard="DO-254",
        section="4.0",
        test_category="Hardware Design",
        test_condition="Verification Process",
        parameter="Verification Coverage",
        value_range="100% of design",
        unit="%",
        source_document="DO-254 Guidelines",
        severity_level="Required",
        page_clause="Section 4",
        confidence=ConfidenceLevel.HIGH,
        notes="All requirements must be verified through review, analysis, simulation, or test."
    ))
    
    return reqs


def create_initial_database() -> AerospaceRequirementsDB:
    """Create initial aerospace requirements database."""
    db = AerospaceRequirementsDB()
    
    # Add DO-160G requirements
    for req in initialize_do160_requirements():
        db.add_certification_requirement(req)
    
    # Add ARP4754/ARP4761 process requirements
    for req in initialize_arp_requirements():
        db.add_certification_requirement(req)
    
    # Add confirmed Honeywell 1-MW generator benchmark (May 2022)
    db.add_product_benchmark(ProductBenchmark(
        manufacturer="Honeywell",
        product_name="1-Megawatt Generator",
        source="Honeywell Press Release, May 31, 2022",
        url="https://aerospace.honeywell.com/us/en/about-us/press-release/2022/05/honeywell-megawatt-generator-achieves-milestone",
        power_kw=1000.0,
        weight_kg=127.0,  # 280 pounds
        efficiency_pct=97.0,
        year=2022,
        confidence=ConfidenceLevel.HIGH,
        notes="Power density: ~8kW/kg. Industry first 1MW aerospace generator. Can also operate as 1MW motor without modifications."
    ))
    
    # Add market comparison benchmark (from Honeywell press release)
    db.add_product_benchmark(ProductBenchmark(
        manufacturer="Market Standard",
        product_name="Typical Aerospace Generator",
        source="Honeywell Benchmark Comparison",
        power_kw=100.0,  # Representative
        efficiency_pct=89.0,  # 88-90% range
        confidence=ConfidenceLevel.MEDIUM,
        notes="Typical power density: 2-3 kW/kg. Efficiency: 88-90%"
    ))
    
    # Add Safran DC starter generator benchmark
    db.add_product_benchmark(ProductBenchmark(
        manufacturer="Safran",
        product_name="23064 Series DC Starter Generator",
        source="Naasco Product Catalog",
        power_kw=9.0,
        voltage_v=28.0,
        rpm=8000,  # Estimated from speed range
        confidence=ConfidenceLevel.MEDIUM,
        notes="300A continuous load. Used on various aircraft platforms."
    ))
    
    # Add confirmed performance targets from Honeywell data
    db.add_performance_target(Requirement(
        parameter="Power Density",
        value="8.0",
        unit="kW/kg",
        source="Honeywell 1-MW Generator Press Release",
        category="performance",
        confidence=ConfidenceLevel.HIGH,
        requirement_type=RequirementType.CONFIRMED,
        notes="Achieved by Honeywell 1-MW generator (2022). Market standard is 2-3 kW/kg."
    ))
    
    db.add_performance_target(Requirement(
        parameter="Efficiency",
        value="97.0",
        unit="%",
        source="Honeywell 1-MW Generator Press Release",
        category="performance",
        confidence=ConfidenceLevel.HIGH,
        requirement_type=RequirementType.CONFIRMED,
        notes="Achieved by Honeywell 1-MW generator. Market standard is 88-90%."
    ))
    
    db.add_performance_target(Requirement(
        parameter="Power",
        value="50-1000",
        unit="kW",
        source="Honeywell Product Range",
        category="performance",
        confidence=ConfidenceLevel.HIGH,
        requirement_type=RequirementType.CONFIRMED,
        notes="Honeywell 1-MW generator demonstrated. Range covers from small aircraft to large hybrid-electric systems."
    ))
    
    db.add_performance_target(Requirement(
        parameter="Weight",
        value="<12",
        unit="kg",
        source="Honeywell Challenge Statement",
        category="performance",
        confidence=ConfidenceLevel.LOW,
        requirement_type=RequirementType.ASSUMED,
        notes="Challenge target for 50kW system. Honeywell 1-MW is 127kg (scaled: ~6.4kg for 50kW). 12kg allows margin."
    ))
    
    db.add_performance_target(Requirement(
        parameter="RPM",
        value="1800-12000",
        unit="rpm",
        source="Aerospace Generator Range",
        category="performance",
        confidence=ConfidenceLevel.MEDIUM,
        requirement_type=RequirementType.INFERRED,
        notes="Typical range for aerospace starter-generators. Lower RPM for direct-drive, higher for geared systems."
    ))
    
    db.add_performance_target(Requirement(
        parameter="Reliability",
        value=">99.0",
        unit="%",
        source="Aerospace Industry Standard",
        category="performance",
        confidence=ConfidenceLevel.MEDIUM,
        requirement_type=RequirementType.INFERRED,
        notes="Typical requirement for critical aircraft systems. 99.2% mentioned in challenge for high-reliability systems."
    ))
    
    db.add_performance_target(Requirement(
        parameter="Fault Tolerance",
        value="Single fault tolerant",
        unit="-",
        source="ARP4761 Safety Assessment",
        category="certification",
        confidence=ConfidenceLevel.HIGH,
        requirement_type=RequirementType.CONFIRMED,
        notes="Required for hazardous/catastrophic failure conditions per ARP4761."
    ))
    
    return db


if __name__ == "__main__":
    # Create initial database
    db = create_initial_database()
    db.save()
    
    # Export markdown report
    db.export_markdown(Path("aerospace_requirements/requirements_report.md"))
    
    print("Aerospace requirements database created.")
    print(f"- {len(db.certification_requirements)} certification requirements")
    print(f"- {len(db.performance_targets)} performance targets")
    print("Exported to: aerospace_requirements/")
