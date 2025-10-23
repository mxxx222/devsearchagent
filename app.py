from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import asyncio
from datetime import datetime
import logging
import re
import html

from search.trending import TopicSearchScheduler, TrendingStorage
from search.ai import AIRecommender, AISuggestionScheduler
from search.manager import SearchManager
from search.social import TwitterAPIv2

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

# Initialize security extensions
csrf = CSRFProtect(app)

# Configure Redis storage for Flask-Limiter (with fallback to memory if Redis unavailable)
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
try:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=redis_url
    )
    print("Flask-Limiter configured with Redis storage")
except Exception as e:
    print(f"Failed to configure Redis storage for Flask-Limiter: {e}. Falling back to in-memory storage.")
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
    return response

# Initialize scheduler and storage
scheduler = None
storage = TrendingStorage()
search_manager = None
ai_recommender = None
ai_scheduler = None
twitter_api = None

logger = logging.getLogger(__name__)

# Input validation and sanitization
def validate_and_sanitize_input(input_string, max_length=500, allowed_chars=None):
    """Validate and sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove null bytes and control characters
    input_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_string)
    
    # HTML escape to prevent XSS
    input_string = html.escape(input_string)
    
    # Limit length
    if len(input_string) > max_length:
        input_string = input_string[:max_length]
    
    # Check allowed characters if specified
    if allowed_chars and not re.match(allowed_chars, input_string):
        raise ValueError("Invalid characters in input")
    
    return input_string.strip()

def validate_query_params(request, allowed_params):
    """Validate query parameters"""
    validated_params = {}
    for param in allowed_params:
        value = request.args.get(param)
        if value is not None:
            if param in ['limit', 'max_results']:
                try:
                    validated_params[param] = max(1, min(int(value), 100))  # Limit to 1-100
                except ValueError:
                    validated_params[param] = allowed_params[param]['default']
            elif param in ['min_confidence']:
                try:
                    validated_params[param] = max(0.0, min(float(value), 1.0))  # Limit to 0-1
                except ValueError:
                    validated_params[param] = allowed_params[param]['default']
            elif param in ['category', 'source']:
                validated_params[param] = validate_and_sanitize_input(value, 100, r'^[a-zA-Z0-9_-]+$')
            else:
                validated_params[param] = validate_and_sanitize_input(value, 200)
    
    return validated_params

# Mock data for demonstration
MOCK_SEARCH_RESULTS = [
    {"title": "Python Programming", "url": "https://python.org", "description": "Official Python website"},
    {"title": "Flask Documentation", "url": "https://flask.palletsprojects.com", "description": "Flask web framework docs"},
    {"title": "Data Science with Python", "url": "https://pandas.pydata.org", "description": "Pandas library for data manipulation"}
]

MOCK_TRENDING_DATA = [
    {"topic": "AI Development", "score": 95, "change": "+15%"},
    {"topic": "Machine Learning", "score": 87, "change": "+8%"},
    {"topic": "Web Development", "score": 78, "change": "+12%"},
    {"topic": "Data Science", "score": 82, "change": "+5%"},
    {"topic": "Cloud Computing", "score": 75, "change": "+10%"}
]

MOCK_AI_RECOMMENDATIONS = [
    {"query": "python tutorials", "confidence": 0.92},
    {"query": "flask web app", "confidence": 0.88},
    {"query": "data visualization", "confidence": 0.85}
]

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
@csrf.exempt  # Allow search without CSRF for API usage
def search():
    try:
        # Validate and sanitize input
        query = request.form.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Sanitize query to prevent injection attacks
        query = validate_and_sanitize_input(query, max_length=200, allowed_chars=r'^[a-zA-Z0-9\s\-_.,!?]+$')
        
        if not query:
            return jsonify({"error": "Invalid query format"}), 400
        
        # Use real search manager
        if search_manager:
            # Run async search in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                search_results = loop.run_until_complete(search_manager.search(query, max_results=10))
                loop.close()
                
                # Convert search results to JSON format with sanitization
                results = []
                for result in search_results.results:
                    results.append({
                        "title": validate_and_sanitize_input(result.title, 200),
                        "url": validate_and_sanitize_input(result.url, 500),
                        "description": validate_and_sanitize_input(result.snippet, 300),
                        "source": validate_and_sanitize_input(result.source, 50)
                    })
                
                return jsonify({"results": results, "query": query})
            except Exception as e:
                loop.close()
                logger.error(f"Search error: {e}")
                return jsonify({"error": "Search failed"}), 500
        else:
            # Fallback to mock data if search manager not initialized
            return jsonify({"results": MOCK_SEARCH_RESULTS, "query": query})
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        return jsonify({"error": "Invalid input format"}), 400
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Search service temporarily unavailable"}), 500

@app.route('/api/trending')
@limiter.limit("30 per minute")  # Rate limiting
def get_trending():
    try:
        # Validate query parameters
        allowed_params = {
            'limit': {'default': 10},
            'hours': {'default': 24}
        }
        params = validate_query_params(request, allowed_params)
        
        limit = params.get('limit', 10)
        hours = params.get('hours', 24)
        
        # Get real trending data from database
        results = storage.get_top_trending_topics(limit=limit, hours=hours)
        trending_data = [
            {
                "topic": validate_and_sanitize_input(result.topic, 200),
                "score": int(result.score * 100),  # Convert to percentage
                "change": validate_and_sanitize_input(str(result.engagement_trend), 50),
                "category": validate_and_sanitize_input(result.category, 100),
                "timestamp": result.search_timestamp.isoformat() if result.search_timestamp else None
            }
            for result in results
        ]
        return jsonify(trending_data)
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error getting trending data: {e}")
        # Fallback to mock data
        return jsonify(MOCK_TRENDING_DATA)

@app.route('/api/recommendations')
@limiter.limit("20 per minute")  # Rate limiting
def get_recommendations():
    """Get AI-generated topic recommendations"""
    try:
        # Validate query parameters
        allowed_params = {
            'limit': {'default': 10},
            'category': {'default': None},
            'min_confidence': {'default': 0.0}
        }
        params = validate_query_params(request, allowed_params)
        
        limit = params.get('limit', 10)
        category = params.get('category')
        min_confidence = params.get('min_confidence', 0.0)

        suggestions = storage.get_active_ai_suggestions(
            limit=limit,
            category=category,
            min_confidence=min_confidence
        )

        # Convert to response format with sanitization
        recommendations = []
        for suggestion in suggestions:
            try:
                # Safely parse JSON for related topics
                related_topics = []
                if suggestion.related_topics:
                    try:
                        parsed_topics = json.loads(suggestion.related_topics)
                        if isinstance(parsed_topics, list):
                            related_topics = [validate_and_sanitize_input(str(topic), 100) for topic in parsed_topics[:5]]
                    except (json.JSONDecodeError, TypeError):
                        related_topics = []
                
                recommendations.append({
                    'topic': validate_and_sanitize_input(suggestion.topic, 200),
                    'category': validate_and_sanitize_input(suggestion.category, 100),
                    'confidence': float(suggestion.confidence_score),
                    'ranking_score': float(suggestion.ranking_score),
                    'source': validate_and_sanitize_input(suggestion.source, 50),
                    'reasoning': validate_and_sanitize_input(suggestion.reasoning or '', 500),
                    'related_topics': related_topics,
                    'created_at': suggestion.created_at.isoformat()
                })
            except Exception as e:
                logger.warning(f"Error processing suggestion: {e}")
                continue

        return jsonify(recommendations)
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return jsonify({"error": "Failed to get AI recommendations"}), 500

@app.route('/api/recommendations/sources/<source>')
@limiter.limit("20 per minute")  # Rate limiting
def get_recommendations_by_source(source):
    """Get AI recommendations by source (openai or gemini)"""
    try:
        # Validate source parameter
        if not source or not re.match(r'^[a-zA-Z0-9_-]+$', source):
            return jsonify({"error": "Invalid source parameter"}), 400
        
        source = validate_and_sanitize_input(source, 50, r'^[a-zA-Z0-9_-]+$')
        
        # Validate limit parameter
        limit = 10
        if 'limit' in request.args:
            try:
                limit = max(1, min(int(request.args.get('limit')), 50))  # Limit to 1-50
            except ValueError:
                return jsonify({"error": "Invalid limit parameter"}), 400

        suggestions = storage.get_ai_suggestions_by_source(source, limit=limit)

        recommendations = []
        for suggestion in suggestions:
            try:
                # Safely parse JSON for related topics
                related_topics = []
                if suggestion.related_topics:
                    try:
                        parsed_topics = json.loads(suggestion.related_topics)
                        if isinstance(parsed_topics, list):
                            related_topics = [validate_and_sanitize_input(str(topic), 100) for topic in parsed_topics[:5]]
                    except (json.JSONDecodeError, TypeError):
                        related_topics = []
                
                recommendations.append({
                    'topic': validate_and_sanitize_input(suggestion.topic, 200),
                    'category': validate_and_sanitize_input(suggestion.category, 100),
                    'confidence': float(suggestion.confidence_score),
                    'ranking_score': float(suggestion.ranking_score),
                    'reasoning': validate_and_sanitize_input(suggestion.reasoning or '', 500),
                    'related_topics': related_topics,
                    'created_at': suggestion.created_at.isoformat()
                })
            except Exception as e:
                logger.warning(f"Error processing suggestion: {e}")
                continue

        return jsonify(recommendations)
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error getting recommendations by source: {e}")
        return jsonify({"error": "Failed to get recommendations by source"}), 500

@app.route('/api/recommendations/trigger', methods=['POST'])
@limiter.limit("5 per hour")  # Strict rate limiting for admin actions
@csrf.exempt  # Allow API calls without CSRF for automation
def trigger_ai_generation():
    """Manually trigger AI suggestion generation"""
    try:
        global ai_scheduler
        if ai_scheduler:
            success = ai_scheduler.trigger_manual_generation()
            return jsonify({"success": success})
        return jsonify({"success": False, "error": "AI scheduler not initialized"}), 503
    except Exception as e:
        logger.error(f"Error triggering AI generation: {e}")
        return jsonify({"success": False, "error": "Failed to trigger generation"}), 500

# Engagement API endpoints
@app.route('/api/engagement/topics/<int:topic_id>/metrics')
def get_topic_engagement_metrics(topic_id):
    """Get engagement metrics for a specific topic"""
    try:
        period = request.args.get('period')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        metrics = storage.get_engagement_metrics_by_topic(topic_id, period, start_dt, end_dt)

        # Convert to response format
        data = []
        for metric in metrics:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'metric_type': metric.metric_type,
                'count': metric.count,
                'period': metric.period
            })

        return jsonify({
            'topic_id': topic_id,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error getting topic engagement metrics: {e}")
        return jsonify({"error": "Failed to get engagement metrics"}), 500

@app.route('/api/engagement/topics/top')
def get_top_engaged_topics():
    """Get top topics by engagement metric"""
    try:
        period = request.args.get('period', 'daily')
        metric = request.args.get('metric', 'likes')
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')

        topics = storage.get_top_engaged_topics_by_period(period, metric, limit, category)
        return jsonify(topics)
    except Exception as e:
        logger.error(f"Error getting top engaged topics: {e}")
        return jsonify({"error": "Failed to get top engaged topics"}), 500

@app.route('/api/engagement/categories/<category>/trends')
def get_category_engagement_trends(category):
    """Get engagement trends for a category"""
    try:
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        trends = storage.get_engagement_trends(category, period, start_dt, end_dt)
        return jsonify({
            'category': category,
            'period': period,
            'data': trends
        })
    except Exception as e:
        logger.error(f"Error getting category engagement trends: {e}")
        return jsonify({"error": "Failed to get engagement trends"}), 500

@app.route('/api/engagement/summary')
def get_engagement_summary():
    """Get overall engagement summary"""
    try:
        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')

        date = datetime.fromisoformat(date_str) if date_str else None
        summary = storage.get_engagement_summary(period, date)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting engagement summary: {e}")
        return jsonify({"error": "Failed to get engagement summary"}), 500

@app.route('/api/engagement/aggregate', methods=['POST'])
def trigger_aggregation():
    """Manually trigger aggregation"""
    try:
        data = request.get_json() or {}
        period = data.get('period', 'daily')
        date_str = data.get('date')

        if period == 'daily':
            date = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
            updated = storage.run_daily_aggregation(date)
        elif period == 'monthly':
            date = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
            updated = storage.run_monthly_aggregation(date.year, date.month)
        elif period == 'yearly':
            year = int(date_str) if date_str else datetime.utcnow().year
            updated = storage.run_yearly_aggregation(year)
        else:
            return jsonify({"error": "Invalid period"}), 400

        return jsonify({"success": True, "updated_topics": updated})
    except Exception as e:
        logger.error(f"Error triggering aggregation: {e}")
        return jsonify({"error": "Failed to trigger aggregation"}), 500

@app.route('/api/scheduler/status')
def get_scheduler_status():
    """Get scheduler status"""
    global scheduler
    if scheduler:
        return jsonify(scheduler.get_scheduler_status())
    return jsonify({"running": False, "error": "Scheduler not initialized"})

# n8n Automation API Endpoints (No CSRF required)
@app.route('/api/n8n/recommendations/trigger', methods=['POST'])
@limiter.limit("10 per hour")  # Rate limiting for automation
def n8n_trigger_ai_generation():
    """n8n automation endpoint to trigger AI generation"""
    try:
        global ai_scheduler
        if ai_scheduler:
            success = ai_scheduler.trigger_manual_generation()
            return jsonify({"status": "success", "triggered": success})
        else:
            return jsonify({"status": "error", "message": "AI scheduler not available"}), 500
    except Exception as e:
        logger.error(f"Error triggering AI generation from n8n: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/n8n/scheduler/trigger', methods=['POST'])
@limiter.limit("10 per hour")  # Rate limiting for automation
def n8n_trigger_manual_search():
    """n8n automation endpoint to trigger topic search"""
    try:
        global scheduler
        if scheduler:
            success = scheduler.trigger_manual_search()
            return jsonify({"status": "success", "triggered": success})
        else:
            return jsonify({"status": "error", "message": "Scheduler not available"}), 500
    except Exception as e:
        logger.error(f"Error triggering manual search from n8n: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/scheduler/trigger', methods=['POST'])
@csrf.exempt  # Allow API calls without CSRF for automation
def trigger_manual_search():
    """Manually trigger a topic search"""
    global scheduler
    if scheduler:
        success = scheduler.trigger_manual_search()
        return jsonify({"success": success})
    return jsonify({"success": False, "error": "Scheduler not initialized"})

# Twitter API v2 endpoints
@app.route('/api/twitter/search')
@limiter.limit("20 per minute")  # Rate limiting
def twitter_search():
    """Search tweets using Twitter API v2"""
    try:
        global twitter_api
        if not twitter_api:
            return jsonify({"error": "Twitter API not initialized"}), 503
        
        # Validate query parameter
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        # Sanitize query
        query = validate_and_sanitize_input(query, max_length=200, allowed_chars=r'^[a-zA-Z0-9\s\-_.,!?#@]+$')
        
        # Validate max_results parameter
        max_results = 10
        if 'max_results' in request.args:
            try:
                max_results = max(1, min(int(request.args.get('max_results')), 100))
            except ValueError:
                return jsonify({"error": "Invalid max_results parameter"}), 400
        
        # Search tweets
        tweets = twitter_api.search_recent_tweets(query, max_results)
        
        # Sanitize tweet data
        sanitized_tweets = []
        for tweet in tweets:
            sanitized_tweets.append({
                'id': tweet['id'],
                'text': validate_and_sanitize_input(tweet['text'], 500),
                'created_at': tweet.get('created_at'),
                'author_name': validate_and_sanitize_input(tweet.get('author_name', ''), 100),
                'author_username': validate_and_sanitize_input(tweet.get('author_username', ''), 50),
                'public_metrics': tweet.get('public_metrics', {}),
                'lang': tweet.get('lang', 'en')
            })
        
        return jsonify({
            'query': query,
            'tweets': sanitized_tweets,
            'count': len(sanitized_tweets)
        })
        
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error searching tweets: {e}")
        return jsonify({"error": "Failed to search tweets"}), 500

@app.route('/api/twitter/trending')
@limiter.limit("30 per minute")  # Rate limiting
def twitter_trending():
    """Get trending topics from Twitter"""
    try:
        global twitter_api
        if not twitter_api:
            return jsonify({"error": "Twitter API not initialized"}), 503
        
        # Validate parameters
        woeid = 1  # Worldwide trends
        if 'woeid' in request.args:
            try:
                woeid = int(request.args.get('woeid'))
            except ValueError:
                return jsonify({"error": "Invalid woeid parameter"}), 400
        
        limit = 20
        if 'limit' in request.args:
            try:
                limit = max(1, min(int(request.args.get('limit')), 50))
            except ValueError:
                return jsonify({"error": "Invalid limit parameter"}), 400
        
        # Get trending topics
        trends = twitter_api.get_trending_topics(woeid, limit)
        
        # Sanitize trend data
        sanitized_trends = []
        for trend in trends:
            sanitized_trends.append({
                'name': validate_and_sanitize_input(trend['name'], 200),
                'url': validate_and_sanitize_input(trend['url'], 500),
                'query': validate_and_sanitize_input(trend['query'], 200),
                'tweet_volume': trend.get('tweet_volume', 0),
                'promoted_content': trend.get('promoted_content')
            })
        
        return jsonify({
            'trends': sanitized_trends,
            'woeid': woeid,
            'count': len(sanitized_trends)
        })
        
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return jsonify({"error": "Failed to get trending topics"}), 500

@app.route('/api/twitter/analyze')
@limiter.limit("10 per minute")  # Rate limiting
def twitter_analyze():
    """Analyze trending topics related to AI and coding"""
    try:
        global twitter_api
        if not twitter_api:
            return jsonify({"error": "Twitter API not initialized"}), 503
        
        # Validate query parameter
        query = request.args.get('q', 'AI coding OR programming OR software development').strip()
        query = validate_and_sanitize_input(query, max_length=300, allowed_chars=r'^[a-zA-Z0-9\s\-_.,!?#@ORAND]+$')
        
        # Analyze trending topics
        trending_topics = twitter_api.analyze_trending_topics(query)
        
        # Sanitize results
        sanitized_topics = []
        for topic in trending_topics:
            sanitized_topics.append({
                'topic': validate_and_sanitize_input(topic['topic'], 200),
                'frequency': topic['frequency'],
                'engagement_score': float(topic['engagement_score']),
                'avg_engagement': float(topic['avg_engagement']),
                'tweets_count': topic['tweets_count'],
                'category': validate_and_sanitize_input(topic['category'], 50)
            })
        
        return jsonify({
            'query': query,
            'trending_topics': sanitized_topics,
            'count': len(sanitized_topics)
        })
        
    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error analyzing trending topics: {e}")
        return jsonify({"error": "Failed to analyze trending topics"}), 500

def initialize_search_manager():
    """Initialize the search manager"""
    global search_manager
    try:
        search_manager = SearchManager(enable_social=True, enable_trending=True, enable_ai=True)
        logger.info("Search manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search manager: {e}")

def initialize_ai_recommender():
    """Initialize the AI recommender and scheduler"""
    global ai_recommender, ai_scheduler
    try:
        ai_recommender = AIRecommender(storage)
        ai_scheduler = AISuggestionScheduler(ai_recommender)
        ai_scheduler.start()
        logger.info("AI recommender and scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI recommender: {e}")

def initialize_twitter_api():
    """Initialize the Twitter API v2 client"""
    global twitter_api
    try:
        twitter_api = TwitterAPIv2()
        logger.info("Twitter API v2 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twitter API: {e}")

def initialize_scheduler():
    """Initialize and start the topic search scheduler"""
    global scheduler
    try:
        # Scheduler configuration
        config = {
            'search_interval_hours': 4,
            'database_url': 'sqlite:///trending_data.db',
            'max_retries': 3,
            'retry_delay_minutes': 5,
            'cleanup_days': 30,
            'max_results_per_search': 50
        }

        scheduler = TopicSearchScheduler(config)
        scheduler.start()
        logger.info("Topic search scheduler initialized and started")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")

if __name__ == '__main__':
    # Initialize search manager and scheduler on startup
    initialize_search_manager()
    initialize_scheduler()
    initialize_ai_recommender()
    initialize_twitter_api()

    try:
        port = int(os.environ.get('PORT', 8080))
        debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    finally:
        # Stop schedulers on shutdown
        if scheduler:
            scheduler.stop()
        if ai_scheduler:
            ai_scheduler.stop()