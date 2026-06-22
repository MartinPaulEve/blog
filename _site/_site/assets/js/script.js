// Theme toggle (light default / dark). Persisted in localStorage.
(function () {
    const root = document.documentElement;
    const toggle = document.querySelector('.theme-toggle');
    const hljsTheme = document.getElementById('hljs-theme');
    const LIGHT_HLJS = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css';
    const DARK_HLJS = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css';

    function applyTheme(theme) {
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
        }
        if (hljsTheme) {
            hljsTheme.setAttribute('href', theme === 'dark' ? DARK_HLJS : LIGHT_HLJS);
        }
        if (toggle) {
            toggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
        }
    }

    // Sync code theme with the pre-paint setting applied in _head.html.
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');

    if (toggle) {
        toggle.addEventListener('click', () => {
            const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            try { localStorage.setItem('theme', next); } catch (e) {}
        });
    }
})();

// Header scroll effect
const header = document.querySelector('.header');
const menuToggle = document.querySelector('.menu-toggle');
const navDesktop = document.querySelector('.nav-desktop');

window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Mobile menu toggle
menuToggle.addEventListener('click', () => {
    navDesktop.classList.toggle('active');

    if (navDesktop.classList.contains('active')) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Close mobile menu when a link is clicked
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navDesktop.classList.remove('active');
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
