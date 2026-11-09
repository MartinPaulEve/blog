// Paragraph/heading anchor links (_plugins/paragraph_anchors.rb,
// assets/css/anchors.css). Clicking an anchor copies the full URL with its
// fragment to the clipboard, moves the address bar to that fragment without
// scrolling, and shows the "Link copied" tag for a moment. The page never
// scrolls on a click: the reader is already looking at the paragraph.
//
// Loaded synchronously from <head> so the handler is armed before any
// content is clickable; it touches the DOM only when a click arrives.
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

    function flash(anchor, className) {
        anchor.classList.remove('is-copied', 'is-failed');
        anchor.classList.add(className);
        window.clearTimeout(anchor._copiedTimer);
        anchor._copiedTimer = window.setTimeout(function () {
            anchor.classList.remove(className);
        }, COPIED_MS);
    }

    // Older copy path, used when the async clipboard API is missing or
    // refuses (e.g. Chrome's "document is not focused" on a first click).
    function legacyCopy(text) {
        var area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.top = '0';
        area.style.left = '0';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        var ok = false;
        try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
        document.body.removeChild(area);
        return ok;
    }

    function finish(anchor, copied) {
        if (copied) {
            flash(anchor, 'is-copied');
            announce('Link copied to clipboard');
        } else {
            flash(anchor, 'is-failed');
            announce('Could not copy the link; the address bar now shows it');
        }
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

        event.preventDefault();
        event.stopPropagation();

        var url = fragmentUrl(anchor);
        var hash = anchor.getAttribute('href');
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, '', hash);
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(function () {
                finish(anchor, true);
            }, function () {
                finish(anchor, legacyCopy(url));
            });
        } else {
            finish(anchor, legacyCopy(url));
        }
    }, true);
})();
