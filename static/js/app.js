// Mamdani Tracker - Main JavaScript

// Global state
let allPromises = [];
let socket = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeSocketIO();
    setupEventListeners();
    loadThemePreference();
});

// Initialize the application
function initializeApp() {
    console.log('Initializing Mamdani Tracker...');
    fetchPromises();
}

// Initialize Socket.IO connection
function initializeSocketIO() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Socket.IO connected');
            updateConnectionStatus(true);
            showNotification('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Socket.IO disconnected');
            updateConnectionStatus(false);
            showNotification('Disconnected from server', 'warning');
        });
        
        socket.on('connected', function(data) {
            console.log('Server message:', data.message);
        });
        
        socket.on('news_update', function(data) {
            console.log('News update received:', data);
            showNotification(`${data.new_articles} new articles found!`);
            // Refresh the current promise view if it's open
            const modalElement = document.getElementById('promiseModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal && modal._isShown) {
                const currentPromiseId = modalElement.dataset.currentPromiseId;
                if (currentPromiseId && parseInt(currentPromiseId) === data.promise_id) {
                    loadPromiseDetails(data.promise_id);
                }
            }
        });
        
        socket.on('promises_update', function(data) {
            console.log('Promises update received');
            allPromises = data.promises;
            renderPromises(allPromises);
        });
        
        socket.on('error', function(data) {
            console.error('Socket.IO error:', data.message);
            showNotification('Error: ' + data.message, 'danger');
        });
        
    } catch (error) {
        console.error('Error initializing Socket.IO:', error);
        updateConnectionStatus(false);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function() {
        filterPromises();
    });
    
    // Category filter
    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter.addEventListener('change', function() {
        filterPromises();
    });
    
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    statusFilter.addEventListener('change', function() {
        filterPromises();
    });
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.addEventListener('click', function() {
        fetchPromises();
    });
    
    // Scrape button
    const scrapeBtn = document.getElementById('scrapeBtn');
    scrapeBtn.addEventListener('click', function() {
        triggerScrape();
    });
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', function() {
        toggleTheme();
    });
}

// Fetch promises from API
async function fetchPromises() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/promises');
        const data = await response.json();
        
        if (data.success) {
            allPromises = data.promises;
            renderPromises(allPromises);
        } else {
            showNotification('Error loading promises: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error fetching promises:', error);
        showNotification('Failed to load promises', 'danger');
    } finally {
        showLoading(false);
    }
}

