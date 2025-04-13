/**
 * Main JavaScript file for Aman website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize menu toggle functionality
    initMenuToggle();
    
    // Initialize search toggle functionality
    initSearchToggle();
    
    // Initialize video background autoplay
    initVideoAutoplay();
});

/**
 * Initialize menu toggle functionality
 */
function initMenuToggle() {
    const hamburgerBtn = document.getElementById('hamburger');
    const headerGlobalNav = document.querySelector('.header__global-nav');
    const headerMenuClose = document.querySelectorAll('.header-menu-close');
    
    if (hamburgerBtn && headerGlobalNav) {
        hamburgerBtn.addEventListener('click', function() {
            headerGlobalNav.classList.add('active');
            document.body.classList.add('menu-open');
        });
        
        headerMenuClose.forEach(element => {
            element.addEventListener('click', function() {
                headerGlobalNav.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
        });
    }
}

/**
 * Initialize search toggle functionality
 */
function initSearchToggle() {
    const searchToggleBtn = document.querySelector('.search-sidebar__toggle-btn');
    const searchSidebar = document.querySelector('.search-sidebar');
    const searchSidebarClose = document.querySelector('.search-sidebar__close');
    const searchSidebarOverlay = document.querySelector('.search-sidebar-overlay');
    
    if (searchToggleBtn && searchSidebar) {
        searchToggleBtn.addEventListener('click', function() {
            searchSidebar.classList.add('active');
            searchSidebarOverlay.classList.add('active');
            document.body.classList.add('search-open');
        });
        
        if (searchSidebarClose) {
            searchSidebarClose.addEventListener('click', function() {
                searchSidebar.classList.remove('active');
                searchSidebarOverlay.classList.remove('active');
                document.body.classList.remove('search-open');
            });
        }
        
        if (searchSidebarOverlay) {
            searchSidebarOverlay.addEventListener('click', function() {
                searchSidebar.classList.remove('active');
                searchSidebarOverlay.classList.remove('active');
                document.body.classList.remove('search-open');
            });
        }
    }
}

/**
 * Initialize video autoplay
 */
function initVideoAutoplay() {
    const videos = document.querySelectorAll('video');
    
    videos.forEach(video => {
        // Only autoplay if video has autoplay attribute
        if (video.hasAttribute('autoplay')) {
            // Play video silently
            video.muted = true;
            video.play().catch(error => {
                console.log('Auto-play prevented: ' + error);
            });
        }
    });
}

/**
 * Reveal elements on scroll
 */
window.addEventListener('scroll', function() {
    const scrollElements = document.querySelectorAll('.scroll-reveal');
    
    scrollElements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.classList.add('revealed');
        }
    });
});

/**
 * Utility functions
 */
const AmanUtils = {
    /**
     * Get viewport width
     * @returns {Number} viewport width
     */
    getViewportWidth: function() {
        return Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    },
    
    /**
     * Check if mobile viewport
     * @returns {Boolean} true if mobile viewport
     */
    isMobile: function() {
        return this.getViewportWidth() <= 768;
    },
    
    /**
     * Format a date for display
     * @param {Date} date Date to format
     * @returns {String} formatted date
     */
    formatDate: function(date) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }
}; 