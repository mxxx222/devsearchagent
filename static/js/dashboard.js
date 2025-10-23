// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    setupSearchForm();
    loadTrendingData();
    loadAIRecommendations();
    loadEngagementData();
    loadTopEngagedTopics();
    initializeCharts();
    setupAIRecommendationsFilter();
    setupNewTopicsRefresh();
    loadQuickStats();
    updateLastUpdateTime();
}

function setupSearchForm() {
    const form = document.getElementById('searchForm');
    const input = document.getElementById('searchInput');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = input.value.trim();
        if (query) {
            performSearch(query);
        }
    });
}

async function performSearch(query) {
    const resultsContainer = document.getElementById('resultsContainer');

    // Show loading state
    resultsContainer.innerHTML = '<p class="placeholder">Searching...</p>';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        });

        const data = await response.json();
        displaySearchResults(data.results);
    } catch (error) {
        console.error('Search error:', error);
        resultsContainer.innerHTML = '<p class="placeholder">Error performing search. Please try again.</p>';
    }
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="placeholder">No results found.</p>';
        return;
    }

    const resultsHtml = results.map(result => `
        <div class="search-result">
            <h3><a href="${result.url}" target="_blank">${result.title}</a></h3>
            <p>${result.description}</p>
        </div>
    `).join('');

    resultsContainer.innerHTML = resultsHtml;
}

async function loadTrendingData() {
    try {
        const response = await fetch('/api/trending');
        const data = await response.json();
        displayTrendingData(data);
        updateTrendingChart(data);
    } catch (error) {
        console.error('Error loading trending data:', error);
    }
}

function displayTrendingData(data) {
    const trendingList = document.getElementById('trendingList');

    const trendingHtml = data.map(item => `
        <div class="trending-item">
            <span class="trending-topic">${item.topic}</span>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="trending-score">${item.score}</span>
                <span class="trending-change">${item.change}</span>
            </div>
        </div>
    `).join('');

    trendingList.innerHTML = trendingHtml;
}

function initializeCharts() {
    // Chart.js initialization will happen when data is loaded
    setupEngagementControls();
}

function updateTrendingChart(data) {
    const ctx = document.getElementById('trendingChart').getContext('2d');

    const labels = data.map(item => item.topic);
    const scores = data.map(item => item.score);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Trending Score',
                data: scores,
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1,
                borderRadius: 5,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

async function loadAIRecommendations() {
    try {
        const response = await fetch('/api/recommendations');
        const data = await response.json();
        displayAIRecommendations(data);
    } catch (error) {
        console.error('Error loading AI recommendations:', error);
    }
}

function displayAIRecommendations(data) {
    const recommendationsList = document.getElementById('recommendationsList');

    if (!data || data.length === 0) {
        recommendationsList.innerHTML = '<p class="placeholder">No AI recommendations available</p>';
        return;
    }

    const recommendationsHtml = data.map(item => `
        <div class="recommendation-item">
            <div class="recommendation-header">
                <span class="recommendation-topic">${item.topic}</span>
                <span class="recommendation-source source-${item.source}">${item.source}</span>
            </div>
            <div class="recommendation-category">${item.category}</div>
            <div class="recommendation-confidence">Confidence: ${(item.confidence * 100).toFixed(1)}%</div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${item.confidence * 100}%"></div>
            </div>
            ${item.reasoning ? `<div class="recommendation-reasoning">${item.reasoning}</div>` : ''}
            ${item.related_topics && item.related_topics.length > 0 ? `
                <div class="related-topics">
                    <small>Related: ${item.related_topics.slice(0, 3).join(', ')}</small>
                </div>
            ` : ''}
        </div>
    `).join('');

    recommendationsList.innerHTML = recommendationsHtml;
}
// Auto-refresh trending data every 30 seconds
setInterval(loadTrendingData, 30000);
setInterval(loadAIRecommendations, 30000);
setInterval(loadEngagementData, 30000);
setInterval(loadTopEngagedTopics, 30000);

async function loadEngagementData() {
    try {
        const period = document.getElementById('engagementPeriod').value;
        const response = await fetch(`/api/engagement/summary?period=${period}`);
        const data = await response.json();

        if (data && data.total_likes !== undefined) {
            displayEngagementSummary(data);
            updateEngagementChart(data);
        }
    } catch (error) {
        console.error('Error loading engagement data:', error);
    }
}

function displayEngagementSummary(data) {
    const summaryContainer = document.getElementById('engagementSummary');
    const period = document.getElementById('engagementPeriod').value;
    const metric = document.getElementById('engagementMetric').value;

    const metricValue = data[`total_${metric}`] || 0;

    summaryContainer.innerHTML = `
        <div class="engagement-metric">
            <span class="metric-label">${period.charAt(0).toUpperCase() + period.slice(1)} ${metric}:</span>
            <span class="metric-value">${metricValue.toLocaleString()}</span>
        </div>
        <div class="engagement-metric">
            <span class="metric-label">Avg Engagement Score:</span>
            <span class="metric-value">${data.avg_engagement_score?.toFixed(2) || '0.00'}</span>
        </div>
        <div class="engagement-metric">
            <span class="metric-label">Topics Tracked:</span>
            <span class="metric-value">${data.topic_count || 0}</span>
        </div>
    `;
}

function updateEngagementChart(data) {
    const ctx = document.getElementById('engagementChart').getContext('2d');
    const metric = document.getElementById('engagementMetric').value;

    // For now, show a simple bar chart with current period data
    // In a full implementation, this would show time-series data
    const labels = ['Likes', 'Shares', 'Comments'];
    const values = [data.total_likes || 0, data.total_shares || 0, data.total_comments || 0];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Engagement Metrics',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 205, 86, 0.6)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 205, 86, 1)'
                ],
                borderWidth: 1,
                borderRadius: 5,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

async function loadTopEngagedTopics() {
    try {
        const period = document.getElementById('engagementPeriod').value;
        const metric = document.getElementById('engagementMetric').value;
        const response = await fetch(`/api/engagement/topics/top?period=${period}&metric=${metric}&limit=10`);
        const topics = await response.json();

        displayTopEngagedTopics(topics);
    } catch (error) {
        console.error('Error loading top engaged topics:', error);
    }
}

function displayTopEngagedTopics(topics) {
    const container = document.getElementById('topEngagedList');

    if (!topics || topics.length === 0) {
        container.innerHTML = '<p class="placeholder">No engagement data available</p>';
        return;
    }

    const metric = document.getElementById('engagementMetric').value;
    const topicsHtml = topics.map((topic, index) => `
        <div class="top-engaged-item">
            <span class="rank">#${index + 1}</span>
            <div class="topic-info">
                <span class="topic-name">${topic.topic}</span>
                <span class="topic-category">${topic.category}</span>
            </div>
            <span class="engagement-count">${(topic[`total_${metric}`] || 0).toLocaleString()}</span>
        </div>
    `).join('');

    container.innerHTML = topicsHtml;
}

function setupEngagementControls() {
    const periodSelect = document.getElementById('engagementPeriod');
    const metricSelect = document.getElementById('engagementMetric');

    periodSelect.addEventListener('change', () => {
        loadEngagementData();
        loadTopEngagedTopics();
    });

    metricSelect.addEventListener('change', () => {
        loadEngagementData();
        loadTopEngagedTopics();
    });
}

// AI Recommendations Filter Setup
function setupAIRecommendationsFilter() {
    const sourceButtons = document.querySelectorAll('.source-btn');
    
    sourceButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            sourceButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Load recommendations for selected source
            const source = this.dataset.source;
            loadAIRecommendations(source);
        });
    });
}

