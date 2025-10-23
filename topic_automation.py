#!/usr/bin/env python3
"""
Topic Automation Script - Alternative to n8n for 4h Updates
Runs every 4 hours to update topics and send notifications
"""

import os
import sys
import time
import json
import requests
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('topic_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TopicAutomation:
    """Automated topic discovery and notification system"""
    
    def __init__(self, base_url: str = "http://localhost:8080", n8n_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.n8n_url = n8n_url
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Load remediation from config
        self.load_config()
        
    def load_config(self):
        """Load configuration from environment variables"""
        try:
            with open('config.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load config.env: {e}")
    
    def trigger_ai_generation(self) -> bool:
        """Trigger AI recommendation generation"""
        try:
            response = self.session.post(
                f"{self.n8n_url}/api/n8n/recommendations/trigger",
                json={"source": "automation_script"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info("✅ AI generation triggered successfully")
                return True
            else:
                logger.error(f"❌ AI generation failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error triggering AI generation: {e}")
            return False
    
    def analyze_twitter_trends(self) -> Dict:
        """Analyze Twitter trends for AI and coding topics"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/twitter/analyze",
                params={"q": "AI coding OR programming OR software development OR machine learning"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Twitter trends analyzed: {data.get('count', 0)} topics found")
                return data
            else:
                logger.error(f"❌ Twitter analysis failed: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error analyzing Twitter trends: {e}")
            return {}
    
    def trigger_topic_search(self) -> bool:
        """Trigger manual topic search"""
        try:
            response = self.session.post(
                f"{self.n8n_url}/api/n8n/scheduler/trigger",
                json={"topics": "AI coding,programming,software development,machine learning,artificial intelligence"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info("✅ Topic search triggered successfully")
                return True
            else:
                logger.error(f"❌ Topic search failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error triggering topic search: {e}")
            return False
    
    def get_new_topics(self) -> Dict:
        """Get latest AI recommendations and trending topics"""
        try:
            # Get AI recommendations
            recommendations_response = self.session.get(
                f"{self.base_url}/api/recommendations",
                params={"limit": 20, "source": "all"}
            )
            
            # Get trending topics
            trending_response = self.session.get(
                f"{self.base_url}/api/trending",
                params={"limit": 10}
            )
            
            recommendations = {}
            trending = {}
            
            if recommendations_response.status_code == 200:
                recommendations = recommendations_response.json()
                logger.info(f"✅ Retrieved {len(recommendations.get('recommendations', []))} AI recommendations")
            
            if trending_response.status_code == 200:
                trending = trending_response.json()
                logger.info(f"✅ Retrieved {len(trending.get('trending', []))} trending topics")
            
            return {
                "recommendations": recommendations,
                "trending": trending,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting new topics: {e}")
            return {}
    
    def search_twitter_tweets(self) -> Dict:
        """Search for relevant Twitter tweets"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/twitter/search",
                params={"q": "AI coding tools", "max_results": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved {data.get('count', 0)} Twitter tweets")
                return data
            else:
                logger.error(f"❌ Twitter search failed: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error searching Twitter tweets: {e}")
            return {}
    
    def process_topics_data(self, topics_data: Dict, twitter_data: Dict) -> Dict:
        """Process and format the topics data"""
        try:
            recommendations = topics_data.get("recommendations", {}).get("recommendations", [])
            trending = topics_data.get("trending", {}).get("trending", [])
            
            # Format topics for notification
            formatted_topics = []
            
            # Add AI recommendations
            for i, rec in enumerate(recommendations[:5]):
                formatted_topics.append({
                    "type": "AI Recommendation",
                    "topic": rec.get("topic", rec.get("query", "Unknown")),
                    "confidence": rec.get("confidence", 0),
                    "source": rec.get("source", "AI"),
                    "rank": i + 1
                })
            
            # Add trending topics
            for i, trend in enumerate(trending[:5]):
                formatted_topics.append({
                    "type": "Trending",
                    "topic": trend.get("topic", trend.get("name", "Unknown")),
                    "score": trend.get("score", trend.get("frequency", 0)),
                    "source": trend.get("source", "Trending"),
                    "rank": i + 1
                })
            
            # Create summary
            summary = {
                "timestamp": topics_data.get("timestamp", datetime.now().isoformat()),
                "totalTopics": len(formatted_topics),
                "aiRecommendations": len(recommendations),
                "trendingTopics": len(trending),
                "twitterTweets": twitter_data.get("count", 0),
                "topics": formatted_topics
            }
            
            logger.info(f"✅ Processed {summary['totalTopics']} topics")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error processing topics data: {e}")
            return {}
    
    def send_slack_notification(self, summary: Dict) -> bool:
        """Send notification to Slack (if webhook configured)"""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logger.info("ℹ️ Slack webhook not configured, skipping Slack notification")
            return True
        
        try:
            # Format message
            topics_text = "\n".join([
                f"{i+1}. {topic['topic']} ({topic['type']})"
                for i, topic in enumerate(summary.get("topics", [])[:5])
            ])
            
            message = {
                "text": f"🔄 New Topics Update (4h)\n\n📊 Summary:\n- Total Topics: {summary['totalTopics']}\n- AI Recommendations: {summary['aiRecommendations']}\n- Trending Topics: {summary['trendingTopics']}\n- Twitter Tweets: {summary['twitterTweets']}\n\n🔥 Top Topics:\n{topics_text}\n\n⏰ Updated: {summary['timestamp']}",
                "username": "TopicBot",
                "icon_emoji": ":robot_face:"
            }
            
            response = requests.post(webhook_url, json=message, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Slack notification sent successfully")
                return True
            else:
                logger.error(f"❌ Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending Slack notification: {e}")
            return False
    
    def send_email_notification(self, summary: Dict) -> bool:
        """Send email notification (if SMTP configured)"""
        smtp_host = os.getenv("SMTP_HOST")
        if not smtp_host:
            logger.info("ℹ️ SMTP not configured, skipping email notification")
            return True
        
        try:
            # Generate HTML content
            html_content = self.generate_email_html(summary)
            
            # Send email using your preferred email service
            # This is a placeholder - implement with your email service
            logger.info("📧 Email notification would be sent here")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email notification: {e}")
            return False
    
    def generate_email_html(self, summary: Dict) -> str:
        """Generate HTML email content"""
        topics_html = ""
        for i, topic in enumerate(summary.get("topics", [])[:10]):
            topic_type_class = "ai-topic" if topic["type"] == "AI Recommendation" else "trending-topic"
            topics_html += f"""
            <div class="topic {topic_type_class}">
                <strong>{i+1}. {topic['topic']}</strong>
                <br><small>Type: {topic['type']} | Source: {topic['source']}</small>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .topic {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007acc; }}
                .ai-topic {{ border-left-color: #28a745; }}
                .trending-topic {{ border-left-color: #ffc107; }}
                .stats {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI Search Dashboard - 4h Update</h1>
                <p>Automated topic discovery and trending analysis</p>
            </div>
            
            <div class="stats">
                <h3>📊 Statistics</h3>
                <ul>
                    <li>Total Topics: {summary['totalTopics']}</li>
                    <li>AI Recommendations: {summary['aiRecommendations']}</li>
                    <li>Trending Topics: {summary['trendingTopics']}</li>
                    <li>Twitter Tweets: {summary['twitterTweets']}</li>
                    <li>Last Updated: {datetime.fromisoformat(summary['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
            </div>
            
            <h3>🔥 Top Topics</h3>
            {topics_html}
            
            <hr>
            <p><small>Generated by automation script at {datetime.now().isoformat()}</small></p>
        </body>
        </html>
        """
    
    def save_to_database(self, summary: Dict) -> bool:
        """Save results to database (if configured)"""
        try:
            # This is a placeholder - implement with your database
            logger.info(f"💾 Would save {summary['totalTopics']} topics to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            return False
    
    def log_execution(self, summary: Dict) -> bool:
        """Log the automation execution"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "automation": "4h_topic_updates",
                "status": "completed",
                "totalTopics": summary.get("totalTopics", 0),
                "aiRecommendations": summary.get("aiRecommendations", 0),
                "trendingTopics": summary.get("trendingTopics", 0),
                "twitterTweets": summary.get("twitterTweets", 0)
            }
            
            # Save to log file
            with open("automation_log.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.info(f"📝 Execution logged: {log_entry}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error logging execution: {e}")
            return False
    
    def run_automation(self):
        """Run the complete automation process"""
        logger.info("🚀 Starting 4h topic automation...")
        start_time = time.time()
        
        try:
            # Step 1: Trigger AI generation
            ai_success = self.trigger_ai_generation()
            
            # Step 2: Analyze Twitter trends
            twitter_trends = self.analyze_twitter_trends()
            
            # Step 3: Trigger topic search
            search_success = self.trigger_topic_search()
            
            # Wait a moment for processing
            time.sleep(5)
            
            # Step 4: Get new topics
            topics_data = self.get_new_topics()
            
            # Step 5: Search Twitter tweets
            twitter_tweets = self.search_twitter_tweets()
            
            # Step 6: Process data
            summary = self.process_topics_data(topics_data, twitter_tweets)
            
            if not summary:
                logger.error("❌ No data to process")
                return False
            
            # Step 7: Send notifications
            slack_success = self.send_slack_notification(summary)
            email_success = self.send_email_notification(summary)
            
            # Step 8: Save to database
            db_success = self.save_to_database(summary)
            
            # Step 9: Log execution
            log_success = self.log_execution(summary)
            
            # Summary
            execution_time = time.time() - start_time
            logger.info(f"✅ Automation completed in {execution_time:.2f} seconds")
            logger.info(f"📊 Results: {summary['totalTopics']} topics, {summary['aiRecommendations']} AI recs, {summary['trendingTopics']} trending")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            return False
    
    def run_once(self):
        """Run automation once (for testing)"""
        logger.info("🧪 Running automation once for testing...")
        return self.run_automation()
    
    def start_scheduler(self):
        """Start the automation scheduler"""
        logger.info("⏰ Starting automation scheduler...")
        
        # Schedule to run every 4 hours
        schedule.every(4).hours.do(self.run_automation)
        
        # Also run immediately
        self.run_automation()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Topic Automation Script")
    parser.add_argument("--once", action="store_true", help="Run once instead of scheduling")
    parser.add_argument("--base-url", default="http://localhost:8080", help="Base URL for API")
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = TopicAutomation(base_url=args.base_url)
    
    if args.once:
        # Run once for testing
        success = automation.run_once()
        sys.exit(0 if success else 1)
    else:
        # Start scheduler
        try:
            automation.start_scheduler()
        except KeyboardInterrupt:
            logger.info("🛑 Automation stopped by user")
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
