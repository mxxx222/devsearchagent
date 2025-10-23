# 🐦 X.com Social Media Integration

This project now includes comprehensive X.com (Twitter) social media integration for tracking trending topics in AI coding, software development, new programming languages, and free AI coding assistants.

## 🚀 Features

### 1. **X.com Trending Topics Detection**
- Real-time trending topics from X.com
- AI coding and software development focus
- Engagement scoring based on likes, shares, comments
- Time-based trend analysis (24h, monthly, yearly)

### 2. **AI Coding Trends Analysis**
- GitHub Copilot, ChatGPT, Claude, Bard tracking
- Free AI coding assistants monitoring
- AI pair programming trends
- AI code generation tools analysis

### computing3. **Software Development Trends**
- Programming language trends
- Framework popularity (React, Vue, Angular, etc.)
- DevOps and cloud computing trends
- New coding methodologies

### 4. **Social Media Analytics**
- Trending by engagement score
- Category-specific trending
- Related topics discovery
- Time pattern analysis

## 🛠️ Installation

### Prerequisites
```bash
# Install Chrome WebDriver (required for X.com scraping)
brew install chromedriver

# Or on Ubuntu/Debian
sudo apt-get install chromium-chromedriver
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file with your API keys:
```env
# Optional API keys (for enhanced functionality)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
BING_API_KEY=your_bing_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# X.com settings
X_USERNAME=pyyhkija
X_EMAIL=pyyhkija@gmail.com
```

## 🧪 Testing

### Basic Tests (No Web Scraping)
```bash
python simple_x_test.py
```

### Full Integration Tests
```bash
python test_x_integration.py
```

## 🌐 Web Interface

### Start the Web Interface
```bash
python x_trends_web_interface.py
```

Then open your browser to: `http://localhost:5000`

### Web Interface Features
- **Real-time trending topics** from X.com
- **AI coding trends** analysis
- **Software development trends** tracking
- **Free AI bot trends** monitoring
- **New programming language** trends
- **Top engagement trends** by clicks, likes, shares

## 📊 API Endpoints

The web interface provides these API endpoints:

- `/api/ai-coding-trends` - AI coding trends
- `/api/software-dev-trends` - Software development trends
- `/api/free-ai-trends` - Free AI bot trends
- `/api/new-lang-trends` - New programming language trends
- `/api/top-engagement-trends` - Top engagement trends
- `/api/stats` - Statistics overview

## 🔧 Usage Examples

### Python API Usage

```python
import asyncio
from search.manager import SearchManager

async def main():
    # Initialize search manager with X.com integration
    manager = SearchManager(enable_social=True)
    
    # Get AI coding trends
    ai_trends = await manager.get_ai_coding_trends()
    print(f"Found {len(ai_trends['ai_coding_trends'])} AI coding trends")
    
    # Get software development trends
    dev_trends = await manager.get_software_development_trends()
    print(f"Found {len(dev_trends['software_development_trends'])} dev trends")
    
    # Search with social media trends
    results = await manager.search_with_social_trends("AI coding")
    print(f"Search results: {len(results['search_results'].results)}")

asyncio.run(main())
```

### Direct X.com Components Usage

```python
from search.social.x_trending import XTrendingDetector
from search.social.x_analyzer import XTrendingAnalyzer

# Initialize components
detector = XTrendingDetector()
analyzer = XTrendingAnalyzer()

# Get trending topics
trending_topics = detector.get_trending_topics()

# Analyze AI coding trends
ai_trends = analyzer.analyze_ai_coding_trends()

# Get comprehensive analysis
comprehensive = analyzer.get_comprehensive_analysis()
```

## 📈 Trending Categories

### 1. **AI Coding** (`ai_coding`)
- GitHub Copilot, ChatGPT, Claude, Bard
- Free AI coding assistants
- AI pair programming tools
- AI code generation platforms

### 2. **Programming Languages** (`programming_languages`)
- Python, JavaScript, TypeScript, Go, Rust
- New and emerging languages
- Language popularity trends

### 3. **Frameworks** (`frameworks`)
- React, Vue, Angular, Django, Flask
- Framework adoption trends
- New framework releases

### 4. **DevOps** (`devops`)
- Docker, Kubernetes, AWS, Azure, GCP
- Cloud computing trends
- Infrastructure as Code

### 5. **Tools** (`tools`)
- GitHub, Git, API development
- Development tools and utilities
- IDE and editor trends

## 🎯 Key Features

### **Engagement Scoring**
- Based on likes, retweets, replies
- Trending direction (rising/falling/stable)
- Time-based pattern analysis

### **Smart Filtering**
- Coding-related content only
- AI and software development focus
- Multi-word phrase detection

### **Real-time Analysis**
- Live trending topics
- Historical trend comparison
- Related topics discovery

### **User-focused Monitoring**
- Monitors tech-focused X.com users
- Tracks @pyyhkija following list
- Analyzes user timeline trends

## 🔍 Search Integration

The X.com integration works seamlessly with the existing search functionality:

```python
# Search with social media trends
results = await manager.search_with_social_trends("AI coding")

# Results include:
# - search_results: Regular search results
# - social_trends: X.com trending topics
# - ai_recommendations: AI-powered recommendations
# - trending_analysis: Trend analysis
```

## 📝 Notes

- **No API Key Required**: X.com integration uses web scraping (no API key needed)
- **Chrome WebDriver Required**: For X.com web scraping functionality
- **Rate Limiting**: Respects X.com rate limits and terms of service
- **Privacy Focused**: Only analyzes public trending data

## 🚨 Important Notes

1. **Web Scraping**: This implementation uses web scraping to access X.com data
2. **Rate Limiting**: Please respect X.com's rate limits and terms of service
3. **Chrome WebDriver**: Required for web scraping functionality
4. **User Monitoring**: Monitors public profiles only (no private data)

## 🎉 Success!

Your Search Agent now has comprehensive X.com social media integration! You can:

- ✅ Track AI coding trends in real-time
- ✅ Monitor software development trends
- ✅ Analyze free AI coding assistant popularity
- ✅ Discover new programming language trends
- ✅ Get engagement-based trending insights
- ✅ View trends through a beautiful web interface

The system is ready to provide valuable insights into the AI coding and software development landscape on X.com!
