#!/usr/bin/env python3
"""
Engagement aggregation service for time-series analysis
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
try:
    from .models import EngagementMetrics, EngagementSummary, TopicSearchResult
    from .storage import TrendingStorage
except ImportError:
    # For direct testing
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models import EngagementMetrics, EngagementSummary, TopicSearchResult
    from storage import TrendingStorage

logger = logging.getLogger(__name__)


class EngagementAggregationService:
    """Service for aggregating engagement metrics across time periods"""

    def __init__(self, storage: TrendingStorage):
        self.storage = storage

    def aggregate_daily_metrics(self, date: datetime) -> int:
        """Aggregate engagement metrics for a specific day"""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)

            with self.storage.SessionLocal() as session:
                # Get all engagement metrics for the day
                metrics = session.query(EngagementMetrics)\
                    .filter(EngagementMetrics.timestamp >= start_date)\
                    .filter(EngagementMetrics.timestamp < end_date)\
                    .all()

                # Group by topic and metric type
                topic_metrics = {}
                for metric in metrics:
                    key = (metric.topic_id, metric.metric_type)
                    if key not in topic_metrics:
                        topic_metrics[key] = 0
                    topic_metrics[key] += metric.count

                # Update topic search results with daily aggregates
                updated_count = 0
                for (topic_id, metric_type), count in topic_metrics.items():
                    topic = session.query(TopicSearchResult)\
                        .filter(TopicSearchResult.id == topic_id)\
                        .first()

                    if topic:
                        if metric_type == 'likes':
                            topic.daily_likes = count
                        elif metric_type == 'shares':
                            topic.daily_shares = count
                        elif metric_type == 'comments':
                            topic.daily_comments = count
                        updated_count += 1

                session.commit()
                logger.info(f"Updated daily metrics for {updated_count} topics on {date.date()}")
                return updated_count

        except Exception as e:
            logger.error(f"Error aggregating daily metrics: {e}")
            return 0

    def aggregate_monthly_metrics(self, year: int, month: int) -> int:
        """Aggregate engagement metrics for a specific month"""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            with self.storage.SessionLocal() as session:
                # Get all engagement metrics for the month
                metrics = session.query(EngagementMetrics)\
                    .filter(EngagementMetrics.timestamp >= start_date)\
                    .filter(EngagementMetrics.timestamp < end_date)\
                    .all()

                # Group by topic and metric type
                topic_metrics = {}
                for metric in metrics:
                    key = (metric.topic_id, metric.metric_type)
                    if key not in topic_metrics:
                        topic_metrics[key] = 0
                    topic_metrics[key] += metric.count

                # Update topic search results with monthly aggregates
                updated_count = 0
                for (topic_id, metric_type), count in topic_metrics.items():
                    topic = session.query(TopicSearchResult)\
                        .filter(TopicSearchResult.id == topic_id)\
                        .first()

                    if topic:
                        if metric_type == 'likes':
                            topic.monthly_likes = count
                        elif metric_type == 'shares':
                            topic.monthly_shares = count
                        elif metric_type == 'comments':
                            topic.monthly_comments = count
                        updated_count += 1

                session.commit()
                logger.info(f"Updated monthly metrics for {updated_count} topics in {year}-{month}")
                return updated_count

        except Exception as e:
            logger.error(f"Error aggregating monthly metrics: {e}")
            return 0

    def aggregate_yearly_metrics(self, year: int) -> int:
        """Aggregate engagement metrics for a specific year"""
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)

            with self.storage.SessionLocal() as session:
                # Get all engagement metrics for the year
                metrics = session.query(EngagementMetrics)\
                    .filter(EngagementMetrics.timestamp >= start_date)\
                    .filter(EngagementMetrics.timestamp < end_date)\
                    .all()

                # Group by topic and metric type
                topic_metrics = {}
                for metric in metrics:
                    key = (metric.topic_id, metric.metric_type)
                    if key not in topic_metrics:
                        topic_metrics[key] = 0
                    topic_metrics[key] += metric.count

                # Update topic search results with yearly aggregates
                updated_count = 0
                for (topic_id, metric_type), count in topic_metrics.items():
                    topic = session.query(TopicSearchResult)\
                        .filter(TopicSearchResult.id == topic_id)\
                        .first()

                    if topic:
                        if metric_type == 'likes':
                            topic.yearly_likes = count
                        elif metric_type == 'shares':
                            topic.yearly_shares = count
                        elif metric_type == 'comments':
                            topic.yearly_comments = count
                        updated_count += 1

                session.commit()
                logger.info(f"Updated yearly metrics for {updated_count} topics in {year}")
                return updated_count

        except Exception as e:
            logger.error(f"Error aggregating yearly metrics: {e}")
            return 0

    def update_topic_engagement_summary(self, topic_id: int) -> bool:
        """Update pre-computed engagement summary for a topic"""
        try:
            with self.storage.SessionLocal() as session:
                topic = session.query(TopicSearchResult)\
                    .filter(TopicSearchResult.id == topic_id)\
                    .first()

                if not topic:
                    return False

                # Calculate daily summary
                daily_summary = EngagementSummary(
                    topic=topic.topic,
                    category=topic.category,
                    period='daily',
                    period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                    period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999),
                    total_likes=topic.daily_likes,
                    total_shares=topic.daily_shares,
                    total_comments=topic.daily_comments,
                    avg_engagement_score=topic.engagement_score,
                    peak_engagement_time=topic.engagement_timestamp
                )

                # Calculate monthly summary
                monthly_summary = EngagementSummary(
                    topic=topic.topic,
                    category=topic.category,
                    period='monthly',
                    period_start=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                    period_end=(datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                    total_likes=topic.monthly_likes,
                    total_shares=topic.monthly_shares,
                    total_comments=topic.monthly_comments,
                    avg_engagement_score=topic.engagement_score,
                    peak_engagement_time=topic.engagement_timestamp
                )

                # Calculate yearly summary
                yearly_summary = EngagementSummary(
                    topic=topic.topic,
                    category=topic.category,
                    period='yearly',
                    period_start=datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
                    period_end=datetime.utcnow().replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999),
                    total_likes=topic.yearly_likes,
                    total_shares=topic.yearly_shares,
                    total_comments=topic.yearly_comments,
                    avg_engagement_score=topic.engagement_score,
                    peak_engagement_time=topic.engagement_timestamp
                )

                # Upsert summaries
                session.merge(daily_summary)
                session.merge(monthly_summary)
                session.merge(yearly_summary)
                session.commit()

                logger.info(f"Updated engagement summaries for topic: {topic.topic}")
                return True

        except Exception as e:
            logger.error(f"Error updating topic engagement summary: {e}")
            return False

    def batch_update_summaries(self, period: str, start_date: datetime, end_date: datetime) -> int:
        """Batch update engagement summaries for a date range"""
        try:
            with self.storage.SessionLocal() as session:
                # Get all topics that have engagement data in the period
                topics = session.query(TopicSearchResult)\
                    .filter(TopicSearchResult.engagement_timestamp >= start_date)\
                    .filter(TopicSearchResult.engagement_timestamp <= end_date)\
                    .all()

                updated_count = 0
                for topic in topics:
                    if self.update_topic_engagement_summary(topic.id):
                        updated_count += 1

                logger.info(f"Batch updated {updated_count} engagement summaries for period {period}")
                return updated_count

        except Exception as e:
            logger.error(f"Error batch updating summaries: {e}")
            return 0


# Aggregation Functions

def calculate_daily_engagement(topic: str, date: datetime) -> Dict[str, int]:
    """Calculate daily engagement metrics for a topic"""
    # Implementation would query the database for daily metrics
    return {
        'likes': 0,
        'shares': 0,
        'comments': 0,
        'total_engagement': 0
    }


def calculate_monthly_engagement(topic: str, year: int, month: int) -> Dict[str, int]:
    """Calculate monthly engagement metrics for a topic"""
    # Implementation would query the database for monthly metrics
    return {
        'likes': 0,
        'shares': 0,
        'comments': 0,
        'total_engagement': 0
    }


def calculate_yearly_engagement(topic: str, year: int) -> Dict[str, int]:
    """Calculate yearly engagement metrics for a topic"""
    # Implementation would query the database for yearly metrics
    return {
        'likes': 0,
        'shares': 0,
        'comments': 0,
        'total_engagement': 0
    }


def get_top_engaged_topics_by_period(
    period: str,
    limit: int = 10,
    metric: str = 'likes'  # 'likes', 'shares', 'comments'
) -> List[Dict]:
    """Get top topics by engagement metric for a time period"""
    # Implementation would query engagement summaries
    return []