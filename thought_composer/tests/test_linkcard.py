from thought_composer.linkcard import fetch_card, parse_open_graph

HTML = """<!doctype html><html><head>
<title>Fallback title</title>
<meta property="og:title" content="OG Title" />
<meta property="og:description" content="A description." />
<meta property="og:image" content="https://example.org/thumb.jpg" />
</head><body></body></html>"""

BARE_HTML = "<html><head><title>Only a title</title></head><body></body></html>"


class FakeResponse:
    def __init__(self, status_code, text="", content=b"", headers=None):
        self.status_code = status_code
        self.text = text
        self.content = content
        self.headers = headers or {}


def test_parse_open_graph_reads_meta_tags():
    og = parse_open_graph(HTML)
    assert og["title"] == "OG Title"
    assert og["description"] == "A description."
    assert og["image"] == "https://example.org/thumb.jpg"


def test_parse_open_graph_falls_back_to_title_tag():
    og = parse_open_graph(BARE_HTML)
    assert og["title"] == "Only a title"
    assert og.get("description") is None


def test_fetch_card_builds_the_embed_dict():
    def get(url, **kwargs):
        if url.endswith("thumb.jpg"):
            return FakeResponse(
                200, content=b"jpegbytes",
                headers={"Content-Type": "image/jpeg"},
            )
        return FakeResponse(200, text=HTML)

    card = fetch_card("https://example.org/page", get=get)
    assert card["uri"] == "https://example.org/page"
    assert card["title"] == "OG Title"
    assert card["description"] == "A description."
    assert card["thumb_data"] == b"jpegbytes"
    assert card["thumb_mime"] == "image/jpeg"


def test_fetch_card_without_image_omits_thumb():
    card = fetch_card(
        "https://example.org/page",
        get=lambda url, **kwargs: FakeResponse(200, text=BARE_HTML),
    )
    assert card["title"] == "Only a title"
    assert "thumb_data" not in card


def test_fetch_card_failure_returns_none():
    def get(url, **kwargs):
        raise OSError("connection refused")

    assert fetch_card("https://example.org/page", get=get) is None
