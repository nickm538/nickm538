/**
 * Mamdani Tracker - Frontend JavaScript
 * 
 * Handles:
 * - AJAX API calls
 * - Socket.IO real-time updates
 * - UI rendering and interactions
 * - Theme toggling
 * - Manual scrape triggering
 * 
 * Note: All external content is sanitized to prevent XSS attacks
 */

// Global state
let promises = [];
let socket = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mamdani Tracker initialized');
    
    initSocketIO();
    initThemeToggle();
    initScrapeButton();
    fetchPromises();
});

/**
 * Initialize Socket.IO connection for real-time updates
 */
function initSocketIO() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Socket.IO connected');
        updateConnectionStatus(true);
        showToast('Connected to server');
    });
    
    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected');
        updateConnectionStatus(false);
        showToast('Disconnected from server', 'warning');
    });
    
    socket.on('connected', function(data) {
        console.log('Server greeting:', data.message);
    });
    
    socket.on('promises_updated', function(data) {
        console.log('Promises updated:', data);
        showToast(`${data.new_count} new promises, ${data.updated_count} updated`);
        fetchPromises();
    });
    
    socket.on('promises_update', function(data) {
        console.log('Received promise update:', data);
        // Could update specific promises in real-time
    });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connectionStatus');
    if (connected) {
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Connected';
        statusBadge.className = 'badge bg-success ms-auto';
    } else {
        statusBadge.innerHTML = '<i class="bi bi-x-circle-fill"></i> Disconnected';
        statusBadge.className = 'badge bg-danger ms-auto';
    }
}

/**
 * Fetch promises from API
 */
async function fetchPromises() {
    try {
        const response = await fetch('/api/promises');
        if (!response.ok) throw new Error('Failed to fetch promises');
        
        promises = await response.json();
        console.log(`Fetched ${promises.length} promises`);
        
        renderPromises();
        updateStats();
        updateStatusMessage(`Loaded ${promises.length} promises`);
        
    } catch (error) {
        console.error('Error fetching promises:', error);
        updateStatusMessage('Error loading promises', 'danger');
        showToast('Failed to load promises', 'danger');
    }
}

/**
 * Render promises in the grid
 */
