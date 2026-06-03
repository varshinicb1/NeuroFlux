"""Novelty scoring for design candidates against patent prior art.

Implements algorithms to assess patentability and identify
inventive deltas between a new design and existing patents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from neuroflux.patents.api import PatentSearchResult
    from neuroflux.discovery import DesignCandidate


class NoveltyScore(BaseModel):
    """Novelty assessment for a design candidate."""
    
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall novelty score (0-1, higher is more novel)")
    patentability_score: float = Field(..., ge=0.0, le=1.0, description="Estimated probability of patent grant")
    inventive_step_score: float = Field(..., ge=0.0, le=1.0, description="Non-obviousness assessment")
    
    # Detailed breakdown
    feature_overlap: float = Field(..., ge=0.0, le=1.0, description="Fraction of features found in prior art")
    novel_features: list[str] = Field(default_factory=list, description="Features not found in prior art")
    overlapping_patents: list[str] = Field(default_factory=list, description="Patent numbers with high overlap")
    
    # Recommendations
    risks: list[str] = Field(default_factory=list, description="Potential patent risks")
    opportunities: list[str] = Field(default_factory=list, description="Patentable opportunities")
    
    # Confidence
    confidence: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    search_coverage: str = Field(default="partial", description="Extent of prior art search")
    
    def to_report(self) -> str:
        """Generate human-readable novelty report."""
        lines = [
            "# Novelty Assessment Report",
            "",
            f"**Overall Novelty Score:** {self.overall_score:.2f}/1.0",
            f"**Patentability Probability:** {self.patentability_score:.1%}",
            f"**Inventive Step:** {self.inventive_step_score:.2f}/1.0",
            f"**Confidence:** {self.confidence.upper()}",
            "",
            "## Feature Analysis",
            f"- Feature Overlap with Prior Art: {self.feature_overlap:.1%}",
            f"- Novel Features: {len(self.novel_features)}",
        ]
        
        if self.novel_features:
            lines.extend([f"  - {f}" for f in self.novel_features])
        
        if self.overlapping_patents:
            lines.extend([
                "",
                "## Potentially Overlapping Patents",
            ])
            lines.extend([f"- {p}" for p in self.overlapping_patents])
        
        if self.risks:
            lines.extend([
                "",
                "## ⚠️ Risks",
            ])
            lines.extend([f"- {r}" for r in self.risks])
        
        if self.opportunities:
            lines.extend([
                "",
                "## ✓ Patentable Opportunities",
            ])
            lines.extend([f"- {o}" for o in self.opportunities])
        
        return "\n".join(lines)


@dataclass
class DesignFeatureExtractor:
    """Extract searchable features from a design candidate."""
    
    def extract(self, candidate: "DesignCandidate") -> list[str]:
        """Extract searchable features from a design.
        
        Args:
            candidate: Design candidate to analyze
        
        Returns:
            List of feature strings suitable for patent search
        """
        features = []
        
        # Geometry features
        geom = candidate.analytical_input.geometry
        if geom:
            features.append(f"axial flux machine")
            features.append(f"outer diameter {geom.outer_diameter_m*1000:.0f} mm")
            if hasattr(geom, 'airgap_m'):
                features.append(f"air gap {geom.airgap_m*1000:.1f} mm")
        
        # Topology
        features.append(f"topology {candidate.analytical_input.topology.value}")
        
        # Operating point
        op = candidate.analytical_input.operating_point
        if op:
            features.append(f"{op.speed_rpm} rpm")
            features.append(f"{op.power_w/1000:.1f} kW")
        
        # Magnet configuration
        mag = candidate.analytical_input.magnet_config
        if mag:
            features.append(f"{mag.magnet_type.value} magnets")
            if mag.is_halbach:
                features.append("Halbach array")
        
        # Performance
        result = candidate.analytical_result
        if result:
            features.append(f"efficiency {result.efficiency:.1%}")
            features.append(f"torque {result.torque_nm:.2f} Nm")
        
        return features


class NoveltyScorer:
    """Score novelty of a design candidate against prior art.
    
    Uses multiple strategies:
    1. Feature overlap analysis
    2. Semantic similarity (future: embeddings)
    3. Citation network analysis
    4. Inventive step assessment
    """
    
    def __init__(self):
        self.feature_extractor = DesignFeatureExtractor()
    
    def score_novelty(
        self,
        candidate: "DesignCandidate",
        prior_art: list["PatentSearchResult"],
    ) -> NoveltyScore:
        """Calculate novelty score for a design candidate.
        
        Args:
            candidate: Design to assess
            prior_art: List of relevant prior art patents
        
        Returns:
            NoveltyScore with detailed analysis
        """
        # Extract features from design
        design_features = self.feature_extractor.extract(candidate)
        
        # Calculate feature overlap
        feature_overlap, novel_features, overlapping = self._analyze_feature_overlap(
            design_features, prior_art
        )
        
        # Calculate scores
        overall_score = 1.0 - feature_overlap  # Inverse of overlap
        patentability = self._estimate_patentability(overall_score, len(prior_art))
        inventive_step = self._assess_inventive_step(novel_features, prior_art)
        
        # Identify risks and opportunities
        risks = self._identify_risks(feature_overlap, overlapping, prior_art)
        opportunities = self._identify_opportunities(novel_features, candidate)
        
        # Determine confidence
        confidence = self._determine_confidence(len(prior_art), len(design_features))
        
        return NoveltyScore(
            overall_score=overall_score,
            patentability_score=patentability,
            inventive_step_score=inventive_step,
            feature_overlap=feature_overlap,
            novel_features=novel_features,
            overlapping_patents=[p.patent_number for p in overlapping],
            risks=risks,
            opportunities=opportunities,
            confidence=confidence,
            search_coverage=f"{len(prior_art)} patents analyzed",
        )
    
    def _analyze_feature_overlap(
        self,
        design_features: list[str],
        prior_art: list["PatentSearchResult"],
    ) -> tuple[float, list[str], list["PatentSearchResult"]]:
        """Analyze which design features appear in prior art.
        
        Returns:
            (overlap_fraction, novel_features, overlapping_patents)
        """
        found_features = set()
        overlapping_patents = []
        
        for patent in prior_art:
            patent_text = f"{patent.title} {patent.abstract}".lower()
            patent_features_found = []
            
            for feature in design_features:
                # Simple keyword matching (future: use embeddings)
                feature_lower = feature.lower()
                if self._feature_in_text(feature_lower, patent_text):
                    found_features.add(feature)
                    patent_features_found.append(feature)
            
            if patent_features_found:
                overlapping_patents.append(patent)
        
        novel_features = [f for f in design_features if f not in found_features]
        overlap_fraction = len(found_features) / len(design_features) if design_features else 0.0
        
        return overlap_fraction, novel_features, overlapping_patents
    
    def _feature_in_text(self, feature: str, text: str) -> bool:
        """Check if a feature is described in text.
        
        Uses fuzzy matching for better recall.
        """
        # Exact match
        if feature in text:
            return True
        
        # Token-based matching for compound features
        tokens = feature.split()
        if len(tokens) > 1:
            # Check if all tokens appear (allowing different order)
            matches = sum(1 for token in tokens if token in text)
            if matches >= len(tokens) * 0.8:  # 80% of tokens
                return True
        
        # Numeric similarity (e.g., "500 mm" vs "0.5 m")
        numbers_in_feature = re.findall(r'[\d.]+', feature)
        numbers_in_text = re.findall(r'[\d.]+', text)
        
        for num in numbers_in_feature:
            try:
                val = float(num)
                # Check if similar number appears (±20% tolerance)
                for text_num in numbers_in_text:
                    try:
                        text_val = float(text_num)
                        if abs(val - text_val) / max(val, text_val) < 0.2:
                            return True
                    except ValueError:
                        continue
            except ValueError:
                continue
        
        return False
    
    def _estimate_patentability(
        self,
        novelty_score: float,
        prior_art_count: int,
    ) -> float:
        """Estimate probability of patent grant.
        
        Based on:
        - Novelty score (higher is better)
        - Amount of prior art (more searched = more confidence)
        """
        # Base probability on novelty
        base_prob = novelty_score
        
        # Adjust for search thoroughness
        # More prior art searched = more confidence in novelty assessment
        if prior_art_count < 5:
            confidence_factor = 0.8  # Low confidence
        elif prior_art_count < 20:
            confidence_factor = 0.9  # Medium confidence
        else:
            confidence_factor = 0.95  # High confidence
        
        return base_prob * confidence_factor
    
    def _assess_inventive_step(
        self,
        novel_features: list[str],
        prior_art: list["PatentSearchResult"],
    ) -> float:
        """Assess non-obviousness (inventive step).
        
        Considers:
        - Number and significance of novel features
        - Whether combination would be obvious
        - Technical problem solved
        """
        if not novel_features:
            return 0.0
        
        # Score based on number and type of novel features
        feature_score = min(len(novel_features) / 3.0, 1.0)  # Cap at 3+ features
        
        # Adjust for feature significance
        # Structural/geometry changes are more inventive than parameter tweaks
        significant_keywords = ["topology", "array", "configuration", "structure", "system"]
        significant_count = sum(
            1 for f in novel_features 
            if any(kw in f.lower() for kw in significant_keywords)
        )
        
        significance_boost = min(significant_count * 0.1, 0.3)  # Max +0.3
        
        return min(feature_score + significance_boost, 1.0)
    
    def _identify_risks(
        self,
        feature_overlap: float,
        overlapping_patents: list["PatentSearchResult"],
        all_prior_art: list["PatentSearchResult"],
    ) -> list[str]:
        """Identify potential patent risks."""
        risks = []
        
        if feature_overlap > 0.8:
            risks.append(f"High feature overlap ({feature_overlap:.0%}) with prior art")
        
        if len(overlapping_patents) > 3:
            risks.append(f"Many overlapping patents ({len(overlapping_patents)}) - crowded field")
        
        # Check for recent patents (higher risk of being active)
        recent_patents = [p for p in overlapping_patents if self._is_recent(p)]
        if recent_patents:
            risks.append(f"{len(recent_patents)} recent patents may still be active")
        
        # Check for broad claims
        broad_patents = [p for p in overlapping_patents if p.claims_count > 20]
        if broad_patents:
            risks.append(f"{len(broad_patents)} patents have broad claim sets")
        
        return risks
    
    def _identify_opportunities(
        self,
        novel_features: list[str],
        candidate: "DesignCandidate",
    ) -> list[str]:
        """Identify patentable opportunities."""
        opportunities = []
        
        if novel_features:
            opportunities.append(f"{len(novel_features)} novel features suitable for patent claims")
        
        # Check for performance improvements
        result = candidate.analytical_result
        if result and result.efficiency > 0.90:
            opportunities.append(f"High efficiency ({result.efficiency:.1%}) is a patentable advantage")
        
        # Check for novel topology
        if "topology" in str(candidate.analytical_input.topology.value).lower():
            opportunities.append("Unique topology configuration is patentable")
        
        # Specific feature-based opportunities
        for feature in novel_features:
            if "halbach" in feature.lower():
                opportunities.append("Halbach array configuration may be patentable")
            if "cooling" in feature.lower() or "thermal" in feature.lower():
                opportunities.append("Thermal management approach is patentable")
            if "modular" in feature.lower():
                opportunities.append("Modular design approach is patentable")
        
        return opportunities
    
    def _determine_confidence(
        self,
        prior_art_count: int,
        feature_count: int,
    ) -> str:
        """Determine confidence level in novelty assessment."""
        if prior_art_count < 5 or feature_count < 3:
            return "low"
        elif prior_art_count < 20:
            return "medium"
        else:
            return "high"
    
    def _is_recent(self, patent: "PatentSearchResult") -> bool:
        """Check if patent is recent (filed in last 5 years)."""
        from datetime import datetime, timedelta
        
        try:
            filing = datetime.strptime(patent.filing_date, "%Y-%m-%d")
            return datetime.now() - filing < timedelta(days=5*365)
        except (ValueError, TypeError):
            return False
