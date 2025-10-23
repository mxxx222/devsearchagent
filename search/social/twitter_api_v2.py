#!/usr/bin/env python3
"""
Twitter API v2 integration based on official sample code
https://github.com/xdevplatform/Twitter-API-v2-sample-code.git
"""

import os
import requests
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class TwitterAPIv2:
    """Twitter API v2 client for trending topics and search"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not self.bearer_token:
            logger.warning("Twitter Bearer Token not found. Twitter API functionality will be limited.")
        
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        } if self.bearer_token else {}

    def bearer_oauth(self, r):
        """Method required by bearer token authentication"""
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2TweetLookupPython"
        return r

    def create_headers(self, bearer_token):
        """Create headers for API requests"""
        headers = {"Authorization": f"Bearer {bearer_token}"}
        return headers

    def connect_to_endpoint(self, url, headers, params=None):
        """Connect to Twitter API endpoint"""
        if not self.bearer_token:
            logger.error("No bearer token available for Twitter API")
            return None
            
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter API request failed: {e}")
            return None

    def get_trending_topics(self, woeid: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending topics for a specific location"""
        # Note: This uses Twitter API v1.1 for trends as v2 doesn't have trends endpoint
        url = f"https://api.twitter.com/1.1/trends/place.json?id={woeid}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                trends_data = response.json()
                if trends_data and len(trends_data) > 0:
                    trends = trends_data[0].get('trends', [])[:limit]
                    return [
                        {
                            'name': trend['name'],
                            'url': trend['url'],
                            'promoted_content': trend.get('promoted_content'),
                            'query': trend['query'],
                            'tweet_volume': trend.get('tweet_volume', 0)
                        }
                        for trend in trends
                    ]
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
        
        return []

    def search_recent_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for recent tweets using Twitter API v2"""
        if not self.bearer_token:
            logger.error("No bearer token available for Twitter API search")
            return []
        
        url = f"{self.base_url}/tweets/search/recent"
        params = {
            'query': query,
            'max_results': min(max_results, 100),  # API limit is 100
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'expansions': 'author_id'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                
                results = []
                for tweet in tweets:
                    author = users.get(tweet.get('author_id', ''), {})
                    results.append({
                        'id': tweet['id'],
                        'text': tweet['text'],
                        'created_at': tweet.get('created_at'),
                        'author_name': author.get('name', 'Unknown'),
                        'author_username': author.get('username', 'unknown'),
                        'public_metrics': tweet.get('public_metrics', {}),
                        'lang': tweet.get('lang', 'en')
                    })
                
                return results
            else:
                logger.error(f"Twitter API search failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
        
        return []

    def get_tweet_by_id(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tweet by ID using Twitter API v2"""
        if not self.bearer_token:
            logger.error("No bearer token available for Twitter API")
            return None
        
        url = f"{self.base_url}/tweets/{tweet_id}"
        params = {
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'expansions': 'author_id'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tweet = data.get('data', {})
                users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                
                if tweet:
                    author = users.get(tweet.get('author_id', ''), {})
                    return {
                        'id': tweet['id'],
                        'text': tweet['text'],
                        'created_at': tweet.get('created_at'),
                        'author_name': author.get('name', 'Unknown'),
                        'author_username': author.get('username', 'unknown'),
                        'public_metrics': tweet.get('public_metrics', {}),
                        'lang': tweet.get('lang', 'en')
                    }
        except Exception as e:
            logger.error(f"Error getting tweet {tweet_id}: {e}")
        
        return None

    def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get tweets from a specific user"""
        if not self.bearer_token:
            logger.error("No bearer token available for Twitter API")
            return []
        
        # First get user ID
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                
                results = []
                for tweet in tweets:
                    results.append({
                        'id': tweet['id'],
                        'text': tweet['text'],
                        'created_at': tweet.get('created_at'),
                        'public_metrics': tweet.get('public_metrics', {}),
                        'lang': tweet.get('lang', 'en')
                    })
                
                return results
            else:
                logger.error(f"Twitter API user tweets failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error getting user tweets: {e}")
        
        return []

    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username"""
        if not self.bearer_token:
            return None
        
        url = f"{self.base_url}/users/by/username/{username}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                user = data.get('data', {})
                return user.get('id')
            else:
                logger.error(f"Twitter API user lookup failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
        
        return None

    def analyze_trending_topics(self, query: str = "AI coding OR programming OR software development") -> List[Dict[str, Any]]:
        """Analyze trending topics related to coding and AI"""
        try:
            # Get recent tweets about the topic
            tweets = self.search_recent_tweets(query, max_results=50)
            
            if not tweets:
                return []
            
            # Analyze engagement metrics
            trending_topics = []
            topic_counts = {}
            
            for tweet in tweets:
                metrics = tweet.get('public_metrics', {})
                engagement_score = (
                    metrics.get('like_count', 0) +
                    metrics.get('retweet_count', 0) * 2 +
                    metrics.get('reply_count', 0) * 1.5 +
                    metrics.get('quote_count', 0) * 2.5
                )
                
                # Extract keywords from tweet text
                text = tweet['text'].lower()
                keywords = self._extract_keywords(text)
                
                for keyword in keywords:
                    if keyword not in topic_counts:
                        topic_counts[keyword] = {
                            'count': 0,
                            'total_engagement': 0,
                            'tweets': []
                        }
                    
                    topic_counts[keyword]['count'] += 1
                    topic_counts[keyword]['total_engagement'] += engagement_score
                    topic_counts[keyword]['tweets'].append(tweet)
            
            # Sort by engagement and frequency
            for keyword, data in topic_counts.items():
                if data['count'] >= 2:  # Only include topics mentioned multiple times
                    trending_topics.append({
                        'topic': keyword,
                        'frequency': data['count'],
                        'engagement_score': data['total_engagement'],
                        'avg_engagement': data['total_engagement'] / data['count'],
                        'tweets_count': len(data['tweets']),
                        'category': self._categorize_topic(keyword)
                    })
            
            # Sort by combined score (frequency * engagement)
            trending_topics.sort(key=lambda x: x['frequency'] * x['avg_engagement'], reverse=True)
            
            return trending_topics[:20]  # Return top 20 trending topics
            
        except Exception as e:
            logger.error(f"Error analyzing trending topics: {e}")
            return []

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from tweet text"""
        # Define relevant keywords for AI and coding
        keywords = [
            'ai coding', 'artificial intelligence', 'machine learning', 'deep learning',
            'python', 'javascript', 'java', 'typescript', 'react', 'vue', 'angular',
            'github', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'chatgpt', 'claude', 'copilot', 'bard', 'openai', 'anthropic',
            'coding', 'programming', 'software development', 'web development',
            'data science', 'data analysis', 'big data', 'analytics',
            'devops', 'cicd', 'automation', 'testing', 'agile', 'scrum'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic based on its content"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['ai', 'artificial', 'machine', 'deep', 'chatgpt', 'claude', 'copilot']):
            return 'AI/ML'
        elif any(word in topic_lower for word in ['python', 'javascript', 'java', 'typescript', 'react', 'vue', 'angular']):
            return 'Programming Languages'
        elif any(word in topic_lower for word in ['github', 'git', 'docker', 'kubernetes', 'devops', 'cicd']):
            return 'Development Tools'
        elif any(word in topic_lower for word in ['data', 'analytics', 'science', 'big data']):
            return 'Data Science'
        elif any(word in topic_lower for word in ['coding', 'programming', 'development', 'software']):
            return 'Software Development'
        else:
            return 'Technology'
