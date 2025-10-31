#!/usr/bin/env python3
"""
Topic search scheduler using APScheduler for continuous trending topic monitoring
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from .detector import XTrendingDetector
from .analyzer import XTrendingAnalyzer
from .storage import TrendingStorage
from .models import TopicSearchResult, SearchJob, EngagementMetrics

logger = logging.getLogger(__name__)

class TopicSearchScheduler:
    """Scheduler for continuous topic search operations"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.detector = XTrendingDetector()
        self.analyzer = XTrendingAnalyzer()
        self.storage = TrendingStorage(self.config.get('database_url', 'sqlite:///trending_data.db'))

        # Initialize scheduler (without AsyncIOExecutor to avoid event loop issues)
        self.scheduler = BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
        )

        # Setup event listeners
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)

        self.running = False

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the scheduler"""
        return {
            'search_interval_hours': 4,
            'database_url': 'sqlite:///trending_data.db',
            'max_retries': 3,
            'retry_delay_minutes': 5,
            'cleanup_days': 30,
            'max_results_per_search': 50
        }

    def start(self) -> None:
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        try:
            # Add the main search job
            self.scheduler.add_job(
                func=self._run_topic_search,
                trigger=IntervalTrigger(hours=self.config['search_interval_hours']),
                id='topic_search_job',
                name='Topic Search Job',
                max_instances=1,
                replace_existing=True
            )

            # Add cleanup job (daily)
            self.scheduler.add_job(
                func=self._cleanup_old_data,
                trigger=IntervalTrigger(days=1),
                id='cleanup_job',
                name='Cleanup Old Data',
                max_instances=1,
                replace_existing=True
            )

            # Start the scheduler
            self.scheduler.start()
            self.running = True
            logger.info(f"Topic search scheduler started with {self.config['search_interval_hours']} hour intervals")

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self) -> None:
        """Stop the scheduler"""
        if not self.running:
            return

        try:
            self.scheduler.shutdown(wait=True)
            self.running = False
            logger.info("Topic search scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def _run_topic_search(self) -> None:
        """Execute the topic search operation"""
        job_id = f"topic_search_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Create job record
            job = self.storage.create_search_job(job_id, 'topic_search')
            if not job:
                logger.error("Failed to create search job record")
                return

            # Update job status to running
            self.storage.update_job_status(job_id, 'running')

            # Perform the search
            logger.info("Starting topic search operation")

            # Get trending data
            trending_data = self.detector.get_trending_data()

            # Analyze the data
            analyses = self.analyzer.analyze_trending_topics()

            # Convert to database models and save
            search_results = []
            search_timestamp = datetime.utcnow()

            for analysis in analyses:
                # Convert analysis to TopicSearchResult with engagement metrics
                result = self.analyzer.convert_to_topic_search_result(analysis)

                # Override search timestamp
                result.search_timestamp = search_timestamp

                # Find corresponding trending data for additional metrics
                for data in trending_data:
                    if data.topic == analysis.topic:
                        result.engagement_score = data.engagement_score
                        result.frequency = data.frequency
                        break

                search_results.append(result)

                # Also save engagement metrics for time-series analysis
                self._save_engagement_metrics(result)

            # Save results
            saved_count = self.storage.save_search_results(search_results)

            # Update job status to completed
            self.storage.update_job_status(job_id, 'completed')

            logger.info(f"Topic search completed successfully. Saved {saved_count} results.")

        except Exception as e:
            logger.error(f"Error during topic search: {e}")

            # Update job status to failed
            self.storage.update_job_status(job_id, 'failed', str(e))

            # Check if we should retry
            job = self.storage.get_pending_jobs()  # This is a simplification; should get specific job
            # In a real implementation, you'd track retry logic here

    def _cleanup_old_data(self) -> None:
        """Clean up old search data"""
        try:
            logger.info("Starting cleanup of old search data")
            deleted_count = self.storage.cleanup_old_data(self.config['cleanup_days'])
            logger.info(f"Cleaned up {deleted_count} old records")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _job_executed_listener(self, event) -> None:
        """Handle job execution events"""
        logger.info(f"Job {event.job_id} executed successfully")

    def _job_error_listener(self, event) -> None:
        """Handle job error events"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")

        # Implement retry logic
        job_id = event.job_id
        job = self.storage.get_failed_jobs_for_retry()
        # Find the specific job and handle retry
        # This is a simplified implementation

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger)
            }
            # Try to get next run time, handle different APScheduler versions
            try:
                if hasattr(job, 'next_run_time') and job.next_run_time:
                    job_info['next_run_time'] = job.next_run_time.isoformat()
                else:
                    job_info['next_run_time'] = None
            except AttributeError:
                job_info['next_run_time'] = None

            jobs_info.append(job_info)

        return {
            'running': self.running,
            'jobs': jobs_info,
            'config': self.config
        }

    def trigger_manual_search(self) -> bool:
        """Manually trigger a topic search"""
        try:
            self.scheduler.add_job(
                func=self._run_topic_search,
                id=f"manual_search_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                name='Manual Topic Search',
                max_instances=1
            )
            logger.info("Manual topic search triggered")
            return True
        except Exception as e:
            logger.error(f"Failed to trigger manual search: {e}")
            return False
    def _save_engagement_metrics(self, topic_result: TopicSearchResult) -> None:
        """Save engagement metrics for time-series analysis"""
        try:
            # Create engagement metrics for each type
            metrics = []

            # Likes metric
            if topic_result.likes_count > 0:
                metrics.append(EngagementMetrics(
                    topic_id=topic_result.id,
                    metric_type='likes',
                    count=topic_result.likes_count,
                    timestamp=topic_result.engagement_timestamp,
                    period='daily'
                ))

            # Shares metric
            if topic_result.shares_count > 0:
                metrics.append(EngagementMetrics(
                    topic_id=topic_result.id,
                    metric_type='shares',
                    count=topic_result.shares_count,
                    timestamp=topic_result.engagement_timestamp,
                    period='daily'
                ))

            # Comments metric
            if topic_result.comments_count > 0:
                metrics.append(EngagementMetrics(
                    topic_id=topic_result.id,
                    metric_type='comments',
                    count=topic_result.comments_count,
                    timestamp=topic_result.engagement_timestamp,
                    period='daily'
                ))

            # Save metrics if any exist
            if metrics:
                self.storage.save_engagement_metrics(metrics)
                logger.info(f"Saved {len(metrics)} engagement metrics for topic: {topic_result.topic}")

        except Exception as e:
            logger.error(f"Error saving engagement metrics for topic {topic_result.topic}: {e}")