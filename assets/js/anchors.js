// Paragraph/heading anchor links (_plugins/paragraph_anchors.rb,
// assets/css/anchors.css). Clicking an anchor copies the full URL with its
// fragment to the clipboard, moves the address bar to that fragment without
// scrolling, and shows the "Link copied" tag for a moment. Without clipboard
// access (plain http, old browsers) the link just behaves as a normal link.
(function () {
    'use strict';

    var COPIED_MS = 1600;
    var live = null;

    function announce(text) {
        if (!live) {
            live = document.createElement('div');
            live.className = 'sr-only';
            live.setAttribute('aria-live', 'polite');
            document.body.appendChild(live);
        }
        live.textContent = '';
        // Re-set on the next tick so repeated copies are re-announced.
        window.setTimeout(function () { live.textContent = text; }, 50);
    }

    function fragmentUrl(anchor) {
        var hash = anchor.getAttribute('href') || '';
        return window.location.origin + window.location.pathname +
            window.location.search + hash;
    }

    function markCopied(anchor) {
        anchor.classList.add('is-copied');
        window.clearTimeout(anchor._copiedTimer);
        anchor._copiedTimer = window.setTimeout(function () {
            anchor.classList.remove('is-copied');
        }, COPIED_MS);
    }

    // Capture phase, so this runs before script.js's per-link smooth-scroll
    // handler (which would otherwise scroll the reader to the paragraph they
    // are already looking at) and can stop it reaching the anchor.
    document.addEventListener('click', function (event) {
        var anchor = event.target.closest && event.target.closest('a.anchor-link');
        if (!anchor) { return; }
        // Let modified clicks (new tab, etc.) behave as the browser intends.
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
            event.button !== 0) { return; }
        if (!navigator.clipboard || !navigator.clipboard.writeText) { return; }

        event.preventDefault();
        event.stopPropagation();
        var url = fragmentUrl(anchor);
        var hash = anchor.getAttribute('href');
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, '', hash);
        }
        navigator.clipboard.writeText(url).then(function () {
            markCopied(anchor);
            announce('Link copied to clipboard');
        }, function () {
            // Clipboard refused: fall back to a plain navigation to the fragment.
            window.location.hash = hash;
        });
    }, true);
})();
