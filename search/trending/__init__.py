#!/usr/bin/env python3
"""
Trending topic search and scheduling module
"""

from .scheduler import TopicSearchScheduler
from .detector import XTrendingDetector, TrendDetector
from .analyzer import XTrendingAnalyzer
from .storage import TrendingStorage
from .models import TopicSearchResult, SearchJob

# Import AISuggestionScheduler from ai module (where it's actually defined)
try:
    from ..ai import AISuggestionScheduler
except ImportError:
    AISuggestionScheduler = None

__all__ = [
    'TopicSearchScheduler',
    'AISuggestionScheduler',
    'XTrendingDetector',
    'XTrendingAnalyzer',
    'TrendingStorage',
    'TrendDetector',
    'TopicSearchResult',
    'SearchJob'
]