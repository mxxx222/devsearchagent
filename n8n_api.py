#!/usr/bin/env python3
"""
Dedicated API endpoints for n8n automation
This file provides simple API endpoints that n8n can call without CSRF tokens
"""

from flask import Flask, jsonify, request
import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app components
try:
    from search.manager import SearchManager
    from search.trending.storage import TrendingStorage
    from search.config import Config
except ImportError as e:
    print(f"Warning: Could not import search components: {e}")

app = Flask(__name__)

# Simple in-memory storage for demo purposes
automation_logs = []

@app.route('/api/n8n/recommendations/trigger', methods=['POST'])
def n8n_trigger_ai_generation():
    """n8n automation endpoint to trigger AI generation"""
    try:
        # Simple mock response for now
        result = {
            "status": "success",
            "triggered": True,
            "timestamp": "2025-10-23T08:50:00Z",
            "message": "AI generation triggered successfully"
        }
        
        # Log the request
        automation_logs.append({
            "endpoint": "ai_generation",
            "timestamp": result["timestamp"],
            "status": "success"
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": "2025-10-23T08:50:00Z"
        }), 500

@app.route('/api/n8n/scheduler/trigger', methods=['POST'])
def n8n_trigger_manual_search():
    """n8n automation endpoint to trigger topic search"""
    try:
        # Simple mock response for now
        result = {
            "status": "success",
            "triggered": True,
            "timestamp": "2025-10-23T08:50:00Z",
            "message": "Topic search triggered successfully"
        }
        
        # Log the request
        automation_logs.append({
            "endpoint": "topic_search",
            "timestamp": result["timestamp"],
            "status": "success"
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": "2025-10-23T08:50:00Z"
        }), 500

@app.route('/api/n8n/recommendations', methods=['GET'])
def n8n_get_recommendations():
    """n8n automation endpoint to get AI recommendations"""
    try:
        # Mock recommendations for n8n
        recommendations = [
            {
                "topic": "AI Coding Tools",
                "confidence": 0.95,
                "source": "n8n_automation",
                "timestamp": "2025-10-23T08:50:00Z"
            },
            {
                "topic": "Software Development Trends",
                "confidence": 0.88,
                "source": "n8n_automation",
                "timestamp": "2025-10-23T08:50:00Z"
            },
            {
                "topic": "Programming Best Practices",
                "confidence": 0.82,
                "source": "n8n_automation",
                "timestamp": "2025-10-23T08:50:00Z"
            }
        ]
        
        return jsonify({
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": "2025-10-23T08:50:00Z"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": "2025-10-23T08:50:00Z"
        }), 500

@app.route('/api/n8n/trending', methods=['GET'])
def n8n_get_trending():
    """n8n automation endpoint to get trending topics"""
    try:
        # Mock trending topics for n8n
        trending_topics = [
            {
                "topic": "AI Coding",
                "score": 0.95,
                "category": "AI",
                "timestamp": "2025-10-23T08:50:00Z"
            },
            {
                "topic": "Software Development",
                "score": 0.88,
                "category": "Development",
                "timestamp": "2025-10-23T08:50:00Z"
            },
            {
                "topic": "Programming Tools",
                "score": 0.82,
                "category": "Tools",
                "timestamp": "2025-10-23T08:50:00Z"
            }
        ]
        
        return jsonify({
            "status": "success",
            "trending_topics": trending_topics,
            "count": len(trending_topics),
            "timestamp": "2025-10-23T08:50:00Z"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": "2025-10-23T08:50:00Z"
        }), 500

@app.route('/api/n8n/logs', methods=['GET'])
def n8n_get_logs():
    """n8n automation endpoint to get automation logs"""
    try:
        return jsonify({
            "status": "success",
            "logs": automation_logs,
            "count": len(automation_logs),
            "timestamp": "2025-10-23T08:50:00Z"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": "2025-10-23T08:50:00Z"
        }), 500

@app.route('/api/n8n/health', methods=['GET'])
def n8n_health_check():
    """n8n automation endpoint for health check"""
    return jsonify({
        "status": "healthy",
        "service": "n8n_api",
        "timestamp": "2025-10-23T08:50:00Z"
    })

if __name__ == '__main__':
    print("🚀 Starting n8n API server...")
    print("📡 Available endpoints:")
    print("   POST /api/n8n/recommendations/trigger")
    print("   POST /api/n8n/scheduler/trigger")
    print("   GET  /api/n8n/recommendations")
    print("   GET  /api/n8n/trending")
    print("   GET  /api/n8n/logs")
    print("   GET  /api/n8n/health")
    print("🌐 Server will run on http://localhost:8081")
    
    app.run(host='0.0.0.0', port=8081, debug=True)
