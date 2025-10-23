from .base import BaseSearchEngine
from .google import GoogleSearchEngine
from .duckduckgo import DuckDuckGoSearchEngine
from .bing import BingSearchEngine

class SearchEngineManager:
    """Manager for search engines"""

    def __init__(self):
        self.engines = {
            'google': GoogleSearchEngine(),
            'bing': BingSearchEngine(),
            'duckduckgo': DuckDuckGoSearchEngine()
        }

    def get_engine(self, name: str):
        """Get a search engine by name"""
        return self.engines.get(name)

__all__ = ['BaseSearchEngine', 'GoogleSearchEngine', 'DuckDuckGoSearchEngine', 'BingSearchEngine', 'SearchEngineManager']
