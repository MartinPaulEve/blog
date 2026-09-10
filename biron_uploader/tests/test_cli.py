import textwrap

from biron_uploader import cli
from biron_uploader.cli import deposit_post, posts_to_deposit
from biron_uploader.ledger import load_ledger, prune_ledger, record_deposit

POST = textwrap.dedent(
    """\
    ---
    title: "A post"
    date: 2026-08-28
    doi: https://doi.org/10.59348/mjvdw-w0051
    ---

    First paragraph.
    """
)

POST_WITH_BIRON = POST.replace("---\n\n", "biron: https://eprints.bbk.ac.uk/id/eprint/1/\n---\n\n")


def make_repo(tmp_path):
    posts = tmp_path / "_posts"
    posts.mkdir()
    (tmp_path / "_biron").mkdir()
    (tmp_path / ".pdf_cache").mkdir()
    return tmp_path


def add_post(repo, name, text=POST):
    path = repo / "_posts" / name
    path.write_text(text, encoding="utf-8")
    (repo / ".pdf_cache" / f"{name[:-3]}.pdf").write_bytes(b"%PDF-fake")
    return path


# --- ledger ----------------------------------------------------------------


def test_ledger_round_trip(tmp_path):
    path = tmp_path / "deposited.yml"
    assert load_ledger(path) == {}
    record_deposit(path, "2026-08-28-a-post.md", 58012)
    record_deposit(path, "2026-08-29-b-post.md", 58013)
    assert load_ledger(path) == {
        "2026-08-28-a-post.md": 58012,
        "2026-08-29-b-post.md": 58013,
    }


def test_prune_ledger_drops_stamped_posts(tmp_path):
    path = tmp_path / "deposited.yml"
    record_deposit(path, "2026-08-28-a-post.md", 58012)
    record_deposit(path, "2026-08-29-b-post.md", 58013)
    removed = prune_ledger(path, {"2026-08-28-a-post.md"})
    assert removed == ["2026-08-28-a-post.md"]
    assert load_ledger(path) == {"2026-08-29-b-post.md": 58013}


# --- candidate selection ---------------------------------------------------


def test_posts_to_deposit_excludes_stamped_pending_and_skipped(tmp_path):
    repo = make_repo(tmp_path)
    eligible = add_post(repo, "2026-09-01-eligible.md")
    add_post(repo, "2026-09-02-already-stamped.md", POST_WITH_BIRON)
    add_post(repo, "2026-09-03-pending.md")
    add_post(repo, "2026-09-04-skipped.md")
    record_deposit(repo / "_biron" / "deposited.yml", "2026-09-03-pending.md", 58012)
    (repo / "_biron" / "skip.yml").write_text(
        "- 2026-09-04-skipped.md\n", encoding="utf-8"
    )
    assert posts_to_deposit(repo) == [eligible]


def test_posts_to_deposit_works_without_ledger_or_skip_files(tmp_path):
    repo = make_repo(tmp_path)
    eligible = add_post(repo, "2026-09-01-eligible.md")
    assert posts_to_deposit(repo) == [eligible]


# --- collection resolution -------------------------------------------------


class Args:
    collection = None
    base_url = "https://eprints.example.org"


def test_explicit_collection_wins(monkeypatch):
    monkeypatch.setenv("BIRON_COLLECTION", "https://x.example/id/contents")
    args = Args()
    assert cli._resolve_collection(None, args) == "https://x.example/id/contents"
    args.collection = "https://y.example/sword-app/deposit/inbox"
    assert cli._resolve_collection(None, args) == (
        "https://y.example/sword-app/deposit/inbox"
    )


def test_collection_discovered_from_service_document(monkeypatch):
    monkeypatch.delenv("BIRON_COLLECTION", raising=False)

    class FakeClient:
        def service_document(self):
            return [
                {"href": "https://e.example/zips", "title": "Zips",
                 "packaging": ["application/zip"]},
                {"href": "https://e.example/id/contents", "title": "Eprints",
                 "packaging": ["http://eprints.org/ep2/data/2.0"]},
            ]

    assert cli._resolve_collection(FakeClient(), Args()) == (
        "https://e.example/id/contents"
    )


def test_collection_falls_back_to_crud_when_service_document_fails(monkeypatch):
    monkeypatch.delenv("BIRON_COLLECTION", raising=False)

    class FailingClient:
        def service_document(self):
            raise cli.BironError("401")

    assert cli._resolve_collection(FailingClient(), Args()) == (
        "https://eprints.example.org/id/contents"
    )


# --- deposit_post ----------------------------------------------------------


class FakeClient:
    def __init__(self):
        self.deposits = []

    def deposit(self, collection_url, xml, files=None):
        self.deposits.append((collection_url, xml, files))
        return {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"}


def test_deposit_post_sends_metadata_and_raw_files(tmp_path):
    repo = make_repo(tmp_path)
    post_path = add_post(repo, "2026-09-01-eligible.md")
    client = FakeClient()
    receipt = deposit_post(
        client, post_path, "https://eprints.bbk.ac.uk/id/contents"
    )
    assert receipt["eprintid"] == 58012
    collection_url, xml, files = client.deposits[0]
    assert collection_url.endswith("/id/contents")
    assert b"https://eve.gd/2026/09/01/eligible/" in xml
    assert b"<data" not in xml  # no base64 payloads in the record XML
    names = [name for name, mime, data in files]
    assert names == ["2026-09-01-eligible.pdf", "2026-09-01-eligible.md"]
    assert files[0][1] == "application/pdf"
    assert files[0][2] == b"%PDF-fake"


# --- deposit reporting -----------------------------------------------------


def test_describe_live_record_uses_the_public_url():
    line = cli._describe(
        {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"},
        "archive",
        "https://eprints.bbk.ac.uk",
    )
    assert "https://eprints.bbk.ac.uk/58012/" in line
    assert "live" in line.lower()


def test_describe_pending_record_uses_the_workflow_url():
    line = cli._describe(
        {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"},
        "inbox",
        "https://eprints.bbk.ac.uk",
    )
    assert "eprintid=58012" in line
    assert "inbox" in line


def test_describe_unknown_status_falls_back_to_the_receipt_url():
    line = cli._describe(
        {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"},
        None,
        "https://eprints.bbk.ac.uk",
    )
    assert "https://eprints.bbk.ac.uk/id/eprint/58012/" in line
