#!/usr/bin/env python3
"""
Configuration for the Search Agent
"""

import os
from typing import Optional

class Config:
    """Configuration settings for the Search Agent"""
    
    # Google API settings
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    # Bing API settings
    BING_API_KEY: Optional[str] = os.getenv("BING_API_KEY")
    
    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Google Gemini API settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    
    # X.com settings (basic)
    X_USERNAME: str = os.getenv("X_USERNAME", "pyyhkija")
    X_EMAIL: str = os.getenv("X_EMAIL", "pyyhkija@gmail.com")
    
    # Twitter API v2 settings
    TWITTER_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///trends.db")
    
    # Trending settings
    TRENDING_THRESHOLD: float = float(os.getenv("TRENDING_THRESHOLD", "0.7"))
    TRENDING_WINDOW_HOURS: int = int(os.getenv("TRENDING_WINDOW_HOURS", "24"))
    
    # Social media settings
    ENABLE_SOCIAL_MEDIA: bool = os.getenv("ENABLE_SOCIAL_MEDIA", "true").lower() == "true"
    X_TRENDING_LIMIT: int = int(os.getenv("X_TRENDING_LIMIT", "20"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate that required API keys are set."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.GOOGLE_SEARCH_ENGINE_ID:
            missing.append("GOOGLE_SEARCH_ENGINE_ID")
        if not cls.BING_API_KEY:
            missing.append("BING_API_KEY")
        
        # At least one AI API key should be available
        if not cls.OPENAI_API_KEY and not cls.GEMINI_API_KEY:
            missing.append("OPENAI_API_KEY or GEMINI_API_KEY (at least one required)")
        
        
        return missing
