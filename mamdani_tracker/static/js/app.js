/**
 * Mamdani Promise Tracker - Frontend Application
 */

// ============ Global State ============
let socket = null;
let currentPromises = [];
let currentFilters = {
    category: '',
    status: '',
    sort: 'rank'
};

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Mamdani Promise Tracker initialized');

    initializeWebSocket();
    loadStats();
    loadPromises();
    setupEventListeners();
});

// ============ WebSocket Connection ============
function initializeWebSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('✅ Connected to server');
        updateConnectionStatus('LIVE', true);
        showNotification('Connection Established', 'Real-time updates are now active', 'success');
    });

    socket.on('disconnect', () => {
        console.log('❌ Disconnected from server');
        updateConnectionStatus('OFFLINE', false);
    });

    socket.on('connected', (data) => {
        console.log('Server message:', data.message);
    });

    socket.on('promise_update', (data) => {
        console.log('📢 Promise update received:', data);
        handlePromiseUpdate(data);
    });

    socket.on('promises_data', (data) => {
        console.log('📊 Promises data received');
        currentPromises = data.promises;
        renderPromises(currentPromises);
    });
}

function updateConnectionStatus(status, isLive) {
    const statusEl = document.getElementById('connection-status');
    const badge = statusEl.closest('.live-badge');

    statusEl.textContent = status;

    if (isLive) {
        badge.style.background = 'rgba(0, 255, 136, 0.1)';
        badge.style.borderColor = 'var(--success)';
        badge.style.color = 'var(--success)';
    } else {
        badge.style.background = 'rgba(255, 68, 68, 0.1)';
        badge.style.borderColor = 'var(--error)';
        badge.style.color = 'var(--error)';
    }
}

