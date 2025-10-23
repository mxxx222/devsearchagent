#!/usr/bin/env python3
"""
X.com (Twitter) trending topics detector for coding and software development
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

@dataclass
class XTrendingTopic:
    """X.com trending topic data"""
    topic: str
    tweet_count: int
    engagement_score: float  # Based on likes, retweets, replies
    category: str
    timestamp: datetime
    url: str
    hashtag: bool = False
    trending_rank: int = 0

@dataclass
class XTrendingData:
    """X.com trending data for analysis"""
    topic: str
    frequency: int
    engagement_score: float
    category: str
    timestamp: datetime
    source: str = "x.com"

class XTrendingDetector:
    """X.com trending topics detector for coding and software development"""
    
    def __init__(self):
        self.base_url = "https://x.com"
        self.trending_url = "https://x.com/explore/tabs/trending"
        self.coding_keywords = {
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'typescript',
            'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'nodejs', 'express', 'spring',
            'laravel', 'rails', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github',
            'linux', 'windows', 'macos', 'api', 'rest', 'graphql', 'microservices', 'devops',
            'ci/cd', 'testing', 'tdd', 'agile', 'scrum', 'machine learning', 'ai', 'data science',
            'blockchain', 'cryptocurrency', 'web3', 'iot', 'cybersecurity', 'cloud', 'serverless'
        }
        
        self.ai_coding_keywords = {
            'github copilot', 'chatgpt', 'claude', 'bard', 'copilot x',
            'tabnine', 'kite', 'codeium', 'amazon codewhisperer',
            'cursor ai', 'replit ghostwriter', 'openai codex',
            'free ai coding assistant', 'ai pair programming',
            'ai code generation', 'ai programming tools',
            'copilot alternative', 'ai coding free', 'github copilot free',
            'chatgpt coding', 'claude coding', 'ai code completion',
            'ai code review', 'ai debugging', 'ai refactoring',
            'ai test generation', 'ai documentation', 'ai code explainer',
            'ai programming assistant', 'ai development tools',
            'free coding ai', 'open source ai coding', 'ai coding tutor'
        }
        
        self.tech_users_to_monitor = [
            '@github', '@microsoft', '@google', '@openai', '@anthropicai',
            '@nvidia', '@awscloud', '@azure', '@docker', '@kubernetesio',
            '@reactjs', '@vuejs', '@angular', '@nodejs', '@python',
            '@javascript', '@typescript', '@golang', '@rustlang',
            '@stackoverflow', '@devdotto', '@hackernews', '@techcrunch',
            '@wired', '@theverge', '@ars_technica'
        ]

    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def get_trending_topics(self) -> List[XTrendingTopic]:
        """Get trending topics from X.com"""
        trending_topics = []
        
        try:
            driver = self._setup_driver()
            
            # Navigate to trending page
            driver.get(self.trending_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='trend']"))
            )
            
            # Find trending topics
            trending_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='trend']")
            
            for i, element in enumerate(trending_elements[:20]):  # Top 20 trending
                try:
                    topic_text = element.text
                    if topic_text:
                        topic = self._extract_topic_from_text(topic_text)
                        if topic and self._is_coding_related(topic):
                            trending_topic = XTrendingTopic(
                                topic=topic,
                                tweet_count=self._extract_tweet_count(topic_text),
                                engagement_score=self._calculate_engagement_score(topic_text),
                                category=self._categorize_topic(topic),
                                timestamp=datetime.now(),
                                url=f"{self.base_url}/search?q={topic.replace(' ', '%20')}",
                                hashtag=topic.startswith('#'),
                                trending_rank=i + 1
                            )
                            trending_topics.append(trending_topic)
                            
                except Exception as e:
                    logger.warning(f"Error processing trending element: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return trending_topics

    def get_user_timeline_trends(self, username: str = "pyyhkija") -> List[XTrendingTopic]:
        """Get trending topics from a specific user's timeline"""
        trending_topics = []
        
        try:
            driver = self._setup_driver()
            
            # Navigate to user profile
            profile_url = f"{self.base_url}/{username}"
            driver.get(profile_url)
            
            # Wait for timeline to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            # Get tweets from timeline
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            for element in tweet_elements[:10]:  # Analyze last 10 tweets
                try:
                    tweet_text = element.text
                    if tweet_text:
                        # Extract hashtags and mentions
                        hashtags = re.findall(r'#\w+', tweet_text)
                        mentions = re.findall(r'@\w+', tweet_text)
                        
                        for hashtag in hashtags:
                            if self._is_coding_related(hashtag):
                                trending_topic = XTrendingTopic(
                                    topic=hashtag,
                                    tweet_count=1,
                                    engagement_score=self._calculate_engagement_score(tweet_text),
                                    category=self._categorize_topic(hashtag),
                                    timestamp=datetime.now(),
                                    url=f"{self.base_url}/search?q={hashtag}",
                                    hashtag=True,
                                    trending_rank=0
                                )
                                trending_topics.append(trending_topic)
                                
                except Exception as e:
                    logger.warning(f"Error processing tweet: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error getting user timeline trends: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return trending_topics

    def search_coding_trends(self, query: str = "AI coding") -> List[XTrendingTopic]:
        """Search for coding-related trends on X.com"""
        trending_topics = []
        
        try:
            driver = self._setup_driver()
            
            # Search for the query
            search_url = f"{self.base_url}/search?q={query.replace(' ', '%20')}&src=trend_click"
            driver.get(search_url)
            
            # Wait for search results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            # Get trending tweets
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            for element in tweet_elements[:15]:  # Top 15 results
                try:
                    tweet_text = element.text
                    if tweet_text:
                        # Extract relevant keywords
                        keywords = self._extract_keywords_from_tweet(tweet_text)
                        for keyword in keywords:
                            if self._is_coding_related(keyword):
                                trending_topic = XTrendingTopic(
                                    topic=keyword,
                                    tweet_count=self._extract_tweet_count(tweet_text),
                                    engagement_score=self._calculate_engagement_score(tweet_text),
                                    category=self._categorize_topic(keyword),
                                    timestamp=datetime.now(),
                                    url=f"{self.base_url}/search?q={keyword.replace(' ', '%20')}",
                                    hashtag=keyword.startswith('#'),
                                    trending_rank=0
                                )
                                trending_topics.append(trending_topic)
                                
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error searching coding trends: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return trending_topics

    def _extract_topic_from_text(self, text: str) -> Optional[str]:
        """Extract topic from trending text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Extract hashtag or topic
        hashtag_match = re.search(r'#\w+', text)
        if hashtag_match:
            return hashtag_match.group()
        
        # Extract topic name (usually the first line)
        lines = text.split('\n')
        if lines:
            return lines[0].strip()
        
        return None

    def _extract_tweet_count(self, text: str) -> int:
        """Extract tweet count from trending text"""
        # Look for patterns like "10.2K Tweets", "1,234 Tweets"
        tweet_match = re.search(r'([\d,\.]+[KMB]?)\s*Tweets?', text, re.IGNORECASE)
        if tweet_match:
            count_str = tweet_match.group(1)
            return self._parse_count(count_str)
        return 0

    def _parse_count(self, count_str: str) -> int:
        """Parse count string to integer"""
        count_str = count_str.replace(',', '')
        if count_str.endswith('K'):
            return int(float(count_str[:-1]) * 1000)
        elif count_str.endswith('M'):
            return int(float(count_str[:-1]) * 1000000)
        elif count_str.endswith('B'):
            return int(float(count_str[:-1]) * 1000000000)
        else:
            return int(count_str)

    def _calculate_engagement_score(self, text: str) -> float:
        """Calculate engagement score based on likes, retweets, replies"""
        # This is a simplified calculation
        # In a real implementation, you'd parse the actual engagement metrics
        
        # Look for engagement indicators in text
        score = 0.0
        
        # Check for high tweet counts (indicates high engagement)
        tweet_count = self._extract_tweet_count(text)
        if tweet_count > 0:
            score += min(tweet_count / 1000.0, 1.0)  # Normalize to 0-1
        
        # Check for trending indicators
        if 'trending' in text.lower():
            score += 0.3
        
        if 'viral' in text.lower():
            score += 0.5
        
        return min(score, 1.0)

    def _is_coding_related(self, topic: str) -> bool:
        """Check if topic is coding/software development related"""
        topic_lower = topic.lower()
        
        # Check against coding keywords
        for keyword in self.coding_keywords:
            if keyword in topic_lower:
                return True
        
        # Check against AI coding keywords
        for keyword in self.ai_coding_keywords:
            if keyword in topic_lower:
                return True
        
        # Check for common coding patterns
        coding_patterns = [
            r'\b(code|coding|programming|development|software|tech|ai|ml)\b',
            r'\b(python|java|javascript|typescript|go|rust|c\+\+|c#)\b',
            r'\b(react|vue|angular|node|docker|kubernetes|aws|azure)\b',
            r'\b(github|git|api|rest|graphql|microservices)\b'
        ]
        
        for pattern in coding_patterns:
            if re.search(pattern, topic_lower):
                return True
        
        return False

    def _categorize_topic(self, topic: str) -> str:
        """Categorize topic into specific categories"""
        topic_lower = topic.lower()
        
        if any(keyword in topic_lower for keyword in self.ai_coding_keywords):
            return "ai_coding"
        elif any(keyword in topic_lower for keyword in ['python', 'java', 'javascript', 'typescript', 'go', 'rust']):
            return "programming_languages"
        elif any(keyword in topic_lower for keyword in ['react', 'vue', 'angular', 'django', 'flask']):
            return "frameworks"
        elif any(keyword in topic_lower for keyword in ['docker', 'kubernetes', 'aws', 'azure', 'gcp']):
            return "devops"
        elif any(keyword in topic_lower for keyword in ['github', 'git', 'api', 'rest', 'graphql']):
            return "tools"
        else:
            return "general_coding"

    def _extract_keywords_from_tweet(self, tweet_text: str) -> List[str]:
        """Extract relevant keywords from tweet text"""
        keywords = []
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', tweet_text)
        keywords.extend(hashtags)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', tweet_text)
        keywords.extend(mentions)
        
        # Extract potential keywords
        words = re.findall(r'\b\w+\b', tweet_text.lower())
        for word in words:
            if len(word) > 3 and word in self.coding_keywords:
                keywords.append(word)
        
        return keywords

    def get_trending_data(self) -> List[XTrendingData]:
        """Get trending data for analysis"""
        trending_topics = self.get_trending_topics()
        
        # Also get user timeline trends
        user_trends = self.get_user_timeline_trends()
        trending_topics.extend(user_trends)
        
        # Also search for specific coding trends
        coding_trends = self.search_coding_trends("AI coding")
        trending_topics.extend(coding_trends)
        
        # Convert to trending data
        trending_data = []
        for topic in trending_topics:
            trending_data.append(XTrendingData(
                topic=topic.topic,
                frequency=topic.tweet_count,
                engagement_score=topic.engagement_score,
                category=topic.category,
                timestamp=topic.timestamp,
                source="x.com"
            ))
        
        return trending_data
