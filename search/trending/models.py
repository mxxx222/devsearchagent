#!/usr/bin/env python3
"""
Database models for trending topic search results
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

@dataclass
class TopicSearchResult(Base):
    """Database model for topic search results with engagement metrics"""
    __tablename__ = 'topic_search_results'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic: str = Column(String(500), nullable=False, index=True)
    category: str = Column(String(100), nullable=False, index=True)
    score: float = Column(Float, nullable=False)
    engagement_score: float = Column(Float, nullable=False)

    # Engagement metrics with timestamps
    likes_count: int = Column(Integer, default=0)
    shares_count: int = Column(Integer, default=0)
    comments_count: int = Column(Integer, default=0)
    engagement_timestamp: datetime = Column(DateTime, nullable=False, index=True)

    # Aggregated metrics for time periods
    daily_likes: int = Column(Integer, default=0)
    daily_shares: int = Column(Integer, default=0)
    daily_comments: int = Column(Integer, default=0)
    monthly_likes: int = Column(Integer, default=0)
    monthly_shares: int = Column(Integer, default=0)
    monthly_comments: int = Column(Integer, default=0)
    yearly_likes: int = Column(Integer, default=0)
    yearly_shares: int = Column(Integer, default=0)
    yearly_comments: int = Column(Integer, default=0)

    frequency: int = Column(Integer, default=0)
    engagement_trend: str = Column(String(50), default='stable')
    time_analysis: str = Column(Text, nullable=True)  # JSON string
    related_topics: str = Column(Text, nullable=True)  # JSON string
    source: str = Column(String(100), default='x.com')
    search_timestamp: datetime = Column(DateTime, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    def __init__(self, topic: str, category: str, score: float, engagement_score: float,
                 frequency: int = 0, engagement_trend: str = 'stable',
                 time_analysis: Optional[str] = None, related_topics: Optional[str] = None,
                 source: str = 'x.com', search_timestamp: Optional[datetime] = None):
        self.topic = topic
        self.category = category
        self.score = score
        self.engagement_score = engagement_score
        self.frequency = frequency
        self.engagement_trend = engagement_trend
        self.time_analysis = time_analysis
        self.related_topics = related_topics
        self.source = source
        self.search_timestamp = search_timestamp or datetime.utcnow()

@dataclass
class SearchJob(Base):
    """Database model for tracking search jobs"""
    __tablename__ = 'search_jobs'
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    job_id: str = Column(String(100), nullable=False, unique=True)
    job_type: str = Column(String(50), nullable=False)  # 'topic_search', 'analysis', etc.
    status: str = Column(String(50), nullable=False, default='pending')  # 'pending', 'running', 'completed', 'failed'
    started_at: datetime = Column(DateTime, nullable=True)
    completed_at: datetime = Column(DateTime, nullable=True)
    error_message: str = Column(Text, nullable=True)
    retry_count: int = Column(Integer, default=0)
    max_retries: int = Column(Integer, default=3)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@dataclass
class EngagementMetrics(Base):
    """Detailed engagement metrics for time-series analysis"""
    __tablename__ = 'engagement_metrics'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic_id: int = Column(Integer, ForeignKey('topic_search_results.id'), nullable=False)
    metric_type: str = Column(String(50), nullable=False)  # 'likes', 'shares', 'comments'
    count: int = Column(Integer, default=0)
    timestamp: datetime = Column(DateTime, nullable=False, index=True)
    period: str = Column(String(20), nullable=False)  # 'hourly', 'daily', 'monthly', 'yearly'
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_topic_metric_timestamp', 'topic_id', 'metric_type', 'timestamp'),
        Index('idx_period_timestamp', 'period', 'timestamp'),
    )


@dataclass
class EngagementSummary(Base):
    """Pre-computed summaries for fast dashboard queries"""
    __tablename__ = 'engagement_summaries'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic: str = Column(String(500), nullable=False, index=True)
    category: str = Column(String(100), nullable=False, index=True)
    period: str = Column(String(20), nullable=False)  # 'daily', 'monthly', 'yearly'
    period_start: datetime = Column(DateTime, nullable=False, index=True)
    period_end: datetime = Column(DateTime, nullable=False)

    total_likes: int = Column(Integer, default=0)
    total_shares: int = Column(Integer, default=0)
    total_comments: int = Column(Integer, default=0)
    avg_engagement_score: float = Column(Float, default=0.0)
    peak_engagement_time: datetime = Column(DateTime, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_topic_period', 'topic', 'period'),
        Index('idx_category_period', 'category', 'period'),
        Index('idx_period_range', 'period', 'period_start', 'period_end'),
    )

    def __init__(self, job_id: str, job_type: str, status: str = 'pending',
                 max_retries: int = 3):
        self.job_id = job_id
        self.job_type = job_type
        self.status = status
        self.max_retries = max_retries

@dataclass
class AISuggestion(Base):
    """Database model for AI-generated topic suggestions"""
    __tablename__ = 'ai_suggestions'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic: str = Column(String(500), nullable=False, index=True)
    category: str = Column(String(100), nullable=False, index=True)
    confidence_score: float = Column(Float, nullable=False)  # 0.0 to 1.0
    ranking_score: float = Column(Float, nullable=False)  # Combined score for ranking
    source: str = Column(String(100), nullable=False)  # 'openai', 'gemini'
    reasoning: str = Column(Text, nullable=True)  # AI's reasoning for the suggestion
    trend_data: str = Column(Text, nullable=True)  # JSON string with trend analysis data
    related_topics: str = Column(Text, nullable=True)  # JSON string with related topics
    batch_id: str = Column(String(100), nullable=False, index=True)  # Links to suggestion batch
    is_active: bool = Column(Boolean, default=True)  # Whether suggestion is still relevant
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    expires_at: datetime = Column(DateTime, nullable=True)  # When suggestion expires

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_topic_confidence', 'topic', 'confidence_score'),
        Index('idx_category_ranking', 'category', 'ranking_score'),
        Index('idx_batch_active', 'batch_id', 'is_active'),
        Index('idx_source_created', 'source', 'created_at'),
    )

    def __init__(self, topic: str, category: str, confidence_score: float,
                 ranking_score: float, source: str, batch_id: str,
                 reasoning: Optional[str] = None, trend_data: Optional[str] = None,
                 related_topics: Optional[str] = None, expires_at: Optional[datetime] = None):
        self.topic = topic
        self.category = category
        self.confidence_score = confidence_score
        self.ranking_score = ranking_score
        self.source = source
        self.batch_id = batch_id
        self.reasoning = reasoning
        self.trend_data = trend_data
        self.related_topics = related_topics
        self.expires_at = expires_at

@dataclass
class AISuggestionBatch(Base):
    """Database model for tracking AI suggestion generation batches"""
    __tablename__ = 'ai_suggestion_batches'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    batch_id: str = Column(String(100), nullable=False, unique=True, index=True)
    status: str = Column(String(50), nullable=False, default='pending')  # 'pending', 'running', 'completed', 'failed'
    sources_used: str = Column(Text, nullable=True)  # JSON string of sources queried
    total_suggestions: int = Column(Integer, default=0)
    openai_suggestions: int = Column(Integer, default=0)
    gemini_suggestions: int = Column(Integer, default=0)
    error_message: str = Column(Text, nullable=True)
    started_at: datetime = Column(DateTime, nullable=True)
    completed_at: datetime = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    def __init__(self, batch_id: str, status: str = 'pending',
                 sources_used: Optional[str] = None):
        self.batch_id = batch_id
        self.status = status
        self.sources_used = sources_used