// New Topics Refresh Setup
function setupNewTopicsRefresh() {
    const refreshBtn = document.getElementById('refreshTopics');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadNewTopics();
            updateLastUpdateTime();
        });
    }
}

// Load New Topics (4-hour updates)
async function loadNewTopics() {
    try {
        const response = await fetch('/api/trending?limit=5');
        const topics = await response.json();
        
        const container = document.getElementById('newTopicsList');
        
        if (topics && topics.length > 0) {
            container.innerHTML = topics.map(topic => `
                <div class="topic-item">
                    <div class="topic-name">${topic.topic}</div>
                    <div class="topic-score">Score: ${topic.score}</div>
                    <div class="topic-category">${topic.category}</div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="placeholder">No new topics available</p>';
        }
    } catch (error) {
        console.error('Error loading new topics:', error);
        document.getElementById('newTopicsList').innerHTML = '<p class="placeholder">Error loading topics</p>';
    }
}

// Load Quick Stats
async function loadQuickStats() {
    try {
        const [trendingResponse, engagementResponse] = await Promise.all([
            fetch('/api/trending?limit=1'),
            fetch('/api/engagement/summary?period=daily')
        ]);
        
        const trendingData = await trendingResponse.json();
        const engagementData = await engagementResponse.json();
        
        const container = document.getElementById('quickStats');
        
        const totalTopics = trendingData ? trendingData.length : 0;
        const totalEngagement = engagementData ? engagementData.total_engagement || 0 : 0;
        const avgScore = trendingData && trendingData.length > 0 ? 
            Math.round(trendingData.reduce((sum, topic) => sum + topic.score, 0) / trendingData.length) : 0;
        const activeSources = 2; // OpenAI and Gemini
        
        container.innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${totalTopics}</span>
                <div class="stat-label">Active Topics</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">${totalEngagement}</span>
                <div class="stat-label">Total Engagement</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">${avgScore}%</span>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">${activeSources}</span>
                <div class="stat-label">AI Sources</div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading quick stats:', error);
    }
}

// Update Last Update Time
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fi-FI', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    document.getElementById('lastUpdateTime').textContent = timeString;
}

// Enhanced AI Recommendations Loading with Source Filter
async function loadAIRecommendations(source = 'all') {
    try {
        let url = '/api/recommendations?limit=10';
        if (source !== 'all') {
            url = `/api/recommendations/sources/${source}?limit=10`;
        }
        
        const response = await fetch(url);
        const recommendations = await response.json();
        
        const container = document.getElementById('recommendationsList');
        
        if (recommendations && recommendations.length > 0) {
            container.innerHTML = recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="recommendation-topic">${rec.topic || rec.query}</div>
                    <div class="recommendation-confidence">
                        Confidence: ${Math.round((rec.confidence || 0) * 100)}%
                    </div>
                    <div class="recommendation-source">
                        Source: ${rec.source || 'AI'}
                    </div>
                    ${rec.reasoning ? `<div class="recommendation-reasoning">${rec.reasoning}</div>` : ''}
                    ${rec.related_topics && rec.related_topics.length > 0 ? `
                        <div class="related-topics">
                            <small>Related: ${rec.related_topics.slice(0, 3).join(', ')}</small>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="placeholder">No AI recommendations available</p>';
        }
    } catch (error) {
        console.error('Error loading AI recommendations:', error);
        document.getElementById('recommendationsList').innerHTML = '<p class="placeholder">Error loading recommendations</p>';
    }
}

// Auto-refresh new topics every 4 hours
setInterval(() => {
    loadNewTopics();
    updateLastUpdateTime();
}, 4 * 60 * 60 * 1000); // 4 hours in milliseconds

// Auto-refresh trending data every 30 seconds
setInterval(loadTrendingData, 30000);
setInterval(loadAIRecommendations, 30000);