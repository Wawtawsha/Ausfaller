/**
 * Trend Intelligence Dashboard
 * Social Media Analytics App
 */

// API Configuration
const API_BASE = '';  // Same origin - served from Railway

// Chart instances registry - prevents memory leaks
const chartRegistry = new Map();

// Store raw analytics data for filtering
let analyticsData = {
    hooks: [],
    audio: [],
    visual: [],
    viral_factors: []
};

// Active chart filter state
let activeChartFilter = null;

// Color palettes
const COLORS = {
    primary: ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'],
    gradient: {
        blue: ['rgba(59, 130, 246, 0.8)', 'rgba(59, 130, 246, 0.1)'],
        purple: ['rgba(139, 92, 246, 0.8)', 'rgba(139, 92, 246, 0.1)'],
        cyan: ['rgba(6, 182, 212, 0.8)', 'rgba(6, 182, 212, 0.1)'],
    }
};

// Chart.js defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'DM Sans', sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';

/**
 * Show skeleton loading states
 */
function showSkeletons() {
    // Metric cards
    document.querySelectorAll('.metric-value').forEach(el => {
        el.dataset.originalContent = el.innerHTML;
        el.innerHTML = '<span class="skeleton skeleton-block"></span>';
    });

    // Leaderboard
    const tbody = document.getElementById('leaderboard-body');
    if (tbody) {
        tbody.innerHTML = Array(5).fill(`
            <tr class="skeleton-row">
                <td><span class="skeleton skeleton-cell" style="width: 80px;"></span></td>
                <td><span class="skeleton skeleton-cell" style="width: 50px;"></span></td>
                <td><span class="skeleton skeleton-cell" style="width: 60px;"></span></td>
                <td><span class="skeleton skeleton-cell" style="width: 200px;"></span></td>
                <td><span class="skeleton skeleton-cell" style="width: 50px;"></span></td>
            </tr>
        `).join('');
    }

    // Breakdown sections (templates, gaps, red flags)
    ['templates-content', 'gaps-content', 'redflags-content'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = `
                <div class="breakdown-skeleton">
                    ${Array(3).fill(`
                        <div class="breakdown-skeleton-card skeleton">
                            <div class="skeleton-text long"></div>
                            <div class="skeleton-text medium"></div>
                            <div class="skeleton-text short"></div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    });

    // Strategic takeaways
    const takeaways = document.getElementById('strategic-takeaways');
    if (takeaways) {
        takeaways.innerHTML = `
            <div class="takeaways-grid">
                ${Array(4).fill(`
                    <div class="takeaway-item">
                        <div class="skeleton" style="width: 24px; height: 24px; border-radius: 4px;"></div>
                        <div style="flex: 1;">
                            <div class="skeleton skeleton-text long" style="margin-bottom: 4px;"></div>
                            <div class="skeleton skeleton-text medium"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Reply content
    const replyContent = document.getElementById('reply-content');
    if (replyContent) {
        replyContent.innerHTML = `
            <div class="reply-grid">
                ${Array(4).fill(`
                    <div class="reply-section">
                        <div class="skeleton skeleton-text short" style="margin-bottom: 12px;"></div>
                        ${Array(4).fill(`
                            <div class="reply-item">
                                <span class="skeleton skeleton-text" style="width: 60px;"></span>
                                <span class="skeleton skeleton-text" style="width: 80px;"></span>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        `;
    }
}

/**
 * Fetch analytics data from API
 */
async function fetchAnalytics() {
    const response = await fetch(`${API_BASE}/analytics/all`);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
}

/**
 * Fetch most recent AI analysis reply
 */
async function fetchRecentReply() {
    const response = await fetch(`${API_BASE}/analytics/recent-reply`);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
}

/**
 * Update connection status indicator
 */
function setStatus(connected, message = '') {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (!dot || !text) return; // Elements not yet in DOM

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Live';
    } else {
        dot.classList.remove('connected');
        text.textContent = message || 'Disconnected';
    }
}

// Track last refresh time
let lastRefreshTime = null;
let refreshIntervalId = null;

/**
 * Update last updated timestamp
 */
function updateTimestamp() {
    lastRefreshTime = Date.now();
    updateRefreshDisplay();

    // Start interval to update elapsed time
    if (refreshIntervalId) clearInterval(refreshIntervalId);
    refreshIntervalId = setInterval(updateRefreshDisplay, 60000); // Update every minute
}

/**
 * Update the refresh display with elapsed time
 */
function updateRefreshDisplay() {
    const el = document.getElementById('last-updated');
    if (!el) return; // Element not yet in DOM

    if (!lastRefreshTime) {
        el.textContent = '';
        return;
    }

    const elapsed = Date.now() - lastRefreshTime;
    const minutes = Math.floor(elapsed / 60000);

    if (minutes < 1) {
        el.textContent = 'Just now';
    } else if (minutes === 1) {
        el.textContent = '1 min ago';
    } else if (minutes < 60) {
        el.textContent = `${minutes} mins ago`;
    } else {
        const hours = Math.floor(minutes / 60);
        el.textContent = hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    }
}

/**
 * Refresh dashboard with loading indicator
 */
async function refreshDashboard() {
    const btn = document.getElementById('refresh-btn');
    if (!btn || btn.classList.contains('loading')) return; // Prevent double-click

    btn.classList.add('loading');
    try {
        await init();
    } finally {
        btn.classList.remove('loading');
    }
}

/**
 * Update summary metric cards
 */
function updateMetrics(summary) {
    const total = summary.total_videos || 0;
    const analyzed = summary.analyzed_videos || 0;
    const hookStr = summary.avg_hook_strength ? parseFloat(summary.avg_hook_strength).toFixed(1) : '—';
    const viral = summary.avg_viral_potential ? parseFloat(summary.avg_viral_potential).toFixed(1) : '—';
    const replicate = summary.avg_replicability ? parseFloat(summary.avg_replicability).toFixed(1) : '—';

    // Safely update text content
    const totalEl = document.getElementById('total-videos');
    const analyzedEl = document.getElementById('analyzed-videos');
    const hookEl = document.getElementById('avg-hook');
    const viralEl = document.getElementById('avg-viral');
    const replicateEl = document.getElementById('avg-replicability');

    if (totalEl) totalEl.textContent = total;
    if (analyzedEl) analyzedEl.textContent = analyzed;
    if (hookEl) hookEl.textContent = hookStr;
    if (viralEl) viralEl.textContent = viral;
    if (replicateEl) replicateEl.textContent = replicate;

    // Update progress bars
    const analyzedPercent = total > 0 ? (analyzed / total) * 100 : 0;
    const analyzedBar = document.querySelector('.metric-bar-fill.analyzed');
    const hookBar = document.querySelector('.metric-bar-fill.hook');
    const viralBar = document.querySelector('.metric-bar-fill.viral');
    const replicateBar = document.querySelector('.metric-bar-fill.replicate');

    if (analyzedBar) analyzedBar.style.width = `${analyzedPercent}%`;
    if (hookBar && hookStr !== '—') hookBar.style.width = `${parseFloat(hookStr) * 10}%`;
    if (viralBar && viral !== '—') viralBar.style.width = `${parseFloat(viral) * 10}%`;
    if (replicateBar && replicate !== '—') replicateBar.style.width = `${parseFloat(replicate) * 10}%`;

    // Update footer
    const footerEl = document.getElementById('video-count-footer');
    if (footerEl) footerEl.textContent = `${analyzed} videos analyzed`;
}

/**
 * Create or update a chart - prevents the expansion bug
 */
function createChart(canvasId, config) {
    // Destroy existing chart if it exists
    if (chartRegistry.has(canvasId)) {
        chartRegistry.get(canvasId).destroy();
    }

    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Create new chart with fixed dimensions
    const chart = new Chart(ctx, {
        ...config,
        options: {
            ...config.options,
            responsive: true,
            maintainAspectRatio: false, // Critical: prevents height expansion
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            }
        }
    });

    chartRegistry.set(canvasId, chart);
    return chart;
}

