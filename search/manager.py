#!/usr/bin/env python3
"""
Enhanced Search Manager with X.com social media integration (web scraping only)
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from .engines.base import BaseSearchEngine
from .engines.google import GoogleSearchEngine
from .engines.duckduckgo import DuckDuckGoSearchEngine
from .engines.bing import BingSearchEngine
from .models import SearchResult, AggregatedResults, AIRecommendation
from .config import Config
from .social.x_trending import XTrendingDetector
from .social.x_analyzer import XTrendingAnalyzer

logger = logging.getLogger(__name__)

class SimpleAIRecommender:
    """Simple AI recommender for basic functionality"""
    
    def get_recommendations(self, query: str, max_results: int = 5) -> List[AIRecommendation]:
        """Get basic AI recommendations"""
        # Simple keyword-based recommendations
        recommendations = []
        if "ai" in query.lower() or "artificial intelligence" in query.lower():
            recommendations.append(AIRecommendation(
                query="AI coding tools",
                confidence=0.8,
                reasoning="AI-related query detected"
            ))
        if "coding" in query.lower() or "programming" in query.lower():
            recommendations.append(AIRecommendation(
                query="Programming tutorials",
                confidence=0.7,
                reasoning="Programming-related query detected"
            ))
        return recommendations[:max_results]

class SearchManager:
    """Enhanced Search Manager with X.com social media integration"""
    
    def __init__(self, enable_trending: bool = True, enable_ai: bool = True, 
                 enable_social: bool = True, db_path: str = "trends.db"):
        self.enable_trending = enable_trending
        self.enable_ai = enable_ai
        self.enable_social = enable_social
        
        # Initialize search engines
        self.search_engines = self._initialize_search_engines()
        
        # Initialize AI recommender
        self.ai_recommender = None
        if enable_ai:
            self.ai_recommender = self._initialize_ai_recommender()
        
        # Initialize trending components
        self.trend_detector = None
        self.trend_storage = None
        if enable_trending:
            self._initialize_trending()
        
        # Initialize X.com social media components
        self.x_trending_detector = None
        self.x_trending_analyzer = None
        if enable_social:
            self._initialize_social_media()
    
    def _initialize_search_engines(self) -> List[BaseSearchEngine]:
        """Initialize available search engines"""
        engines = []
        
        # Try to initialize each search engine
        try:
            engines.append(GoogleSearchEngine())
            logger.info("Google search engine initialized")
        except ValueError as e:
            logger.warning(f"Google search engine not available: {e}")
        
        try:
            engines.append(DuckDuckGoSearchEngine())
            logger.info("DuckDuckGo search engine initialized")
        except ValueError as e:
            logger.warning(f"DuckDuckGo search engine not available: {e}")
        
        try:
            engines.append(BingSearchEngine())
            logger.info("Bing search engine initialized")
        except ValueError as e:
            logger.warning(f"Bing search engine not available: {e}")
        
        if not engines:
            logger.error("No search engines available!")
            raise RuntimeError("No search engines available")
        
        return engines
    
    def _initialize_ai_recommender(self):
        """Initialize AI recommender"""
        try:
            return SimpleAIRecommender()
        except Exception as e:
            logger.warning(f"AI recommender not available: {e}")
            return None
    
    def _initialize_trending(self):
        """Initialize trending components"""
        try:
            from .trending import TrendDetector, TrendingStorage
            self.trend_storage = TrendingStorage(database_url="sqlite:///trends.db")
            self.trend_detector = TrendDetector(self.trend_storage)
            logger.info("Trending components initialized")
        except Exception as e:
            logger.warning(f"Trending components not available: {e}")
            self.enable_trending = False
    
    def _initialize_social_media(self):
        """Initialize X.com social media components"""
        try:
            self.x_trending_detector = XTrendingDetector()
            self.x_trending_analyzer = XTrendingAnalyzer()
            logger.info("X.com social media components initialized")
        except Exception as e:
            logger.warning(f"X.com social media components not available: {e}")
            self.enable_social = False
    
    async def search(self, query: str, max_results: int = 10) -> AggregatedResults:
        """Perform search across all available engines"""
        logger.info(f"Searching for: {query}")
        
        all_results = []
        
        # Search with each engine
        for engine in self.search_engines:
            try:
                results = await engine.search(query, max_results)
                all_results.extend(results)
                logger.info(f"Found {len(results)} results from {engine.name}")
            except Exception as e:
                logger.error(f"Error searching with {engine.name}: {e}")
        
        # Remove duplicates and sort by relevance
        unique_results = self._remove_duplicates(all_results)
        sorted_results = self._sort_by_relevance(unique_results, query)
        
        # Create aggregated results
        aggregated_results = AggregatedResults(
            query=query,
            results=sorted_results[:max_results],
            total_results=len(sorted_results),
            timestamp=datetime.now()
        )
        
        return aggregated_results
    
    async def search_with_social_trends(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform search with X.com social media trends integration"""
        logger.info(f"Searching with social trends for: {query}")
        
        # Perform regular search
        search_results = await self.search(query, max_results)
        
        # Get X.com trending data
        social_trends = {}
        if self.enable_social and self.x_trending_detector:
            try:
                social_trends = await self._get_social_trends(query)
            except Exception as e:
                logger.error(f"Error getting social trends: {e}")
        
        # Get AI recommendations
        ai_recommendations = []
        if self.ai_recommender:
            try:
                ai_recommendations = await self.ai_recommender.generate_recommendations(search_results)
            except Exception as e:
                logger.error(f"Error generating AI recommendations: {e}")
        
        # Get trending analysis
        trending_analysis = {}
        if self.enable_trending and self.trend_detector:
            try:
                trending_analysis = await self._get_trending_analysis(search_results)
            except Exception as e:
                logger.error(f"Error getting trending analysis: {e}")
        
        return {
            "search_results": search_results,
            "social_trends": social_trends,
            "ai_recommendations": ai_recommendations,
            "trending_analysis": trending_analysis
        }
    
    async def get_ai_coding_trends(self) -> Dict[str, Any]:
        """Get comprehensive AI coding trends from X.com"""
        logger.info("Getting AI coding trends from X.com")
        
        if not self.enable_social or not self.x_trending_analyzer:
            return {"error": "X.com social media integration not available"}
        
        try:
            # Get comprehensive analysis
            analysis = self.x_trending_analyzer.get_comprehensive_analysis()
            
            # Get specific AI coding trends
            ai_coding_trends = self.x_trending_analyzer.analyze_ai_coding_trends()
            
            # Get free AI bot trends
            free_ai_trends = self.x_trending_analyzer.analyze_free_ai_bots_trends()
            
            return {
                "ai_coding_trends": ai_coding_trends,
                "free_ai_bots": free_ai_trends,
                "comprehensive_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI coding trends: {e}")
            return {"error": str(e)}
    
    async def get_software_development_trends(self) -> Dict[str, Any]:
        """Get software development trends from X.com"""
        logger.info("Getting software development trends from X.com")
        
        if not self.enable_social or not self.x_trending_analyzer:
            return {"error": "X.com social media integration not available"}
        
        try:
            # Get software development trends
            dev_trends = self.x_trending_analyzer.analyze_software_development_trends()
            
            # Get new language trends
            language_trends = self.x_trending_analyzer.analyze_new_language_trends()
            
            # Get top engagement trends
            engagement_trends = self.x_trending_analyzer.get_trending_by_engagement(15)
            
            return {
                "software_development_trends": dev_trends,
                "new_language_trends": language_trends,
                "top_engagement_trends": engagement_trends,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting software development trends: {e}")
            return {"error": str(e)}
    
    async def _get_social_trends(self, query: str) -> Dict[str, Any]:
        """Get social media trends related to query"""
        try:
            # Get trending topics
            trending_topics = self.x_trending_detector.get_trending_topics()
            
            # Search for coding trends
            coding_trends = self.x_trending_detector.search_coding_trends(query)
            
            # Get user timeline trends
            user_trends = self.x_trending_detector.get_user_timeline_trends()
            
            return {
                "trending_topics": trending_topics,
                "coding_trends": coding_trends,
                "user_timeline_trends": user_trends
            }
        except Exception as e:
            logger.error(f"Error getting social trends: {e}")
            return {}
    
    async def _get_trending_analysis(self, search_results: AggregatedResults) -> Dict[str, Any]:
        """Get trending analysis for search results"""
        try:
            if not self.trend_detector:
                return {}
            
            # Analyze search results for trends
            trend_data = self.trend_detector.analyze_search_results(search_results)
            
            # Detect trending topics
            trending_topics = self.trend_detector.detect_trending_topics(trend_data)
            
            return {
                "trend_data": trend_data,
                "trending_topics": trending_topics
            }
        except Exception as e:
            logger.error(f"Error getting trending analysis: {e}")
            return {}
    
    def _remove_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate search results"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def _sort_by_relevance(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Sort results by relevance to query"""
        query_words = set(query.lower().split())
        
        def relevance_score(result: SearchResult) -> float:
            title_words = set(result.title.lower().split())
            snippet_words = set(result.snippet.lower().split())
            
            # Calculate relevance score
            title_matches = len(query_words.intersection(title_words))
            snippet_matches = len(query_words.intersection(snippet_words))
            
            return title_matches * 2 + snippet_matches
        
        return sorted(results, key=relevance_score, reverse=True)
    
    async def get_comprehensive_trends_report(self) -> Dict[str, Any]:
        """Get comprehensive trends report including X.com social media"""
        logger.info("Generating comprehensive trends report")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "search_engines": [engine.name for engine in self.search_engines],
            "features": {
                "trending": self.enable_trending,
                "ai_recommendations": self.ai_recommender is not None,
                "social_media": self.enable_social
            }
        }
        
        # Get X.com trends
        if self.enable_social:
            try:
                ai_trends = await self.get_ai_coding_trends()
                dev_trends = await self.get_software_development_trends()
                report["x_com_trends"] = {
                    "ai_coding": ai_trends,
                    "software_development": dev_trends
                }
            except Exception as e:
                logger.error(f"Error getting X.com trends: {e}")
                report["x_com_trends"] = {"error": str(e)}
        
        return report
