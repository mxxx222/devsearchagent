#!/usr/bin/env python3
"""
X.com trending topics analyzer for coding and software development
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter
from dataclasses import dataclass
from .x_trending import XTrendingDetector, XTrendingData, XTrendingTopic

logger = logging.getLogger(__name__)

@dataclass
class XTrendingAnalysis:
    """X.com trending analysis results"""
    topic: str
    score: float
    category: str
    engagement_trend: str  # "rising", "stable", "falling"
    time_analysis: Dict[str, Any]
    related_topics: List[str]
    timestamp: datetime

class XTrendingAnalyzer:
    """X.com trending topics analyzer"""
    
    def __init__(self):
        self.detector = XTrendingDetector()
        self.historical_data = []  # Store historical trending data
        
    def analyze_trending_topics(self, time_window: str = "24h") -> List[XTrendingAnalysis]:
        """Analyze trending topics over a time window"""
        logger.info(f"Analyzing X.com trending topics for {time_window}")
        
        # Get current trending data
        current_data = self.detector.get_trending_data()
        
        # Store historical data
        self.historical_data.extend(current_data)
        
        # Keep only recent data (last 7 days)
        cutoff = datetime.now() - timedelta(days=7)
        self.historical_data = [
            data for data in self.historical_data 
            if data.timestamp >= cutoff
        ]
        
        # Analyze trends
        analyses = []
        topic_groups = self._group_topics_by_name(current_data)
        
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses[:20]  # Top 20 trending topics
    
    def analyze_ai_coding_trends(self) -> List[XTrendingAnalysis]:
        """Specifically analyze AI coding trends"""
        logger.info("Analyzing AI coding trends on X.com")
        
        # Get trending data
        trending_data = self.detector.get_trending_data()
        
        # Filter for AI coding topics
        ai_coding_data = [
            data for data in trending_data 
            if data.category == "ai_coding"
        ]
        
        # Group by topic
        topic_groups = self._group_topics_by_name(ai_coding_data)
        
        analyses = []
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses
    
    def analyze_software_development_trends(self) -> List[XTrendingAnalysis]:
        """Analyze software development trends"""
        logger.info("Analyzing software development trends on X.com")
        
        # Get trending data
        trending_data = self.detector.get_trending_data()
        
        # Filter for software development topics
        dev_topics = [
            'programming_languages', 'frameworks', 'devops', 'tools'
        ]
        
        dev_data = [
            data for data in trending_data 
            if data.category in dev_topics
        ]
        
        # Group by topic
        topic_groups = self._group_topics_by_name(dev_data)
        
        analyses = []
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses
    
    def analyze_new_language_trends(self) -> List[XTrendingAnalysis]:
        """Analyze trends for new programming languages"""
        logger.info("Analyzing new programming language trends on X.com")
        
        # Get trending data
        trending_data = self.detector.get_trending_data()
        
        # Filter for programming language topics
        lang_data = [
            data for data in trending_data 
            if data.category == "programming_languages"
        ]
        
        # Group by topic
        topic_groups = self._group_topics_by_name(lang_data)
        
        analyses = []
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses
    
    def analyze_free_ai_bots_trends(self) -> List[XTrendingAnalysis]:
        """Analyze trends for free AI coding bots"""
        logger.info("Analyzing free AI coding bot trends on X.com")
        
        # Get trending data
        trending_data = self.detector.get_trending_data()
        
        # Filter for free AI coding topics
        free_ai_data = [
            data for data in trending_data 
            if data.category == "ai_coding" and 
            any(free_term in data.topic.lower() for free_term in ['free', 'open source', 'gratis'])
        ]
        
        # Group by topic
        topic_groups = self._group_topics_by_name(free_ai_data)
        
        analyses = []
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses
    
    def get_trending_by_engagement(self, limit: int = 10) -> List[XTrendingAnalysis]:
        """Get trending topics sorted by engagement score"""
        logger.info(f"Getting top {limit} trending topics by engagement")
        
        # Get trending data
        trending_data = self.detector.get_trending_data()
        
        # Group by topic
        topic_groups = self._group_topics_by_name(trending_data)
        
        analyses = []
        for topic_name, topic_data_list in topic_groups.items():
            if len(topic_data_list) > 0:
                analysis = self._analyze_topic(topic_name, topic_data_list)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by engagement score
        analyses.sort(key=lambda x: x.score, reverse=True)
        
        return analyses[:limit]
    
    def _group_topics_by_name(self, trending_data: List[XTrendingData]) -> Dict[str, List[XTrendingData]]:
        """Group trending data by topic name"""
        groups = {}
        for data in trending_data:
            if data.topic not in groups:
                groups[data.topic] = []
            groups[data.topic].append(data)
        return groups
    
    def _analyze_topic(self, topic_name: str, topic_data_list: List[XTrendingData]) -> Optional[XTrendingAnalysis]:
        """Analyze a specific topic"""
        if not topic_data_list:
            return None
        
        # Calculate overall score
        total_frequency = sum(data.frequency for data in topic_data_list)
        avg_engagement = sum(data.engagement_score for data in topic_data_list) / len(topic_data_list)
        
        # Calculate trend direction
        engagement_trend = self._calculate_engagement_trend(topic_data_list)
        
        # Get category
        category = topic_data_list[0].category if topic_data_list else "general"
        
        # Calculate time analysis
        time_analysis = self._analyze_time_patterns(topic_data_list)
        
        # Find related topics
        related_topics = self._find_related_topics(topic_name, topic_data_list)
        
        # Calculate final score
        score = self._calculate_final_score(total_frequency, avg_engagement, engagement_trend)
        
        return XTrendingAnalysis(
            topic=topic_name,
            score=score,
            category=category,
            engagement_trend=engagement_trend,
            time_analysis=time_analysis,
            related_topics=related_topics,
            timestamp=datetime.now()
        )
    
    def _calculate_engagement_trend(self, topic_data_list: List[XTrendingData]) -> str:
        """Calculate engagement trend direction"""
        if len(topic_data_list) < 2:
            return "stable"
        
        # Sort by timestamp
        sorted_data = sorted(topic_data_list, key=lambda x: x.timestamp)
        
        # Calculate trend
        recent_engagement = sum(data.engagement_score for data in sorted_data[-3:]) / min(3, len(sorted_data))
        older_engagement = sum(data.engagement_score for data in sorted_data[:-3]) / max(1, len(sorted_data) - 3)
        
        if recent_engagement > older_engagement * 1.2:
            return "rising"
        elif recent_engagement < older_engagement * 0.8:
            return "falling"
        else:
            return "stable"
    
    def _analyze_time_patterns(self, topic_data_list: List[XTrendingData]) -> Dict[str, Any]:
        """Analyze time patterns for a topic"""
        if not topic_data_list:
            return {}
        
        # Group by hour of day
        hourly_data = {}
        for data in topic_data_list:
            hour = data.timestamp.hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(data)
        
        # Find peak hours
        peak_hours = sorted(hourly_data.keys(), key=lambda h: len(hourly_data[h]), reverse=True)[:3]
        
        return {
            "peak_hours": peak_hours,
            "total_data_points": len(topic_data_list),
            "time_span_hours": (max(data.timestamp for data in topic_data_list) - 
                               min(data.timestamp for data in topic_data_list)).total_seconds() / 3600
        }
    
    def _find_related_topics(self, topic_name: str, topic_data_list: List[XTrendingData]) -> List[str]:
        """Find related topics"""
        # Simple implementation - in a real system, you'd use more sophisticated methods
        related = []
        
        # Get all topics from historical data
        all_topics = set()
        for data in self.historical_data:
            if data.topic != topic_name:
                all_topics.add(data.topic)
        
        # Find topics that appear together
        topic_words = set(topic_name.lower().split())
        for other_topic in all_topics:
            other_words = set(other_topic.lower().split())
            if topic_words.intersection(other_words):
                related.append(other_topic)
        
        return related[:5]  # Top 5 related topics
    
    def _calculate_final_score(self, frequency: int, engagement: float, trend: str) -> float:
        """Calculate final trending score"""
        base_score = min(frequency / 1000.0, 1.0) * 0.4 + engagement * 0.6
        
        # Apply trend multiplier
        if trend == "rising":
            base_score *= 1.3
        elif trend == "falling":
            base_score *= 0.7
        
        return min(base_score, 1.0)
    
    def get_comprehensive_analysis(self) -> Dict[str, List[XTrendingAnalysis]]:
        """Get comprehensive analysis of all trending categories"""
        logger.info("Getting comprehensive X.com trending analysis")
        
        return {
            "ai_coding": self.analyze_ai_coding_trends(),
            "software_development": self.analyze_software_development_trends(),
            "new_languages": self.analyze_new_language_trends(),
            "free_ai_bots": self.analyze_free_ai_bots_trends(),
            "top_engagement": self.get_trending_by_engagement(10)
        }
