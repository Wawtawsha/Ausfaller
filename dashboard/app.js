/**
 * Trend Intelligence Dashboard
 * Social Media Analytics App
 */

// API Configuration - Update this after Railway deployment
const API_BASE = window.ANALYTICS_API_URL || 'https://social-scraper-api.up.railway.app';

// Chart instances registry - prevents memory leaks
const chartRegistry = new Map();

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
 * Update connection status indicator
 */
function setStatus(connected, message = '') {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Live';
    } else {
        dot.classList.remove('connected');
        text.textContent = message || 'Disconnected';
    }
}

/**
 * Update last updated timestamp
 */
function updateTimestamp() {
    const el = document.getElementById('last-updated');
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
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

    document.getElementById('total-videos').textContent = total;
    document.getElementById('analyzed-videos').textContent = analyzed;
    document.getElementById('avg-hook').textContent = hookStr;
    document.getElementById('avg-viral').textContent = viral;
    document.getElementById('avg-replicability').textContent = replicate;

    // Update progress bars
    const analyzedPercent = total > 0 ? (analyzed / total) * 100 : 0;
    document.querySelector('.metric-bar-fill.analyzed').style.width = `${analyzedPercent}%`;

    if (hookStr !== '—') {
        document.querySelector('.metric-bar-fill.hook').style.width = `${parseFloat(hookStr) * 10}%`;
    }
    if (viral !== '—') {
        document.querySelector('.metric-bar-fill.viral').style.width = `${parseFloat(viral) * 10}%`;
    }
    if (replicate !== '—') {
        document.querySelector('.metric-bar-fill.replicate').style.width = `${parseFloat(replicate) * 10}%`;
    }

    // Update footer
    document.getElementById('video-count-footer').textContent = `${analyzed} videos analyzed`;
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
 * Create doughnut chart
 */
function createDoughnutChart(canvasId, data, key) {
    const aggregated = aggregateByKey(data, key);
    const labels = Object.keys(aggregated);
    const values = Object.values(aggregated);

    if (labels.length === 0) {
        labels.push('No data');
        values.push(1);
    }

    createChart(canvasId, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.primary.slice(0, labels.length),
                borderWidth: 0,
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
            }
        }
    });
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
 * Populate leaderboard table
 */
function updateLeaderboard(videos) {
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

    videos.slice(0, 10).forEach(video => {
        const score = video.replicability_score || 0;
        const scoreClass = score >= 8 ? 'high' : 'medium';
        const difficulty = (video.difficulty || 'unknown').toLowerCase();
        const whyText = video.why_it_works || 'Analysis pending...';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="creator-name">@${video.author_username || 'unknown'}</span></td>
            <td><span class="score-pill ${scoreClass}">${score}/10</span></td>
            <td><span class="difficulty-badge ${difficulty}">${difficulty}</span></td>
            <td class="why-cell" title="${whyText}">${whyText}</td>
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
 * Show error modal
 */
function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-modal').classList.add('visible');
}

/**
 * Main initialization
 */
async function init() {
    try {
        setStatus(false, 'Loading...');

        const data = await fetchAnalytics();

        // Update all components
        updateMetrics(data.summary || {});

        // Hook charts
        createDoughnutChart('hook-types-chart', data.hooks || [], 'hook_type');
        createHorizontalBarChart('hook-techniques-chart', data.hooks || [], 'hook_technique', 'Videos');

        // Audio & Visual charts
        createDoughnutChart('audio-chart', data.audio || [], 'category');
        createDoughnutChart('visual-chart', data.visual || [], 'style');

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

// Manual refresh only - uncomment below for auto-refresh
// setInterval(init, 5 * 60 * 1000);
