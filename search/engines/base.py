#!/usr/bin/env python3
"""
Base search engine class
"""

from abc import ABC, abstractmethod
from typing import List
from ..models import SearchResult

class BaseSearchEngine(ABC):
    """Base class for search engines"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search for results"""
        pass
