/* Whole-archive search for /thoughts/ and its per-month pages.
   Each page carries one server-rendered month and the month nav is
   plain links, so browsing costs nothing extra. Searching fetches
   /thoughts/search.json once — the pregzipped .json.gz twin when the
   browser can inflate it — then filters every thought in memory:
   case-insensitive AND-of-terms over the text, image alt text and the
   displayed date, exactly as the old single-page search did. Matches
   render in batches of 200 (a "show more" button pages through the
   rest), each linking to its home on its month page. Clearing the
   query restores the month view. */

(function () {
    "use strict";

    var input = document.getElementById("thought-search");
    var count = document.getElementById("thought-search-count");
    var nav = document.querySelector(".thoughts-months");
    var monthList = document.querySelector(".thoughts-list.h-feed");
    var results = document.getElementById("thought-search-results");
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

    var more = document.createElement("button");
    more.type = "button";
    more.className = "thoughts-more";
    more.addEventListener("click", renderMore);

    function monthUrl(id) {
        return "/thoughts/" + id.slice(0, 4) + "-" + id.slice(4, 6) + "/";
    }

    /* "2012-05-16T18:20:00+01:00" -> "16 May 2012, 18:20" — read from
       the string, not through Date, so the entry keeps the timezone it
       was written in (matching the server-rendered dates). */
    function displayDate(iso) {
        return parseInt(iso.slice(8, 10), 10) + " " +
            MONTH_NAMES[parseInt(iso.slice(5, 7), 10) - 1] + " " +
            iso.slice(0, 4) + ", " + iso.slice(11, 16);
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /* Port of the Liquid linkify_urls filter (_plugins/thoughts.rb):
       escape everything, link bare URLs, keep trailing punctuation and
       unbalanced closing parens outside the link, <br> the newlines. */
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
        return fetch("/thoughts/search.json").then(function (response) {
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
        return fetch("/thoughts/search.json.gz").then(function (response) {
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
        count.textContent = "Loading the archive…";
        loading = fetchIndex().then(function (data) {
            index = data.map(function (entry) {
                var alts = (entry.i || []).map(function (pair) {
                    return pair[1];
                }).join(" ");
                entry.display = displayDate(entry.d);
                entry.haystack = (entry.t + " " + alts + " " +
                    entry.display).toLowerCase();
                return entry;
            });
        }, function (error) {
            loading = null;
            count.textContent =
                "Search is unavailable (the archive failed to load).";
            throw error;
        });
        return loading;
    }

    function renderEntry(entry) {
        var article = document.createElement("article");
        article.className = "thought-entry";
        var text = document.createElement("p");
        text.className = "thought-text";
        text.innerHTML = linkify(entry.t);
        article.appendChild(text);
        if (entry.i && entry.i.length) {
            var wrap = document.createElement("div");
            wrap.className = "thought-images";
            entry.i.forEach(function (pair) {
                var img = document.createElement("img");
                img.src = pair[0];
                img.alt = pair[1];
                img.loading = "lazy";
                wrap.appendChild(img);
            });
            article.appendChild(wrap);
        }
        var footer = document.createElement("footer");
        footer.className = "thought-meta";
        var link = document.createElement("a");
        link.href = monthUrl(entry.id) + "#t" + entry.id;
        var time = document.createElement("time");
        time.dateTime = entry.d;
        time.textContent = entry.display;
        link.appendChild(time);
        footer.appendChild(link);
        [["b", "Bluesky"], ["m", "Mastodon"], ["x", "Twitter"]]
            .forEach(function (pair) {
                var url = entry[pair[0]];
                if (!url) {
                    return;
                }
                footer.appendChild(document.createTextNode(" · "));
                var syndication = document.createElement("a");
                syndication.href = url;
                syndication.className = "u-syndication";
                syndication.rel = "syndication";
                syndication.textContent = pair[1];
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
            /* Re-filter once the archive arrives; a failed load keeps
               its message and waits for the next keystroke to retry. */
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
            ? "1 thought matches"
            : matches.length + " thoughts match";
        renderMore();
    }

    input.addEventListener("input", applySearch);
})();
