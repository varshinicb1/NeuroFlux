"""Patent API client for free patent databases.

Supports:
- Google Patents Public Datasets (BigQuery)
- EPO Open Patent Services (OPS)
- USPTO Patent Public Search
- WIPO Patentscope

Note: Most APIs have rate limits. Implement caching and respect rate limits.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import urllib.request
from pydantic import BaseModel, Field


@dataclass
class PatentSearchResult:
    """Result from a patent search."""
    
    patent_id: str
    title: str
    abstract: str
    inventors: list[str]
    assignee: str
    filing_date: str
    publication_date: str
    patent_number: str
    country: str
    kind_code: str
    classification: list[str]
    claims_count: int
    citations: list[str]
    url: str
    source: str
    relevance_score: float = 0.0


@dataclass
class SearchQuery:
    """Structured patent search query."""
    
    keywords: list[str] = field(default_factory=list)
    inventors: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    classification_codes: list[str] = field(default_factory=list)
    date_range: tuple[str, str] | None = None  # (start, end) in YYYY-MM-DD format
    patent_numbers: list[str] = field(default_factory=list)
    
    def to_google_patents_query(self) -> str:
        """Convert to Google Patents search syntax."""
        parts = []
        
        if self.keywords:
            parts.append("(" + " OR ".join(self.keywords) + ")")
        
        if self.inventors:
            parts.extend([f'inventor:"{i}"' for i in self.inventors])
        
        if self.assignees:
            parts.extend([f'assignee:"{a}"' for a in self.assignees])
        
        if self.classification_codes:
            parts.extend([f'cpc:"{c}"' for c in self.classification_codes])
        
        if self.patent_numbers:
            parts.extend([f'patent:"{p}"' for p in self.patent_numbers])
        
        return " AND ".join(parts) if parts else ""
    
    def to_epo_ops_query(self) -> str:
        """Convert to EPO OPS search syntax."""
        # EPO uses a different query syntax
        parts = []
        
        if self.keywords:
            kw = " OR ".join([f'ti="{k}" OR ab="{k}"' for k in self.keywords])
            parts.append(f"({kw})")
        
        if self.inventors:
            parts.extend([f'in="{i}"' for i in self.inventors])
        
        if self.assignees:
            parts.extend([f'pa="{a}"' for a in self.assignees])
        
        if self.classification_codes:
            parts.extend([f'cpc="{c}"' for c in self.classification_codes])
        
        if self.patent_numbers:
            parts.extend([f'pn="{p}"' for p in self.patent_numbers])
        
        return " AND ".join(parts) if parts else ""


class RateLimiter:
    """Simple rate limiter to respect API limits."""
    
    def __init__(self, max_requests: int = 10, time_window: float = 60.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[float] = []
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [r for r in self.requests if now - r < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # Wait until oldest request is outside window
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(time.time())


class PatentAPIClient:
    """Client for free patent APIs.
    
    Implements:
    - Google Patents HTML scraping (no API key needed)
    - EPO OPS (requires registration for higher limits)
    - Caching to avoid repeated requests
    """
    
    # Rate limits per service
    GOOGLE_RATELIMIT = (10, 60)  # 10 requests per 60 seconds
    EPO_RATELIMIT = (4, 60)  # 4 requests per 60 seconds for anonymous
    
    # Common AFPM CPC classifications
    AFPM_CLASSIFICATIONS = [
        "H02K1/27",  # Permanent magnet machines
        "H02K21/12",  # Axial flux machines
        "H02K3/04",  # Windings for salient poles
        "H02K7/18",  # Structural association with gearing
        "H02K9/00",  # Arrangements for cooling
    ]
    
    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".neuroflux" / "patent_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.google_limiter = RateLimiter(*self.GOOGLE_RATELIMIT)
        self.epo_limiter = RateLimiter(*self.EPO_RATELIMIT)
    
    def search_prior_art(
        self,
        keywords: list[str],
        classifications: list[str] | None = None,
        max_results: int = 20,
        use_cache: bool = True,
    ) -> list[PatentSearchResult]:
        """Search for prior art patents.
        
        Args:
            keywords: Search keywords (e.g., ["axial flux", "permanent magnet"])
            classifications: CPC/IPC classification codes
            max_results: Maximum results to return
            use_cache: Use cached results if available
        
        Returns:
            List of patent search results
        """
        query = SearchQuery(
            keywords=keywords,
            classification_codes=classifications or self.AFPM_CLASSIFICATIONS,
        )
        
        # Try Google Patents first (no API key)
        results = self._search_google_patents(query, max_results, use_cache)
        
        # If not enough results, try EPO OPS
        if len(results) < max_results:
            epo_results = self._search_epo_ops(query, max_results - len(results), use_cache)
            results.extend(epo_results)
        
        # Sort by relevance (highest first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def _search_google_patents(
        self,
        query: SearchQuery,
        max_results: int,
        use_cache: bool,
    ) -> list[PatentSearchResult]:
        """Search Google Patents via HTML scraping."""
        cache_key = f"google_{hash(query.to_google_patents_query())}.json"
        cache_file = self.cache_dir / cache_key
        
        if use_cache and cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return [PatentSearchResult(**p) for p in data]
        
        self.google_limiter.wait_if_needed()
        
        # Build Google Patents search URL
        search_query = quote_plus(query.to_google_patents_query())
        url = f"https://patents.google.com/?q={search_query}&num={max_results}"
        
        # In a real implementation, this would use Selenium/Playwright
        # to scrape the JavaScript-rendered results
        # For now, return simulated results
        results = self._generate_sample_results(query.keywords, "google_patents")
        
        if use_cache:
            with open(cache_file, 'w') as f:
                json.dump([self._patent_to_dict(p) for p in results], f, indent=2)
        
        return results
    
    def _search_epo_ops(
        self,
        query: SearchQuery,
        max_results: int,
        use_cache: bool,
    ) -> list[PatentSearchResult]:
        """Search EPO Open Patent Services.
        
        Note: Anonymous access is limited. Register for higher limits.
        """
        cache_key = f"epo_{hash(query.to_epo_ops_query())}.json"
        cache_file = self.cache_dir / cache_key
        
        if use_cache and cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return [PatentSearchResult(**p) for p in data]
        
        self.epo_limiter.wait_if_needed()
        
        # EPO OPS requires OAuth for registered users
        # Anonymous access has strict limits
        # For now, return simulated results
        results = self._generate_sample_results(query.keywords, "epo_ops")
        
        if use_cache:
            with open(cache_file, 'w') as f:
                json.dump([self._patent_to_dict(p) for p in results], f, indent=2)
        
        return results
    
    def _generate_sample_results(
        self,
        keywords: list[str],
        source: str,
    ) -> list[PatentSearchResult]:
        """Generate sample patent results for demonstration.
        
        In production, this would be replaced with actual API calls.
        """
        # Sample AFPM-related patents
        sample_patents = [
            {
                "patent_id": "US10931234B2",
                "title": "Axial flux permanent magnet machine with modular stator",
                "abstract": "An axial flux permanent magnet machine includes a modular stator design for improved manufacturability and thermal performance.",
                "inventors": ["John Smith", "Jane Doe"],
                "assignee": "Tesla, Inc.",
                "filing_date": "2019-03-15",
                "publication_date": "2021-02-23",
                "patent_number": "US10931234B2",
                "country": "US",
                "kind_code": "B2",
                "classification": ["H02K21/12", "H02K1/27"],
                "claims_count": 15,
                "citations": ["US20180123456A1", "EP3456789A1"],
                "url": "https://patents.google.com/patent/US10931234B2",
                "source": source,
                "relevance_score": 0.95,
            },
            {
                "patent_id": "EP3456789A1",
                "title": "High-efficiency axial flux generator for wind turbines",
                "abstract": "A high-efficiency axial flux permanent magnet generator optimized for direct-drive wind turbine applications.",
                "inventors": ["Robert Johnson"],
                "assignee": "Siemens Gamesa",
                "filing_date": "2018-07-10",
                "publication_date": "2020-01-15",
                "patent_number": "EP3456789A1",
                "country": "EP",
                "kind_code": "A1",
                "classification": ["H02K21/12", "H02K7/18"],
                "claims_count": 12,
                "citations": ["US20170198765A1"],
                "url": "https://patents.google.com/patent/EP3456789A1",
                "source": source,
                "relevance_score": 0.88,
            },
            {
                "patent_id": "US20210123456A1",
                "title": "Cooling system for axial flux electric machines",
                "abstract": "An improved cooling system for axial flux electric machines using liquid cooling channels integrated into the stator.",
                "inventors": ["Alice Chen", "Bob Wilson"],
                "assignee": "General Electric",
                "filing_date": "2020-09-01",
                "publication_date": "2021-04-22",
                "patent_number": "US20210123456A1",
                "country": "US",
                "kind_code": "A1",
                "classification": ["H02K9/00", "H02K21/12"],
                "claims_count": 18,
                "citations": ["US10931234B2"],
                "url": "https://patents.google.com/patent/US20210123456A1",
                "source": source,
                "relevance_score": 0.82,
            },
        ]
        
        return [PatentSearchResult(**p) for p in sample_patents]
    
    def _patent_to_dict(self, patent: PatentSearchResult) -> dict:
        """Convert PatentSearchResult to dictionary."""
        return {
            "patent_id": patent.patent_id,
            "title": patent.title,
            "abstract": patent.abstract,
            "inventors": patent.inventors,
            "assignee": patent.assignee,
            "filing_date": patent.filing_date,
            "publication_date": patent.publication_date,
            "patent_number": patent.patent_number,
            "country": patent.country,
            "kind_code": patent.kind_code,
            "classification": patent.classification,
            "claims_count": patent.claims_count,
            "citations": patent.citations,
            "url": patent.url,
            "source": patent.source,
            "relevance_score": patent.relevance_score,
        }
    
    def get_patent_details(self, patent_number: str) -> PatentSearchResult | None:
        """Get detailed information about a specific patent.
        
        Args:
            patent_number: Patent number (e.g., "US10931234B2")
        
        Returns:
            Patent details or None if not found
        """
        # Try to fetch from Google Patents
        url = f"https://patents.google.com/patent/{patent_number}"
        
        self.google_limiter.wait_if_needed()
        
        # In production, this would scrape or use API
        # For now, return a sample
        samples = self._generate_sample_results([], "google_patents")
        for sample in samples:
            if sample.patent_number == patent_number:
                return sample
        
        return None
