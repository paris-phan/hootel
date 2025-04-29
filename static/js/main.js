// <!-- {#
//     REFERENCES
//     Written For The Course: [CS 3240, Spring 2025]
  
//     © 2025 Paris Phan | SPDX-License-Identifier: MIT
  
//     Resource: Claude 3.7 Sonnet
//     Author: Anthropic
//     Date: Spring 2024
//     URL: https://claude.ai
  
//     - Visual-only snippets (CSS/layout) assisted by Claude 3.7 Sonnet (Anthropic).
//     - No multi-line algorithms or backend logic were AI-generated.
//     - Full provenance & prompt logs → _documentation/code_references.md
  
//     This reference acts as a record of LLM assistance for all html/css lines in this file.
//   #} -->

document.addEventListener('DOMContentLoaded', function() {

    initMenuToggle();
    initSearchToggle();
    initVideoAutoplay();
    initDestinationsMenuToggle();
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

//unused i think
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

const HootelUtils = {
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


function initDestinationsMenuToggle() {
    // Main Destinations toggle
    const destinationsToggle = document.querySelector('.toggle-link[data-toggle="destinations"]');
    const destinationsSubmenu = document.getElementById('destinations-submenu');
    
    if (destinationsToggle && destinationsSubmenu) {
        // Initially hide the destinations submenu
        destinationsToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle active class
            destinationsToggle.classList.toggle('active');
            
            // Display or hide the destinations column
            if (destinationsToggle.classList.contains('active')) {
                destinationsSubmenu.style.display = 'block';
                
                document.getElementById('americas-submenu').style.display = 'none';
                document.getElementById('asia-submenu').style.display = 'none';
                document.getElementById('europe-submenu').style.display = 'none';
                
                document.querySelectorAll('.toggle-link[data-toggle="americas"], .toggle-link[data-toggle="asia"], .toggle-link[data-toggle="europe"]').forEach(toggle => {
                    toggle.classList.remove('active');
                });
            } else {
                destinationsSubmenu.style.display = 'none';
            }
        });
    }
    
    // Initialize continent toggles
    initContinentToggle('americas');
    initContinentToggle('asia');
    initContinentToggle('europe');
}


function initContinentToggle(continent) {
    const continentToggle = document.querySelector(`.toggle-link[data-toggle="${continent}"]`);
    const continentSubmenu = document.getElementById(`${continent}-submenu`);
    
    if (continentToggle && continentSubmenu) {
        continentToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle active class
            const wasActive = continentToggle.classList.contains('active');
            
            // Remove active from all continent toggles
            document.querySelectorAll('.toggle-link[data-toggle="americas"], .toggle-link[data-toggle="asia"], .toggle-link[data-toggle="europe"]').forEach(toggle => {
                toggle.classList.remove('active');
            });
            
            document.getElementById('americas-submenu').style.display = 'none';
            document.getElementById('asia-submenu').style.display = 'none';
            document.getElementById('europe-submenu').style.display = 'none';
            
            if (!wasActive) {
                continentToggle.classList.add('active');
                
                continentSubmenu.style.display = 'block';
            }
        });
    }
} 