function renderPromises() {
    const grid = document.getElementById('promisesGrid');
    
    if (promises.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-inbox" style="font-size: 3rem; color: #6c757d;"></i>
                <p class="mt-3 text-muted">No promises found. Click "Run Scrape Now" to fetch data.</p>
            </div>
        `;
        return;
    }
    
    // Sort by created_at descending
    const sortedPromises = [...promises].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
    );
    
    grid.innerHTML = sortedPromises.map(promise => createPromiseCard(promise)).join('');
    
    // Add click handlers
    document.querySelectorAll('.promise-card').forEach(card => {
        card.addEventListener('click', function() {
            const promiseId = this.dataset.promiseId;
            showPromiseDetail(promiseId);
        });
    });
}

/**
 * Create HTML for a promise card
 * Note: Using textContent for user-generated content to prevent XSS
 */
function createPromiseCard(promise) {
    const title = escapeHtml(promise.title || 'Untitled Promise');
    const description = escapeHtml(promise.description || 'No description available');
    const source = escapeHtml(promise.source || 'Unknown');
    
    const feasibilityClass = getScoreClass(promise.feasibility_score);
    const impactClass = getScoreClass(promise.impact_score);
    const priorityClass = getScoreClass(promise.priority_score);
    
    return `
        <div class="col-md-6 col-lg-4">
            <div class="promise-card fade-in" data-promise-id="${promise.id}">
                <div class="promise-card-header">
                    <h5 class="promise-title">${title}</h5>
                </div>
                <div class="promise-card-body">
                    <p class="promise-description">${description}</p>
                    
                    <div class="mb-2">
                        <span class="score-badge ${feasibilityClass}">
                            Feasibility: ${(promise.feasibility_score * 100).toFixed(0)}%
                        </span>
                        <span class="score-badge ${impactClass}">
                            Impact: ${(promise.impact_score * 100).toFixed(0)}%
                        </span>
                        <span class="score-badge ${priorityClass}">
                            Priority: ${(promise.priority_score * 100).toFixed(0)}%
                        </span>
                    </div>
                    
                    <div class="promise-meta">
                        <span class="source-tag">
                            <i class="bi bi-link-45deg"></i> ${source}
                        </span>
                        <br>
                        <small class="text-muted">
                            <i class="bi bi-clock"></i> ${formatDate(promise.created_at)}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Show promise detail modal
 */
async function showPromiseDetail(promiseId) {
    try {
        const response = await fetch(`/api/promises/${promiseId}`);
        if (!response.ok) throw new Error('Failed to fetch promise details');
        
        const promise = await response.json();
        
        // Sanitize content
        const title = escapeHtml(promise.title || 'Untitled Promise');
        const description = escapeHtml(promise.description || 'No description available');
        const source = escapeHtml(promise.source || 'Unknown');
        const sourceUrl = promise.source_url || '#';
        
        document.getElementById('promiseModalTitle').textContent = promise.title;
        document.getElementById('promiseModalBody').innerHTML = `
            <div class="mb-3">
                <h6>Description</h6>
                <p>${description}</p>
            </div>
            
            <div class="mb-3">
                <h6>Source</h6>
                <span class="source-tag">${source}</span>
                ${sourceUrl !== '#' ? `<br><a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary mt-2">
                    <i class="bi bi-box-arrow-up-right"></i> View Source
                </a>` : ''}
                <p class="xss-note mt-2">Note: External links are sanitized for security</p>
            </div>
            
            <div class="mb-3">
                <h6>Scores</h6>
                <div class="row">
                    <div class="col-6 mb-3">
                        <label class="form-label">Feasibility</label>
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${promise.feasibility_score * 100}%">
                                ${(promise.feasibility_score * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <label class="form-label">Impact</label>
                        <div class="progress">
                            <div class="progress-bar bg-warning" style="width: ${promise.impact_score * 100}%">
                                ${(promise.impact_score * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <label class="form-label">Priority</label>
                        <div class="progress">
                            <div class="progress-bar bg-danger" style="width: ${promise.priority_score * 100}%">
                                ${(promise.priority_score * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <label class="form-label">Legislative Complexity</label>
                        <div class="progress">
                            <div class="progress-bar bg-info" style="width: ${promise.legislative_complexity * 100}%">
                                ${(promise.legislative_complexity * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <h6>Budget Required</h6>
                <p class="h4 text-primary">$${promise.budget_required.toFixed(1)}M</p>
            </div>
            
            <div class="mb-3">
                <h6>Timestamps</h6>
                <small class="text-muted">
                    Created: ${formatDate(promise.created_at)}<br>
                    Updated: ${formatDate(promise.updated_at)}
                </small>
            </div>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('promiseModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading promise details:', error);
        showToast('Failed to load promise details', 'danger');
    }
}

/**
 * Update statistics
 */
function updateStats() {
    const totalCount = promises.length;
    document.getElementById('totalCount').textContent = totalCount;
    
    if (totalCount === 0) {
        document.getElementById('avgFeasibility').textContent = '0.0';
        document.getElementById('avgImpact').textContent = '0.0';
        document.getElementById('highPriorityCount').textContent = '0';
        return;
    }
    
    const avgFeasibility = promises.reduce((sum, p) => sum + p.feasibility_score, 0) / totalCount;
    const avgImpact = promises.reduce((sum, p) => sum + p.impact_score, 0) / totalCount;
    const highPriorityCount = promises.filter(p => p.priority_score > 0.7).length;
    
    document.getElementById('avgFeasibility').textContent = avgFeasibility.toFixed(2);
    document.getElementById('avgImpact').textContent = avgImpact.toFixed(2);
    document.getElementById('highPriorityCount').textContent = highPriorityCount;
}

/**
 * Initialize theme toggle
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

/**
 * Update theme toggle icon
 */
function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
}

/**
 * Initialize manual scrape button
 */
function initScrapeButton() {
    const scrapeBtn = document.getElementById('scrapeBtn');
    
    scrapeBtn.addEventListener('click', async function() {
        const originalHtml = scrapeBtn.innerHTML;
        scrapeBtn.disabled = true;
        scrapeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scraping...';
        
        try {
            const response = await fetch('/api/scrape/now', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showToast('Scrape completed successfully!');
                setTimeout(() => fetchPromises(), 1000);
            } else {
                showToast(`Scrape failed: ${result.message}`, 'danger');
            }
            
        } catch (error) {
            console.error('Error triggering scrape:', error);
            showToast('Failed to trigger scrape', 'danger');
        } finally {
            scrapeBtn.disabled = false;
            scrapeBtn.innerHTML = originalHtml;
        }
    });
}

/**
 * Update status message
 */
function updateStatusMessage(message, type = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    
    const alertDiv = statusDiv.closest('.alert');
    alertDiv.className = `alert alert-${type} d-flex align-items-center`;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toastBody = document.getElementById('toastBody');
    const toastElement = document.getElementById('notificationToast');
    
    toastBody.textContent = message;
    
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    
    toast.show();
}

/**
 * Get score CSS class based on value
 */
function getScoreClass(score) {
    if (score >= 0.7) return 'score-high';
    if (score >= 0.4) return 'score-medium';
    return 'score-low';
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
}

/**
 * Escape HTML to prevent XSS attacks
 * IMPORTANT: Always sanitize user-generated content
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