/**
 * Aggregate data by key
 */
function aggregateByKey(data, key) {
    const counts = {};
    data.forEach(item => {
        const value = item[key];
        if (value && value !== 'unknown') {
            counts[value] = (counts[value] || 0) + parseInt(item.video_count || item.count || 1);
        }
    });
    return counts;
}

/**
 * Create doughnut chart with optional filter support
 */
function createDoughnutChart(canvasId, data, key, filterType = null) {
    const aggregated = aggregateByKey(data, key);
    const labels = Object.keys(aggregated);
    const values = Object.values(aggregated);

    if (labels.length === 0) {
        labels.push('No data');
        values.push(1);
    }

    // Highlight active filter segment
    const backgroundColors = labels.map((label, i) => {
        if (activeChartFilter && activeChartFilter.type === filterType && activeChartFilter.value === label) {
            return COLORS.primary[i]; // Full color for selected
        }
        return activeChartFilter && activeChartFilter.type === filterType
            ? `${COLORS.primary[i]}40` // Dimmed for non-selected
            : COLORS.primary[i]; // Normal when no filter
    });

    const chart = createChart(canvasId, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                borderWidth: activeChartFilter ? 2 : 0,
                borderColor: labels.map((label, i) =>
                    activeChartFilter?.type === filterType && activeChartFilter?.value === label
                        ? '#fff' : 'transparent'
                ),
                hoverOffset: 8
            }]
        },
        options: {
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 16,
                        font: { size: 11 }
                    }
                }
            },
            onClick: filterType ? (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const label = labels[index];
                    if (label !== 'No data') {
                        setChartFilter(filterType, label);
                    }
                }
            } : undefined
        }
    });

    return chart;
}

