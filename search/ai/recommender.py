#!/usr/bin/env python3
"""
AI-powered topic recommender using OpenAI and Gemini APIs
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import os

import openai
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..trending.storage import TrendingStorage
from ..trending.models import AISuggestion, AISuggestionBatch
from ..engines import SearchEngineManager
from ..social import XAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class TopicSuggestion:
    """Represents a topic suggestion from AI"""
    topic: str
    category: str
    confidence_score: float
    reasoning: str
    trend_data: Dict[str, Any]
    related_topics: List[str]
    source: str  # 'openai' or 'gemini'

class AIRecommender:
    """AI-powered topic recommender integrating OpenAI and Gemini APIs"""

    def __init__(self, storage: TrendingStorage, config: Optional[Dict[str, Any]] = None):
        self.storage = storage
        self.config = config or self._default_config()

        # Initialize AI clients
        self._init_openai()
        self._init_gemini()

        # Initialize data sources
        self.search_manager = SearchEngineManager()
        self.x_analyzer = XAnalyzer()

        self.sources = {
            'google': self.search_manager.get_engine('google'),
            'bing': self.search_manager.get_engine('bing'),
            'duckduckgo': self.search_manager.get_engine('duckduckgo'),
            'x': self.x_analyzer
        }

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'openai_model': 'gpt-4',
            'gemini_model': 'gemini-1.5-flash',
            'max_suggestions_per_source': 5,
            'confidence_threshold': 0.7,
            'suggestion_expiry_hours': 24,
            'trend_analysis_days': 7
        }

    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = self.config.get('openai_api_key')
        if api_key:
            openai.api_key = api_key
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found")

    def _init_gemini(self):
        """Initialize Gemini client"""
        api_key = self.config.get('gemini_api_key')
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(self.config['gemini_model'])
            logger.info("Gemini client initialized")
        else:
            logger.warning("Gemini API key not found")

    async def generate_suggestions(self, batch_id: str) -> List[TopicSuggestion]:
        """Generate topic suggestions from multiple AI sources"""
        suggestions = []

        # Get current trends data
        trend_data = await self._gather_trend_data()

        # Generate suggestions from OpenAI
        if self.config.get('openai_api_key'):
            try:
                openai_suggestions = await self._generate_openai_suggestions(trend_data)
                suggestions.extend(openai_suggestions)
                logger.info(f"Generated {len(openai_suggestions)} suggestions from OpenAI")
            except Exception as e:
                logger.error(f"Error generating OpenAI suggestions: {e}")

        # Generate suggestions from Gemini
        if self.config.get('gemini_api_key'):
            try:
                gemini_suggestions = await self._generate_gemini_suggestions(trend_data)
                suggestions.extend(gemini_suggestions)
                logger.info(f"Generated {len(gemini_suggestions)} suggestions from Gemini")
            except Exception as e:
                logger.error(f"Error generating Gemini suggestions: {e}")

        # Rank and filter suggestions
        ranked_suggestions = self._rank_suggestions(suggestions)

        return ranked_suggestions

    async def _gather_trend_data(self) -> Dict[str, Any]:
        """Gather trend data from multiple sources"""
        trend_data = {
            'google_trends': [],
            'bing_trends': [],
            'duckduckgo_trends': [],
            'x_trends': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Gather data from each source
        for source_name, source in self.sources.items():
            try:
                if source_name == 'x':
                    trends = await source.get_trending_topics(limit=20)
                else:
                    trends = await source.search_trending_topics()

                trend_data[f'{source_name}_trends'] = [
                    {
                        'topic': t.get('topic', t.get('title', '')),
                        'score': t.get('score', t.get('engagement_score', 0)),
                        'category': t.get('category', 'general'),
                        'volume': t.get('volume', t.get('frequency', 0))
                    }
                    for t in trends[:20]  # Limit to top 20
                ]
                logger.info(f"Gathered {len(trend_data[f'{source_name}_trends'])} trends from {source_name}")
            except Exception as e:
                logger.error(f"Error gathering trends from {source_name}: {e}")

        return trend_data

    async def _generate_openai_suggestions(self, trend_data: Dict[str, Any]) -> List[TopicSuggestion]:
        """Generate suggestions using OpenAI"""
        prompt = self._build_openai_prompt(trend_data)

        response = await openai.ChatCompletion.acreate(
            model=self.config['openai_model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

        suggestions_text = response.choices[0].message.content
        return self._parse_ai_response(suggestions_text, 'openai')

    async def _generate_gemini_suggestions(self, trend_data: Dict[str, Any]) -> List[TopicSuggestion]:
        """Generate suggestions using Gemini"""
        prompt = self._build_gemini_prompt(trend_data)

        response = self.gemini_model.generate_content(prompt)
        suggestions_text = response.text

        return self._parse_ai_response(suggestions_text, 'gemini')

    def _build_openai_prompt(self, trend_data: Dict[str, Any]) -> str:
        """Build prompt for OpenAI"""
        return f"""
        Analyze the following trending topics from multiple sources and suggest 10 new topics that are likely to trend in the next 6-24 hours.

        Current Trends Data:
        {json.dumps(trend_data, indent=2)}

        Instructions:
        1. Analyze patterns across Google, Bing, DuckDuckGo, and X (Twitter) trends
        2. Identify emerging topics, breaking news, or topics with increasing momentum
        3. Suggest topics from diverse categories: technology, entertainment, sports, politics, science, etc.
        4. Focus on topics that would be interesting for search and social media engagement
        5. Provide confidence scores (0.0-1.0) based on trend analysis
        6. Include reasoning for each suggestion

        Format your response as a JSON array of objects with this structure:
        [
          {{
            "topic": "Topic Name",
            "category": "Category",
            "confidence_score": 0.85,
            "reasoning": "Explanation of why this topic will trend",
            "related_topics": ["related1", "related2"]
          }}
        ]
        """

    def _build_gemini_prompt(self, trend_data: Dict[str, Any]) -> str:
        """Build prompt for Gemini (similar to OpenAI but adapted)"""
        return f"""
        Based on current trending data from multiple sources, predict 10 topics likely to trend soon.

        Current Trends:
        {json.dumps(trend_data, indent=2)}

        Analyze cross-platform trends and suggest emerging topics. Return as JSON array with topic, category, confidence_score, reasoning, and related_topics.
        """

    def _parse_ai_response(self, response_text: str, source: str) -> List[TopicSuggestion]:
        """Parse AI response into TopicSuggestion objects"""
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            json_str = response_text[json_start:json_end]

            suggestions_data = json.loads(json_str)
            suggestions = []

            for item in suggestions_data[:self.config['max_suggestions_per_source']]:
                suggestion = TopicSuggestion(
                    topic=item['topic'],
                    category=item.get('category', 'general'),
                    confidence_score=float(item['confidence_score']),
                    reasoning=item.get('reasoning', ''),
                    trend_data={},  # Will be filled later
                    related_topics=item.get('related_topics', []),
                    source=source
                )
                suggestions.append(suggestion)

            return suggestions
        except Exception as e:
            logger.error(f"Error parsing AI response from {source}: {e}")
            return []

    def _rank_suggestions(self, suggestions: List[TopicSuggestion]) -> List[TopicSuggestion]:
        """Rank suggestions based on confidence and other factors"""
        # Filter by confidence threshold
        filtered = [s for s in suggestions if s.confidence_score >= self.config['confidence_threshold']]

        # Sort by confidence score (highest first)
        ranked = sorted(filtered, key=lambda s: s.confidence_score, reverse=True)

        # Limit to top suggestions
        return ranked[:10]

    def save_suggestions(self, suggestions: List[TopicSuggestion], batch_id: str) -> int:
        """Save suggestions to database"""
        try:
            ai_suggestions = []
            expires_at = datetime.utcnow() + timedelta(hours=self.config['suggestion_expiry_hours'])

            for suggestion in suggestions:
                ai_suggestion = AISuggestion(
                    topic=suggestion.topic,
                    category=suggestion.category,
                    confidence_score=suggestion.confidence_score,
                    ranking_score=suggestion.confidence_score,  # Simple ranking for now
                    source=suggestion.source,
                    reasoning=suggestion.reasoning,
                    trend_data=json.dumps(suggestion.trend_data),
                    related_topics=json.dumps(suggestion.related_topics),
                    batch_id=batch_id,
                    expires_at=expires_at
                )
                ai_suggestions.append(ai_suggestion)

            saved_count = self.storage.save_ai_suggestions(ai_suggestions)
            logger.info(f"Saved {saved_count} AI suggestions for batch {batch_id}")
            return saved_count

        except Exception as e:
            logger.error(f"Error saving AI suggestions: {e}")
            return 0

class AISuggestionScheduler:
    """Scheduler for AI suggestion generation every 6 hours"""

    def __init__(self, recommender: AIRecommender, config: Optional[Dict[str, Any]] = None):
        self.recommender = recommender
        self.config = config or {'interval_hours': 6}

        self.scheduler = BackgroundScheduler(
            job_defaults={'coalesce': True, 'max_instances': 1}
        )
        self.running = False

    def start(self):
        """Start the scheduler"""
        if self.running:
            return

        self.scheduler.add_job(
            func=self._generate_suggestions_job,
            trigger=IntervalTrigger(hours=self.config['interval_hours']),
            id='ai_suggestion_job',
            name='AI Suggestion Generation',
            max_instances=1,
            replace_existing=True
        )

        self.scheduler.start()
        self.running = True
        logger.info(f"AI suggestion scheduler started with {self.config['interval_hours']} hour intervals")

    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return

        self.scheduler.shutdown(wait=True)
        self.running = False
        logger.info("AI suggestion scheduler stopped")

    def _generate_suggestions_job(self):
        """Job to generate AI suggestions"""
        batch_id = f"ai_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Create batch record
            batch = AISuggestionBatch(batch_id=batch_id, status='running')
            self.recommender.storage.save_ai_suggestion_batch(batch)

            # Generate suggestions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            suggestions = loop.run_until_complete(self.recommender.generate_suggestions(batch_id))
            loop.close()

            # Save suggestions
            saved_count = self.recommender.save_suggestions(suggestions, batch_id)

            # Update batch status
            batch.status = 'completed'
            batch.total_suggestions = saved_count
            batch.openai_suggestions = len([s for s in suggestions if s.source == 'openai'])
            batch.gemini_suggestions = len([s for s in suggestions if s.source == 'gemini'])
            batch.completed_at = datetime.utcnow()
            self.recommender.storage.update_ai_suggestion_batch(batch)

            logger.info(f"AI suggestion batch {batch_id} completed with {saved_count} suggestions")

        except Exception as e:
            logger.error(f"Error in AI suggestion job: {e}")

            # Update batch status to failed
            batch.status = 'failed'
            batch.error_message = str(e)
            self.recommender.storage.update_ai_suggestion_batch(batch)

    def trigger_manual_generation(self) -> bool:
        """Manually trigger suggestion generation"""
        try:
            self.scheduler.add_job(
                func=self._generate_suggestions_job,
                id=f"manual_ai_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                name='Manual AI Suggestion Generation'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to trigger manual AI generation: {e}")
            return False