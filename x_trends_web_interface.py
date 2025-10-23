#!/usr/bin/env python3
"""
Web interface for X.com trending topics and social media integration
"""

import asyncio
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from search.manager import SearchManager
from search.social.x_trending import XTrendingDetector
from search.social.x_analyzer import XTrendingAnalyzer

app = Flask(__name__)

# Initialize components
search_manager = None
x_trending_detector = None
x_trending_analyzer = None

def initialize_components():
    """Initialize search manager and X.com components"""
    global search_manager, x_trending_detector, x_trending_analyzer
    
    try:
        search_manager = SearchManager(enable_social=True, enable_trending=False, enable_ai=False)
        x_trending_detector = XTrendingDetector()
        x_trending_analyzer = XTrendingAnalyzer()
        return True
    except Exception as e:
        print(f"Error initializing components: {e}")
        return False

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X.com Trending Topics - AI Coding & Software Development</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1da1f2;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
        }
        .section h2 {
            color: #14171a;
            margin-top: 0;
        }
        .trending-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #1da1f2;
        }
        .trending-item.ai-coding {
            border-left-color: #ff6b6b;
        }
        .trending-item.software-dev {
            border-left-color: #4ecdc4;
        }
        .trending-item.free-ai {
            border-left-color: #45b7d1;
        }
        .trending-item.new-lang {
            border-left-color: #96ceb4;
        }
        .topic-name {
            font-weight: bold;
            color: #14171a;
        }
        .topic-score {
            background-color: #1da1f2;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        .topic-category {
            font-size: 0.9em;
            color: #657786;
            margin-left: 10px;
        }
        .refresh-btn {
            background-color: #1da1f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 5px;
        }
        .refresh-btn:hover {
            background-color: #0d8bd9;
        }
        .loading {
            text-align: center;
            color: #657786;
            font-style: italic;
        }
        .error {
            color: #e0245e;
            background-color: #ffeaea;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #1da1f2;
        }
        .stat-label {
            color: #657786;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 X.com Trending Topics</h1>
        <p style="text-align: center; color: #657786;">Insights into AI Coding, Software Development, and Tech Trends</p>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-topics">-</div>
                <div class="stat-label">Total Topics</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="ai-topics">-</div>
                <div class="stat-label">AI Coding</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="dev-topics">-</div>
                <div class="stat-label">Software Dev</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="free-ai-topics">-</div>
                <div class="stat-label">Free AI Bots</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-bottom: 20px;">
            <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh All</button>
            <button class="refresh-btn" onclick="refreshAICoding()">🤖 AI Coding</button>
            <button class="refresh-btn" onclick="refreshSoftwareDev()">💻 Software Dev</button>
            <button class="refresh-btn" onclick="refreshFreeAI()">🆓 Free AI Bots</button>
        </div>
        
        <div class="section">
            <h2>🤖 AI Coding Trends</h2>
            <div id="ai-coding-trends" class="loading">Loading AI coding trends...</div>
        </div>
        
        <div class="section">
            <h2>💻 Software Development Trends</h2>
            <div id="software-dev-trends" class="loading">Loading software development trends...</div>
        </div>
        
        <div class="section">
            <h2>🆓 Free AI Coding Bots</h2>
            <div id="free-ai-trends" class="loading">Loading free AI bot trends...</div>
        </div>
        
        <div class="section">
            <h2>🆕 New Programming Languages</h2>
            <div id="new-lang-trends" class="loading">Loading new language trends...</div>
        </div>
        
        <div class="section">
            <h2>🔥 Top Engagement Trends</h2>
            <div id="top-engagement-trends" class="loading">Loading top engagement trends...</div>
        </div>
    </div>
    
    <script>
        function formatScore(score) {
            return (score * 100).toFixed(1) + '%';
        }
        
        function formatTrend(trend) {
            const icons = {
                'rising': '📈',
                'falling': '📉',
                'stable': '➡️'
            };
            return icons[trend] || '➡️';
        }
        
        function renderTrends(containerId, trends, categoryClass = '') {
            const container = document.getElementById(containerId);
            
            if (!trends || trends.length === 0) {
                container.innerHTML = '<div class="error">No trends found</div>';
                return;
            }
            
            const html = trends.map(trend => `
                <div class="trending-item ${categoryClass}">
                    <div>
                        <span class="topic-name">${trend.topic}</span>
                        <span class="topic-category">${trend.category}</span>
                        <span class="topic-category">${formatTrend(trend.engagement_trend)}</span>
                    </div>
                    <div class="topic-score">${formatScore(trend.score)}</div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }
        
        async function refreshAICoding() {
            const container = document.getElementById('ai-coding-trends');
            container.innerHTML = '<div class="loading">Loading AI coding trends...</div>';
            
            try {
                const response = await fetch('/api/ai-coding-trends');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    renderTrends('ai-coding-trends', data.trends, 'ai-coding');
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading AI coding trends: ${error.message}</div>`;
            }
        }
        
        async function refreshSoftwareDev() {
            const container = document.getElementById('software-dev-trends');
            container.innerHTML = '<div class="loading">Loading software development trends...</div>';
            
            try {
                const response = await fetch('/api/software-dev-trends');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    renderTrends('software-dev-trends', data.trends, 'software-dev');
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading software development trends: ${error.message}</div>`;
            }
        }
        
        async function refreshFreeAI() {
            const container = document.getElementById('free-ai-trends');
            container.innerHTML = '<div class="loading">Loading free AI bot trends...</div>';
            
            try {
                const response = await fetch('/api/free-ai-trends');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    renderTrends('free-ai-trends', data.trends, 'free-ai');
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading free AI bot trends: ${error.message}</div>`;
            }
        }
        
        async function refreshNewLanguages() {
            const container = document.getElementById('new-lang-trends');
            container.innerHTML = '<div class="loading">Loading new language trends...</div>';
            
            try {
                const response = await fetch('/api/new-lang-trends');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    renderTrends('new-lang-trends', data.trends, 'new-lang');
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading new language trends: ${error.message}</div>`;
            }
        }
        
        async function refreshTopEngagement() {
            const container = document.getElementById('top-engagement-trends');
            container.innerHTML = '<div class="loading">Loading top engagement trends...</div>';
            
            try {
                const response = await fetch('/api/top-engagement-trends');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    renderTrends('top-engagement-trends', data.trends, '');
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading top engagement trends: ${error.message}</div>`;
            }
        }
        
        async function refreshAll() {
            await Promise.all([
                refreshAICoding(),
                refreshSoftwareDev(),
                refreshFreeAI(),
                refreshNewLanguages(),
                refreshTopEngagement()
            ]);
            updateStats();
        }
        
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.total_topics !== undefined) {
                    document.getElementById('total-topics').textContent = data.total_topics;
                }
                if (data.ai_topics !== undefined) {
                    document.getElementById('ai-topics').textContent = data.ai_topics;
                }
                if (data.dev_topics !== undefined) {
                    document.getElementById('dev-topics').textContent = data.dev_topics;
                }
                if (data.free_ai_topics !== undefined) {
                    document.getElementById('free-ai-topics').textContent = data.free_ai_topics;
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        // Load initial data
        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ai-coding-trends')
async def api_ai_coding_trends():
    """API endpoint for AI coding trends"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        trends = x_trending_analyzer.analyze_ai_coding_trends()
        
        # Convert to JSON-serializable format
        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "score": trend.score,
                "category": trend.category,
                "engagement_trend": trend.engagement_trend,
                "related_topics": trend.related_topics
            })
        
        return jsonify({"trends": trends_data})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/software-dev-trends')
async def api_software_dev_trends():
    """API endpoint for software development trends"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        trends = x_trending_analyzer.analyze_software_development_trends()
        
        # Convert to JSON-serializable format
        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "score": trend.score,
                "category": trend.category,
                "engagement_trend": trend.engagement_trend,
                "related_topics": trend.related_topics
            })
        
        return jsonify({"trends": trends_data})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/free-ai-trends')
