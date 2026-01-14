/**
 * Data Engineering Dashboard - Application Logic
 * Handles data fetching and rendering for educational content analytics
 */

const API_BASE_URL = 'https://ausfaller.up.railway.app';

// DOM Elements
const elements = {
    totalVideos: document.getElementById('total-videos'),
    analyzedCount: document.getElementById('analyzed-count'),
    avgClarity: document.getElementById('avg-clarity'),
    avgDepth: document.getElementById('avg-depth'),
    avgValue: document.getElementById('avg-value'),
    avgReplicability: document.getElementById('avg-replicability'),
    totalCreators: document.getElementById('total-creators'),
    toolGrid: document.getElementById('toolGrid'),
    contentTypeChart: document.getElementById('contentTypeChart'),
    techniqueGrid: document.getElementById('techniqueGrid'),
    skillDistribution: document.getElementById('skillDistribution'),
    contextGrid: document.getElementById('contextGrid'),
    cloudPlatforms: document.getElementById('cloudPlatforms'),
    dataLayers: document.getElementById('dataLayers'),
    patterns: document.getElementById('patterns'),
    strategicAnalysis: document.getElementById('strategicAnalysis'),
    leaderboard: document.getElementById('leaderboard'),
    lastUpdated: document.getElementById('lastUpdated'),
    refreshBtn: document.getElementById('refreshBtn'),
};

// Tool icons mapping
const toolIcons = {
    'Microsoft Fabric': `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.18l6.9 3.45L12 11.09 5.1 7.63 12 4.18zM4 8.81l7 3.5v7.88l-7-3.5V8.81zm9 11.38V12.3l7-3.5v7.89l-7 3.5z"/></svg>`,
    'Azure Data Factory': `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>`,
    'Power BI': `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1zm10 4h-6a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1z"/></svg>`,
    'Databricks': `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`,
    'Synapse': `<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M6 12h12" stroke="#0a0a0a" stroke-width="2"/></svg>`,
    'dbt': `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>`,
};

// Content type colors
const contentTypeColors = {
    'Tutorial': 'var(--accent-primary)',
    'Demo': 'var(--accent-secondary)',
    'Concept': 'var(--accent-warning)',
    'Career': 'var(--accent-tertiary)',
    'Comparison': 'var(--text-muted)',
    'Best Practices': 'var(--accent-info)',
};

