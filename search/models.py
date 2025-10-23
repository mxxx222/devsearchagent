#!/usr/bin/env python3
"""
Data models for the Search Agent
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class SearchResult:
    """Search result data"""
    title: str
    url: str
    snippet: str
    source: str
    rank: int

@dataclass
class AggregatedResults:
    """Aggregated search results"""
    query: str
    results: List[SearchResult]
    total_results: int
    timestamp: datetime

@dataclass
class AIRecommendation:
    """AI-powered recommendation"""
    tool: str
    description: str
    category: str
    confidence: float
    reasoning: str

@dataclass
class TrendData:
    """Trend data for analysis"""
    keyword: str
    frequency: int
    google_trends_score: Optional[float] = None
    timestamp: datetime = None
    category: str = "general"

@dataclass
class TrendingTopic:
    """Trending topic data"""
    topic: str
    score: float
    keywords: List[str]
    category: str
    detected_at: datetime
    is_new: bool = False
