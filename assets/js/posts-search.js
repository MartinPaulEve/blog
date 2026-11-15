/* Full-text search for /posts/.
   The archive page already lists every post, so searching never renders
   anything new: it fetches /posts/search.json once — the pregzipped
   .json.gz twin when the browser can inflate it — and then hides the
   entries that do not match. The index (see _plugins/posts_search.rb)
   is an inverted one: the posts' URLs plus, for each distinct word in
   any post, the gap-encoded positions of the posts containing it. Each
   query term is matched as a case-insensitive substring of that
   vocabulary (so "access" finds "inaccessible"); a post matches when
   every term matches it. Years whose posts are all hidden hide too.
   The query rides in ?q= so a search can be linked to. */

(function () {
    "use strict";

    var input = document.getElementById("post-search");
    var count = document.getElementById("post-search-count");
    var archive = document.getElementById("post-archive");
    if (!input || !count || !archive) {
        return;
    }

    var MIN_LENGTH = 2;
    var INDEX_URL = "/posts/search.json";

    /* Same tokeniser as the build: lowercase, split on anything that is
       not a letter or digit, drop single characters. Older engines
       without Unicode property escapes fall back to ASCII classes. */
    var splitter;
    try {
        splitter = new RegExp("[^\\p{L}\\p{N}]+", "u");
    } catch (error) {
        splitter = /[^a-z0-9]+/i;
    }

    function terms(query) {
        return query.toLowerCase().split(splitter).filter(function (term) {
            return term.length >= MIN_LENGTH;
        });
    }

    /* The archive's DOM: year headings each followed by their entries. */
    var years = [];
    var entries = [];
    var byUrl = {};
    var current = null;
    Array.prototype.forEach.call(archive.children, function (node) {
        if (node.matches("h2.archive-year")) {
            current = { el: node, entries: [] };
            years.push(current);
        } else if (node.matches("article.h-entry")) {
            var link = node.querySelector(".u-url");
            var entry = {
                el: node,
                url: link ? pathOf(link.getAttribute("href")) : null
            };
            entries.push(entry);
            if (entry.url) {
                byUrl[entry.url] = entry;
            }
            if (current) {
                current.entries.push(entry);
            }
        }
    });

    function pathOf(href) {
        try {
            return new URL(href, location.href).pathname;
        } catch (error) {
            return href;
        }
    }

    var index = null;
    var loading = null;

    function fetchPlain() {
        return fetch(INDEX_URL).then(function (response) {
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
        return fetch(INDEX_URL + ".gz").then(function (response) {
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

    /* Expand the gap-encoded posting lists back to absolute positions
       and resolve those positions to archive entries once, up front. */
    function unpack(data) {
        var posts = data.u.map(function (url) {
            return byUrl[pathOf(url)] || null;
        });
        var vocab = Object.keys(data.w);
        var postings = vocab.map(function (word) {
            var position = -1;
            return data.w[word].map(function (gap) {
                position += gap + 1;
                return position;
            });
        });
        return { posts: posts, vocab: vocab, postings: postings };
    }

    function loadIndex() {
        if (loading) {
            return loading;
        }
        count.hidden = false;
        count.textContent = "Loading the index…";
        loading = fetchIndex().then(function (data) {
            index = unpack(data);
        }, function (error) {
            loading = null;
            count.textContent =
                "Search is unavailable (the index failed to load).";
            throw error;
        });
        return loading;
    }

    /* Which posts (by index position) contain every term: OR over the
       vocabulary words containing a term, AND across terms. */
    function matching(queryTerms) {
        var total = index.posts.length;
        var result = null;
        queryTerms.forEach(function (term) {
            var hits = new Uint8Array(total);
            index.vocab.forEach(function (word, w) {
                if (word.indexOf(term) === -1) {
                    return;
                }
                index.postings[w].forEach(function (position) {
                    hits[position] = 1;
                });
            });
            if (!result) {
                result = hits;
                return;
            }
            for (var i = 0; i < total; i++) {
                result[i] = result[i] && hits[i] ? 1 : 0;
            }
        });
        return result;
    }

    function showAll() {
        entries.forEach(function (entry) {
            entry.el.hidden = false;
        });
        years.forEach(function (year) {
            year.el.hidden = false;
        });
        count.hidden = true;
        count.textContent = "";
    }

    function applySearch() {
        var queryTerms = terms(input.value);
        if (!queryTerms.length) {
            showAll();
            return;
        }
        if (!index) {
            /* Re-filter once the index arrives; a failed load keeps its
               message and waits for the next keystroke to retry. */
            loadIndex().then(applySearch, function () {});
            return;
        }
        var hits = matching(queryTerms);
        var shown = 0;
        entries.forEach(function (entry) {
            entry.el.hidden = true;
        });
        index.posts.forEach(function (entry, position) {
            if (entry && hits[position]) {
                entry.el.hidden = false;
                shown += 1;
            }
        });
        years.forEach(function (year) {
            year.el.hidden = !year.entries.some(function (entry) {
                return !entry.el.hidden;
            });
        });
        count.hidden = false;
        count.textContent = shown === 1
            ? "1 post matches"
            : shown + " posts match";
    }

    function syncUrl() {
        if (!window.history || !history.replaceState) {
            return;
        }
        var url = new URL(location.href);
        if (input.value.trim()) {
            url.searchParams.set("q", input.value.trim());
        } else {
            url.searchParams.delete("q");
        }
        history.replaceState(null, "", url.pathname + url.search + url.hash);
    }

    input.addEventListener("input", function () {
        syncUrl();
        applySearch();
    });

    var initial = new URL(location.href).searchParams.get("q");
    if (initial) {
        input.value = initial;
        applySearch();
    }
})();