async def api_free_ai_trends():
    """API endpoint for free AI bot trends"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        trends = x_trending_analyzer.analyze_free_ai_bots_trends()
        
        # Convert to JSON-serializable format
        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "score": trend.score,
                "category": trend.category,
                "engagement_trend": trend.engagement_trend,
                "related_topics": trend.related_topics
            })
        
        return jsonify({"trends": trends_data})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/new-lang-trends')
async def api_new_lang_trends():
    """API endpoint for new programming language trends"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        trends = x_trending_analyzer.analyze_new_language_trends()
        
        # Convert to JSON-serializable format
        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "score": trend.score,
                "category": trend.category,
                "engagement_trend": trend.engagement_trend,
                "related_topics": trend.related_topics
            })
        
        return jsonify({"trends": trends_data})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/top-engagement-trends')
async def api_top_engagement_trends():
    """API endpoint for top engagement trends"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        trends = x_trending_analyzer.get_trending_by_engagement(15)
        
        # Convert to JSON-serializable format
        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "score": trend.score,
                "category": trend.category,
                "engagement_trend": trend.engagement_trend,
                "related_topics": trend.related_topics
            })
        
        return jsonify({"trends": trends_data})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stats')
async def api_stats():
    """API endpoint for statistics"""
    try:
        if not x_trending_analyzer:
            return jsonify({"error": "X.com analyzer not initialized"})
        
        # Get comprehensive analysis
        analysis = x_trending_analyzer.get_comprehensive_analysis()
        
        stats = {
            "total_topics": len(analysis.get("top_engagement", [])),
            "ai_topics": len(analysis.get("ai_coding", [])),
            "dev_topics": len(analysis.get("software_development", [])),
            "free_ai_topics": len(analysis.get("free_ai_bots", []))
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)})

def main():
    """Main function to run the web interface"""
    print("🚀 Starting X.com Trending Topics Web Interface...")
    
    # Initialize components
    if not initialize_components():
        print("❌ Failed to initialize components")
        return
    
    print("✅ Components initialized successfully")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("🐦 Explore X.com trending topics for AI coding and software development!")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
