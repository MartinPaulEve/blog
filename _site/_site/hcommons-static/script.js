/**
 * Knowledge Commons - Static Site JavaScript
 * Simple interactions without frameworks
 */

document.addEventListener('DOMContentLoaded', function() {
  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileOverlay = document.getElementById('mobileOverlay');
  const hamburgerIcon = mobileMenuBtn.querySelector('.hamburger-icon');
  const closeIcon = mobileMenuBtn.querySelector('.close-icon');

  function toggleMobileMenu() {
    const isOpen = mobileMenu.classList.contains('active');
    
    if (isOpen) {
      mobileMenu.classList.remove('active');
      mobileOverlay.classList.remove('active');
      hamburgerIcon.style.display = 'inline';
      closeIcon.style.display = 'none';
      document.body.style.overflow = '';
    } else {
      mobileMenu.classList.add('active');
      mobileOverlay.classList.add('active');
      hamburgerIcon.style.display = 'none';
      closeIcon.style.display = 'inline';
      document.body.style.overflow = 'hidden';
    }
  }

  mobileMenuBtn.addEventListener('click', toggleMobileMenu);
  mobileOverlay.addEventListener('click', toggleMobileMenu);

  // Close mobile menu when clicking a link
  const mobileNavLinks = mobileMenu.querySelectorAll('.mobile-nav-link');
  mobileNavLinks.forEach(function(link) {
    link.addEventListener('click', function() {
      if (mobileMenu.classList.contains('active')) {
        toggleMobileMenu();
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });

  // Header background on scroll
  const header = document.querySelector('.header');
  let lastScroll = 0;

  window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
      header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    } else {
      header.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
  });

  // Newsletter form submission (placeholder)
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const email = this.querySelector('.newsletter-input').value;
      if (email) {
        alert('Thank you for subscribing! (This is a demo)');
        this.querySelector('.newsletter-input').value = '';
      }
    });
  }

  // Button click handlers (placeholder actions)
  document.querySelectorAll('.btn-primary, .btn-primary-sm, .btn-primary-pill, .btn-white').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      if (!this.closest('form') && !this.closest('a')) {
        e.preventDefault();
        const text = this.textContent.trim();
        if (text.includes('Account') || text.includes('Register')) {
          alert('Registration feature coming soon!');
        } else if (text.includes('Subscribe')) {
          // Handled by form
        } else {
          alert('Feature coming soon!');
        }
      }
    });
  });

  document.querySelectorAll('.btn-outline, .btn-outline-sm, .btn-outline-pill, .btn-outline-white').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      if (!this.closest('a')) {
        e.preventDefault();
        alert('Feature coming soon!');
      }
    });
  });

  document.querySelectorAll('.btn-text-arrow').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      alert('Feature coming soon!');
    });
  });

  // Log In button
  document.querySelectorAll('.btn-text').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      alert('Login feature coming soon!');
    });
  });
});
