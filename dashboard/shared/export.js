/**
 * Dashboard Export Functionality
 * Supports PDF, CSV, and PNG exports
 * Based on industry best practices for analytics dashboards
 */

class DashboardExport {
    constructor(options = {}) {
        this.dashboardSelector = options.dashboardSelector || '.container';
        this.filename = options.filename || 'dashboard-report';
        this.scale = options.scale || 2; // Higher scale for better quality
    }

    /**
     * Initialize export buttons
     * Call this after DOM is ready
     */
    init() {
        // Add event listeners to export buttons
        document.querySelectorAll('[data-export]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.currentTarget.dataset.export;
                this.export(format);
            });
        });
    }

    /**
     * Export dashboard in specified format
     * @param {string} format - 'pdf', 'csv', or 'png'
     */
    async export(format) {
        const btn = document.querySelector(`[data-export="${format}"]`);
        if (btn) {
            btn.classList.add('exporting');
            btn.disabled = true;
        }

        try {
            switch (format) {
                case 'pdf':
                    await this.exportPDF();
                    break;
                case 'csv':
                    this.exportCSV();
                    break;
                case 'png':
                    await this.exportPNG();
                    break;
                default:
                    console.warn(`Unknown export format: ${format}`);
            }
        } catch (error) {
            console.error(`Export failed:`, error);
            this.showError(`Export failed: ${error.message}`);
        } finally {
            if (btn) {
                btn.classList.remove('exporting');
                btn.disabled = false;
            }
        }
    }

    /**
     * Export dashboard as PDF
     * Uses html2canvas and jsPDF libraries
     */
    async exportPDF() {
        // Check for required libraries
        if (typeof html2canvas === 'undefined') {
            throw new Error('html2canvas library not loaded');
        }
        if (typeof jspdf === 'undefined' && typeof jsPDF === 'undefined') {
            throw new Error('jsPDF library not loaded');
        }

        const element = document.querySelector(this.dashboardSelector);
        if (!element) {
            throw new Error('Dashboard element not found');
        }

        // Temporarily remove animations for clean capture
        element.classList.add('export-mode');

        try {
            const canvas = await html2canvas(element, {
                scale: this.scale,
                useCORS: true,
                logging: false,
                backgroundColor: getComputedStyle(document.body).backgroundColor || '#0a0a0a'
            });

            const imgData = canvas.toDataURL('image/png');

            // Create PDF (landscape A4)
            const PDF = typeof jsPDF !== 'undefined' ? jsPDF : jspdf.jsPDF;
            const pdf = new PDF({
                orientation: 'landscape',
                unit: 'mm',
                format: 'a4'
            });

            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();

            // Calculate dimensions to fit
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;
            const ratio = Math.min(
                (pageWidth - 20) / imgWidth,
                (pageHeight - 20) / imgHeight
            );

            const width = imgWidth * ratio;
            const height = imgHeight * ratio;
            const x = (pageWidth - width) / 2;
            const y = 10;

            pdf.addImage(imgData, 'PNG', x, y, width, height);

            // Add metadata
            pdf.setProperties({
                title: `${this.filename} - ${new Date().toLocaleDateString()}`,
                creator: 'Trend Intelligence Dashboard'
            });

            // Download
            pdf.save(`${this.filename}-${this.getDateString()}.pdf`);
            this.showSuccess('PDF exported successfully');

        } finally {
            element.classList.remove('export-mode');
        }
    }

    /**
     * Export dashboard as PNG image
     */
    async exportPNG() {
        if (typeof html2canvas === 'undefined') {
            throw new Error('html2canvas library not loaded');
        }

        const element = document.querySelector(this.dashboardSelector);
        if (!element) {
            throw new Error('Dashboard element not found');
        }

        element.classList.add('export-mode');

        try {
            const canvas = await html2canvas(element, {
                scale: this.scale,
                useCORS: true,
                logging: false,
                backgroundColor: getComputedStyle(document.body).backgroundColor || '#0a0a0a'
            });

            // Create download link
            const link = document.createElement('a');
            link.download = `${this.filename}-${this.getDateString()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();

            this.showSuccess('PNG exported successfully');

        } finally {
            element.classList.remove('export-mode');
        }
    }

    /**
     * Export dashboard data as CSV
     * Collects data from metric cards and tables
     */
    exportCSV() {
        const data = this.collectDashboardData();

        if (data.length === 0) {
            throw new Error('No data to export');
        }

        // Convert to CSV format
        const headers = Object.keys(data[0]);
        const csvRows = [
            headers.join(','),
            ...data.map(row =>
                headers.map(header => {
                    const value = row[header] ?? '';
                    // Escape quotes and wrap in quotes if contains comma
                    const escaped = String(value).replace(/"/g, '""');
                    return escaped.includes(',') ? `"${escaped}"` : escaped;
                }).join(',')
            )
        ];

        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Download
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${this.filename}-${this.getDateString()}.csv`;
        link.click();

        // Cleanup
        URL.revokeObjectURL(link.href);

        this.showSuccess('CSV exported successfully');
    }

    /**
     * Collect data from dashboard for CSV export
     * @returns {Array} Array of data objects
     */
    collectDashboardData() {
        const data = [];

        // Collect from metric cards
        document.querySelectorAll('.metric-card').forEach(card => {
            const label = card.querySelector('.metric-label')?.textContent?.trim();
            const value = card.querySelector('.metric-value')?.textContent?.trim();
            if (label && value) {
                data.push({
                    type: 'Metric',
                    label,
                    value: value.replace(/[^\d.,/]/g, ''),
                    category: 'Overview'
                });
            }
        });

        // Collect from tables
        document.querySelectorAll('table').forEach(table => {
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
            table.querySelectorAll('tbody tr').forEach(row => {
                const cells = Array.from(row.querySelectorAll('td'));
                const rowData = { type: 'Table Row' };
                cells.forEach((cell, i) => {
                    rowData[headers[i] || `Column ${i + 1}`] = cell.textContent.trim();
                });
                if (Object.keys(rowData).length > 1) {
                    data.push(rowData);
                }
            });
        });

        // Collect from chart data if available
        if (window.analyticsData) {
            Object.entries(window.analyticsData).forEach(([key, value]) => {
                if (typeof value === 'object' && !Array.isArray(value)) {
                    Object.entries(value).forEach(([subKey, subValue]) => {
                        if (typeof subValue === 'number' || typeof subValue === 'string') {
                            data.push({
                                type: 'Analytics',
                                label: `${key} - ${subKey}`,
                                value: subValue,
                                category: key
                            });
                        }
                    });
                }
            });
        }

        return data;
    }

    /**
     * Export specific chart as PNG
     * @param {HTMLCanvasElement|string} chartElement - Canvas element or selector
     * @param {string} filename - Output filename
     */
    async exportChart(chartElement, filename = 'chart') {
        const element = typeof chartElement === 'string'
            ? document.querySelector(chartElement)
            : chartElement;

        if (!element) {
            throw new Error('Chart element not found');
        }

        let canvas;
        if (element instanceof HTMLCanvasElement) {
            canvas = element;
        } else {
            canvas = await html2canvas(element, {
                scale: this.scale,
                useCORS: true,
                logging: false,
                backgroundColor: 'transparent'
            });
        }

        const link = document.createElement('a');
        link.download = `${filename}-${this.getDateString()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }

    /**
     * Get formatted date string for filenames
     */
    getDateString() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    }

    /**
     * Show success notification
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error notification
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show notification toast
     */
    showNotification(message, type = 'info') {
        // Remove existing notifications
        document.querySelectorAll('.export-notification').forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `export-notification export-notification-${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
            <span class="notification-message">${message}</span>
        `;

        document.body.appendChild(notification);

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

/**
 * Create export toolbar HTML
 * Add this to your dashboard header
 */
function createExportToolbar() {
    return `
        <div class="export-toolbar" role="toolbar" aria-label="Export options">
            <button class="export-btn" data-export="pdf" title="Export as PDF">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                <span>PDF</span>
            </button>
            <button class="export-btn" data-export="csv" title="Export data as CSV">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="8" y1="13" x2="16" y2="13"/>
                    <line x1="8" y1="17" x2="16" y2="17"/>
                    <line x1="10" y1="9" x2="14" y2="9"/>
                </svg>
                <span>CSV</span>
            </button>
            <button class="export-btn" data-export="png" title="Export as image">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
                <span>PNG</span>
            </button>
        </div>
    `;
}

// Export for use
window.DashboardExport = DashboardExport;
window.createExportToolbar = createExportToolbar;