// ============ Data Loading ============
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('stat-total').textContent = data.total_promises;
        document.getElementById('stat-delivered').textContent = data.status_breakdown['Delivered'] || 0;
        document.getElementById('stat-progress').textContent = data.status_breakdown['In Progress'] || 0;
        document.getElementById('stat-likelihood').textContent = Math.round(data.average_likelihood * 100) + '%';

        if (data.last_scrape) {
            const lastScanTime = new Date(data.last_scrape.scrape_time);
            document.getElementById('last-scan-time').textContent = formatRelativeTime(lastScanTime);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadPromises() {
    try {
        const params = new URLSearchParams(currentFilters);
        const response = await fetch(`/api/promises?${params}`);
        const data = await response.json();

        currentPromises = data.promises;
        renderPromises(currentPromises);
    } catch (error) {
        console.error('Error loading promises:', error);
        showError('Failed to load promises. Please try again.');
    }
}

// ============ Rendering ============
function renderPromises(promises) {
    const container = document.getElementById('promises-container');

    if (promises.length === 0) {
        container.innerHTML = `
            <div class="loading-state">
                <p style="color: var(--text-secondary);">No promises found matching your filters.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = promises.map(promise => `
        <div class="promise-card" onclick="showPromiseDetails(${promise.id})">
            <div class="promise-header">
                <div class="promise-rank">#${promise.likelihood_rank}</div>
                <div class="promise-main">
                    <h3 class="promise-title">${escapeHtml(promise.title)}</h3>
                    <div class="promise-meta">
                        <span class="badge badge-category">${escapeHtml(promise.category || 'Other')}</span>
                        <span class="badge badge-status ${getStatusClass(promise.status)}">${escapeHtml(promise.status)}</span>
                    </div>
                </div>
            </div>

            <p class="promise-description">${escapeHtml(promise.description)}</p>

            <div class="promise-likelihood">
                <div class="likelihood-bar-container">
                    <div class="likelihood-bar" style="width: ${promise.likelihood_score * 100}%"></div>
                </div>
                <div class="likelihood-score">${Math.round(promise.likelihood_score * 100)}%</div>
            </div>

            <div class="promise-factors">
                <div class="factor">
                    <span class="factor-icon">💰</span>
                    <span>${escapeHtml(promise.budget_required || 'Unknown')} Budget</span>
                </div>
                <div class="factor">
                    <span class="factor-icon">⚙️</span>
                    <span>${escapeHtml(promise.legislative_complexity || 'Unknown')} Complexity</span>
                </div>
                <div class="factor">
                    <span class="factor-icon">👥</span>
                    <span>${Math.round((promise.public_support || 0.5) * 100)}% Public Support</span>
                </div>
            </div>

            <div class="promise-footer">
                <span class="updates-count">
                    ${promise.updates_count || 0} ${promise.updates_count === 1 ? 'update' : 'updates'}
                </span>
                <span class="view-details">
                    View Details →
                </span>
            </div>
        </div>
    `).join('');
}

async function showPromiseDetails(promiseId) {
    try {
        const response = await fetch(`/api/promises/${promiseId}`);
        const data = await response.json();

        const modal = document.getElementById('promise-modal');
        const modalBody = document.getElementById('modal-body');

        modalBody.innerHTML = `
            <div style="margin-bottom: 30px;">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                    <div style="font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, var(--primary-cyan), var(--primary-blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        #${data.promise.likelihood_rank}
                    </div>
                    <h2 style="flex: 1; font-size: 2rem; line-height: 1.3;">${escapeHtml(data.promise.title)}</h2>
                </div>

                <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
                    <span class="badge badge-category">${escapeHtml(data.promise.category || 'Other')}</span>
                    <span class="badge badge-status ${getStatusClass(data.promise.status)}">${escapeHtml(data.promise.status)}</span>
                </div>

                <p style="font-size: 1.1rem; color: var(--text-secondary); line-height: 1.8; margin-bottom: 30px;">
                    ${escapeHtml(data.promise.description)}
                </p>

                <div style="background: rgba(0, 255, 255, 0.05); border-left: 3px solid var(--primary-cyan); padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                    <h3 style="margin-bottom: 15px; color: var(--primary-cyan);">Likelihood Analysis</h3>
                    <div style="white-space: pre-wrap; color: var(--text-secondary); line-height: 1.8;">
                        ${escapeHtml(data.promise.analysis_text || 'Analysis not available.')}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
                    <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 5px;">Likelihood Score</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary-cyan);">
                            ${Math.round(data.promise.likelihood_score * 100)}%
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 5px;">Budget Required</div>
                        <div style="font-size: 1.3rem; font-weight: 600;">
                            ${escapeHtml(data.promise.budget_required || 'Unknown')}
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 5px;">Complexity</div>
                        <div style="font-size: 1.3rem; font-weight: 600;">
                            ${escapeHtml(data.promise.legislative_complexity || 'Unknown')}
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <h3 style="font-size: 1.5rem; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <span>📰</span> Recent Updates (${data.updates.length})
                </h3>

                ${data.updates.length > 0 ? `
                    <div style="display: flex; flex-direction: column; gap: 15px;">
                        ${data.updates.map(update => `
                            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px;">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                    <h4 style="font-size: 1.1rem; flex: 1;">${escapeHtml(update.title)}</h4>
                                    ${update.status_changed ? `
                                        <span class="badge badge-status ${getStatusClass(update.new_status)}">
                                            Status Changed
                                        </span>
                                    ` : ''}
                                </div>
                                <p style="color: var(--text-secondary); margin-bottom: 10px;">
                                    ${escapeHtml(update.content || 'No summary available.')}
                                </p>
                                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--text-muted);">
                                    <span>${escapeHtml(update.source_name)}</span>
                                    <span>${formatRelativeTime(new Date(update.created_at))}</span>
                                </div>
                                ${update.source_url ? `
                                    <a href="${escapeHtml(update.source_url)}" target="_blank" style="color: var(--primary-cyan); text-decoration: none; font-size: 0.9rem; display: inline-block; margin-top: 10px;">
                                        Read full article →
                                    </a>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <p style="color: var(--text-secondary); text-align: center; padding: 40px;">
                        No updates found yet. The system will automatically check for news every 6 hours.
                    </p>
                `}
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading promise details:', error);
        showError('Failed to load promise details.');
    }
}

function closeModal() {
    const modal = document.getElementById('promise-modal');
    modal.classList.remove('active');
}

// ============ Event Handlers ============
function setupEventListeners() {
    // Filter changes
    document.getElementById('filter-category').addEventListener('change', (e) => {
        currentFilters.category = e.target.value;
        loadPromises();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        currentFilters.status = e.target.value;
        loadPromises();
    });

    document.getElementById('filter-sort').addEventListener('change', (e) => {
        currentFilters.sort = e.target.value;
        loadPromises();
    });

    // Close modal on outside click
    document.getElementById('promise-modal').addEventListener('click', (e) => {
        if (e.target.id === 'promise-modal') {
            closeModal();
        }
    });
}

function handlePromiseUpdate(data) {
    const { promise, update, message } = data;

    // Show notification
    showNotification(
        `Promise Update: ${promise.title}`,
        message,
        'info'
    );

    // Reload data
    loadStats();
    loadPromises();
}

// ============ Manual Scrape ============
async function triggerManualScrape() {
    const btn = document.getElementById('btn-refresh');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<span class="refresh-icon" style="animation: spin 1s linear infinite;">↻</span> Scanning...';

    try {
        const response = await fetch('/api/scrape/now', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showNotification('Scan Complete', 'Latest news has been checked for promise updates.', 'success');
            loadStats();
            loadPromises();
        } else {
            showError('Scan failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error triggering scrape:', error);
        showError('Failed to trigger scan. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// ============ Notifications ============
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notifications-container');
    const notification = document.createElement('div');
    notification.className = 'notification';

    let borderColor = 'var(--primary-cyan)';
    if (type === 'success') borderColor = 'var(--success)';
    if (type === 'error') borderColor = 'var(--error)';
    if (type === 'warning') borderColor = 'var(--warning)';

    notification.style.borderColor = borderColor;

    notification.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">${escapeHtml(title)}</div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
        <div class="notification-body">${escapeHtml(message)}</div>
    `;

    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function showError(message) {
    showNotification('Error', message, 'error');
}

// ============ Utility Functions ============
function getStatusClass(status) {
    const statusMap = {
        'Not Yet In Office': 'not-yet',
        'Not Discussed': 'not-yet',
        'In Progress': 'in-progress',
        'Delivered': 'delivered',
        'Failed': 'failed'
    };
    return statusMap[status] || 'not-yet';
}

function formatRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ Export for Global Access ============
window.closeModal = closeModal;
window.showPromiseDetails = showPromiseDetails;
window.triggerManualScrape = triggerManualScrape;
