#!/usr/bin/env python3
"""
Google Custom Search API implementation
"""

import logging
import aiohttp
from typing import List
from .base import BaseSearchEngine
from ..models import SearchResult
from ..config import Config

logger = logging.getLogger(__name__)

class GoogleSearchEngine(BaseSearchEngine):
    """Google Custom Search API integration"""
    
    def __init__(self):
        super().__init__("google")
        if not Config.GOOGLE_API_KEY or not Config.GOOGLE_SEARCH_ENGINE_ID:
            raise ValueError("Google API key and search engine ID are required")
        
        self.api_key = Config.GOOGLE_API_KEY
        self.search_engine_id = Config.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': query,
                    'num': min(max_results, 10)  # Google API limit
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('items', []):
                            search_result = SearchResult(
                                title=item.get('title', ''),
                                url=item.get('link', ''),
                                snippet=item.get('snippet', ''),
                                source=self.name,
                                rank=len(results) + 1
                            )
                            results.append(search_result)
                        
                        logger.info(f"Google found {len(results)} results")
                        return results
                    else:
                        logger.error(f"Google API error: {response.status} - {await response.text()}")
                        return []
                        
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
