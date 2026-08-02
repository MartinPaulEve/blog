// Theme toggle (light default / dark). Persisted in localStorage.
(function () {
    const root = document.documentElement;
    const toggle = document.querySelector('.theme-toggle');
    const hljsTheme = document.getElementById('hljs-theme');
    const LIGHT_HLJS = '/assets/highlightjs/styles/atom-one-light.min.css';
    const DARK_HLJS = '/assets/highlightjs/styles/atom-one-dark.min.css';

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

// Mastodon share: Mastodon has no central share URL, so ask for the user's
// instance (remembered) and open its /share composer.
document.querySelectorAll('[data-share-mastodon]').forEach((btn) => {
    btn.addEventListener('click', () => {
        let instance;
        try { instance = localStorage.getItem('mastodon-instance') || ''; } catch (e) { instance = ''; }
        instance = window.prompt('Enter your Mastodon instance (e.g. mastodon.social):', instance);
        if (!instance) return;
        instance = instance.trim().replace(/^https?:\/\//, '').replace(/\/+$/, '');
        if (!instance) return;
        try { localStorage.setItem('mastodon-instance', instance); } catch (e) {}
        const text = (btn.dataset.title || '') + ' ' + (btn.dataset.url || '');
        window.open('https://' + instance + '/share?text=' + encodeURIComponent(text), '_blank', 'noopener');
    });
});

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

// Mobile menu toggle. aria-expanded mirrors the open state for assistive tech.
function setMenuOpen(open) {
    navDesktop.classList.toggle('active', open);
    menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');

    if (open) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
}

menuToggle.addEventListener('click', () => {
    setMenuOpen(!navDesktop.classList.contains('active'));
});

// Escape closes the open mobile menu and returns focus to the toggle.
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navDesktop.classList.contains('active')) {
        setMenuOpen(false);
        menuToggle.focus();
    }
});

// Close mobile menu when a link is clicked
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        setMenuOpen(false);
    });
});

// In-page anchor links: honour reduced-motion preferences and move keyboard
// focus to the target so skip links and TOC links work for keyboard and
// screen-reader users, not just visually.
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const hash = this.getAttribute('href');
        if (hash.length < 2) return;
        const target = document.querySelector(hash);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: prefersReducedMotion.matches ? 'auto' : 'smooth' });
            if (!target.hasAttribute('tabindex')) {
                target.setAttribute('tabindex', '-1');
            }
            target.focus({ preventScroll: true });
        }
    });
});
