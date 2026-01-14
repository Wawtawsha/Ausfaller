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
    contentSources: document.getElementById('cloudPlatforms'),
    strategicAnalysis: document.getElementById('strategicAnalysis'),
    leaderboard: document.getElementById('leaderboard'),
    lastUpdated: document.getElementById('lastUpdated'),
    refreshBtn: document.getElementById('refreshBtn'),
};

// Tool colors for visual distinction
const toolColors = {
    'Microsoft Fabric': '#f25022',
    'Azure Data Factory': '#0078d4',
    'Power BI': '#f2c811',
    'Databricks': '#ff3621',
    'Snowflake': '#29b5e8',
    'dbt': '#ff694b',
    'Python': '#3776ab',
    'SQL': '#e38c00',
    'Azure (General)': '#0078d4',
    'Other': '#666666',
};

// Content type colors
const contentTypeColors = {
    'Tutorial': '#ff6b2c',
    'Newsletter/Blog': '#00d48a',
    'General': '#ffc107',
    'Course': '#3498db',
    'Tips & Tricks': '#9b59b6',
};

// Skill level colors
const skillLevelColors = {
    'Beginner': '#4ade80',
    'Intermediate': '#ffc107',
    'Advanced': '#ff6b2c',
    'Mixed/All Levels': '#00d48a',
    'Career-Focused': '#3498db',
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
function animateNumber(element, target, duration = 800) {
    if (!element) return;
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * easeOut);

        const numEl = element.querySelector('.value-num');
        if (numEl) {
            numEl.textContent = current;
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

    // Handle nested metrics array from API
    const metrics = data.metrics?.[0] || data;

    if (metrics.total_videos !== undefined) {
        animateNumber(elements.totalVideos, metrics.total_videos);
    }
    if (metrics.analyzed_count !== undefined) {
        animateNumber(elements.analyzedCount, metrics.analyzed_count);
    }
    if (metrics.unique_creators !== undefined) {
        animateNumber(elements.totalCreators, metrics.unique_creators);
    }

    // Update score metrics
    updateScoreMetric('avg-clarity', metrics.avg_clarity, 'clarity-bar');
    updateScoreMetric('avg-depth', metrics.avg_depth, 'depth-bar');
    updateScoreMetric('avg-value', metrics.avg_value, 'value-bar');

    if (metrics.avg_replicability !== undefined) {
        const repEl = document.getElementById('avg-replicability');
        const numEl = repEl?.querySelector('.value-num');
        if (numEl) {
            numEl.textContent = parseFloat(metrics.avg_replicability).toFixed(1);
        }
    }

    elements.lastUpdated.textContent = new Date().toLocaleString();
}

/**
 * Render tool coverage - compact horizontal bars
 */
async function renderToolCoverage() {
    const data = await fetchData('/analytics/tools');
    if (!data?.tools?.length) {
        elements.toolGrid.innerHTML = '<p class="empty-state">No tool data available</p>';
        return;
    }

    // Filter out "Other" for cleaner display, limit to top 8
    const tools = data.tools
        .filter(t => t.tool_name !== 'Other')
        .slice(0, 8);

    const maxCount = Math.max(...tools.map(t => t.video_count)) || 1;

    elements.toolGrid.innerHTML = `
        <div class="tools-list">
            ${tools.map((tool, i) => {
                const color = toolColors[tool.tool_name] || '#666';
                const width = (tool.video_count / maxCount) * 100;
                return `
                    <div class="tool-row" style="animation-delay: ${i * 0.05}s">
                        <div class="tool-label">
                            <span class="tool-dot" style="background: ${color}"></span>
                            <span class="tool-name">${tool.tool_name}</span>
                        </div>
                        <div class="tool-bar-wrap">
                            <div class="tool-bar-bg">
                                <div class="tool-bar-fill" style="width: ${width}%; background: ${color}"></div>
                            </div>
                            <span class="tool-stats">${tool.video_count} <span class="tool-pct">(${tool.percentage}%)</span></span>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Render content types - horizontal bar chart
 */
async function renderContentTypes() {
    const data = await fetchData('/analytics/content-types');
    if (!data?.content_types?.length) {
        elements.contentTypeChart.innerHTML = '<p class="empty-state">No content type data</p>';
        return;
    }

    const maxCount = Math.max(...data.content_types.map(c => c.video_count)) || 1;

    elements.contentTypeChart.innerHTML = `
        <div class="bar-list">
            ${data.content_types.map((type, i) => {
                const color = contentTypeColors[type.content_type] || '#ff6b2c';
                const width = (type.video_count / maxCount) * 100;
                return `
                    <div class="bar-row" style="animation-delay: ${i * 0.08}s">
                        <div class="bar-label">${type.content_type}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${width}%; background: ${color}"></div>
                        </div>
                        <div class="bar-value">${type.video_count} <span class="bar-pct">(${type.percentage}%)</span></div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Render teaching techniques - compact cards
 */
async function renderTeachingTechniques() {
    const data = await fetchData('/analytics/teaching-techniques');
    if (!data?.techniques?.length) {
        elements.techniqueGrid.innerHTML = '<p class="empty-state">No technique data</p>';
        return;
    }

    elements.techniqueGrid.innerHTML = `
        <div class="techniques-list">
            ${data.techniques.map((tech, i) => `
                <div class="technique-item" style="animation-delay: ${i * 0.08}s">
                    <div class="technique-info">
                        <span class="technique-name">${tech.technique}</span>
                        <span class="technique-count">${tech.video_count} videos</span>
                    </div>
                    <div class="technique-pct">${tech.percentage}%</div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render skill level distribution - stacked bar
 */
async function renderSkillLevels() {
    const data = await fetchData('/analytics/skill-levels');
    if (!data?.skill_levels?.length) {
        elements.skillDistribution.innerHTML = '<p class="empty-state">No skill level data</p>';
        return;
    }

    const total = data.skill_levels.reduce((sum, l) => sum + l.video_count, 0);

    elements.skillDistribution.innerHTML = `
        <div class="skill-stack">
            <div class="skill-bar-stacked">
                ${data.skill_levels.map(level => {
                    const color = skillLevelColors[level.skill_level] || '#666';
                    const width = (level.video_count / total) * 100;
                    return `<div class="skill-segment" style="width: ${width}%; background: ${color}" title="${level.skill_level}: ${level.video_count}"></div>`;
                }).join('')}
            </div>
            <div class="skill-legend">
                ${data.skill_levels.map(level => {
                    const color = skillLevelColors[level.skill_level] || '#666';
                    return `
                        <div class="legend-item">
                            <span class="legend-dot" style="background: ${color}"></span>
                            <span class="legend-label">${level.skill_level}</span>
                            <span class="legend-value">${level.percentage}%</span>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

/**
 * Render content sources - source categories
 */
async function renderContext() {
    const data = await fetchData('/analytics/data-engineering-context');
    if (!data?.context?.length) {
        if (elements.contentSources) {
            elements.contentSources.innerHTML = '<p class="empty-state">No source data available</p>';
        }
        return;
    }

    if (elements.contentSources) {
        elements.contentSources.innerHTML = data.context.map(ctx => `
            <div class="context-chip">
                <span class="chip-name">${ctx.source_category}</span>
                <span class="chip-count">${ctx.post_count}</span>
                <span class="chip-creators">${ctx.unique_creators} creators</span>
            </div>
        `).join('');
    }
}

/**
 * Render strategic analysis
 */
async function renderStrategicAnalysis() {
    const data = await fetchData('/analytics/strategic-analysis');
    if (!data?.content) {
        elements.strategicAnalysis.innerHTML = `
            <div class="analysis-empty">
                <p>Strategic analysis will be generated after content is analyzed by AI.</p>
                <p class="analysis-note">Run Gemini analysis on data engineering posts to generate insights.</p>
            </div>
        `;
        return;
    }

    elements.strategicAnalysis.innerHTML = `
        <div class="analysis-card">
            <div class="analysis-body">
                ${formatAnalysisText(data.content)}
            </div>
            <div class="analysis-footer">
                Generated ${new Date(data.updated_at || Date.now()).toLocaleDateString()}
            </div>
        </div>
    `;
}

/**
 * Format analysis text with sections
 */
function formatAnalysisText(text) {
    if (!text) return '<p>No analysis content</p>';

    const sections = text.split('\n\n');
    return sections.map(section => {
        if (section.startsWith('**') || section.startsWith('##')) {
            const title = section.replace(/^\*\*|^\#\#|\*\*$/g, '').trim();
            return `<h4 class="analysis-title">${title}</h4>`;
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
    // For now, show placeholder since we don't have analyzed data
    elements.leaderboard.innerHTML = `
        <div class="leaderboard-empty">
            <p>Leaderboard will populate after content analysis.</p>
            <p class="leaderboard-note">649 videos collected, awaiting AI analysis.</p>
        </div>
    `;
}

/**
 * Refresh all dashboard data
 */
async function refreshDashboard() {
    elements.refreshBtn?.classList.add('loading');

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
        elements.refreshBtn?.classList.remove('loading');
    }
}

/**
 * Initialize dashboard
 */
async function init() {
    elements.refreshBtn?.addEventListener('click', refreshDashboard);
    await refreshDashboard();
    setInterval(refreshDashboard, 5 * 60 * 1000);
}

document.addEventListener('DOMContentLoaded', init);
