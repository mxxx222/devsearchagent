from .x_trending import XTrendingDetector
from .x_analyzer import XTrendingAnalyzer
from .twitter_api_v2 import TwitterAPIv2

class XAnalyzer:
    """X.com analyzer wrapper with Twitter API v2 integration"""

    def __init__(self):
        self.analyzer = XTrendingAnalyzer()
        self.twitter_api = TwitterAPIv2()

    async def get_trending_topics(self, limit: int = 20):
        """Get trending topics using both web scraping and API"""
        try:
            # Try Twitter API v2 first
            api_trends = self.twitter_api.analyze_trending_topics()
            if api_trends:
                return api_trends[:limit]
            
            # Fallback to web scraping
            return self.analyzer.analyze_trending_topics()[:limit]
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

    def search_tweets(self, query: str, max_results: int = 10):
        """Search tweets using Twitter API v2"""
        return self.twitter_api.search_recent_tweets(query, max_results)

    def get_trending_topics_api(self, woeid: int = 1, limit: int = 20):
        """Get trending topics using Twitter API"""
        return self.twitter_api.get_trending_topics(woeid, limit)

__all__ = ['XTrendingDetector', 'XTrendingAnalyzer', 'XAnalyzer', 'TwitterAPIv2']
