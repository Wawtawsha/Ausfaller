/**
 * Sparkline Component
 * Lightweight SVG-based sparklines for KPI cards
 * Based on industry best practices from Stephen Few and modern dashboard design
 */

class Sparkline {
    constructor(options = {}) {
        this.width = options.width || 80;
        this.height = options.height || 28;
        this.strokeWidth = options.strokeWidth || 1.5;
        this.fillOpacity = options.fillOpacity || 0.1;
        this.showDot = options.showDot !== false;
        this.animate = options.animate !== false;
    }

    /**
     * Create an SVG sparkline from data points
     * @param {number[]} data - Array of numeric values
     * @param {object} options - Override default options
     * @returns {string} SVG markup
     */
    create(data, options = {}) {
        if (!data || data.length < 2) {
            return this.createEmpty();
        }

        const width = options.width || this.width;
        const height = options.height || this.height;
        const strokeWidth = options.strokeWidth || this.strokeWidth;

        // Calculate bounds with padding for stroke
        const padding = strokeWidth;
        const chartWidth = width - (padding * 2);
        const chartHeight = height - (padding * 2);

        // Normalize data
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        // Generate points
        const points = data.map((val, i) => {
            const x = padding + (i / (data.length - 1)) * chartWidth;
            const y = padding + chartHeight - ((val - min) / range) * chartHeight;
            return { x, y };
        });

        const pathData = points.map((p, i) =>
            `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`
        ).join(' ');

        // Area fill path (extends to bottom)
        const areaPath = pathData +
            ` L ${points[points.length - 1].x.toFixed(2)} ${height - padding}` +
            ` L ${padding} ${height - padding} Z`;

        // Determine trend color
        const trend = data[data.length - 1] - data[0];
        const colorClass = trend > 0 ? 'sparkline-up' : trend < 0 ? 'sparkline-down' : 'sparkline-neutral';

        // Last point for dot
        const lastPoint = points[points.length - 1];

        const animationStyle = this.animate ?
            `stroke-dasharray: 200; stroke-dashoffset: 200; animation: sparkline-draw 0.8s ease-out forwards;` : '';

        return `
            <svg class="sparkline ${colorClass}"
                 width="${width}"
                 height="${height}"
                 viewBox="0 0 ${width} ${height}"
                 role="img"
                 aria-label="Trend: ${trend > 0 ? 'increasing' : trend < 0 ? 'decreasing' : 'stable'}">
                <defs>
                    <linearGradient id="sparkline-gradient-${Date.now()}" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color: currentColor; stop-opacity: ${this.fillOpacity}"/>
                        <stop offset="100%" style="stop-color: currentColor; stop-opacity: 0"/>
                    </linearGradient>
                </defs>
                <path class="sparkline-area" d="${areaPath}" fill="url(#sparkline-gradient-${Date.now()})" />
                <path class="sparkline-line" d="${pathData}" fill="none" stroke="currentColor" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round" style="${animationStyle}"/>
                ${this.showDot ? `<circle class="sparkline-dot" cx="${lastPoint.x.toFixed(2)}" cy="${lastPoint.y.toFixed(2)}" r="2.5" fill="currentColor"/>` : ''}
            </svg>
        `;
    }

    /**
     * Create empty sparkline placeholder
     */
    createEmpty() {
        return `
            <svg class="sparkline sparkline-empty" width="${this.width}" height="${this.height}" role="img" aria-label="No trend data available">
                <line x1="0" y1="${this.height / 2}" x2="${this.width}" y2="${this.height / 2}" stroke="currentColor" stroke-width="1" stroke-dasharray="4,4" opacity="0.3"/>
            </svg>
        `;
    }

    /**
     * Generate sparkline with trend indicator
     * @param {number[]} data - Array of values
     * @param {object} options - Display options
     * @returns {string} HTML with sparkline and trend
     */
    createWithTrend(data, options = {}) {
        const sparkline = this.create(data, options);
        const trend = this.calculateTrend(data);

        return `
            <div class="sparkline-container">
                ${sparkline}
                ${trend.html}
            </div>
        `;
    }

