#!/usr/bin/env python3
"""
DuckDuckGo search engine implementation
"""

import logging
from typing import List
from .base import BaseSearchEngine
from ..models import SearchResult

logger = logging.getLogger(__name__)

class DuckDuckGoSearchEngine(BaseSearchEngine):
    """DuckDuckGo search engine implementation"""
    
    def __init__(self):
        super().__init__("duckduckgo")
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        try:
            from ddgs import DDGS
            
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        url=result.get('href', ''),
                        snippet=result.get('body', ''),
                        source=self.name,
                        rank=len(results) + 1
                    )
                    results.append(search_result)
            
            logger.info(f"DuckDuckGo found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
