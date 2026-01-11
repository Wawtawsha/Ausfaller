// Dashboard App - Social Media Analytics

// Configuration
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8080'
    : 'http://127.0.0.1:8080'; // Update this for production

// Chart instances (for cleanup)
let charts = {};

// Color palette for charts
const COLORS = {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#0ea5e9',
    palette: [
        '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
        '#ec4899', '#f43f5e', '#ef4444', '#f97316',
        '#f59e0b', '#eab308', '#84cc16', '#22c55e',
        '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    ]
};

// Fetch all analytics data
async function fetchAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/analytics/all`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch analytics:', error);
        throw error;
    }
}

// Update summary cards
function updateSummary(summary) {
    document.getElementById('total-videos').textContent = summary.total_videos || 0;
    document.getElementById('analyzed-videos').textContent = summary.analyzed_videos || 0;
    document.getElementById('avg-hook').textContent = summary.avg_hook_strength
        ? parseFloat(summary.avg_hook_strength).toFixed(1)
        : '-';
    document.getElementById('avg-viral').textContent = summary.avg_viral_potential
        ? parseFloat(summary.avg_viral_potential).toFixed(1)
        : '-';
    document.getElementById('avg-replicability').textContent = summary.avg_replicability
        ? parseFloat(summary.avg_replicability).toFixed(1)
        : '-';
}

// Create or update a chart
function createChart(canvasId, type, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#f8fafc',
                    font: { size: 12 }
                }
            }
        }
    };

    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: COLORS.palette.slice(0, labels.length),
                borderColor: 'transparent',
                borderWidth: 0,
            }]
        },
        options: { ...defaultOptions, ...options }
    });
}

// Create bar chart
function createBarChart(canvasId, labels, data, label) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: COLORS.primary,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f8fafc' }
                }
            }
        }
    });
}

// Update hook charts
function updateHookCharts(hooks) {
    // Aggregate by hook type
    const typeCount = {};
    const techniqueCount = {};

    hooks.forEach(h => {
        if (h.hook_type) {
            typeCount[h.hook_type] = (typeCount[h.hook_type] || 0) + parseInt(h.video_count);
        }
        if (h.hook_technique) {
            techniqueCount[h.hook_technique] = (techniqueCount[h.hook_technique] || 0) + parseInt(h.video_count);
        }
    });

    // Hook Types pie chart
    const typeLabels = Object.keys(typeCount);
    const typeData = Object.values(typeCount);
    createChart('hook-types-chart', 'doughnut', typeLabels, typeData);

    // Hook Techniques bar chart
    const techLabels = Object.keys(techniqueCount);
    const techData = Object.values(techniqueCount);
    createBarChart('hook-techniques-chart', techLabels, techData, 'Videos');
}

// Update audio chart
function updateAudioChart(audio) {
    const categoryCount = {};

    audio.forEach(a => {
        if (a.category) {
            categoryCount[a.category] = (categoryCount[a.category] || 0) + parseInt(a.count);
        }
    });

    const labels = Object.keys(categoryCount);
    const data = Object.values(categoryCount);
    createChart('audio-chart', 'doughnut', labels, data);
}

// Update visual chart
function updateVisualChart(visual) {
    const styleCount = {};

    visual.forEach(v => {
        if (v.style) {
            styleCount[v.style] = (styleCount[v.style] || 0) + parseInt(v.count);
        }
    });

    const labels = Object.keys(styleCount);
    const data = Object.values(styleCount);
    createChart('visual-chart', 'doughnut', labels, data);
}

// Update viral factors chart
function updateViralFactorsChart(factors) {
    const labels = factors.map(f => f.factor);
    const data = factors.map(f => parseInt(f.count));
    createBarChart('viral-factors-chart', labels, data, 'Occurrences');
}

// Update replicability leaderboard
function updateLeaderboard(videos) {
    const tbody = document.querySelector('#replicability-table tbody');
    tbody.innerHTML = '';

    if (!videos || videos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #94a3b8;">No data available</td></tr>';
        return;
    }

    videos.forEach(video => {
        const row = document.createElement('tr');

        const scoreClass = video.replicability_score >= 8 ? 'score-high' : 'score-medium';
        const difficultyClass = `difficulty-${(video.difficulty || 'easy').toLowerCase()}`;

        row.innerHTML = `
            <td>@${video.author_username || 'unknown'}</td>
            <td><span class="score-badge ${scoreClass}">${video.replicability_score}/10</span></td>
            <td class="${difficultyClass}">${video.difficulty || 'N/A'}</td>
            <td class="why-text" title="${video.why_it_works || ''}">${video.why_it_works || 'N/A'}</td>
            <td><a href="${video.video_url}" target="_blank" class="video-link">View</a></td>
        `;

        tbody.appendChild(row);
    });
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Hide loading state
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Main initialization
async function init() {
    try {
        const data = await fetchAnalytics();

        // Update all components
        updateSummary(data.summary || {});
        updateHookCharts(data.hooks || []);
        updateAudioChart(data.audio || []);
        updateVisualChart(data.visual || []);
        updateViralFactorsChart(data.viral_factors || []);
        updateLeaderboard(data.top_replicable || []);

        // Update timestamp
        document.getElementById('last-updated').textContent =
            `Last updated: ${new Date().toLocaleString()}`;

        hideLoading();
    } catch (error) {
        hideLoading();
        showError(`Failed to load analytics: ${error.message}. Make sure the API server is running.`);
    }
}

// Auto-refresh every 5 minutes
setInterval(init, 5 * 60 * 1000);

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
