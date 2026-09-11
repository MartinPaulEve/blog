/* Month view + search for /thoughts/.
   One month is shown at a time (newest by default; the pipe nav and
   URL hash select others), but every thought stays in the DOM, so the
   page is also the search index — rebuilt ("reindexed") on every
   deploy. A query searches across ALL months: matching entries show
   with their month headings regardless of the selected month, and
   clearing the query restores the single-month view. Without
   JavaScript the page degrades to showing every month. Matching is
   case-insensitive AND-of-terms over the thought text, image alt text,
   and the displayed date. */

(function () {
    "use strict";

    var input = document.getElementById("thought-search");
    var count = document.getElementById("thought-search-count");
    var nav = document.querySelector(".thoughts-months");
    var entries = Array.prototype.slice.call(
        document.querySelectorAll(".thought-entry")
    );
    var sections = Array.prototype.slice.call(
        document.querySelectorAll(".thoughts-month")
    );
    if (!input || !count || !nav || !sections.length) {
        return;
    }
    var links = Array.prototype.slice.call(nav.querySelectorAll("a"));

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

    var selected = sections[0].id;

    function showMonth(id) {
        selected = id;
        sections.forEach(function (section) {
            section.hidden = section.id !== id;
        });
        links.forEach(function (link) {
            if (link.getAttribute("href") === "#" + id) {
                link.setAttribute("aria-current", "true");
            } else {
                link.removeAttribute("aria-current");
            }
        });
    }

    function searchTerms() {
        return input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    }

    function applySearch() {
        var terms = searchTerms();
        var searching = terms.length > 0;
        nav.hidden = searching;
        count.hidden = !searching;

        if (!searching) {
            entries.forEach(function (entry) { entry.hidden = false; });
            showMonth(selected);
            return;
        }

        var shown = 0;
        entries.forEach(function (entry, index) {
            var match = terms.every(function (term) {
                return haystacks[index].indexOf(term) !== -1;
            });
            entry.hidden = !match;
            if (match) {
                shown += 1;
            }
        });
        sections.forEach(function (section) {
            section.hidden =
                !section.querySelector(".thought-entry:not([hidden])");
        });
        count.textContent = shown === 1
            ? "1 thought matches"
            : shown + " thoughts match";
    }

    function selectFromHash() {
        var target = location.hash &&
            document.getElementById(location.hash.slice(1));
        var section = target && target.closest(".thoughts-month");
        if (!section) {
            showMonth(sections[0].id);
            return;
        }
        showMonth(section.id);
        // The browser's own jump happened while the target was hidden
        // (or before this script selected the month), so scroll now.
        if (target !== section) {
            target.scrollIntoView();
        }
    }

    window.addEventListener("hashchange", function () {
        if (!searchTerms().length) {
            selectFromHash();
        }
    });
    input.addEventListener("input", applySearch);
    selectFromHash();
})();
