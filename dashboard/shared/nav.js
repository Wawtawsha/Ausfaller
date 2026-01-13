/**
 * Shared Niche Navigation Component
 * Creates a top-level navigation bar for switching between niche dashboards
 */

class NicheNavigation {
    constructor() {
        this.currentNiche = this.detectCurrentNiche();
        this.init();
    }

    detectCurrentNiche() {
        const path = window.location.pathname;
        if (path.includes('data-engineering')) return 'data-engineering';
        if (path.includes('bartender')) return 'bartender';
        // Default based on index.html content or first load
        return 'bartender';
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const nav = document.createElement('nav');
        nav.className = 'niche-nav';
        nav.innerHTML = `
            <div class="niche-nav-container">
                <div class="niche-nav-brand">
                    <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    <span class="brand-text">Trend Intelligence</span>
                </div>
                <div class="niche-nav-links">
                    <a href="bartender.html" class="niche-link ${this.currentNiche === 'bartender' ? 'active' : ''}" data-niche="bartender">
                        <span class="niche-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M8 22h8M12 11v11M5 3l7 8 7-8"/>
                            </svg>
                        </span>
                        <span class="niche-label">Bartender</span>
                        <span class="niche-indicator"></span>
                    </a>
                    <a href="data-engineering.html" class="niche-link ${this.currentNiche === 'data-engineering' ? 'active' : ''}" data-niche="data-engineering">
                        <span class="niche-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                                <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
                                <polyline points="7.5 19.79 7.5 14.6 3 12"/>
                                <polyline points="21 12 16.5 14.6 16.5 19.79"/>
                                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                                <line x1="12" y1="22.08" x2="12" y2="12"/>
                            </svg>
                        </span>
                        <span class="niche-label">Data Engineering</span>
                        <span class="niche-indicator"></span>
                    </a>
                </div>
            </div>
        `;

        // Insert at the very beginning of body
        document.body.insertBefore(nav, document.body.firstChild);

        // Add body class for current niche
        document.body.classList.add(`niche-${this.currentNiche}`);
    }

    attachEventListeners() {
        const links = document.querySelectorAll('.niche-link');
        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.classList.add('hover');
            });
            link.addEventListener('mouseleave', () => {
                link.classList.remove('hover');
            });
        });
    }
}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new NicheNavigation();
});
