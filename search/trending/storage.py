#!/usr/bin/env python3
"""
Database storage layer for trending topic search results
"""

import json
import logging
from datetime import datetime, timedelta, UTC
from typing import List, Optional, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .models import TopicSearchResult, SearchJob, EngagementMetrics, EngagementSummary, AISuggestion, AISuggestionBatch, Base

logger = logging.getLogger(__name__)

class TrendingStorage:
    """Database storage for trending topic data"""

    def __init__(self, database_url: str = "sqlite:///trending_data.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

        # Initialize aggregation service
        try:
            from .aggregation import EngagementAggregationService
            self.aggregation_service = EngagementAggregationService(self)
        except ImportError as e:
            logger.warning(f"Could not initialize aggregation service: {e}")
            self.aggregation_service = None

    def save_search_result(self, result: TopicSearchResult) -> bool:
        """Save a topic search result to database"""
        try:
            with self.SessionLocal() as session:
                session.add(result)
                session.commit()
                logger.info(f"Saved search result for topic: {result.topic}")
                return True
        except Exception as e:
            logger.error(f"Error saving search result: {e}")
            return False

    def save_search_results(self, results: List[TopicSearchResult]) -> int:
        """Save multiple search results to database"""
        saved_count = 0
        try:
            with self.SessionLocal() as session:
                for result in results:
                    session.add(result)
                    saved_count += 1
                session.commit()
                logger.info(f"Saved {saved_count} search results")
                return saved_count
        except Exception as e:
            logger.error(f"Error saving search results: {e}")
            return 0

    def get_recent_results(self, hours: int = 24, limit: int = 100) -> List[TopicSearchResult]:
        """Get recent search results within specified hours"""
        try:
            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            with self.SessionLocal() as session:
                results = session.query(TopicSearchResult)\
                    .filter(TopicSearchResult.search_timestamp >= cutoff_time)\
                    .order_by(TopicSearchResult.search_timestamp.desc())\
                    .limit(limit)\
                    .all()
                return results
        except Exception as e:
            logger.error(f"Error getting recent results: {e}")
            return []

    def get_results_by_category(self, category: str, hours: int = 24) -> List[TopicSearchResult]:
        """Get search results by category"""
        try:
            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            with self.SessionLocal() as session:
                results = session.query(TopicSearchResult)\
                    .filter(
                        TopicSearchResult.category == category,
                        TopicSearchResult.search_timestamp >= cutoff_time
                    )\
                    .order_by(TopicSearchResult.score.desc())\
                    .all()
                return results
        except Exception as e:
            logger.error(f"Error getting results by category: {e}")
            return []

    def get_top_trending_topics(self, limit: int = 10, hours: int = 24) -> List[TopicSearchResult]:
        """Get top trending topics by score"""
        try:
            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            with self.SessionLocal() as session:
                results = session.query(TopicSearchResult)\
                    .filter(TopicSearchResult.search_timestamp >= cutoff_time)\
                    .order_by(TopicSearchResult.score.desc())\
                    .limit(limit)\
                    .all()
                return results
        except Exception as e:
            logger.error(f"Error getting top trending topics: {e}")
            return []

    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old search results"""
        try:
            cutoff_time = datetime.now(UTC) - timedelta(days=days)
            with self.SessionLocal() as session:
                deleted_count = session.query(TopicSearchResult)\
                    .filter(TopicSearchResult.search_timestamp < cutoff_time)\
                    .delete()
                session.commit()
                logger.info(f"Cleaned up {deleted_count} old search results")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0

    # SearchJob methods
    def create_search_job(self, job_id: str, job_type: str) -> Optional[SearchJob]:
        """Create a new search job"""
        try:
            job = SearchJob(job_id=job_id, job_type=job_type)
            with self.SessionLocal() as session:
                session.add(job)
                session.commit()
                session.refresh(job)
                return job
        except Exception as e:
            logger.error(f"Error creating search job: {e}")
            return None

    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """Update search job status"""
        try:
            with self.SessionLocal() as session:
                job = session.query(SearchJob).filter(SearchJob.job_id == job_id).first()
                if job:
                    job.status = status
                    if status == 'running' and not job.started_at:
                        job.started_at = datetime.now(UTC)
                    elif status in ['completed', 'failed']:
                        job.completed_at = datetime.now(UTC)
                    if error_message:
                        job.error_message = error_message
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return False

    def increment_retry_count(self, job_id: str) -> bool:
        """Increment retry count for a job"""
        try:
            with self.SessionLocal() as session:
                job = session.query(SearchJob).filter(SearchJob.job_id == job_id).first()
                if job:
                    job.retry_count += 1
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error incrementing retry count: {e}")
            return False

    def get_pending_jobs(self) -> List[SearchJob]:
        """Get pending search jobs"""
        try:
            with self.SessionLocal() as session:
                jobs = session.query(SearchJob)\
                    .filter(SearchJob.status == 'pending')\
                    .order_by(SearchJob.created_at)\
                    .all()
                return jobs
        except Exception as e:
            logger.error(f"Error getting pending jobs: {e}")
            return []

    def get_failed_jobs_for_retry(self) -> List[SearchJob]:
        """Get failed jobs that can be retried"""
        try:
            with self.SessionLocal() as session:
                jobs = session.query(SearchJob)\
                    .filter(
                        SearchJob.status == 'failed',
                        SearchJob.retry_count < SearchJob.max_retries
                    )\
                    .order_by(SearchJob.created_at)\
                    .all()
                return jobs
        except Exception as e:
            logger.error(f"Error getting failed jobs for retry: {e}")
            return []

    # Engagement metrics methods
    def save_engagement_metric(self, metric: EngagementMetrics) -> bool:
        """Save an engagement metric to database"""
        try:
            with self.SessionLocal() as session:
                session.add(metric)
                session.commit()
                logger.info(f"Saved engagement metric: {metric.metric_type} for topic {metric.topic_id}")
                return True
        except Exception as e:
            logger.error(f"Error saving engagement metric: {e}")
            return False

    def save_engagement_metrics(self, metrics: List[EngagementMetrics]) -> int:
        """Save multiple engagement metrics to database"""
        saved_count = 0
        try:
            with self.SessionLocal() as session:
                for metric in metrics:
                    session.add(metric)
                    saved_count += 1
                session.commit()
                logger.info(f"Saved {saved_count} engagement metrics")
                return saved_count
        except Exception as e:
            logger.error(f"Error saving engagement metrics: {e}")
            return 0

    def get_engagement_metrics_by_topic(self, topic_id: int, period: str = None,
                                       start_date: datetime = None, end_date: datetime = None) -> List[EngagementMetrics]:
        """Get engagement metrics for a specific topic"""
        try:
            with self.SessionLocal() as session:
                query = session.query(EngagementMetrics).filter(EngagementMetrics.topic_id == topic_id)

                if period:
                    query = query.filter(EngagementMetrics.period == period)
                if start_date:
                    query = query.filter(EngagementMetrics.timestamp >= start_date)
                if end_date:
                    query = query.filter(EngagementMetrics.timestamp <= end_date)

                metrics = query.order_by(EngagementMetrics.timestamp).all()
                return metrics
        except Exception as e:
            logger.error(f"Error getting engagement metrics by topic: {e}")
            return []

    def get_top_engaged_topics_by_period(self, period: str, metric: str = 'likes',
                                        limit: int = 10, category: str = None) -> List[Dict]:
        """Get top engaged topics by period and metric"""
        try:
            with self.SessionLocal() as session:
                # Query engagement summaries
                query = session.query(EngagementSummary)\
                    .filter(EngagementSummary.period == period)

                if category:
                    query = query.filter(EngagementSummary.category == category)

                # Order by the specified metric
                if metric == 'likes':
                    query = query.order_by(EngagementSummary.total_likes.desc())
                elif metric == 'shares':
                    query = query.order_by(EngagementSummary.total_shares.desc())
                elif metric == 'comments':
                    query = query.order_by(EngagementSummary.total_comments.desc())

                summaries = query.limit(limit).all()

                # Convert to dict format
                result = []
                for summary in summaries:
                    result.append({
                        'topic': summary.topic,
                        'category': summary.category,
                        'period': summary.period,
                        'total_likes': summary.total_likes,
                        'total_shares': summary.total_shares,
                        'total_comments': summary.total_comments,
                        'avg_engagement_score': summary.avg_engagement_score,
                        'peak_engagement_time': summary.peak_engagement_time.isoformat() if summary.peak_engagement_time else None
                    })

                return result
        except Exception as e:
            logger.error(f"Error getting top engaged topics by period: {e}")
            return []

    def get_engagement_trends(self, category: str = None, period: str = 'daily',
                             start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get engagement trends for categories or all topics"""
        try:
            with self.SessionLocal() as session:
                query = session.query(EngagementSummary)\
                    .filter(EngagementSummary.period == period)

                if category:
                    query = query.filter(EngagementSummary.category == category)
                if start_date:
                    query = query.filter(EngagementSummary.period_start >= start_date)
                if end_date:
                    query = query.filter(EngagementSummary.period_end <= end_date)

                summaries = query.order_by(EngagementSummary.period_start).all()

                # Group by period start and aggregate
                trends = {}
                for summary in summaries:
                    key = summary.period_start.date().isoformat()
                    if key not in trends:
                        trends[key] = {
                            'date': key,
                            'total_likes': 0,
                            'total_shares': 0,
                            'total_comments': 0,
                            'avg_engagement_score': 0.0,
                            'topic_count': 0
                        }

                    trends[key]['total_likes'] += summary.total_likes
                    trends[key]['total_shares'] += summary.total_shares
                    trends[key]['total_comments'] += summary.total_comments
                    trends[key]['avg_engagement_score'] += summary.avg_engagement_score
                    trends[key]['topic_count'] += 1

                # Calculate averages
                for trend in trends.values():
                    if trend['topic_count'] > 0:
                        trend['avg_engagement_score'] /= trend['topic_count']

                return list(trends.values())
        except Exception as e:
            logger.error(f"Error getting engagement trends: {e}")
            return []

    def get_engagement_summary(self, period: str, date: datetime = None) -> Dict:
        """Get overall engagement summary for a period"""
        try:
            if not date:
                date = datetime.now(UTC)

            with self.SessionLocal() as session:
                # Calculate period boundaries
                if period == 'daily':
                    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date + timedelta(days=1)
                elif period == 'monthly':
                    start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = (start_date + timedelta(days=32)).replace(day=1)
                elif period == 'yearly':
                    start_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = date.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
                else:
                    return {}

                # Aggregate from engagement summaries
                summaries = session.query(EngagementSummary)\
                    .filter(EngagementSummary.period == period)\
                    .filter(EngagementSummary.period_start >= start_date)\
                    .filter(EngagementSummary.period_end <= end_date)\
                    .all()

                total_likes = sum(s.total_likes for s in summaries)
                total_shares = sum(s.total_shares for s in summaries)
                total_comments = sum(s.total_comments for s in summaries)
                avg_engagement = sum(s.avg_engagement_score for s in summaries) / len(summaries) if summaries else 0.0

                return {
                    'period': period,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_likes': total_likes,
                    'total_shares': total_shares,
                    'total_comments': total_comments,
                    'avg_engagement_score': avg_engagement,
                    'topic_count': len(summaries)
                }
        except Exception as e:
            logger.error(f"Error getting engagement summary: {e}")
            return {}

    # Aggregation methods
    def run_daily_aggregation(self, date: datetime = None) -> int:
        """Run daily aggregation for engagement metrics"""
        if self.aggregation_service is None:
            logger.warning("Aggregation service not available")
            return 0
        if not date:
            date = datetime.now(UTC)
        return self.aggregation_service.aggregate_daily_metrics(date)

    def run_monthly_aggregation(self, year: int = None, month: int = None) -> int:
        """Run monthly aggregation for engagement metrics"""
        if self.aggregation_service is None:
            logger.warning("Aggregation service not available")
            return 0
        if not year or not month:
            now = datetime.now(UTC)
            year = now.year
            month = now.month
        return self.aggregation_service.aggregate_monthly_metrics(year, month)

    def run_yearly_aggregation(self, year: int = None) -> int:
        """Run yearly aggregation for engagement metrics"""
        if self.aggregation_service is None:
            logger.warning("Aggregation service not available")
            return 0
        if not year:
            year = datetime.now(UTC).year
        return self.aggregation_service.aggregate_yearly_metrics(year)

    def update_engagement_summaries(self, period: str, start_date: datetime = None, end_date: datetime = None) -> int:
        """Update engagement summaries for a date range"""
        if self.aggregation_service is None:
            logger.warning("Aggregation service not available")
            return 0
        if not start_date:
            start_date = datetime.now(UTC) - timedelta(days=1)
        if not end_date:
            end_date = datetime.now(UTC)
        return self.aggregation_service.batch_update_summaries(period, start_date, end_date)

    # AI Suggestions methods
    def save_ai_suggestion(self, suggestion: AISuggestion) -> bool:
        """Save an AI suggestion to database"""
        try:
            with self.SessionLocal() as session:
                session.add(suggestion)
                session.commit()
                logger.info(f"Saved AI suggestion: {suggestion.topic} from {suggestion.source}")
                return True
        except Exception as e:
            logger.error(f"Error saving AI suggestion: {e}")
            return False

    def save_ai_suggestions(self, suggestions: List[AISuggestion]) -> int:
        """Save multiple AI suggestions to database"""
        saved_count = 0
        try:
            with self.SessionLocal() as session:
                for suggestion in suggestions:
                    session.add(suggestion)
                    saved_count += 1
                session.commit()
                logger.info(f"Saved {saved_count} AI suggestions")
                return saved_count
        except Exception as e:
            logger.error(f"Error saving AI suggestions: {e}")
            return 0

    def get_active_ai_suggestions(self, limit: int = 10, category: str = None,
                                 min_confidence: float = 0.0) -> List[AISuggestion]:
        """Get active AI suggestions sorted by ranking score"""
        try:
            with self.SessionLocal() as session:
                query = session.query(AISuggestion)\
                    .filter(
                        AISuggestion.is_active == True,
                        AISuggestion.confidence_score >= min_confidence
                    )

                if category:
                    query = query.filter(AISuggestion.category == category)

                suggestions = query.order_by(AISuggestion.ranking_score.desc())\
                    .limit(limit)\
                    .all()

                return suggestions
        except Exception as e:
            logger.error(f"Error getting active AI suggestions: {e}")
            return []

    def get_ai_suggestions_by_source(self, source: str, limit: int = 10) -> List[AISuggestion]:
        """Get AI suggestions by source"""
        try:
            with self.SessionLocal() as session:
                suggestions = session.query(AISuggestion)\
                    .filter(
                        AISuggestion.source == source,
                        AISuggestion.is_active == True
                    )\
                    .order_by(AISuggestion.confidence_score.desc())\
                    .limit(limit)\
                    .all()
                return suggestions
        except Exception as e:
            logger.error(f"Error getting AI suggestions by source: {e}")
            return []

    def deactivate_expired_suggestions(self) -> int:
        """Deactivate expired AI suggestions"""
        try:
            with self.SessionLocal() as session:
                now = datetime.now(UTC)
                updated_count = session.query(AISuggestion)\
                    .filter(
                        AISuggestion.is_active == True,
                        AISuggestion.expires_at <= now
                    )\
                    .update({'is_active': False})
                session.commit()
                logger.info(f"Deactivated {updated_count} expired AI suggestions")
                return updated_count
        except Exception as e:
            logger.error(f"Error deactivating expired suggestions: {e}")
            return 0

    def save_ai_suggestion_batch(self, batch: AISuggestionBatch) -> bool:
        """Save an AI suggestion batch to database"""
        try:
            with self.SessionLocal() as session:
                session.add(batch)
                session.commit()
                logger.info(f"Saved AI suggestion batch: {batch.batch_id}")
                return True
        except Exception as e:
            logger.error(f"Error saving AI suggestion batch: {e}")
            return False

    def update_ai_suggestion_batch(self, batch: AISuggestionBatch) -> bool:
        """Update an AI suggestion batch in database"""
        try:
            with self.SessionLocal() as session:
                existing_batch = session.query(AISuggestionBatch)\
                    .filter(AISuggestionBatch.batch_id == batch.batch_id)\
                    .first()

                if existing_batch:
                    existing_batch.status = batch.status
                    existing_batch.total_suggestions = batch.total_suggestions
                    existing_batch.openai_suggestions = batch.openai_suggestions
                    existing_batch.gemini_suggestions = batch.gemini_suggestions
                    existing_batch.error_message = batch.error_message
                    existing_batch.completed_at = batch.completed_at
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating AI suggestion batch: {e}")
            return False

    def get_recent_ai_batches(self, limit: int = 5) -> List[AISuggestionBatch]:
        """Get recent AI suggestion batches"""
        try:
            with self.SessionLocal() as session:
                batches = session.query(AISuggestionBatch)\
                    .order_by(AISuggestionBatch.created_at.desc())\
                    .limit(limit)\
                    .all()
                return batches
        except Exception as e:
            logger.error(f"Error getting recent AI batches: {e}")
            return []