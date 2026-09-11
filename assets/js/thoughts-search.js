/* Search for /thoughts/: filters the rendered entries in place.
   Every thought is already on the page, so the page is the index —
   rebuilt (and thus "reindexed") on every deploy. Matching is
   case-insensitive AND-of-terms over the thought text, image alt text,
   and the displayed date. No query means everything shows. */

(function () {
    "use strict";

    var input = document.getElementById("thought-search");
    var count = document.getElementById("thought-search-count");
    if (!input || !count) {
        return;
    }

    var entries = Array.prototype.slice.call(
        document.querySelectorAll(".thought-entry")
    );
    var sections = Array.prototype.slice.call(
        document.querySelectorAll(".thoughts-month")
    );
    var nav = document.querySelector(".thoughts-months");

    var haystacks = entries.map(function (entry) {
        var text = entry.querySelector(".thought-text");
        var time = entry.querySelector("time");
        var alts = Array.prototype.slice
            .call(entry.querySelectorAll(".thought-images img"))
            .map(function (img) { return img.alt; })
            .join(" ");
        return (
            (text ? text.textContent : "") + " " +
            alts + " " +
            (time ? time.textContent : "")
        ).toLowerCase();
    });

    function apply() {
        var terms = input.value.trim().toLowerCase().split(/\s+/)
            .filter(Boolean);
        var searching = terms.length > 0;
        var shown = 0;

        entries.forEach(function (entry, index) {
            var match = terms.every(function (term) {
                return haystacks[index].indexOf(term) !== -1;
            });
            entry.hidden = searching && !match;
            if (!entry.hidden) {
                shown += 1;
            }
        });
        sections.forEach(function (section) {
            section.hidden = searching &&
                !section.querySelector(".thought-entry:not([hidden])");
        });
        if (nav) {
            nav.hidden = searching;
        }
        count.hidden = !searching;
        if (searching) {
            count.textContent = shown === 1
                ? "1 thought matches"
                : shown + " thoughts match";
        }
    }

    input.addEventListener("input", apply);
})();
