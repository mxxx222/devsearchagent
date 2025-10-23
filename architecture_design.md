# Engagement Metrics Architecture Design

## Overview
This document outlines the architecture for displaying top comments, likes, or shares by day, month, and year. The system extends existing trending topic models to include detailed engagement metrics with time-series analysis capabilities.

## Data Models

### Extended TopicSearchResult Model
```python
@dataclass
class TopicSearchResult(Base):
    """Database model for topic search results with engagement metrics"""
    __tablename__ = 'topic_search_results'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic: str = Column(String(500), nullable=False, index=True)
    category: str = Column(String(100), nullable=False, index=True)
    score: float = Column(Float, nullable=False)
    engagement_score: float = Column(Float, nullable=False)

    # Engagement metrics with timestamps
    likes_count: int = Column(Integer, default=0)
    shares_count: int = Column(Integer, default=0)
    comments_count: int = Column(Integer, default=0)
    engagement_timestamp: datetime = Column(DateTime, nullable=False, index=True)

    # Aggregated metrics for time periods
    daily_likes: int = Column(Integer, default=0)
    daily_shares: int = Column(Integer, default=0)
    daily_comments: int = Column(Integer, default=0)
    monthly_likes: int = Column(Integer, default=0)
    monthly_shares: int = Column(Integer, default=0)
    monthly_comments: int = Column(Integer, default=0)
    yearly_likes: int = Column(Integer, default=0)
    yearly_shares: int = Column(Integer, default=0)
    yearly_comments: int = Column(Integer, default=0)

    frequency: int = Column(Integer, default=0)
    engagement_trend: str = Column(String(50), default='stable')
    time_analysis: str = Column(Text, nullable=True)  # JSON string
    related_topics: str = Column(Text, nullable=True)  # JSON string
    source: str = Column(String(100), default='x.com')
    search_timestamp: datetime = Column(DateTime, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

### EngagementMetrics Model
```python
@dataclass
class EngagementMetrics(Base):
    """Detailed engagement metrics for time-series analysis"""
    __tablename__ = 'engagement_metrics'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic_id: int = Column(Integer, ForeignKey('topic_search_results.id'), nullable=False)
    metric_type: str = Column(String(50), nullable=False)  # 'likes', 'shares', 'comments'
    count: int = Column(Integer, default=0)
    timestamp: datetime = Column(DateTime, nullable=False, index=True)
    period: str = Column(String(20), nullable=False)  # 'hourly', 'daily', 'monthly', 'yearly'
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_topic_metric_timestamp', 'topic_id', 'metric_type', 'timestamp'),
        Index('idx_period_timestamp', 'period', 'timestamp'),
    )
```

### EngagementSummary Model
```python
@dataclass
class EngagementSummary(Base):
    """Pre-computed summaries for fast dashboard queries"""
    __tablename__ = 'engagement_summaries'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    topic: str = Column(String(500), nullable=False, index=True)
    category: str = Column(String(100), nullable=False, index=True)
    period: str = Column(String(20), nullable=False)  # 'daily', 'monthly', 'yearly'
    period_start: datetime = Column(DateTime, nullable=False, index=True)
    period_end: datetime = Column(DateTime, nullable=False)

    total_likes: int = Column(Integer, default=0)
    total_shares: int = Column(Integer, default=0)
    total_comments: int = Column(Integer, default=0)
    avg_engagement_score: float = Column(Float, default=0.0)
    peak_engagement_time: datetime = Column(DateTime, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_topic_period', 'topic', 'period'),
        Index('idx_category_period', 'category', 'period'),
        Index('idx_period_range', 'period', 'period_start', 'period_end'),
    )
```

## Time-Series Aggregation Functions

### Aggregation Service
```python
class EngagementAggregationService:
    """Service for aggregating engagement metrics across time periods"""

    def __init__(self, storage: TrendingStorage):
        self.storage = storage

    def aggregate_daily_metrics(self, date: datetime) -> int:
        """Aggregate engagement metrics for a specific day"""
        # Implementation for daily aggregation

    def aggregate_monthly_metrics(self, year: int, month: int) -> int:
        """Aggregate engagement metrics for a specific month"""

    def aggregate_yearly_metrics(self, year: int) -> int:
        """Aggregate engagement metrics for a specific year"""

    def update_topic_engagement_summary(self, topic_id: int) -> bool:
        """Update pre-computed engagement summary for a topic"""

    def batch_update_summaries(self, period: str, start_date: datetime, end_date: datetime) -> int:
        """Batch update engagement summaries for a date range"""
