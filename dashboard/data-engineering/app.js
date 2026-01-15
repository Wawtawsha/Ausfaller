/**
 * Data Engineering Dashboard - Application Logic
 * Handles data fetching and rendering for educational content analytics
 */

// Use relative URL to work both locally and in production
const API_BASE_URL = '';

// Current niche mode for this dashboard
const currentNicheMode = 'data_engineering';

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
 * Fetch data from API endpoint with niche_mode parameter
 */
async function fetchData(endpoint, extraParams = {}) {
    try {
        const url = new URL(`${API_BASE_URL}${endpoint}`, window.location.origin);

        // Always include niche_mode for proper data filtering
        const params = { niche_mode: currentNicheMode, ...extraParams };
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                url.searchParams.set(key, value);
            }
        });

        const response = await fetch(url.toString());
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
    // API returns analyzed_videos, not analyzed_count
    if (metrics.analyzed_videos !== undefined) {
        animateNumber(elements.analyzedCount, metrics.analyzed_videos);
    }
    if (metrics.unique_creators !== undefined) {
        animateNumber(elements.totalCreators, metrics.unique_creators);
    }

    // Update score metrics - API uses avg_edu_value and avg_practical
    updateScoreMetric('avg-clarity', metrics.avg_clarity, 'clarity-bar');
    updateScoreMetric('avg-depth', metrics.avg_depth, 'depth-bar');
    updateScoreMetric('avg-value', metrics.avg_edu_value, 'value-bar');

    // API returns avg_practical, not avg_replicability
    if (metrics.avg_practical !== undefined) {
        const repEl = document.getElementById('avg-replicability');
        const numEl = repEl?.querySelector('.value-num');
        if (numEl) {
            numEl.textContent = parseFloat(metrics.avg_practical).toFixed(1);
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

    // Calculate total for percentages
    const total = data.tools.reduce((sum, t) => sum + (t.mention_count || 0), 0);

    // Filter out empty tool names, limit to top 8
    const tools = data.tools
        .filter(t => t.tool && t.tool.trim() !== '')
        .slice(0, 8);

    const maxCount = Math.max(...tools.map(t => t.mention_count)) || 1;

    elements.toolGrid.innerHTML = `
        <div class="tools-list">
            ${tools.map((tool, i) => {
                // Normalize tool name for color lookup
                const toolName = tool.tool.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                const color = toolColors[toolName] || toolColors[tool.tool] || '#666';
                const width = (tool.mention_count / maxCount) * 100;
                const pct = total > 0 ? ((tool.mention_count / total) * 100).toFixed(1) : 0;
                return `
                    <div class="tool-row" style="animation-delay: ${i * 0.05}s">
                        <div class="tool-label">
                            <span class="tool-dot" style="background: ${color}"></span>
                            <span class="tool-name">${toolName}</span>
                        </div>
                        <div class="tool-bar-wrap">
                            <div class="tool-bar-bg">
                                <div class="tool-bar-fill" style="width: ${width}%; background: ${color}"></div>
                            </div>
                            <span class="tool-stats">${tool.mention_count} <span class="tool-pct">(${pct}%)</span></span>
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

    // Filter out empty content types, calculate total for percentages
    const contentTypes = data.content_types
        .filter(c => c.content_type && c.content_type.trim() !== '' && c.content_type !== 'none')
        .slice(0, 6);
    const total = contentTypes.reduce((sum, c) => sum + c.video_count, 0);
    const maxCount = Math.max(...contentTypes.map(c => c.video_count)) || 1;

    elements.contentTypeChart.innerHTML = `
        <div class="bar-list">
            ${contentTypes.map((type, i) => {
                // Normalize content type name
                const typeName = type.content_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                const color = contentTypeColors[typeName] || contentTypeColors[type.content_type] || '#ff6b2c';
                const width = (type.video_count / maxCount) * 100;
                const pct = total > 0 ? ((type.video_count / total) * 100).toFixed(1) : 0;
                return `
                    <div class="bar-row" style="animation-delay: ${i * 0.08}s">
                        <div class="bar-label">${typeName}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${width}%; background: ${color}"></div>
                        </div>
                        <div class="bar-value">${type.video_count} <span class="bar-pct">(${pct}%)</span></div>
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

    // Filter and group by cloud platform
    const platforms = {};
    data.context.forEach(ctx => {
        const platform = ctx.cloud_platform || 'General';
        if (!platforms[platform]) {
            platforms[platform] = { name: platform, count: 0 };
        }
        platforms[platform].count += ctx.video_count;
    });

    // Sort by count and take top 6
    const topPlatforms = Object.values(platforms)
        .filter(p => p.name && p.name !== '')
        .sort((a, b) => b.count - a.count)
        .slice(0, 6);

    if (elements.contentSources) {
        elements.contentSources.innerHTML = topPlatforms.map(p => {
            const platformName = p.name === 'General' ? 'General / Multi' :
                p.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            return `
                <div class="context-chip">
                    <span class="chip-name">${platformName}</span>
                    <span class="chip-count">${p.count} videos</span>
                </div>
            `;
        }).join('');
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
 * Format analysis text - converts markdown to styled HTML
 */
function formatAnalysisText(text) {
    if (!text) return '<p>No analysis content</p>';

    let html = text;

    // Escape HTML entities first
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Process tables (must be done before other transformations)
    html = processMarkdownTables(html);

    // Horizontal rules
    html = html.replace(/^---+$/gm, '<hr class="analysis-hr">');
    html = html.replace(/^\*\*\*+$/gm, '<hr class="analysis-hr">');

    // Headers (process in order from h1 to h4 to avoid conflicts)
    html = html.replace(/^#### (.+)$/gm, '<h6 class="analysis-h6">$1</h6>');
    html = html.replace(/^### (.+)$/gm, '<h5 class="analysis-h5">$1</h5>');
    html = html.replace(/^## (.+)$/gm, '<h4 class="analysis-h4">$1</h4>');
    html = html.replace(/^# (.+)$/gm, '<h3 class="analysis-h3">$1</h3>');

    // Bold headers at start of line (e.g., **Section Title**)
    html = html.replace(/^\*\*(.+?)\*\*$/gm, '<h4 class="analysis-h4">$1</h4>');

    // Inline formatting
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // Process bullet lists
    html = processMarkdownLists(html);

    // Numbered lists
    html = processNumberedLists(html);

    // Paragraphs - wrap remaining text blocks
    html = html.split('\n\n').map(block => {
        block = block.trim();
        if (!block) return '';
        // Don't wrap if already wrapped in HTML tags
        if (block.startsWith('<')) return block;
        return `<p>${block.replace(/\n/g, '<br>')}</p>`;
    }).join('\n');

    return html;
}

/**
 * Process markdown tables
 */
function processMarkdownTables(text) {
    const lines = text.split('\n');
    let result = [];
    let inTable = false;
    let tableRows = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Check if line looks like a table row
        if (line.startsWith('|') && line.endsWith('|')) {
            // Check if next line is separator (|---|---|)
            const nextLine = lines[i + 1]?.trim() || '';
            const isSeparator = /^\|[\s\-:|]+\|$/.test(line);

            if (!inTable && !isSeparator) {
                inTable = true;
                tableRows = [];
            }

            if (inTable && !isSeparator) {
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                tableRows.push(cells);
            }
        } else if (inTable) {
            // End of table
            result.push(buildTable(tableRows));
            tableRows = [];
            inTable = false;
            result.push(line);
        } else {
            result.push(line);
        }
    }

    // Handle table at end of text
    if (inTable && tableRows.length > 0) {
        result.push(buildTable(tableRows));
    }

    return result.join('\n');
}

function buildTable(rows) {
    if (rows.length === 0) return '';

    const headerRow = rows[0];
    const bodyRows = rows.slice(1);

    let html = '<table class="analysis-table">';
    html += '<thead><tr>';
    headerRow.forEach(cell => {
        html += `<th>${cell}</th>`;
    });
    html += '</tr></thead>';

    if (bodyRows.length > 0) {
        html += '<tbody>';
        bodyRows.forEach(row => {
            html += '<tr>';
            row.forEach(cell => {
                html += `<td>${cell}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody>';
    }

    html += '</table>';
    return html;
}

/**
 * Process markdown bullet lists
 */
function processMarkdownLists(text) {
    const lines = text.split('\n');
    let result = [];
    let inList = false;

    for (const line of lines) {
        const match = line.match(/^(\s*)([-*])\s+(.+)$/);

        if (match) {
            if (!inList) {
                result.push('<ul class="analysis-list">');
                inList = true;
            }
            result.push(`<li>${match[3]}</li>`);
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
    }

    if (inList) {
        result.push('</ul>');
    }

    return result.join('\n');
}

/**
 * Process numbered lists
 */
function processNumberedLists(text) {
    const lines = text.split('\n');
    let result = [];
    let inList = false;

    for (const line of lines) {
        const match = line.match(/^(\s*)\d+\.\s+(.+)$/);

        if (match) {
            if (!inList) {
                result.push('<ol class="analysis-ordered-list">');
                inList = true;
            }
            result.push(`<li>${match[2]}</li>`);
        } else {
            if (inList) {
                result.push('</ol>');
                inList = false;
            }
            result.push(line);
        }
    }

    if (inList) {
        result.push('</ol>');
    }

    return result.join('\n');
}

/**
 * Render top educators leaderboard from analyzed posts
 */
async function renderLeaderboard() {
    const data = await fetchData('/analytics/raw-posts', { limit: 500 });

    if (!data || !data.posts || data.posts.length === 0) {
        elements.leaderboard.innerHTML = `
            <div class="leaderboard-empty">
                <p>No analyzed content yet.</p>
            </div>
        `;
        return;
    }

    // Aggregate by creator
    const creatorStats = {};
    data.posts.forEach(post => {
        const username = post.author_username || 'Unknown';
        if (!creatorStats[username]) {
            creatorStats[username] = {
                username,
                platform: post.platform,
                videos: 0,
                totalClarity: 0,
                totalDepth: 0,
                totalValue: 0,
            };
        }
        const stats = creatorStats[username];
        stats.videos++;

        // Extract educational scores from analysis
        if (post.analysis?.educational) {
            const edu = post.analysis.educational;
            stats.totalClarity += edu.explanation_clarity || 0;
            stats.totalDepth += edu.technical_depth || 0;
            stats.totalValue += edu.educational_value || 0;
        }
    });

    // Calculate averages and sort by educational value
    const creators = Object.values(creatorStats)
        .map(c => ({
            ...c,
            avgClarity: c.videos > 0 ? (c.totalClarity / c.videos).toFixed(1) : 0,
            avgDepth: c.videos > 0 ? (c.totalDepth / c.videos).toFixed(1) : 0,
            avgValue: c.videos > 0 ? (c.totalValue / c.videos).toFixed(1) : 0,
        }))
        .filter(c => c.videos >= 2)  // Require at least 2 videos
        .sort((a, b) => b.avgValue - a.avgValue)
        .slice(0, 10);

    if (creators.length === 0) {
        elements.leaderboard.innerHTML = `
            <div class="leaderboard-empty">
                <p>Not enough analyzed content for rankings.</p>
            </div>
        `;
        return;
    }

    elements.leaderboard.innerHTML = creators.map((creator, i) => `
        <div class="leaderboard-item">
            <div class="rank">${i + 1}</div>
            <div class="creator-info">
                <div class="creator-name">@${creator.username}</div>
                <div class="creator-stats">${creator.videos} videos • ${creator.platform}</div>
            </div>
            <div class="scores">
                <span class="score" title="Educational Value">${creator.avgValue}</span>
            </div>
        </div>
    `).join('');
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