    /**
     * Calculate trend from data
     * @param {number[]} data - Array of values
     * @returns {object} Trend info with HTML
     */
    calculateTrend(data) {
        if (!data || data.length < 2) {
            return { change: 0, percent: 0, direction: 'neutral', html: '' };
        }

        const current = data[data.length - 1];
        const previous = data[0];
        const change = current - previous;
        const percent = previous !== 0 ? ((change / Math.abs(previous)) * 100) : 0;

        let direction, arrow, colorClass;
        if (change > 0) {
            direction = 'up';
            arrow = '↑';
            colorClass = 'trend-up';
        } else if (change < 0) {
            direction = 'down';
            arrow = '↓';
            colorClass = 'trend-down';
        } else {
            direction = 'neutral';
            arrow = '→';
            colorClass = 'trend-neutral';
        }

        const html = `
            <span class="trend-indicator ${colorClass}" aria-label="${Math.abs(percent).toFixed(1)}% ${direction}">
                <span class="trend-arrow">${arrow}</span>
                <span class="trend-value">${Math.abs(percent).toFixed(1)}%</span>
            </span>
        `;

        return { change, percent, direction, html };
    }
}

/**
 * Trend Indicator Component
 * Standalone trend indicator for values with context
 */
class TrendIndicator {
    /**
     * Create trend indicator HTML
     * @param {number} current - Current value
     * @param {number} previous - Previous value for comparison
     * @param {object} options - Display options
     */
    static create(current, previous, options = {}) {
        const format = options.format || 'percent'; // 'percent' or 'value'
        const label = options.label || '';
        const showValue = options.showValue !== false;

        if (previous === undefined || previous === null) {
            return `<span class="trend-indicator trend-new" aria-label="New">NEW</span>`;
        }

        const change = current - previous;
        const percent = previous !== 0 ? ((change / Math.abs(previous)) * 100) : 0;

        let arrow, colorClass, ariaLabel;
        if (change > 0) {
            arrow = '↑';
            colorClass = 'trend-up';
            ariaLabel = 'increased';
        } else if (change < 0) {
            arrow = '↓';
            colorClass = 'trend-down';
            ariaLabel = 'decreased';
        } else {
            arrow = '→';
            colorClass = 'trend-neutral';
            ariaLabel = 'unchanged';
        }

        const displayValue = format === 'percent'
            ? `${Math.abs(percent).toFixed(1)}%`
            : `${Math.abs(change).toFixed(1)}`;

        return `
            <span class="trend-indicator ${colorClass}" aria-label="${ariaLabel} by ${displayValue} ${label}">
                <span class="trend-arrow">${arrow}</span>
                ${showValue ? `<span class="trend-value">${displayValue}</span>` : ''}
                ${label ? `<span class="trend-label">${label}</span>` : ''}
            </span>
        `;
    }

    /**
     * Create comparison indicator (vs target/benchmark)
     */
    static createComparison(current, target, options = {}) {
        const diff = current - target;
        const percent = target !== 0 ? ((diff / target) * 100) : 0;
        const label = options.label || 'vs target';

        let colorClass, status;
        if (diff >= 0) {
            colorClass = 'trend-success';
            status = 'above';
        } else {
            colorClass = 'trend-warning';
            status = 'below';
        }

        return `
            <span class="trend-comparison ${colorClass}" aria-label="${Math.abs(percent).toFixed(1)}% ${status} ${label}">
                <span class="comparison-value">${diff >= 0 ? '+' : ''}${percent.toFixed(1)}%</span>
                <span class="comparison-label">${label}</span>
            </span>
        `;
    }
}

// Export for use
window.Sparkline = Sparkline;
window.TrendIndicator = TrendIndicator;
