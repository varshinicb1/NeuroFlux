"""Patent landscape analysis for AFPM technology domain.

Analyzes patent trends, key players, technology evolution, and
white space opportunities in the axial flux permanent magnet space.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neuroflux.patents.api import PatentSearchResult


@dataclass
class LandscapeMetrics:
    """Key metrics from patent landscape analysis."""
    
    total_patents: int = 0
    date_range: tuple[str, str] = ("", "")
    
    # Trends
    filings_by_year: dict[str, int] = field(default_factory=dict)
    
    # Players
    top_assignees: list[tuple[str, int]] = field(default_factory=list)
    top_inventors: list[tuple[str, int]] = field(default_factory=list)
    
    # Technology
    top_classifications: list[tuple[str, int]] = field(default_factory=list)
    technology_clusters: list[dict] = field(default_factory=list)
    
    # Geography
    filings_by_country: dict[str, int] = field(default_factory=dict)
    
    # Quality
    avg_citations_per_patent: float = 0.0
    highly_cited_patents: list[str] = field(default_factory=list)


@dataclass
class WhiteSpaceOpportunity:
    """Identified white space opportunity."""
    
    domain: str
    description: str
    evidence: str
    opportunity_score: float  # 0-1, higher is better opportunity
    recommended_actions: list[str] = field(default_factory=list)


class PatentLandscapeAnalyzer:
    """Analyze patent landscape for AFPM technology.
    
    Provides:
    - Competitive intelligence
    - Technology trend analysis
    - White space identification
    - Freedom-to-operate insights
    """
    
    def __init__(self):
        self.cache_dir = Path.home() / ".neuroflux" / "patent_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_landscape(
        self,
        patents: list["PatentSearchResult"],
    ) -> LandscapeMetrics:
        """Analyze patent landscape from search results.
        
        Args:
            patents: List of patents to analyze
        
        Returns:
            LandscapeMetrics with comprehensive analysis
        """
        if not patents:
            return LandscapeMetrics()
        
        metrics = LandscapeMetrics(total_patents=len(patents))
        
        # Date range
        dates = [p.filing_date for p in patents if p.filing_date]
        if dates:
            metrics.date_range = (min(dates), max(dates))
        
        # Filings by year
        for patent in patents:
            if patent.filing_date:
                year = patent.filing_date[:4]
                metrics.filings_by_year[year] = metrics.filings_by_year.get(year, 0) + 1
        
        # Top assignees
        assignee_counts = defaultdict(int)
        for patent in patents:
            if patent.assignee:
                assignee_counts[patent.assignee] += 1
        metrics.top_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top inventors
        inventor_counts = defaultdict(int)
        for patent in patents:
            for inventor in patent.inventors:
                inventor_counts[inventor] += 1
        metrics.top_inventors = sorted(inventor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Classifications
        class_counts = defaultdict(int)
        for patent in patents:
            for cls in patent.classification:
                class_counts[cls] += 1
        metrics.top_classifications = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Geography
        for patent in patents:
            metrics.filings_by_country[patent.country] = metrics.filings_by_country.get(patent.country, 0) + 1
        
        # Citations
        total_citations = sum(len(p.citations) for p in patents)
        metrics.avg_citations_per_patent = total_citations / len(patents) if patents else 0
        
        # Highly cited patents (top 10%)
        sorted_by_citations = sorted(patents, key=lambda p: len(p.citations), reverse=True)
        top_10_percent = max(1, len(sorted_by_citations) // 10)
        metrics.highly_cited_patents = [p.patent_number for p in sorted_by_citations[:top_10_percent]]
        
        return metrics
    
    def identify_white_spaces(
        self,
        patents: list["PatentSearchResult"],
        technology_areas: list[str] | None = None,
    ) -> list[WhiteSpaceOpportunity]:
        """Identify white space opportunities in the patent landscape.
        
        Args:
            patents: Patent landscape to analyze
            technology_areas: Specific areas to focus on
        
        Returns:
            List of white space opportunities
        """
        opportunities = []
        
        # Default technology areas for AFPM
        if technology_areas is None:
            technology_areas = [
                "cooling_systems",
                "magnet_configurations",
                "winding_topologies",
                "manufacturing_methods",
                "control_systems",
                "structural_designs",
            ]
        
        # Analyze each technology area
        for area in technology_areas:
            area_patents = self._filter_by_technology(patents, area)
            
            if len(area_patents) < 3:
                # Low patent activity = potential white space
                opportunities.append(WhiteSpaceOpportunity(
                    domain=area,
                    description=f"Limited patent activity in {area.replace('_', ' ')}",
                    evidence=f"Only {len(area_patents)} patents found in this area",
                    opportunity_score=0.8,
                    recommended_actions=[
                        f"Investigate {area.replace('_', ' ')} innovations",
                        "Review academic literature for unpatented advances",
                        "Assess technical feasibility of novel approaches",
                    ]
                ))
            elif len(area_patents) > 50:
                # Crowded field but may have sub-areas
                sub_opportunities = self._find_sub_niches(area_patents, area)
                opportunities.extend(sub_opportunities)
        
        # Check for cross-domain opportunities
        cross_domain = self._identify_cross_domain_opportunities(patents)
        opportunities.extend(cross_domain)
        
        # Check for recent filing gaps
        gaps = self._identify_filing_gaps(patents)
        opportunities.extend(gaps)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return opportunities
    
    def _filter_by_technology(
        self,
        patents: list["PatentSearchResult"],
        area: str,
    ) -> list["PatentSearchResult"]:
        """Filter patents by technology area."""
        keywords = {
            "cooling_systems": ["cool", "thermal", "heat", "liquid", "air", "ventilation"],
            "magnet_configurations": ["magnet", "halbach", "array", "pole", "flux"],
            "winding_topologies": ["winding", "coil", "concentrated", "distributed", "turn"],
            "manufacturing_methods": ["manufactur", "assemble", "winding", "coil", "stator"],
            "control_systems": ["control", "sensor", "feedback", "driver", "inverter"],
            "structural_designs": ["structur", "modular", "segment", "core", "support"],
        }
        
        area_keywords = keywords.get(area, [area])
        
        filtered = []
        for patent in patents:
            text = f"{patent.title} {patent.abstract}".lower()
            if any(kw in text for kw in area_keywords):
                filtered.append(patent)
        
        return filtered
    
    def _find_sub_niches(
        self,
        patents: list["PatentSearchResult"],
        area: str,
    ) -> list[WhiteSpaceOpportunity]:
        """Find sub-niches in a crowded technology area."""
        opportunities = []
        
        # Look for under-represented combinations
        # Example: cooling + specific topology
        cooling_patents = [p for p in patents if "cool" in p.title.lower() or "thermal" in p.title.lower()]
        
        if len(cooling_patents) < len(patents) * 0.2:
            opportunities.append(WhiteSpaceOpportunity(
                domain=f"{area}_cooling",
                description=f"Limited cooling-related patents in {area}",
                evidence=f"Only {len(cooling_patents)}/{len(patents)} patents address cooling",
                opportunity_score=0.7,
                recommended_actions=[
                    f"Investigate thermal management in {area}",
                    "Explore novel cooling integration methods",
                ]
            ))
        
        return opportunities
    
    def _identify_cross_domain_opportunities(
        self,
        patents: list["PatentSearchResult"],
    ) -> list[WhiteSpaceOpportunity]:
        """Identify opportunities at intersection of multiple domains."""
        opportunities = []
        
        # Check for additive manufacturing + AFPM
        am_keywords = ["additive", "3d print", "am ", "metal print"]
        am_patents = []
        for patent in patents:
            text = f"{patent.title} {patent.abstract}".lower()
            if any(kw in text for kw in am_keywords):
                am_patents.append(patent)
        
        if len(am_patents) < 2:
            opportunities.append(WhiteSpaceOpportunity(
                domain="additive_manufacturing_afpm",
                description="Additive manufacturing for AFPM components",
                evidence=f"Only {len(am_patents)} patents on AM for AFPM",
                opportunity_score=0.85,
                recommended_actions=[
                    "Investigate 3D printed stator cores",
                    "Explore conformal cooling channels via AM",
                    "Assess cost-benefit of AM for prototyping vs production",
                ]
            ))
        
        # Check for AI/ML + design optimization
        ai_keywords = ["machine learning", "ai", "neural", "optimization", "genetic"]
        ai_patents = []
        for patent in patents:
            text = f"{patent.title} {patent.abstract}".lower()
            if any(kw in text for kw in ai_keywords):
                ai_patents.append(patent)
        
        if len(ai_patents) < 3:
            opportunities.append(WhiteSpaceOpportunity(
                domain="ai_design_optimization",
                description="AI/ML for AFPM design optimization",
                evidence=f"Limited AI patent activity ({len(ai_patents)} patents)",
                opportunity_score=0.9,
                recommended_actions=[
                    "Develop ML-based design optimization workflows",
                    "Investigate generative design for novel topologies",
                    "Create patent on AI-assisted AFPM discovery",
                ]
            ))
        
        return opportunities
    
    def _identify_filing_gaps(
        self,
        patents: list["PatentSearchResult"],
    ) -> list[WhiteSpaceOpportunity]:
        """Identify recent filing gaps that may indicate opportunities."""
        opportunities = []
        
        # Check filing trends in recent years
        recent_years = [str(datetime.now().year - i) for i in range(3)]
        recent_count = sum(
            1 for p in patents 
            if p.filing_date and any(year in p.filing_date for year in recent_years)
        )
        
        if recent_count < len(patents) * 0.1:
            opportunities.append(WhiteSpaceOpportunity(
                domain="recent_filing_gap",
                description="Significant drop in recent patent filings",
                evidence=f"Only {recent_count} patents filed in last 3 years",
                opportunity_score=0.75,
                recommended_actions=[
                    "Accelerate patent filings in active development areas",
                    "Review why patent activity has declined",
                    "Assess if technology is maturing or shifting",
                ]
            ))
        
        return opportunities
    
    def generate_report(
        self,
        metrics: LandscapeMetrics,
        opportunities: list[WhiteSpaceOpportunity],
    ) -> str:
        """Generate comprehensive landscape report."""
        lines = [
            "# Patent Landscape Analysis Report",
            "",
            "## Executive Summary",
            f"- **Total Patents Analyzed:** {metrics.total_patents}",
            f"- **Date Range:** {metrics.date_range[0]} to {metrics.date_range[1]}",
            f"- **White Space Opportunities:** {len(opportunities)}",
            "",
            "## Filing Trends",
        ]
        
        if metrics.filings_by_year:
            lines.extend([
                "| Year | Filings |",
                "|------|---------|",
            ])
            for year in sorted(metrics.filings_by_year.keys()):
                lines.append(f"| {year} | {metrics.filings_by_year[year]} |")
        
        lines.extend([
            "",
            "## Top Patent Holders",
        ])
        
        if metrics.top_assignees:
            lines.extend([
                "| Company | Patents |",
                "|---------|---------|",
            ])
            for company, count in metrics.top_assignees[:5]:
                lines.append(f"| {company} | {count} |")
        
        lines.extend([
            "",
            "## Technology Classifications",
        ])
        
        if metrics.top_classifications:
            lines.extend([
                "| Classification | Count | Description |",
                "|----------------|-------|-------------|",
            ])
            for cls, count in metrics.top_classifications[:5]:
                desc = self._get_classification_description(cls)
                lines.append(f"| {cls} | {count} | {desc} |")
        
        lines.extend([
            "",
            "## Geographic Distribution",
        ])
        
        if metrics.filings_by_country:
            for country, count in sorted(metrics.filings_by_country.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- {country}: {count} patents")
        
        lines.extend([
            "",
            f"## Patent Quality Metrics",
            f"- Average citations per patent: {metrics.avg_citations_per_patent:.1f}",
            f"- Highly cited patents: {len(metrics.highly_cited_patents)}",
            "",
            "## Top White Space Opportunities",
        ])
        
        for i, opp in enumerate(opportunities[:5], 1):
            lines.extend([
                f"### {i}. {opp.domain.replace('_', ' ').title()}",
                f"**Opportunity Score:** {opp.opportunity_score:.2f}/1.0",
                f"**Description:** {opp.description}",
                f"**Evidence:** {opp.evidence}",
                "",
                "**Recommended Actions:**",
            ])
            lines.extend([f"- {action}" for action in opp.recommended_actions])
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_classification_description(self, code: str) -> str:
        """Get human-readable description for CPC classification."""
        descriptions = {
            "H02K1/27": "Permanent magnet machines",
            "H02K21/12": "Axial flux machines",
            "H02K3/04": "Windings for salient poles",
            "H02K7/18": "Structural association with gearing",
            "H02K9/00": "Arrangements for cooling",
        }
        return descriptions.get(code, "Machine components")
    
    def save_analysis(
        self,
        metrics: LandscapeMetrics,
        opportunities: list[WhiteSpaceOpportunity],
        output_path: str | Path,
    ) -> None:
        """Save landscape analysis to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "metrics": {
                "total_patents": metrics.total_patents,
                "date_range": metrics.date_range,
                "filings_by_year": metrics.filings_by_year,
                "top_assignees": metrics.top_assignees,
                "top_classifications": metrics.top_classifications,
                "filings_by_country": metrics.filings_by_country,
                "avg_citations": metrics.avg_citations_per_patent,
            },
            "opportunities": [
                {
                    "domain": o.domain,
                    "description": o.description,
                    "score": o.opportunity_score,
                    "actions": o.recommended_actions,
                }
                for o in opportunities
            ],
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
