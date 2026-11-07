/* Whole-log search for /activity/ and its per-month pages — the
   /thoughts/ search (thoughts-search.js) over every kind of entry.
   Each page carries one server-rendered month and the month nav is
   plain links, so browsing costs nothing extra. Searching fetches
   /activity/search.json once — the pregzipped .json.gz twin when the
   browser can inflate it — then filters every entry in memory:
   case-insensitive AND-of-terms over the text (title and excerpt for a
   post; track, artist and album for a play), image alt text and the
   displayed date. Matches render in batches of 200 as cards of their
   kind, each linking to its home page. Clearing the query restores the
   month view. */

(function () {
    "use strict";

    var input = document.getElementById("activity-search");
    var count = document.getElementById("activity-search-count");
    var nav = document.querySelector(".thoughts-months");
    var monthList = document.querySelector(".activity-month-list");
    var results = document.getElementById("activity-search-results");
    if (!input || !count || !nav || !monthList || !results) {
        return;
    }

    var BATCH = 200;
    var MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ];
    var KICKERS = { p: "Post", t: "Short thought", i: "Today I learned",
                    s: "Listening" };

    var index = null;
    var loading = null;
    var matches = [];
    var rendered = 0;

    var more = document.createElement("button");
    more.type = "button";
    more.className = "thoughts-more";
    more.addEventListener("click", renderMore);

    /* "2026-10-04T14:09:08+01:00" -> "4 October 2026, 14:09" — read from
       the string, not through Date, so the entry keeps the timezone it
       was written in (matching the server-rendered dates). */
    function displayDate(iso, withTime) {
        var day = parseInt(iso.slice(8, 10), 10) + " " +
            MONTH_NAMES[parseInt(iso.slice(5, 7), 10) - 1] + " " +
            iso.slice(0, 4);
        return withTime ? day + ", " + iso.slice(11, 16) : day;
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /* Port of the Liquid linkify_urls filter (_plugins/thoughts.rb). */
    function linkify(text) {
        var out = "";
        var last = 0;
        var re = /https?:\/\/[^\s<]+/g;
        var match;
        while ((match = re.exec(text)) !== null) {
            var url = match[0];
            var trail = "";
            for (;;) {
                if (/[.,;:!?…'"”’]$/.test(url)) {
                    trail = url.slice(-1) + trail;
                    url = url.slice(0, -1);
                } else if (url.slice(-1) === ")" &&
                        url.split("(").length < url.split(")").length) {
                    trail = ")" + trail;
                    url = url.slice(0, -1);
                } else {
                    break;
                }
            }
            out += escapeHtml(text.slice(last, match.index));
            var escaped = escapeHtml(url);
            out += "<a href=\"" + escaped + "\">" + escaped + "</a>";
            out += escapeHtml(trail);
            last = match.index + match[0].length;
        }
        out += escapeHtml(text.slice(last));
        return out.replace(/\n/g, "<br>\n");
    }

    function fetchPlain() {
        return fetch("/activity/search.json").then(function (response) {
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
        return fetch("/activity/search.json.gz").then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.arrayBuffer();
        }).then(function (buffer) {
            var bytes = new Uint8Array(buffer);
            if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) {
                return JSON.parse(new TextDecoder().decode(buffer));
            }
            return new Response(
                new Blob([buffer]).stream()
                    .pipeThrough(new DecompressionStream("gzip"))
            ).json();
        }).catch(fetchPlain);
    }

    function haystackOf(entry) {
        var parts = [entry.t || ""];
        if (entry.k === "p") {
            parts.push(entry.e || "");
        } else if (entry.k === "s") {
            parts.push(entry.a || "", entry.l || "");
        } else {
            (entry.i || []).forEach(function (pair) { parts.push(pair[1]); });
        }
        parts.push(entry.display);
        return parts.join(" ").toLowerCase();
    }

    function loadIndex() {
        if (loading) {
            return loading;
        }
        count.hidden = false;
        count.textContent = "Loading the log…";
        loading = fetchIndex().then(function (data) {
            index = data.map(function (entry) {
                entry.display = displayDate(entry.d, entry.k !== "p");
                entry.haystack = haystackOf(entry);
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

    function element(tag, className, text) {
        var node = document.createElement(tag);
        if (className) {
            node.className = className;
        }
        if (text !== undefined) {
            node.textContent = text;
        }
        return node;
    }

    function link(className, href, text) {
        var anchor = element("a", className, text);
        anchor.href = href;
        return anchor;
    }

    /* Thoughts and TILs carry no URL in the index: their id encodes the
       month (YYYYMMDD…), so their home page follows from the kind. */
    function homeUrl(entry) {
        if (entry.k === "t") {
            return "/thoughts/" + entry.id.slice(0, 4) + "-" +
                entry.id.slice(4, 6) + "/#t" + entry.id;
        }
        if (entry.k === "i") {
            return "/til/#t" + entry.id;
        }
        return entry.u;
    }

    function timeLink(entry) {
        var anchor = link("", homeUrl(entry), "");
        var time = document.createElement("time");
        time.dateTime = entry.d;
        time.textContent = entry.display;
        anchor.appendChild(time);
        return anchor;
    }

    function renderEntry(entry) {
        var kind = { p: "post", t: "thought", i: "til", s: "listening" }[entry.k];
        var article = element("article",
            "thought-entry activity-entry activity-" + kind);
        article.appendChild(element("span", "activity-kicker", KICKERS[entry.k]));
        var footer = element("footer", "thought-meta");

        if (entry.k === "p") {
            var title = element("h3", "activity-post-title");
            title.appendChild(link("", homeUrl(entry), entry.t));
            article.appendChild(title);
            if (entry.e) {
                article.appendChild(element("p", "thought-text", entry.e));
            }
        } else if (entry.k === "s") {
            var list = element("ol", "listening-plays activity-plays");
            var item = element("li", "play");
            var when = link("play-time", homeUrl(entry), "");
            var time = document.createElement("time");
            time.dateTime = entry.d;
            time.textContent = entry.d.slice(11, 16);
            when.appendChild(time);
            item.appendChild(when);
            var what = element("span", "play-what");
            what.appendChild(link("play-track", entry.tu, entry.t));
            what.appendChild(document.createTextNode(" "));
            var artist = element("span", "play-artist", "by ");
            artist.appendChild(link("", entry.au, entry.a));
            what.appendChild(artist);
            if (entry.l) {
                what.appendChild(document.createTextNode(" "));
                what.appendChild(element("span", "play-album", "on " + entry.l));
            }
            if (entry.n) {
                what.appendChild(document.createTextNode(" "));
                var badge = element("span", "play-count", "×" + entry.n);
                badge.title = "Played " + entry.n + " times in a row";
                what.appendChild(badge);
            }
            item.appendChild(what);
            list.appendChild(item);
            article.appendChild(list);
        } else {
            var text = element("p", "thought-text");
            text.innerHTML = linkify(entry.t);
            article.appendChild(text);
            if (entry.i && entry.i.length) {
                var wrap = element("div", "thought-images");
                entry.i.forEach(function (pair) {
                    var img = document.createElement("img");
                    img.src = pair[0];
                    img.alt = pair[1];
                    img.loading = "lazy";
                    wrap.appendChild(img);
                });
                article.appendChild(wrap);
            }
        }

        footer.appendChild(timeLink(entry));
        [["b", "Bluesky"], ["m", "Mastodon"], ["x", "Twitter"]]
            .forEach(function (pair) {
                var url = entry[pair[0]];
                if (!url) {
                    return;
                }
                footer.appendChild(document.createTextNode(" · "));
                var syndication = link("", url, pair[1]);
                syndication.rel = "syndication";
                footer.appendChild(syndication);
            });
        article.appendChild(footer);
        return article;
    }

    function renderMore() {
        var slice = matches.slice(rendered, rendered + BATCH);
        var fragment = document.createDocumentFragment();
        slice.forEach(function (entry) {
            fragment.appendChild(renderEntry(entry));
        });
        more.remove();
        results.appendChild(fragment);
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
            loadIndex().then(applySearch, function () {});
            return;
        }
        matches = index.filter(function (entry) {
            return terms.every(function (term) {
                return entry.haystack.indexOf(term) !== -1;
            });
        });
        results.textContent = "";
        rendered = 0;
        count.textContent = matches.length === 1
            ? "1 entry matches"
            : matches.length + " entries match";
        renderMore();
    }

    input.addEventListener("input", applySearch);
})();
