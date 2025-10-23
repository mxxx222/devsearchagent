#!/usr/bin/env python3
"""
X.com trending detector wrapper for scheduler integration
"""

import logging
from typing import List
from .models import TopicSearchResult
from ..social.x_trending import XTrendingDetector as BaseXTrendingDetector, XTrendingData

logger = logging.getLogger(__name__)

class TrendDetector:
    """Main trend detector class for compatibility"""
    
    def __init__(self, storage=None):
        self.storage = storage
        self.base_detector = BaseXTrendingDetector()
    
    def get_trending_topics(self, limit: int = 10) -> List[dict]:
        """Get trending topics"""
        try:
            data = self.base_detector.get_trending_data()
            return [
                {
                    "topic": item.topic,
                    "score": item.score,
                    "category": item.category,
                    "timestamp": item.timestamp
                }
                for item in data[:limit]
            ]
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

class XTrendingDetector:
    """Wrapper for XTrendingDetector with scheduler-friendly interface"""

    def __init__(self):
        self.base_detector = BaseXTrendingDetector()

    def get_trending_data(self) -> List[XTrendingData]:
        """Get trending data from X.com"""
        try:
            logger.info("Fetching trending data from X.com")
            return self.base_detector.get_trending_data()
        except Exception as e:
            logger.error(f"Error fetching trending data: {e}")
            return []