/**
 * Create horizontal bar chart
 */
function createHorizontalBarChart(canvasId, data, key, label) {
    const aggregated = aggregateByKey(data, key);

    // Sort by value descending
    const sorted = Object.entries(aggregated)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6); // Top 6

    const labels = sorted.map(([k]) => k.replace(/_/g, ' '));
    const values = sorted.map(([, v]) => v);

    if (labels.length === 0) {
        labels.push('No data');
        values.push(0);
    }

    createChart(canvasId, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderRadius: 4,
                barThickness: 20
            }]
        },
        options: {
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    ticks: { font: { size: 10 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } }
                }
            }
        }
    });
}

/**
 * Create viral factors bar chart
 */
function createViralFactorsChart(factors) {
    const labels = factors.map(f => f.factor?.replace(/_/g, ' ') || 'Unknown');
    const values = factors.map(f => parseInt(f.count) || 0);

    // Gradient colors for bars
    const colors = values.map((_, i) => {
        const opacity = 1 - (i * 0.08);
        return `rgba(139, 92, 246, ${Math.max(0.3, opacity)})`;
    });

    createChart('viral-factors-chart', {
        type: 'bar',
        data: {
            labels: labels.slice(0, 10),
            datasets: [{
                label: 'Occurrences',
                data: values.slice(0, 10),
                backgroundColor: colors,
                borderRadius: 6,
                barThickness: 32
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

/**
 * Set chart filter and refresh related charts
 */
function setChartFilter(filterType, filterValue) {
    // Toggle off if clicking same filter
    if (activeChartFilter && activeChartFilter.type === filterType && activeChartFilter.value === filterValue) {
        clearChartFilter();
        return;
    }

    activeChartFilter = { type: filterType, value: filterValue };
    showFilterIndicator(filterType, filterValue);
    refreshChartsWithFilter();
}

/**
 * Clear active chart filter
 */
function clearChartFilter() {
    activeChartFilter = null;
    hideFilterIndicator();
    refreshChartsWithFilter();
}

/**
 * Show filter indicator badge
 */
function showFilterIndicator(type, value) {
    let indicator = document.getElementById('chart-filter-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'chart-filter-indicator';
        indicator.className = 'chart-filter-indicator';
        const chartsSection = document.getElementById('charts-section');
        if (chartsSection) {
            chartsSection.insertBefore(indicator, chartsSection.firstChild);
        }
    }

    const displayValue = value.replace(/_/g, ' ');
    const displayType = type.replace(/_/g, ' ');
    indicator.innerHTML = `
        <span class="filter-label">Filtered by ${displayType}:</span>
        <span class="filter-value">${displayValue}</span>
        <button class="filter-clear" onclick="clearChartFilter()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    indicator.style.display = 'flex';
}

/**
 * Hide filter indicator
 */
function hideFilterIndicator() {
    const indicator = document.getElementById('chart-filter-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * Refresh all charts with current filter
 */
function refreshChartsWithFilter() {
    let hooksData = analyticsData.hooks;
    let audioData = analyticsData.audio;
    let visualData = analyticsData.visual;

    // Apply filter if active
    if (activeChartFilter) {
        const { type, value } = activeChartFilter;

        if (type === 'hook_type') {
            // Filter hooks data by hook_type
            hooksData = analyticsData.hooks.filter(h => h.hook_type === value);
        } else if (type === 'hook_technique') {
            hooksData = analyticsData.hooks.filter(h => h.hook_technique === value);
        } else if (type === 'audio') {
            audioData = analyticsData.audio.filter(a => a.category === value);
        } else if (type === 'visual') {
            visualData = analyticsData.visual.filter(v => v.style === value);
        }
    }

    // Re-render charts with filtered data
    createDoughnutChart('hook-types-chart', hooksData, 'hook_type', 'hook_type');
    createHorizontalBarChart('hook-techniques-chart', hooksData, 'hook_technique', 'Videos');
    createDoughnutChart('audio-chart', audioData, 'category', 'audio');
    createDoughnutChart('visual-chart', visualData, 'style', 'visual');
}

// Store full leaderboard data for filtering
let allLeaderboardData = [];

/**
 * Populate leaderboard table
 */
function updateLeaderboard(videos, isFiltered = false) {
    // Store full data on initial load (not when filtering)
    if (!isFiltered && videos) {
        allLeaderboardData = videos;
    }

    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = '';

    if (!videos || videos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 40px;">
                    No replicable videos found yet
                </td>
            </tr>
        `;
        return;
    }

    videos.slice(0, 10).forEach((video, index) => {
        const score = video.replicability_score || 0;
        const scoreClass = score >= 8 ? 'high' : 'medium';
        const difficulty = (video.difficulty || 'unknown').toLowerCase();
        const whyText = video.why_it_works || 'Analysis pending...';
        const truncatedWhy = whyText.length > 60 ? whyText.substring(0, 60) + '...' : whyText;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="creator-name">@${video.author_username || 'unknown'}</span></td>
            <td><span class="score-pill ${scoreClass}">${score}/10</span></td>
            <td><span class="difficulty-badge ${difficulty}">${difficulty}</span></td>
            <td class="why-cell">
                <div class="why-content" id="why-${index}">
                    <span class="why-truncated">${truncatedWhy}</span>
                    <span class="why-full" style="display: none;">${whyText}</span>
                </div>
                ${whyText.length > 60 ? `<button class="why-toggle" onclick="toggleWhy(${index})">more</button>` : ''}
            </td>
            <td>
                <a href="${video.video_url || '#'}" target="_blank" class="view-btn">
                    View
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                        <polyline points="15 3 21 3 21 9"/>
                        <line x1="10" y1="14" x2="21" y2="3"/>
                    </svg>
                </a>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Toggle "Why It Works" expansion
 */
function toggleWhy(index) {
    const container = document.getElementById(`why-${index}`);
    const truncated = container.querySelector('.why-truncated');
    const full = container.querySelector('.why-full');
    const btn = container.parentElement.querySelector('.why-toggle');

    if (full.style.display === 'none') {
        truncated.style.display = 'none';
        full.style.display = 'inline';
        btn.textContent = 'less';
    } else {
        truncated.style.display = 'inline';
        full.style.display = 'none';
        btn.textContent = 'more';
    }
}

/**
 * Filter leaderboard by criteria
 */
function filterLeaderboard(filter) {
    let filtered = allLeaderboardData;

    if (filter === 'easy') {
        filtered = allLeaderboardData.filter(v =>
            (v.difficulty || '').toLowerCase() === 'easy'
        );
    } else if (filter === 'score8') {
        filtered = allLeaderboardData.filter(v =>
            (v.replicability_score || 0) >= 8
        );
    }
    // 'all' uses full data

    updateLeaderboard(filtered, true);
}

/**
 * Initialize leaderboard filter click handlers
 */
function initLeaderboardFilters() {
    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
            tag.classList.add('active');

            // Determine filter type from text content
            const text = tag.textContent.toLowerCase();
            let filter = 'all';
            if (text.includes('easy')) filter = 'easy';
            else if (text.includes('8+')) filter = 'score8';

            filterLeaderboard(filter);
        });
    });
}

/**
 * Show error modal
 */
function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-modal').classList.add('visible');
}

/**
 * Get score class for styling
 */
function getScoreClass(score) {
    if (score >= 8) return 'high';
    if (score >= 5) return 'medium';
    return 'low';
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Render the most recent AI analysis reply
 */
function renderRecentReply(data) {
    const contentEl = document.getElementById('reply-content');
    const metaEl = document.getElementById('reply-meta');
    const footerEl = document.getElementById('reply-footer');
    const linkEl = document.getElementById('reply-video-link');

    if (!data || !data.recent_reply) {
        contentEl.innerHTML = `
            <div class="reply-empty">
                <div class="reply-empty-icon">📊</div>
                <p>No analyzed videos yet. Run the pipeline to see AI analysis here.</p>
            </div>
        `;
        return;
    }

    const post = data.recent_reply;
    const analysis = post.analysis || {};

    // Update meta info
    metaEl.innerHTML = `
        <span class="reply-author">@${post.author_username || 'unknown'}</span>
        <span class="reply-time">${formatDate(post.analyzed_at)}</span>
    `;

    // Build the content sections
    const hook = analysis.hook || {};
    const audio = analysis.audio || {};
    const visual = analysis.visual || {};
    const trends = analysis.trends || {};
    const replicability = analysis.replicability || {};
    const emotion = analysis.emotion || {};

    // Build tags from various sources
    const tags = [
        ...(analysis.niche?.sub_niches || []),
        ...(analysis.niche?.keywords || []).slice(0, 5)
    ].filter(Boolean).slice(0, 8);

    contentEl.innerHTML = `
        ${analysis.description ? `<div class="reply-description">${analysis.description}</div>` : ''}

        <div class="reply-grid">
            <div class="reply-section">
                <div class="reply-section-title">Hook Analysis</div>
                <div class="reply-item">
                    <span class="reply-item-label">Type</span>
                    <span class="reply-item-value">${hook.hook_type || '—'}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Technique</span>
                    <span class="reply-item-value">${(hook.hook_technique || '—').replace(/_/g, ' ')}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Strength</span>
                    <span class="reply-item-value score ${getScoreClass(hook.hook_strength)}">${hook.hook_strength || 0}/10</span>
                </div>
                ${hook.hook_text ? `
                <div class="reply-item">
                    <span class="reply-item-label">Text</span>
                    <span class="reply-item-value" style="font-size: 0.75rem; max-width: 150px; text-align: right;">"${hook.hook_text}"</span>
                </div>` : ''}
            </div>

            <div class="reply-section">
                <div class="reply-section-title">Viral Potential</div>
                <div class="reply-item">
                    <span class="reply-item-label">Score</span>
                    <span class="reply-item-value score ${getScoreClass(trends.viral_potential_score)}">${trends.viral_potential_score || 0}/10</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Relatability</span>
                    <span class="reply-item-value score ${getScoreClass(emotion.relatability_score)}">${emotion.relatability_score || 0}/10</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Format</span>
                    <span class="reply-item-value">${(trends.format_originality || '—').replace(/_/g, ' ')}</span>
                </div>
                ${trends.viral_factors?.length ? `
                <div class="reply-tags">
                    ${trends.viral_factors.slice(0, 4).map(f => `<span class="reply-tag">${f.replace(/_/g, ' ')}</span>`).join('')}
                </div>` : ''}
            </div>

            <div class="reply-section">
                <div class="reply-section-title">Audio & Visual</div>
                <div class="reply-item">
                    <span class="reply-item-label">Sound</span>
                    <span class="reply-item-value">${(audio.sound_category || '—').replace(/_/g, ' ')}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Mood</span>
                    <span class="reply-item-value">${audio.sound_mood || '—'}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Style</span>
                    <span class="reply-item-value">${visual.visual_style || '—'}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Camera</span>
                    <span class="reply-item-value">${(visual.camera_type || '—').replace(/_/g, ' ')}</span>
                </div>
            </div>

            <div class="reply-section">
                <div class="reply-section-title">Replicability</div>
                <div class="reply-item">
                    <span class="reply-item-label">Score</span>
                    <span class="reply-item-value score ${getScoreClass(replicability.replicability_score)}">${replicability.replicability_score || 0}/10</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Difficulty</span>
                    <span class="reply-item-value">${replicability.difficulty_level || '—'}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Time</span>
                    <span class="reply-item-value">${(replicability.time_investment || '—').replace(/_/g, ' ')}</span>
                </div>
                <div class="reply-item">
                    <span class="reply-item-label">Budget</span>
                    <span class="reply-item-value">${(replicability.budget_estimate || '—').replace(/_/g, ' ')}</span>
                </div>
            </div>
        </div>

        ${tags.length ? `
        <div class="reply-tags" style="margin-top: 20px;">
            ${tags.map(t => `<span class="reply-tag">${t}</span>`).join('')}
        </div>` : ''}

        ${analysis.why_it_works ? `
        <div class="reply-why">
            <div class="reply-why-title">Why It Works</div>
            <div class="reply-why-text">${analysis.why_it_works}</div>
        </div>` : ''}
    `;

    // Update footer link
    if (post.video_url) {
        linkEl.href = post.video_url;
        footerEl.style.display = 'block';
    } else {
        footerEl.style.display = 'none';
    }
}

/**
 * Fetch strategic analysis
 */
async function fetchStrategicAnalysis() {
    const response = await fetch(`${API_BASE}/analytics/strategic-analysis`);
    if (!response.ok) throw new Error('Failed to fetch strategic analysis');
    return response.json();
}

/**
 * Extract executive summary bullets from markdown
 */
function extractKeyTakeaways(content) {
    // Find the Executive Summary section and extract bullet points
    const summaryMatch = content.match(/## Executive Summary\s*\n([\s\S]*?)(?=\n---|\n## )/);
    if (!summaryMatch) return [];

    const summaryText = summaryMatch[1];
    const bullets = summaryText.match(/^- \*\*(.+?)\*\*(.*)$/gm);

    if (!bullets) return [];

    return bullets.map(bullet => {
        const match = bullet.match(/^- \*\*(.+?)\*\*(.*)$/);
        if (match) {
            return { highlight: match[1], detail: match[2].trim() };
        }
        return { highlight: bullet.replace(/^- /, ''), detail: '' };
    }).slice(0, 4); // Max 4 takeaways
}

/**
 * Render key takeaways (always visible)
 */
function renderKeyTakeaways(data) {
    const takeawaysEl = document.getElementById('strategic-takeaways');

    if (!data || !data.content) {
        takeawaysEl.innerHTML = '';
        takeawaysEl.style.display = 'none';
        return;
    }

    const takeaways = extractKeyTakeaways(data.content);

    if (takeaways.length === 0) {
        takeawaysEl.innerHTML = '';
        takeawaysEl.style.display = 'none';
        return;
    }

    takeawaysEl.style.display = 'block';
    takeawaysEl.innerHTML = `
        <div class="takeaways-grid">
            ${takeaways.map((t, i) => `
                <div class="takeaway-item" style="--delay: ${i}">
                    <div class="takeaway-icon">${['💡', '⚠️', '🎯', '📊'][i] || '•'}</div>
                    <div class="takeaway-text">
                        <span class="takeaway-highlight">${t.highlight}</span>
                        ${t.detail ? `<span class="takeaway-detail">${t.detail}</span>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Extract a section from markdown by heading
 */
function extractSection(content, headingPattern) {
    const regex = new RegExp(`## ${headingPattern}[\\s\\S]*?(?=\\n## |\\n---\\n## |$)`, 'i');
    const match = content.match(regex);
    return match ? match[0] : null;
}

/**
 * Parse templates from Content Playbook section
 */
function parseTemplates(content) {
    const section = extractSection(content, 'Content Playbook');
    if (!section) return [];

    const templates = [];
    const templateBlocks = section.split(/### Template \d+:/);

    templateBlocks.slice(1).forEach(block => {
        const lines = block.trim().split('\n');
        const name = lines[0]?.replace(/[*#]/g, '').trim();

        const template = { name, items: [], why: '' };

        lines.forEach(line => {
            const hookMatch = line.match(/\*\*Hook:\*\*\s*(.+)/);
            const audioMatch = line.match(/\*\*Audio:\*\*\s*(.+)/);
            const visualMatch = line.match(/\*\*Visual:\*\*\s*(.+)/);
            const difficultyMatch = line.match(/\*\*Difficulty:\*\*\s*(.+)/);
            const whyMatch = line.match(/\*\*Why it works:\*\*\s*(.+)/);

            if (hookMatch) template.items.push({ label: 'Hook', value: hookMatch[1] });
            if (audioMatch) template.items.push({ label: 'Audio', value: audioMatch[1] });
            if (visualMatch) template.items.push({ label: 'Visual', value: visualMatch[1] });
            if (difficultyMatch) template.items.push({ label: 'Difficulty', value: difficultyMatch[1] });
            if (whyMatch) template.why = whyMatch[1];
        });

        if (template.name) templates.push(template);
    });

    return templates;
}

/**
 * Parse gaps from Gaps & Opportunities section
 */
function parseGaps(content) {
    const section = extractSection(content, 'Gaps');
    if (!section) return [];

    const gaps = [];
    const lines = section.split('\n');
    let currentGap = null;

    lines.forEach(line => {
        const numMatch = line.match(/^\d+\.\s+\*\*(.+?)\*\*\s*[-–]?\s*(.*)$/);
        if (numMatch) {
            if (currentGap) gaps.push(currentGap);
            currentGap = { title: numMatch[1], description: numMatch[2] || '' };
        } else if (currentGap && line.trim() && !line.startsWith('#')) {
            currentGap.description += ' ' + line.trim();
        }
    });
    if (currentGap) gaps.push(currentGap);

    return gaps.slice(0, 6); // Max 6
}

/**
 * Parse red flags from Red Flags section
 */
function parseRedFlags(content) {
    const section = extractSection(content, 'Red Flags');
    if (!section) return [];

    const flags = [];
    const subsections = section.split(/### /);

    subsections.slice(1).forEach(sub => {
        const lines = sub.trim().split('\n');
        const title = lines[0]?.trim();
        const items = [];

        lines.slice(1).forEach(line => {
            const itemMatch = line.match(/^- (.+)$/);
            if (itemMatch) items.push(itemMatch[1]);
        });

        if (title && items.length > 0) {
            flags.push({ title, items });
        }
    });

    return flags;
}

/**
 * Render templates section
 */
function renderTemplates(data) {
    const contentEl = document.getElementById('templates-content');

    if (!data || !data.content) {
        contentEl.innerHTML = '<div class="breakdown-loading">No templates available</div>';
        return;
    }

    const templates = parseTemplates(data.content);

    if (templates.length === 0) {
        contentEl.innerHTML = '<div class="breakdown-loading">No templates found in analysis</div>';
        return;
    }

    contentEl.innerHTML = `
        <div class="templates-grid">
            ${templates.map(t => `
                <div class="template-card">
                    <h4>${t.name}</h4>
                    ${t.items.map(item => `
                        <div class="template-item">
                            <span class="template-label">${item.label}:</span>
                            <span class="template-value">${item.value}</span>
                        </div>
                    `).join('')}
                    ${t.why ? `<div class="template-why">${t.why}</div>` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render gaps section
 */
function renderGaps(data) {
    const contentEl = document.getElementById('gaps-content');

    if (!data || !data.content) {
        contentEl.innerHTML = '<div class="breakdown-loading">No gaps data available</div>';
        return;
    }

    const gaps = parseGaps(data.content);

    if (gaps.length === 0) {
        contentEl.innerHTML = '<div class="breakdown-loading">No gaps found in analysis</div>';
        return;
    }

    contentEl.innerHTML = `
        <div class="gaps-grid">
            ${gaps.map(g => `
                <div class="gap-card">
                    <h4>${g.title}</h4>
                    <p>${g.description}</p>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render red flags section
 */
function renderRedFlags(data) {
    const contentEl = document.getElementById('redflags-content');

    if (!data || !data.content) {
        contentEl.innerHTML = '<div class="breakdown-loading">No warnings available</div>';
        return;
    }

    const flags = parseRedFlags(data.content);

    if (flags.length === 0) {
        contentEl.innerHTML = '<div class="breakdown-loading">No red flags found in analysis</div>';
        return;
    }

    contentEl.innerHTML = `
        <div class="redflags-grid">
            ${flags.map(f => `
                <div class="redflag-card">
                    <h4>${f.title}</h4>
                    <ul>
                        ${f.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render strategic analysis markdown
 */
function renderStrategicAnalysis(data) {
    const contentEl = document.getElementById('strategic-content');
    const updatedEl = document.getElementById('strategic-updated');

    // Render key takeaways first (always visible)
    renderKeyTakeaways(data);

    // Render breakdown sections
    renderTemplates(data);
    renderGaps(data);
    renderRedFlags(data);

    if (!data || !data.content) {
        contentEl.innerHTML = `
            <div class="strategic-empty">
                <p>No strategic analysis available yet. Run analysis to generate insights.</p>
            </div>
        `;
        return;
    }

    // Update timestamp
    if (data.updated_at) {
        updatedEl.textContent = `Updated ${formatDate(data.updated_at)}`;
    }

    // Render markdown
    contentEl.innerHTML = `<div class="markdown-body">${marked.parse(data.content)}</div>`;
}

/**
 * Toggle strategic analysis section
 */
let strategicExpanded = true;  // Open by default
function toggleStrategicAnalysis() {
    const contentEl = document.getElementById('strategic-content');
    const chevronEl = document.getElementById('strategic-chevron');

    strategicExpanded = !strategicExpanded;

    if (strategicExpanded) {
        contentEl.classList.add('expanded');
        chevronEl.classList.add('rotated');
    } else {
        contentEl.classList.remove('expanded');
        chevronEl.classList.remove('rotated');
    }
}

/**
 * Main initialization
 */
async function init() {
    try {
        setStatus(false, 'Loading...');

        // Show skeleton loading states immediately
        showSkeletons();

        // Fetch analytics, recent reply, and strategic analysis in parallel
        const [data, replyData, strategicData] = await Promise.all([
            fetchAnalytics(),
            fetchRecentReply().catch(err => {
                console.warn('Failed to fetch recent reply:', err);
                return null;
            }),
            fetchStrategicAnalysis().catch(err => {
                console.warn('Failed to fetch strategic analysis:', err);
                return null;
            })
        ]);

        // Update all components
        updateMetrics(data.summary || {});

        // Render recent AI reply
        renderRecentReply(replyData);

        // Render strategic analysis
        renderStrategicAnalysis(strategicData);

        // Store raw data for cross-chart filtering
        analyticsData.hooks = data.hooks || [];
        analyticsData.audio = data.audio || [];
        analyticsData.visual = data.visual || [];
        analyticsData.viral_factors = data.viral_factors || [];

        // Clear any active filter on refresh
        activeChartFilter = null;
        hideFilterIndicator();

        // Hook charts (with filter support)
        createDoughnutChart('hook-types-chart', data.hooks || [], 'hook_type', 'hook_type');
        createHorizontalBarChart('hook-techniques-chart', data.hooks || [], 'hook_technique', 'Videos');

        // Audio & Visual charts (with filter support)
        createDoughnutChart('audio-chart', data.audio || [], 'category', 'audio');
        createDoughnutChart('visual-chart', data.visual || [], 'style', 'visual');

        // Viral factors
        createViralFactorsChart(data.viral_factors || []);

        // Leaderboard
        updateLeaderboard(data.top_replicable || []);

        // Update status
        setStatus(true);
        updateTimestamp();

    } catch (error) {
        console.error('Dashboard error:', error);
        setStatus(false, 'Error');
        showError(error.message || 'Failed to connect to analytics API');
    }
}

// Initialize on load - only once, no auto-refresh to prevent expansion
document.addEventListener('DOMContentLoaded', init);

// Section navigation - update active pill on scroll
document.addEventListener('DOMContentLoaded', () => {
    // Initialize leaderboard filters
    initLeaderboardFilters();

    const navPills = document.querySelectorAll('.nav-pill');
    const sections = ['metrics-section', 'strategic-section', 'templates-section', 'gaps-section', 'redflags-section', 'charts-section', 'leaderboard-section'];

    // Smooth scroll on click
    navPills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = pill.getAttribute('href').slice(1);
            const target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Update active pill on scroll
    const updateActiveNav = () => {
        const scrollPos = window.scrollY + 100;

        let activeSection = sections[0];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section && section.offsetTop <= scrollPos) {
                activeSection = sectionId;
            }
        });

        navPills.forEach(pill => {
            const pillSection = pill.getAttribute('href').slice(1);
            pill.classList.toggle('active', pillSection === activeSection);
        });
    };

    window.addEventListener('scroll', updateActiveNav, { passive: true });
    updateActiveNav();
});

// Manual refresh only - uncomment below for auto-refresh
// setInterval(init, 5 * 60 * 1000);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ignore if typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    switch(e.key) {
        case '1': document.getElementById('metrics-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '2': document.getElementById('strategic-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '3': document.getElementById('templates-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '4': document.getElementById('gaps-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '5': document.getElementById('redflags-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '6': document.getElementById('charts-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case '7': document.getElementById('leaderboard-section')?.scrollIntoView({ behavior: 'smooth' }); break;
        case 's': case 'S': toggleStrategicAnalysis(); break;
        case 'r': case 'R': if (!e.ctrlKey && !e.metaKey) { init(); } break;
        case '?': showKeyboardHelp(); break;
    }
});

function showKeyboardHelp() {
    const existing = document.getElementById('keyboard-help');
    if (existing) { existing.remove(); return; }

    const help = document.createElement('div');
    help.id = 'keyboard-help';
    help.className = 'keyboard-help';
    help.innerHTML = `
        <div class="keyboard-help-content">
            <h4>Keyboard Shortcuts</h4>
            <div class="shortcut"><kbd>1-7</kbd> Jump to section</div>
            <div class="shortcut"><kbd>S</kbd> Toggle strategy panel</div>
            <div class="shortcut"><kbd>R</kbd> Refresh data</div>
            <div class="shortcut"><kbd>?</kbd> Toggle this help</div>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    document.body.appendChild(help);
}
