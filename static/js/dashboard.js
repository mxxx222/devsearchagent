// AI Code Agent - Modern Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupQuickSearch();
    setupFileTree();
    setupTabs();
    setupAIChat();
    setupTerminal();
    loadProjectData();
    updateStatusIndicators();
    
    // Start auto-refresh
    setInterval(updateStatusIndicators, 30000);
}

// Quick Search (Cmd+K)
function setupQuickSearch() {
    const quickSearch = document.getElementById('quickSearch');
    
    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
            quickSearch.focus();
        }
    });
    
    quickSearch.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.blur();
        }
    });
}

// File Tree Expand/Collapse
function setupFileTree() {
    const fileItems = document.querySelectorAll('.file-item');
    
    fileItems.forEach(item => {
        const caret = item.querySelector('.fa-caret-down, .fa-caret-right');
        if (caret) {
            item.addEventListener('click', function() {
                caret.classList.toggle('fa-caret-down');
                caret.classList.toggle('fa-caret-right');
            });
        }
    });
}

// Tab Management
function setupTabs() {
    const tabs = document.querySelectorAll('.tab-item');
    const closeBtns = document.querySelectorAll('.close-tab');
    const tabBtn = document.querySelector('.tab-btn');
    
    // Switch tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            if (!e.target.classList.contains('close-tab')) {
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Close tabs
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const tab = this.closest('.tab-item');
            const isActive = tab.classList.contains('active');
            
            tab.remove();
            
            // Activate another tab if current was closed
            if (isActive) {
                const remainingTabs = document.querySelectorAll('.tab-item');
                if (remainingTabs.length > 0) {
                    remainingTabs[0].classList.add('active');
                }
            }
        });
    });
    
    // Add new tab
    if (tabBtn) {
        tabBtn.addEventListener('click', function() {
            // Would open file picker in real app
            console.log('Open file picker');
        });
    }
}

// AI Chat
function setupAIChat() {
    const aiInput = document.querySelector('.ai-input');
    const sendBtn = document.querySelector('.send-btn');
    
    function sendMessage() {
        const message = aiInput.value.trim();
        if (message) {
            addAIMessage(message);
            aiInput.value = '';
        }
    }
    
    sendBtn.addEventListener('click', sendMessage);
    aiInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

function addAIMessage(userMessage) {
    const messagesContainer = document.getElementById('aiMessages');
    
    // User message
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-message';
    userMsg.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <p>${userMessage}</p>
        </div>
    `;
    messagesContainer.appendChild(userMsg);
    
    // Simulate AI response
    setTimeout(() => {
        const aiMsg = document.createElement('div');
        aiMsg.className = 'ai-message';
        aiMsg.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>I understand your request. Let me help you with that...</p>
            </div>
        `;
        messagesContainer.appendChild(aiMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 500);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Terminal
function setupTerminal() {
    const terminal = document.querySelector('.terminal');
    
    // Simulate terminal output
    setTimeout(() => {
        const output = terminal.querySelector('.terminal-output');
        const newLine = document.createElement('div');
        newLine.textContent = '> Ready for commands';
        output.appendChild(newLine);
    }, 2000);
}

// Load Project Data
async function loadProjectData() {
    try {
        // Load trending topics
        const trendingResponse = await fetch('/api/trending?limit=10');
        if (trendingResponse.ok) {
            const data = await trendingResponse.json();
            console.log('Loaded trending topics:', data);
        }
        
        // Load engagement data
        const engagementResponse = await fetch('/api/engagement/summary?period=daily');
        if (engagementResponse.ok) {
            const data = await engagementResponse.json();
            console.log('Loaded engagement data:', data);
        }
    } catch (error) {
        console.error('Error loading project data:', error);
    }
}

// Update Status Indicators
function updateStatusIndicators() {
    // Update activity list
    updateActivityLog();
    
    // Update insights
    updateInsights();
}

function updateActivityLog() {
    const activityList = document.querySelector('.activity-list');
    const firstActivity = activityList.querySelector('.activity-item');
    
    // Simulate new activity
    if (firstActivity && Math.random() > 0.7) {
        const activities = [
            { icon: 'fa-code', action: 'Code committed', time: 'just now' },
            { icon: 'fa-check', action: 'Tests passed', time: '1 min ago' },
            { icon: 'fa-sync', action: 'Project synced', time: '2 min ago' },
        ];
        
        const activity = activities[Math.floor(Math.random() * activities.length)];
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon"><i class="fas ${activity.icon}"></i></div>
            <div class="activity-content">
                <span class="activity-action">${activity.action}</span>
                <span class="activity-time">${activity.time}</span>
        </div>
    `;
        
        activityList.insertBefore(activityItem, firstActivity);
        
        // Remove old activities if too many
        const items = activityList.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
}

function updateInsights() {
    // Update insight values with slight variations
    const insightValues = document.querySelectorAll('.insight-value');
    insightValues.forEach(value => {
        const current = parseInt(value.textContent);
        if (!isNaN(current)) {
            const variation = Math.floor(Math.random() * 3 - 1); // -1, 0, or 1
            const newValue = Math.max(0, Math.min(100, current + variation));
            if (newValue !== current) {
                value.textContent = newValue + '%';
            }
        }
    });
}

// Search functionality
async function performSearch(query) {
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Search results:', data);
            return data.results || [];
        }
    } catch (error) {
        console.error('Search error:', error);
    }
    return [];
}

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Cmd/Ctrl + B - Toggle sidebar
    if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault();
        const sidebar = document.querySelector('.left-sidebar');
        sidebar.classList.toggle('hidden');
    }
    
    // Cmd/Ctrl + J - Toggle bottom panel
    if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
        e.preventDefault();
        const bottomPanel = document.querySelector('.bottom-panel');
        bottomPanel.classList.toggle('hidden');
    }
});

// Quick Actions
document.querySelectorAll('.quick-action-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const action = this.querySelector('span').textContent;
        console.log(`Quick action: ${action}`);
        
        // Add activity log entry
        const activityList = document.querySelector('.activity-list');
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon"><i class="fas fa-rocket"></i></div>
            <div class="activity-content">
                <span class="activity-action">${action} started</span>
                <span class="activity-time">just now</span>
            </div>
        `;
        activityList.insertBefore(activityItem, activityList.firstChild);
    });
});

// Agent Status Updates
function updateAgentStatus() {
    const statusDots = document.querySelectorAll('.status-dot');
    statusDots.forEach(dot => {
        // Simulate status changes
        if (Math.random() > 0.95) {
            dot.style.animation = 'none';
            setTimeout(() => {
                dot.style.animation = 'pulse 2s infinite';
            }, 10);
        }
    });
}

// Initialize agent status updates
setInterval(updateAgentStatus, 5000);

console.log('🤖 AI Code Agent initialized');
