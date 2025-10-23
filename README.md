# 🔍 DevSearchAgent

**AI-powered search dashboard for trending topics, coding trends, and automated recommendations**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 **Features**

### 🔍 **Search & Analytics**
- **Multi-Engine Search**: Google Custom Search, DuckDuckGo, Bing
- **AI-Powered Recommendations**: OpenAI GPT & Google Gemini integration
- **Real-time Trending Detection**: AI coding trends, software development news
- **Social Media Integration**: X.com (Twitter) trending topics

### 🤖 **AI & Automation**
- **Smart Recommendations**: AI-generated topic suggestions
- **Automated Scheduling**: 4-hour topic updates with n8n integration
- **Trend Analysis**: Time-based trending (daily, monthly, yearly)
- **Engagement Tracking**: Likes, shares, comments analytics

### 🌐 **Web Interface**
- **Modern Dashboard**: Responsive design with real-time updates
- **Interactive Charts**: Scalable diagrams and trend visualizations
- **AI Recommendations Sidebar**: Filter by source (OpenAI/Gemini)
- **New Topics Widget**: 4-hour update cycle with manual refresh

### 🔧 **Technical Features**
- **RESTful API**: Comprehensive API endpoints
- **Security**: CSRF protection, rate limiting, input validation
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **Automation**: n8n workflow integration + Python automation scripts

## 📋 **Quick Start**

### **Prerequisites**
- Python 3.13+
- Node.js 18+ (for n8n)
- Git

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/devsearchagent.git
cd devsearchagent
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp config.env.example config.env
# Edit config.env with your API keys
```

4. **Set up Node.js dependencies**
```bash
npm install
```

5. **Run the application**
```bash
# Start Flask app
npm run start

# Start n8n (in another terminal)
npm run n8n

# Start automation (optional)
npm run automation
```

## 🔑 **API Keys Setup**

### **Required APIs**
- **Google Custom Search API**: For web search results
- **Google Gemini API**: For AI recommendations
- **OpenAI API**: For AI recommendations (optional)

### **Optional APIs**
- **Twitter API v2**: For enhanced social media integration
- **Slack Webhook**: For notifications
- **SMTP**: For email notifications

## 🌐 **Usage**

### **Web Interface**
- **Main Dashboard**: `http://localhost:8080`
- **n8n Automation**: `http://localhost:5678`
- **n8n API Server**: `http://localhost:8081`

### **API Endpoints**
- **Search**: `POST /api/search`
- **Recommendations**: `GET /api/recommendations`
- **Trending**: `GET /api/trending`
- **Twitter**: `GET /api/twitter/analyze`
- **Automation**: `POST /api/n8n/recommendations/trigger`

## 🛠️ **Architecture**

```
devsearchagent/
├── search/                 # Core search engine
│   ├── engines/           # Search engine implementations
│   ├── trending/          # Trending detection & storage
│   └── social/            # Social media integration
├── templates/             # HTML templates
├── static/                # CSS, JS, assets
├── app.py                 # Main Flask application
├── n8n_api.py            # n8n automation API server
├── topic_automation.py   # Python automation script
└── requirements.txt      # Python dependencies
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
PORT=8080

# API Keys
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=sqlite:///trending_data.db

# Security
SECRET_KEY=your_secret_key
WTF_CSRF_ENABLED=true
```

## 📊 **Features Overview**

| Feature | Status | Description |
|---------|--------|-------------|
| 🔍 Multi-Engine Search | ✅ | Google, DuckDuckGo, Bing integration |
| 🤖 AI Recommendations | ✅ | OpenAI & Gemini powered suggestions |
| 📈 Trending Detection | ✅ | Real-time trend analysis |
| 🐦 Social Media | ✅ | X.com trending topics |
| 🔄 Automation | ✅ | n8n + Python automation |
| 🌐 Web Dashboard | ✅ | Modern responsive interface |
| 🔒 Security | ✅ | CSRF, rate limiting, validation |
| 📱 Mobile Support | ✅ | Responsive design |

## 🚀 **Deployment**

### **Development**
```bash
npm run dev
```

### **Production**
```bash
npm run start
```

### **Docker** (Coming Soon)
```bash
docker-compose up -d
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI** for GPT API
- **Google** for Gemini API and Custom Search
- **n8n** for workflow automation
- **Flask** for the web framework
- **Chart.js** for visualizations

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/yourusername/devsearchagent/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/devsearchagent/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/devsearchagent/discussions)

---

**Made with ❤️ for developers by developers**