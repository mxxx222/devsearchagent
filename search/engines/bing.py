#!/usr/bin/env python3
"""
Bing Search API implementation
"""

import logging
import aiohttp
from typing import List
from .base import BaseSearchEngine
from ..models import SearchResult
from ..config import Config

logger = logging.getLogger(__name__)

class BingSearchEngine(BaseSearchEngine):
    """Bing Search API integration"""
    
    def __init__(self):
        super().__init__("bing")
        if not Config.BING_API_KEY:
            raise ValueError("Bing API key is required")
        
        self.api_key = Config.BING_API_KEY
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Bing Search API"""
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            params = {
                'q': query,
                'count': min(max_results, 50)  # Bing API limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('webPages', {}).get('value', []):
                            search_result = SearchResult(
                                title=item.get('name', ''),
                                url=item.get('url', ''),
                                snippet=item.get('snippet', ''),
                                source=self.name,
                                rank=len(results) + 1
                            )
                            results.append(search_result)
                        
                        logger.info(f"Bing found {len(results)} results")
                        return results
                    else:
                        logger.error(f"Bing API error: {response.status} - {await response.text()}")
                        return []
                        
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