// Render promises to the grid
function renderPromises(promises) {
    const container = document.getElementById('promisesContainer');
    const noResults = document.getElementById('noResults');
    
    // Clear existing cards
    container.innerHTML = '';
    
    if (promises.length === 0) {
        container.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    container.style.display = 'grid';
    noResults.style.display = 'none';
    
    promises.forEach((promise, index) => {
        const card = createPromiseCard(promise, index);
        container.appendChild(card);
    });
}

// Create a promise card element
function createPromiseCard(promise, index) {
    const col = document.createElement('div');
    col.className = 'col';
    
    const statusClass = getStatusClass(promise.status);
    const categoryColor = getCategoryColor(promise.category);
    
    col.innerHTML = `
        <div class="card promise-card" onclick="openPromiseModal(${promise.id})" style="animation-delay: ${index * 0.1}s;">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="category-badge ${categoryColor}">${escapeHtml(promise.category)}</span>
                    <span class="status-badge ${statusClass}">${escapeHtml(promise.status)}</span>
                </div>
                
                <h5 class="card-title">${escapeHtml(promise.title)}</h5>
                <p class="card-text">${escapeHtml(truncateText(promise.description, 120))}</p>
                
                <div class="score-container">
                    <div class="score-item">
                        <span class="score-label">Overall</span>
                        <span class="score-value ${getScoreClass(promise.overall_score)}">
                            ${formatScore(promise.overall_score)}
                        </span>
                        <div class="progress score-progress">
                            <div class="progress-bar ${getScoreProgressClass(promise.overall_score)}" 
                                 style="width: ${promise.overall_score * 100}%"></div>
                        </div>
                    </div>
                    
                    <div class="score-item">
                        <span class="score-label">Priority</span>
                        <span class="score-value ${getScoreClass(promise.priority_score)}">
                            ${formatScore(promise.priority_score)}
                        </span>
                    </div>
                    
                    <div class="score-item">
                        <span class="score-label">Feasibility</span>
                        <span class="score-value ${getScoreClass(promise.feasibility_score)}">
                            ${formatScore(promise.feasibility_score)}
                        </span>
                    </div>
                </div>
                
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="bi bi-calendar-event"></i> ${formatDate(promise.date_made)}
                    </small>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

// Open promise detail modal
async function openPromiseModal(promiseId) {
    const modal = new bootstrap.Modal(document.getElementById('promiseModal'));
    const modalTitle = document.getElementById('promiseModalTitle');
    const modalBody = document.getElementById('promiseModalBody');
    const modalElement = document.getElementById('promiseModal');
    
    // Store current promise ID for updates
    modalElement.dataset.currentPromiseId = promiseId;
    
    modalTitle.textContent = 'Loading...';
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    modal.show();
    
    await loadPromiseDetails(promiseId);
}

// Load promise details
async function loadPromiseDetails(promiseId) {
    try {
        const response = await fetch(`/api/promises/${promiseId}`);
        const data = await response.json();
        
        if (data.success) {
            displayPromiseDetails(data.promise, data.articles);
        } else {
            showNotification('Error loading promise details', 'danger');
        }
    } catch (error) {
        console.error('Error loading promise details:', error);
        showNotification('Failed to load promise details', 'danger');
    }
}

// Display promise details in modal
function displayPromiseDetails(promise, articles) {
    const modalTitle = document.getElementById('promiseModalTitle');
    const modalBody = document.getElementById('promiseModalBody');
    
    modalTitle.textContent = promise.title;
    
    const statusClass = getStatusClass(promise.status);
    const categoryColor = getCategoryColor(promise.category);
    
    let articlesHtml = '';
    if (articles && articles.length > 0) {
        articlesHtml = articles.map(article => `
            <div class="article-item">
                <a href="${escapeHtml(article.url)}" target="_blank" class="article-title">
                    ${escapeHtml(article.title)}
                </a>
                <div class="article-source">
                    <i class="bi bi-newspaper"></i> ${escapeHtml(article.source)}
                    ${article.published_date ? ' • ' + formatDate(article.published_date) : ''}
                </div>
                ${article.snippet ? `<div class="article-snippet">${escapeHtml(article.snippet)}</div>` : ''}
            </div>
        `).join('');
    } else {
        articlesHtml = '<p class="text-muted">No related news articles found yet. Click "Scrape News" to fetch updates.</p>';
    }
    
    modalBody.innerHTML = `
        <div class="promise-detail-section">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="category-badge ${categoryColor}">${escapeHtml(promise.category)}</span>
                <span class="status-badge ${statusClass}">${escapeHtml(promise.status)}</span>
            </div>
            
            <p class="lead">${escapeHtml(promise.description)}</p>
        </div>
        
        <div class="promise-detail-section">
            <h6><i class="bi bi-graph-up"></i> Scores & Metrics</h6>
            <div class="row">
                <div class="col-md-6">
                    <div class="detail-item">
                        <span class="detail-label">Overall Score</span>
                        <span class="detail-value ${getScoreClass(promise.overall_score)}">
                            ${formatScore(promise.overall_score)}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Priority</span>
                        <span class="detail-value ${getScoreClass(promise.priority_score)}">
                            ${formatScore(promise.priority_score)}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Feasibility</span>
                        <span class="detail-value ${getScoreClass(promise.feasibility_score)}">
                            ${formatScore(promise.feasibility_score)}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Impact</span>
                        <span class="detail-value ${getScoreClass(promise.impact_score)}">
                            ${formatScore(promise.impact_score)}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Urgency</span>
                        <span class="detail-value ${getScoreClass(promise.urgency_score)}">
                            ${formatScore(promise.urgency_score)}
                        </span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="detail-item">
                        <span class="detail-label">Budget Required</span>
                        <span class="detail-value">$${promise.budget_required}M</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Legislative Complexity</span>
                        <span class="detail-value">${promise.legislative_complexity}/5</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Public Interest</span>
                        <span class="detail-value">${promise.public_interest}/10</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Deadline</span>
                        <span class="detail-value">
                            ${promise.deadline_days ? promise.deadline_days + ' days' : 'No deadline'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Date Made</span>
                        <span class="detail-value">${formatDate(promise.date_made)}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="promise-detail-section">
            <h6><i class="bi bi-newspaper"></i> Related News Articles</h6>
            ${articlesHtml}
        </div>
    `;
}

// Filter promises based on search and filters
function filterPromises() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    const filtered = allPromises.filter(promise => {
        const matchesSearch = !searchTerm || 
            promise.title.toLowerCase().includes(searchTerm) || 
            promise.description.toLowerCase().includes(searchTerm);
        
        const matchesCategory = !categoryFilter || promise.category === categoryFilter;
        const matchesStatus = !statusFilter || promise.status === statusFilter;
        
        return matchesSearch && matchesCategory && matchesStatus;
    });
    
    renderPromises(filtered);
}

// Trigger manual scrape
async function triggerScrape() {
    const btn = document.getElementById('scrapeBtn');
    const originalHtml = btn.innerHTML;
    
    try {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Scraping...';
        
        const response = await fetch('/api/scrape', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('News scraping started! Updates will appear shortly.', 'success');
        } else {
            showNotification('Error starting scrape: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error triggering scrape:', error);
        showNotification('Failed to start scraping', 'danger');
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }, 2000);
    }
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    
    if (connected) {
        statusElement.className = 'badge status-connected';
        statusElement.innerHTML = '<i class="bi bi-circle-fill"></i> Connected';
    } else {
        statusElement.className = 'badge status-disconnected';
        statusElement.innerHTML = '<i class="bi bi-circle-fill"></i> Disconnected';
    }
}

// Show/hide loading spinner
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('promisesContainer');
    
    if (show) {
        spinner.style.display = 'block';
        container.style.display = 'none';
    } else {
        spinner.style.display = 'none';
        container.style.display = 'grid';
    }
}

// Show notification toast
function showNotification(message, type = 'info') {
    const toastElement = document.getElementById('notificationToast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    
    // Update toast color based on type
    const toastHeader = toastElement.querySelector('.toast-header');
    toastHeader.className = `toast-header bg-${type} text-white`;
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

// Theme toggle
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    
    body.classList.toggle('dark-theme');
    
    if (body.classList.contains('dark-theme')) {
        themeIcon.className = 'bi bi-moon-fill';
        localStorage.setItem('theme', 'dark');
    } else {
        themeIcon.className = 'bi bi-sun-fill';
        localStorage.setItem('theme', 'light');
    }
}

// Load theme preference
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.className = 'bi bi-moon-fill';
    }
}

// Helper functions

function getStatusClass(status) {
    const statusMap = {
        'Not Started': 'bg-secondary',
        'In Progress': 'bg-primary',
        'Completed': 'bg-success'
    };
    return statusMap[status] || 'bg-secondary';
}

function getCategoryColor(category) {
    const colorMap = {
        'Infrastructure': 'bg-info text-dark',
        'Healthcare': 'bg-danger text-white',
        'Environment': 'bg-success text-white',
        'Education': 'bg-warning text-dark',
        'Housing': 'bg-primary text-white',
        'Economy': 'bg-secondary text-white'
    };
    return colorMap[category] || 'bg-secondary text-white';
}

function getScoreClass(score) {
    if (score >= 0.7) return 'score-high';
    if (score >= 0.4) return 'score-medium';
    return 'score-low';
}

function getScoreProgressClass(score) {
    if (score >= 0.7) return 'bg-success';
    if (score >= 0.4) return 'bg-warning';
    return 'bg-danger';
}

function formatScore(score) {
    return (score * 100).toFixed(0) + '%';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