```

### Aggregation Functions
```python
def calculate_daily_engagement(topic: str, date: datetime) -> Dict[str, int]:
    """Calculate daily engagement metrics for a topic"""

def calculate_monthly_engagement(topic: str, year: int, month: int) -> Dict[str, int]:
    """Calculate monthly engagement metrics for a topic"""

def calculate_yearly_engagement(topic: str, year: int) -> Dict[str, int]:
    """Calculate yearly engagement metrics for a topic"""

def get_top_engaged_topics_by_period(
    period: str,
    limit: int = 10,
    metric: str = 'likes'  # 'likes', 'shares', 'comments'
) -> List[Dict]:
    """Get top topics by engagement metric for a time period"""
```

## API Endpoints

### Engagement Data Endpoints
```
GET /api/engagement/topics/{topic_id}/metrics
- Query parameters: period (daily/monthly/yearly), start_date, end_date
- Returns: Time-series engagement data for a specific topic

GET /api/engagement/topics/top
- Query parameters: period, metric (likes/shares/comments), limit, category
- Returns: Top topics by engagement metric for the specified period

GET /api/engagement/categories/{category}/trends
- Query parameters: period, start_date, end_date
- Returns: Engagement trends for all topics in a category

GET /api/engagement/summary
- Query parameters: period, date
- Returns: Overall engagement summary for the specified period

POST /api/engagement/aggregate
- Body: {"period": "daily", "date": "2025-01-01"}
- Triggers manual aggregation for specified period
```

### Response Formats
```json
{
  "topic": "AI Development",
  "period": "daily",
  "data": [
    {
      "date": "2025-01-01",
      "likes": 1250,
      "shares": 340,
      "comments": 89,
      "engagement_score": 85.5
    },
    {
      "date": "2025-01-02",
      "likes": 1380,
      "shares": 395,
      "comments": 102,
      "engagement_score": 88.2
    }
  ]
}
```

## Dashboard Components

### EngagementTrendChart Component
```javascript
class EngagementTrendChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      period: 'daily',
      metric: 'likes',
      loading: false
    };
  }

  componentDidMount() {
    this.loadEngagementData();
  }

  loadEngagementData() {
    // Fetch engagement data from API
  }

  render() {
    // Render line chart with engagement trends
  }
}
```

### TopEngagedTopicsWidget Component
```javascript
class TopEngagedTopicsWidget extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      topics: [],
      period: 'monthly',
      metric: 'likes',
      limit: 10
    };
  }

  render() {
    // Render ranked list of top engaged topics
  }
}
```

### EngagementHeatmap Component
```javascript
class EngagementHeatmap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      period: 'daily'
    };
  }

  render() {
    // Render heatmap showing engagement intensity over time
  }
}
```

### Dashboard Layout
```html
<div class="engagement-dashboard">
  <div class="controls">
    <select id="period-selector">
      <option value="daily">Daily</option>
      <option value="monthly">Monthly</option>
      <option value="yearly">Yearly</option>
    </select>
    <select id="metric-selector">
      <option value="likes">Likes</option>
      <option value="shares">Shares</option>
      <option value="comments">Comments</option>
    </select>
  </div>

  <div class="charts-container">
    <div class="chart-panel">
      <h3>Engagement Trends</h3>
      <div id="engagement-trend-chart"></div>
    </div>

    <div class="chart-panel">
      <h3>Top Engaged Topics</h3>
      <div id="top-topics-widget"></div>
    </div>
  </div>

  <div class="summary-panel">
    <h3>Engagement Summary</h3>
    <div id="engagement-summary"></div>
  </div>
</div>
```

## Database Schema Migrations

### Migration Strategy
1. Add new columns to existing `topic_search_results` table
2. Create new `engagement_metrics` table for detailed time-series data
3. Create new `engagement_summaries` table for pre-computed aggregates
4. Add indexes for efficient querying of time-series data
5. Create migration scripts for backward compatibility

### Performance Optimizations
- Pre-computed summary tables for fast dashboard queries
- Database indexes on timestamp and topic columns
- Partitioning strategy for large time-series datasets
- Caching layer for frequently accessed engagement data

## Implementation Considerations

### Data Collection
- Integrate with social media APIs for real-time engagement data
- Batch processing for historical data import
- Data validation and cleansing pipelines

### Scalability
- Horizontal scaling for aggregation services
- Database sharding by time periods
- Caching strategies for dashboard performance

### Monitoring
- Track aggregation job performance
- Monitor API response times
- Alert on data collection failures

This design provides a comprehensive architecture for tracking and visualizing engagement metrics across different time periods while maintaining performance and scalability.