// Teaching technique icons
const techniqueIcons = {
    'Screen Share': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
    'Live Coding': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
    'Slides': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 8h6"/><path d="M7 12h10"/></svg>`,
    'Talking Head': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 1 0-16 0"/></svg>`,
    'Whiteboard': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9l6 6"/><path d="M15 9l-6 6"/></svg>`,
    'Animation': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>`,
};

/**
 * Fetch data from API endpoint
 */
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        return null;
    }
}

/**
 * Animate number counting up
 */
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * easeOut);

        if (element.querySelector('.value-num')) {
            element.querySelector('.value-num').textContent = current;
        } else {
            element.textContent = current.toLocaleString();
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Update metric score with bar
 */
function updateScoreMetric(elementId, score, barClass) {
    const element = document.getElementById(elementId);
    const bar = document.querySelector(`.${barClass}`);

    if (element && score !== null && score !== undefined) {
        const numEl = element.querySelector('.value-num');
        if (numEl) {
            animateNumber(element, parseFloat(score).toFixed(1));
            numEl.textContent = parseFloat(score).toFixed(1);
        }
        if (bar) {
            bar.style.width = `${(score / 10) * 100}%`;
        }
    }
}

/**
 * Render educational metrics
 */
async function renderEducationalMetrics() {
    const data = await fetchData('/analytics/educational');
    if (!data) return;

    // Animate main counts
    if (data.total_videos !== undefined) {
        animateNumber(elements.totalVideos, data.total_videos);
    }
    if (data.analyzed_count !== undefined) {
        animateNumber(elements.analyzedCount, data.analyzed_count);
    }
    if (data.unique_creators !== undefined) {
        animateNumber(elements.totalCreators, data.unique_creators);
    }

    // Update score metrics
    updateScoreMetric('avg-clarity', data.avg_clarity, 'clarity-bar');
    updateScoreMetric('avg-depth', data.avg_depth, 'depth-bar');
    updateScoreMetric('avg-value', data.avg_value, 'value-bar');

    if (data.avg_replicability !== undefined) {
        const repEl = document.getElementById('avg-replicability');
        const numEl = repEl?.querySelector('.value-num');
        if (numEl) {
            numEl.textContent = parseFloat(data.avg_replicability).toFixed(1);
        }
    }

    // Update last updated
    elements.lastUpdated.textContent = new Date().toLocaleString();
}

/**
 * Render tool coverage grid
 */
async function renderToolCoverage() {
    const data = await fetchData('/analytics/tools');
    if (!data || !data.tools) {
        elements.toolGrid.innerHTML = '<p class="empty-state">No tool data available</p>';
        return;
    }

    const totalCount = data.tools.reduce((sum, t) => sum + t.count, 0) || 1;

    elements.toolGrid.innerHTML = data.tools.map(tool => {
        const percentage = ((tool.count / totalCount) * 100).toFixed(1);
        const icon = toolIcons[tool.name] || toolIcons['dbt'];

        return `
            <div class="tool-card" data-tool="${tool.name}">
                <div class="tool-icon">${icon}</div>
                <div class="tool-info">
                    <span class="tool-name">${tool.name}</span>
                    <span class="tool-count">${tool.count} videos</span>
                </div>
                <div class="tool-bar">
                    <div class="tool-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="tool-percentage">${percentage}%</span>
            </div>
        `;
    }).join('');
}

/**
 * Render content types bar chart
 */
async function renderContentTypes() {
    const data = await fetchData('/analytics/content-types');
    if (!data || !data.content_types) {
        elements.contentTypeChart.innerHTML = '<p class="empty-state">No content type data</p>';
        return;
    }

    const maxCount = Math.max(...data.content_types.map(c => c.count)) || 1;

    elements.contentTypeChart.innerHTML = data.content_types.map((type, index) => {
        const width = (type.count / maxCount) * 100;
        const color = contentTypeColors[type.name] || 'var(--accent-primary)';

        return `
            <div class="bar-item" style="animation-delay: ${index * 0.1}s">
                <div class="bar-label">${type.name}</div>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${width}%; background: ${color}"></div>
                </div>
                <div class="bar-value">${type.count}</div>
            </div>
        `;
    }).join('');
}

/**
 * Render teaching techniques
 */
async function renderTeachingTechniques() {
    const data = await fetchData('/analytics/teaching-techniques');
    if (!data || !data.techniques) {
        elements.techniqueGrid.innerHTML = '<p class="empty-state">No technique data</p>';
        return;
    }

    const totalCount = data.techniques.reduce((sum, t) => sum + t.count, 0) || 1;

    elements.techniqueGrid.innerHTML = data.techniques.map((technique, index) => {
        const percentage = ((technique.count / totalCount) * 100).toFixed(0);
        const icon = techniqueIcons[technique.name] || techniqueIcons['Screen Share'];

        return `
            <div class="technique-card" style="animation-delay: ${index * 0.08}s">
                <div class="technique-icon">${icon}</div>
                <div class="technique-info">
                    <span class="technique-name">${technique.name}</span>
                    <div class="technique-stats">
                        <span class="technique-count">${technique.count}</span>
                        <span class="technique-pct">${percentage}%</span>
                    </div>
                </div>
                <div class="technique-ring">
                    <svg viewBox="0 0 36 36">
                        <path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        <path class="ring-fill" stroke-dasharray="${percentage}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    </svg>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render skill level distribution
 */
async function renderSkillLevels() {
    const data = await fetchData('/analytics/skill-levels');
    if (!data || !data.levels) {
        elements.skillDistribution.innerHTML = '<p class="empty-state">No skill level data</p>';
        return;
    }

    const totalCount = data.levels.reduce((sum, l) => sum + l.count, 0) || 1;
    const levelColors = {
        'Beginner': 'var(--accent-secondary)',
        'Intermediate': 'var(--accent-primary)',
        'Advanced': 'var(--accent-warning)',
        'Expert': 'var(--accent-danger)',
    };

    elements.skillDistribution.innerHTML = `
        <div class="skill-bars">
            ${data.levels.map((level, index) => {
                const percentage = ((level.count / totalCount) * 100).toFixed(1);
                const color = levelColors[level.name] || 'var(--accent-primary)';
                return `
                    <div class="skill-bar-item" style="animation-delay: ${index * 0.12}s">
                        <div class="skill-bar-header">
                            <span class="skill-name">${level.name}</span>
                            <span class="skill-pct">${percentage}%</span>
                        </div>
                        <div class="skill-bar-track">
                            <div class="skill-bar-fill" style="width: ${percentage}%; background: ${color}"></div>
                        </div>
                        <span class="skill-count">${level.count} videos</span>
                    </div>
                `;
            }).join('')}
        </div>
        <div class="skill-legend">
            ${data.levels.map(level => {
                const color = levelColors[level.name] || 'var(--accent-primary)';
                return `<span class="legend-item"><span class="legend-dot" style="background: ${color}"></span>${level.name}</span>`;
            }).join('')}
        </div>
    `;
}

/**
 * Render data engineering context
 */
async function renderContext() {
    const data = await fetchData('/analytics/data-engineering-context');
    if (!data) return;

    // Cloud platforms
    if (data.cloud_platforms && elements.cloudPlatforms) {
        elements.cloudPlatforms.innerHTML = data.cloud_platforms.map(platform => `
            <div class="context-chip" data-platform="${platform.name.toLowerCase()}">
                <span class="chip-name">${platform.name}</span>
                <span class="chip-count">${platform.count}</span>
            </div>
        `).join('');
    }

    // Data layers
    if (data.data_layers && elements.dataLayers) {
        const layerColors = {
            'Bronze': '#cd7f32',
            'Silver': '#c0c0c0',
            'Gold': '#ffd700',
        };
        elements.dataLayers.innerHTML = data.data_layers.map(layer => `
            <div class="context-chip layer-chip" style="--layer-color: ${layerColors[layer.name] || 'var(--accent-primary)'}">
                <span class="chip-name">${layer.name}</span>
                <span class="chip-count">${layer.count}</span>
            </div>
        `).join('');
    }

    // Patterns
    if (data.patterns && elements.patterns) {
        elements.patterns.innerHTML = data.patterns.map(pattern => `
            <div class="context-chip pattern-chip">
                <span class="chip-name">${pattern.name}</span>
                <span class="chip-count">${pattern.count}</span>
            </div>
        `).join('');
    }
}

/**
 * Render strategic analysis
 */
async function renderStrategicAnalysis() {
    const data = await fetchData('/analytics/strategic-analysis');
    if (!data || !data.analysis) {
        elements.strategicAnalysis.innerHTML = '<p class="empty-state">No strategic analysis available</p>';
        return;
    }

    elements.strategicAnalysis.innerHTML = `
        <div class="analysis-card">
            <div class="analysis-header">
                <span class="analysis-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 16v-4M12 8h.01"/>
                    </svg>
                </span>
                <span class="analysis-timestamp">Generated ${new Date(data.generated_at || Date.now()).toLocaleDateString()}</span>
            </div>
            <div class="analysis-body">
                ${formatAnalysisText(data.analysis)}
            </div>
        </div>
    `;
}

/**
 * Format analysis text with sections
 */
function formatAnalysisText(text) {
    if (!text) return '<p>No analysis content</p>';

    // Split by newlines and format
    const sections = text.split('\n\n');
    return sections.map(section => {
        if (section.startsWith('**') || section.startsWith('##')) {
            const title = section.replace(/^\*\*|^\#\#|\*\*$/g, '').trim();
            return `<h4 class="analysis-section-title">${title}</h4>`;
        }
        if (section.startsWith('- ') || section.startsWith('* ')) {
            const items = section.split('\n').filter(l => l.trim());
            return `<ul class="analysis-list">${items.map(item =>
                `<li>${item.replace(/^[-*]\s*/, '')}</li>`
            ).join('')}</ul>`;
        }
        return `<p>${section}</p>`;
    }).join('');
}

/**
 * Render top creators leaderboard
 */
async function renderLeaderboard() {
    // For now, we'll simulate this with educational metrics
    // In production, this would come from a dedicated endpoint
    const data = await fetchData('/analytics/educational');
    if (!data || !data.top_creators) {
        elements.leaderboard.innerHTML = `
            <div class="leaderboard-empty">
                <span class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="8" r="7"/>
                        <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>
                    </svg>
                </span>
                <p>Leaderboard data coming soon</p>
            </div>
        `;
        return;
    }

    elements.leaderboard.innerHTML = data.top_creators.map((creator, index) => {
        const rank = index + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : '';

        return `
            <div class="leaderboard-item ${rankClass}">
                <span class="leaderboard-rank">${rank}</span>
                <div class="leaderboard-info">
                    <span class="leaderboard-name">${creator.name}</span>
                    <span class="leaderboard-stats">${creator.video_count} videos</span>
                </div>
                <div class="leaderboard-scores">
                    <span class="score clarity" title="Clarity">${creator.avg_clarity?.toFixed(1) || '-'}</span>
                    <span class="score depth" title="Depth">${creator.avg_depth?.toFixed(1) || '-'}</span>
                    <span class="score value" title="Value">${creator.avg_value?.toFixed(1) || '-'}</span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Refresh all dashboard data
 */
async function refreshDashboard() {
    elements.refreshBtn.classList.add('loading');

    try {
        await Promise.all([
            renderEducationalMetrics(),
            renderToolCoverage(),
            renderContentTypes(),
            renderTeachingTechniques(),
            renderSkillLevels(),
            renderContext(),
            renderStrategicAnalysis(),
            renderLeaderboard(),
        ]);
    } catch (error) {
        console.error('Dashboard refresh failed:', error);
    } finally {
        elements.refreshBtn.classList.remove('loading');
    }
}

/**
 * Initialize dashboard
 */
async function init() {
    // Set up refresh button
    elements.refreshBtn?.addEventListener('click', refreshDashboard);

    // Initial data load
    await refreshDashboard();

    // Auto-refresh every 5 minutes
    setInterval(refreshDashboard, 5 * 60 * 1000);
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);
