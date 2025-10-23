#!/usr/bin/env python3
"""
X.com trending analyzer wrapper for scheduler integration
"""

import logging
from typing import List
from .models import TopicSearchResult
from ..social.x_analyzer import XTrendingAnalyzer as BaseXTrendingAnalyzer, XTrendingAnalysis

logger = logging.getLogger(__name__)

class XTrendingAnalyzer:
    """Wrapper for XTrendingAnalyzer with scheduler-friendly interface"""

    def __init__(self):
        self.base_analyzer = BaseXTrendingAnalyzer()

    def analyze_trending_topics(self, time_window: str = "24h") -> List[XTrendingAnalysis]:
        """Analyze trending topics over a time window"""
        try:
            logger.info(f"Analyzing trending topics for {time_window}")
            return self.base_analyzer.analyze_trending_topics(time_window)
        except Exception as e:
            logger.error(f"Error analyzing trending topics: {e}")
    def convert_to_topic_search_result(self, analysis: XTrendingAnalysis) -> TopicSearchResult:
        """Convert XTrendingAnalysis to TopicSearchResult with engagement metrics"""
        import json
        from datetime import datetime

        # Generate mock engagement data based on analysis
        # In a real implementation, this would come from actual social media API data
        likes_count = int(analysis.score * 1000)  # Mock likes based on score
        shares_count = int(analysis.score * 500)   # Mock shares
        comments_count = int(analysis.score * 200) # Mock comments

        result = TopicSearchResult(
            topic=analysis.topic,
            category=analysis.category,
            score=analysis.score,
            engagement_score=analysis.score,  # Use same score for now
            likes_count=likes_count,
            shares_count=shares_count,
            comments_count=comments_count,
            engagement_timestamp=datetime.now(),
            frequency=1,  # Default frequency
            engagement_trend=analysis.engagement_trend,
            time_analysis=json.dumps(analysis.time_analysis),
            related_topics=json.dumps(analysis.related_topics),
            search_timestamp=datetime.now()
        )

        return result