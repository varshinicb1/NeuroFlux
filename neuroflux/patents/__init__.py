"""Patent integration module for NeuroFlux.

Provides prior art search, novelty scoring, and patent landscape analysis
using free patent APIs (Google Patents, EPO Open Patent Services).
"""

from neuroflux.patents.api import PatentAPIClient, PatentSearchResult
from neuroflux.patents.novelty import NoveltyScorer, NoveltyScore
from neuroflux.patents.landscape import PatentLandscapeAnalyzer

__all__ = [
    "PatentAPIClient",
    "PatentSearchResult",
    "NoveltyScorer",
    "NoveltyScore",
    "PatentLandscapeAnalyzer",
]
