/**
 * LeatherCraft Designer - Main JavaScript (Phase 1)
 * Mobile navigation handling and placeholder interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Navigation Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const isOpen = navMenu.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', isOpen.toString());
        });

        // Close menu when clicking outside
        document.addEventListener('click', (event) => {
            if (!navMenu.contains(event.target) && !navToggle.contains(event.target) && navMenu.classList.contains('open')) {
                navMenu.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // 2. Smooth Scroll for internal anchor links (e.g. #articles, #features)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // 3. Log Phase 1 Initialization Info
    console.log('LeatherCraft Designer - Phase 1 Foundation Initialized.');
});
