// AI Search Dashboard - Simplified
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    setupSearch();
    loadTrendingArticles();
    
    // Refresh trending articles every 5 minutes
    setInterval(loadTrendingArticles, 5 * 60 * 1000);
}

// Search functionality
function setupSearch() {
    const quickSearch = document.getElementById('quickSearch');
    const searchBtn = document.getElementById('searchBtn');
    
    function performSearch() {
        const query = quickSearch.value.trim();
        if (!query) return;
        
        searchArticles(query);
    }
    
    searchBtn.addEventListener('click', performSearch);
    
    quickSearch.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
}

// Search articles
async function searchArticles(query) {
    try {
        const searchResultsSection = document.getElementById('searchResults');
        const resultsContainer = document.getElementById('resultsContainer');
        
        // Show loading
        resultsContainer.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i><p>Haetaan artikkeleita...</p></div>';
        searchResultsSection.style.display = 'block';
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data.results || [], query);
        } else {
            resultsContainer.innerHTML = '<div class="error-state"><i class="fas fa-exclamation-circle"></i><p>Haku epäonnistui</p></div>';
        }
    } catch (error) {
        console.error('Search error:', error);
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = '<div class="error-state"><i class="fas fa-exclamation-circle"></i><p>Haku epäonnistui</p></div>';
    }
}

// Display search results
function displaySearchResults(results, query) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="empty-state"><i class="fas fa-search"></i><p>Ei tuloksia hakusanalle: ' + escapeHtml(query) + '</p></div>';
        return;
    }
    
    let html = '<div class="results-list">';
    results.forEach(result => {
        html += `
            <div class="result-item">
                <h3><a href="${escapeHtml(result.url)}" target="_blank">${escapeHtml(result.title || 'Ei otsikkoa')}</a></h3>
                <p class="result-meta">
                    <span class="result-source">${escapeHtml(result.source || 'Unknown')}</span>
                </p>
                <p class="result-description">${escapeHtml(result.description || 'Ei kuvausta')}</p>
            </div>
        `;
    });
    html += '</div>';
    
    resultsContainer.innerHTML = html;
    
    // Scroll to results
    document.getElementById('searchResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Load trending articles
async function loadTrendingArticles() {
    try {
        const trendingArticles = document.getElementById('trendingArticles');
        
        // Show loading
        trendingArticles.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i><p>Ladataan trendaavia artikkeleita...</p></div>';
        
        const response = await fetch('/api/trending/articles');
        
        if (response.ok) {
            const data = await response.json();
            displayTrendingArticles(data.articles || []);
        } else {
            trendingArticles.innerHTML = '<div class="error-state"><i class="fas fa-exclamation-circle"></i><p>Artikkeleiden lataaminen epäonnistui</p></div>';
        }
    } catch (error) {
        console.error('Error loading trending articles:', error);
        const trendingArticles = document.getElementById('trendingArticles');
        trendingArticles.innerHTML = '<div class="error-state"><i class="fas fa-exclamation-circle"></i><p>Artikkeleiden lataaminen epäonnistui</p></div>';
    }
}

// Display trending articles
function displayTrendingArticles(articles) {
    const trendingArticles = document.getElementById('trendingArticles');
    
    if (articles.length === 0) {
        trendingArticles.innerHTML = '<div class="empty-state"><i class="fas fa-fire"></i><p>Ei trendaavia artikkeleita tällä hetkellä</p></div>';
        return;
    }
    
    let html = '<div class="articles-grid">';
    articles.forEach((article, index) => {
        html += `
            <div class="article-card">
                <div class="article-number">${index + 1}</div>
                <div class="article-content">
                    <h3><a href="${escapeHtml(article.url)}" target="_blank">${escapeHtml(article.title || 'Ei otsikkoa')}</a></h3>
                    <p class="article-meta">
                        <span class="article-source"><i class="fas fa-tag"></i> ${escapeHtml(article.source || 'Unknown')}</span>
                        ${article.topic ? `<span class="article-topic"><i class="fas fa-hashtag"></i> ${escapeHtml(article.topic)}</span>` : ''}
                    </p>
                    <p class="article-description">${escapeHtml(article.description || 'Ei kuvausta')}</p>
                    ${article.score ? `<div class="article-score"><i class="fas fa-chart-line"></i> ${article.score}%</div>` : ''}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    trendingArticles.innerHTML = html;
}

// Refresh button handler
document.getElementById('refreshTrending').addEventListener('click', function() {
    this.querySelector('i').classList.add('fa-spin');
    loadTrendingArticles().finally(() => {
        setTimeout(() => {
            this.querySelector('i').classList.remove('fa-spin');
        }, 500);
    });
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

console.log('🔍 AI Search Dashboard initialized');
