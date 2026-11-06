/* Whole-log search for /listening/ and its per-month pages — the
   /thoughts/ search (thoughts-search.js) applied to the play log.
   Each page carries one server-rendered month and the month nav is
   plain links, so browsing costs nothing extra. Searching fetches
   /listening/search.json once — the pregzipped .json.gz twin when the
   browser can inflate it — then filters every play in memory:
   case-insensitive AND-of-terms over track, artist, album and the
   displayed date. Matches render in batches of 200 (a "show more"
   button pages through the rest), each linking to its home on its
   month page. Clearing the query restores the month view. */

(function () {
    "use strict";

    var input = document.getElementById("listening-search");
    var count = document.getElementById("listening-search-count");
    var nav = document.querySelector(".thoughts-months");
    var monthList = document.querySelector(".listening-month-list");
    var results = document.getElementById("listening-search-results");
    if (!input || !count || !nav || !monthList || !results) {
        return;
    }

    var BATCH = 200;
    var MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ];

    var index = null;
    var loading = null;
    var matches = [];
    var rendered = 0;
    var list = null;

    var more = document.createElement("button");
    more.type = "button";
    more.className = "thoughts-more";
    more.addEventListener("click", renderMore);

    function monthUrl(iso) {
        return "/listening/" + iso.slice(0, 7) + "/";
    }

    /* "2026-10-04T14:09:08+01:00" -> "4 October 2026, 14:09" — read from
       the string, not through Date, so the entry keeps the timezone it
       was written in (matching the server-rendered dates). */
    function displayDate(iso) {
        return parseInt(iso.slice(8, 10), 10) + " " +
            MONTH_NAMES[parseInt(iso.slice(5, 7), 10) - 1] + " " +
            iso.slice(0, 4) + ", " + iso.slice(11, 16);
    }

    function fetchPlain() {
        return fetch("/listening/search.json").then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        });
    }

    function fetchIndex() {
        if (!window.DecompressionStream) {
            return fetchPlain();
        }
        return fetch("/listening/search.json.gz").then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.arrayBuffer();
        }).then(function (buffer) {
            var bytes = new Uint8Array(buffer);
            /* No gzip magic: the server (or a proxy) already inflated
               the response, so it is the JSON itself. */
            if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) {
                return JSON.parse(new TextDecoder().decode(buffer));
            }
            return new Response(
                new Blob([buffer]).stream()
                    .pipeThrough(new DecompressionStream("gzip"))
            ).json();
        }).catch(fetchPlain);
    }

    function loadIndex() {
        if (loading) {
            return loading;
        }
        count.hidden = false;
        count.textContent = "Loading the log…";
        loading = fetchIndex().then(function (data) {
            index = data.map(function (entry) {
                entry.display = displayDate(entry.d);
                entry.haystack = (entry.t + " " + entry.a + " " +
                    (entry.l || "") + " " + entry.display).toLowerCase();
                return entry;
            });
        }, function (error) {
            loading = null;
            count.textContent =
                "Search is unavailable (the log failed to load).";
            throw error;
        });
        return loading;
    }

    function link(className, href, text) {
        var anchor = document.createElement("a");
        anchor.className = className;
        anchor.href = href;
        anchor.textContent = text;
        return anchor;
    }

    function span(className, text) {
        var element = document.createElement("span");
        element.className = className;
        element.textContent = text;
        return element;
    }

    function renderEntry(entry) {
        var item = document.createElement("li");
        item.className = "play";
        var when = link("play-time play-time-full",
            monthUrl(entry.d) + "#s" + entry.ts, "");
        var time = document.createElement("time");
        time.dateTime = entry.d;
        time.textContent = entry.display;
        when.appendChild(time);
        item.appendChild(when);

        var what = document.createElement("span");
        what.className = "play-what";
        what.appendChild(link("play-track", entry.u, entry.t));
        what.appendChild(document.createTextNode(" "));
        var artist = span("play-artist", "by ");
        artist.appendChild(link("", entry.au, entry.a));
        what.appendChild(artist);
        if (entry.l) {
            what.appendChild(document.createTextNode(" "));
            what.appendChild(span("play-album", "on " + entry.l));
        }
        if (entry.n) {
            what.appendChild(document.createTextNode(" "));
            var badge = span("play-count", "×" + entry.n);
            badge.title = "Played " + entry.n + " times in a row";
            what.appendChild(badge);
        }
        item.appendChild(what);
        return item;
    }

    function renderMore() {
        var slice = matches.slice(rendered, rendered + BATCH);
        var fragment = document.createDocumentFragment();
        slice.forEach(function (entry) {
            fragment.appendChild(renderEntry(entry));
        });
        more.remove();
        list.appendChild(fragment);
        rendered += slice.length;
        if (rendered < matches.length) {
            more.textContent = "Show more (" +
                (matches.length - rendered) + " remaining)";
            results.appendChild(more);
        }
    }

    function searchTerms() {
        return input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    }

    function applySearch() {
        var terms = searchTerms();
        var searching = terms.length > 0;
        nav.hidden = searching;
        monthList.hidden = searching;
        results.hidden = !searching;
        count.hidden = !searching;

        if (!searching) {
            results.textContent = "";
            return;
        }
        if (!index) {
            /* Re-filter once the log arrives; a failed load keeps its
               message and waits for the next keystroke to retry. */
            loadIndex().then(applySearch, function () {});
            return;
        }
        matches = index.filter(function (entry) {
            return terms.every(function (term) {
                return entry.haystack.indexOf(term) !== -1;
            });
        });
        results.textContent = "";
        list = document.createElement("ol");
        list.className = "listening-plays";
        if (matches.length) {
            results.appendChild(list);
        }
        rendered = 0;
        count.textContent = matches.length === 1
            ? "1 play matches"
            : matches.length + " plays match";
        renderMore();
    }

    input.addEventListener("input", applySearch);
})();
