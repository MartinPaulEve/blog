import textwrap

from biron_uploader import cli
from biron_uploader.cli import deposit_post, posts_to_deposit
from biron_uploader.cookiejar import write_cookie_file
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
    def __init__(self, status="archive"):
        self.deposits = []
        self.status = status

    def deposit(self, collection_url, xml, documents=None, make_live=False):
        self.deposits.append((collection_url, xml, documents, make_live))
        return {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"}

    def eprint_status(self, eprintid):
        return self.status


def test_deposit_post_sends_metadata_and_documents_for_live_publication(tmp_path):
    repo = make_repo(tmp_path)
    post_path = add_post(repo, "2026-09-01-eligible.md")
    client = FakeClient()
    receipt = deposit_post(
        client, post_path, "https://eprints.bbk.ac.uk/id/contents"
    )
    assert receipt["eprintid"] == 58012
    collection_url, xml, documents, make_live = client.deposits[0]
    assert collection_url.endswith("/id/contents")
    assert b"https://eve.gd/2026/09/01/eligible/" in xml
    assert b"<data" not in xml  # no base64 payloads anywhere
    assert make_live is True
    names = [d["filename"] for d in documents]
    assert names == ["2026-09-01-eligible.pdf", "2026-09-01-eligible.md"]
    assert documents[0]["mime"] == "application/pdf"
    assert documents[0]["data"] == b"%PDF-fake"
    assert b"<data" not in documents[0]["xml"]
    assert b"public" in documents[0]["xml"]  # the required Visible-to field


# --- finalise: stamp or ledger ---------------------------------------------


STUB_APPLY_BIRON = '''
def insert_biron(text, biron=None):
    return text.replace("---\\n\\n", f"biron: {biron}\\n---\\n\\n", 1)
'''


def test_finalise_stamps_the_post_when_the_record_is_live(tmp_path):
    repo = make_repo(tmp_path)
    post_path = add_post(repo, "2026-09-01-eligible.md")
    (repo / "_biron" / "apply_biron.py").write_text(STUB_APPLY_BIRON)
    line = cli.finalise(
        FakeClient(status="archive"),
        post_path,
        {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"},
        "https://eprints.bbk.ac.uk",
    )
    assert "biron: https://eprints.bbk.ac.uk/id/eprint/58012/" in post_path.read_text()
    assert "58012" in line and "live" in line.lower()
    assert load_ledger(repo / "_biron" / "deposited.yml") == {}
    from biron_uploader.ledger import file_digest, load_shipped
    assert load_shipped(repo / "_biron" / "shipped.yml") == {
        post_path.name: file_digest(post_path)
    }


def test_finalise_ledgers_the_post_when_still_in_review(tmp_path):
    repo = make_repo(tmp_path)
    post_path = add_post(repo, "2026-09-01-eligible.md")
    line = cli.finalise(
        FakeClient(status="buffer"),
        post_path,
        {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"},
        "https://eprints.bbk.ac.uk",
    )
    assert "biron:" not in post_path.read_text()
    assert load_ledger(repo / "_biron" / "deposited.yml") == {
        "2026-09-01-eligible.md": 58012
    }
    assert "buffer" in line


# --- update: shipped ledger and staleness -----------------------------------


def test_shipped_ledger_round_trip(tmp_path):
    from biron_uploader.ledger import file_digest, load_shipped, record_shipped

    path = tmp_path / "shipped.yml"
    assert load_shipped(path) == {}
    record_shipped(path, "a.md", "abc123")
    record_shipped(path, "b.md", "def456")
    assert load_shipped(path) == {"a.md": "abc123", "b.md": "def456"}
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"hello")
    assert file_digest(sample) == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_eprintid_extracted_from_the_biron_marker(tmp_path):
    repo = make_repo(tmp_path)
    path = add_post(repo, "2026-09-02-already-stamped.md", POST_WITH_BIRON)
    assert cli._biron_eprintid(path) == 1
    plain = add_post(repo, "2026-09-01-eligible.md")
    assert cli._biron_eprintid(plain) is None


def test_update_pass_baselines_unknown_posts_without_touching_biron(tmp_path, capsys):
    from biron_uploader.ledger import load_shipped

    repo = make_repo(tmp_path)
    add_post(repo, "2026-09-02-already-stamped.md", POST_WITH_BIRON)
    result = cli.update_main(["--root", str(repo)])
    assert result == 0
    shipped = load_shipped(repo / "_biron" / "shipped.yml")
    assert "2026-09-02-already-stamped.md" in shipped
    assert "baselined" in capsys.readouterr().out


def test_update_pass_updates_changed_posts_and_refreshes_the_digest(
    tmp_path, monkeypatch
):
    from biron_uploader.ledger import file_digest, load_shipped, record_shipped

    repo = make_repo(tmp_path)
    path = add_post(repo, "2026-09-02-already-stamped.md", POST_WITH_BIRON)
    record_shipped(repo / "_biron" / "shipped.yml", path.name, "stale-digest")

    updates = []

    class FakeUpdateClient:
        def update(self, eprintid, xml, documents=None):
            updates.append((eprintid, xml, [d["filename"] for d in documents]))
            return {"eprintid": eprintid, "url": f"https://e/{eprintid}/"}

    monkeypatch.setattr(cli, "_ensure_client", lambda *a, **k: FakeUpdateClient())
    result = cli.update_main(["--root", str(repo)])
    assert result == 0
    (update,) = updates
    assert update[0] == 1
    assert "2026-09-02-already-stamped.pdf" in update[2]
    shipped = load_shipped(repo / "_biron" / "shipped.yml")
    assert shipped[path.name] == file_digest(path)


def test_update_pass_dry_run_reports_but_does_not_touch(tmp_path, monkeypatch, capsys):
    from biron_uploader.ledger import load_shipped, record_shipped

    repo = make_repo(tmp_path)
    path = add_post(repo, "2026-09-02-already-stamped.md", POST_WITH_BIRON)
    record_shipped(repo / "_biron" / "shipped.yml", path.name, "stale-digest")
    monkeypatch.setattr(
        cli, "_ensure_client",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("no network on dry-run")),
    )
    assert cli.update_main(["--root", str(repo), "--dry-run"]) == 0
    assert path.name in capsys.readouterr().out
    assert load_shipped(repo / "_biron" / "shipped.yml") == {
        path.name: "stale-digest"
    }


# --- cookie resolution and refresh -----------------------------------------


def test_cookie_resolution_prefers_explicit_env(monkeypatch, tmp_path):
    monkeypatch.setenv("BIRON_COOKIE", "name=explicit")
    write_cookie_file(tmp_path, "name=fromfile")
    assert cli._resolve_cookie(tmp_path) == ("name=explicit", "env")


def test_cookie_resolution_auto_defers_to_the_harvested_file(monkeypatch, tmp_path):
    write_cookie_file(tmp_path, "name=fromfile")
    monkeypatch.setenv("BIRON_COOKIE", "auto")
    assert cli._resolve_cookie(tmp_path) == ("name=fromfile", "file")
    monkeypatch.delenv("BIRON_COOKIE")
    assert cli._resolve_cookie(tmp_path) == ("name=fromfile", "file")


def test_cookie_resolution_empty(monkeypatch, tmp_path):
    monkeypatch.delenv("BIRON_COOKIE", raising=False)
    assert cli._resolve_cookie(tmp_path) == (None, None)


class FakeStatusClient:
    def __init__(self, username=None, password=None, base_url=None,
                 cookie=None, statuses=None):
        self.cookie = cookie
        self.username = username
        self._statuses = statuses or {}

    def contents_status(self):
        return self._statuses.get(self.cookie, 401)


def test_ensure_client_refreshes_a_stale_harvested_cookie(monkeypatch, tmp_path):
    monkeypatch.delenv("BIRON_COOKIE", raising=False)
    monkeypatch.delenv("BIRON_USERNAME", raising=False)
    write_cookie_file(tmp_path, "name=stale")
    statuses = {"name=stale": 401, "name=fresh": 200}
    monkeypatch.setattr(
        cli, "BironClient",
        lambda **kwargs: FakeStatusClient(statuses=statuses, **kwargs),
    )
    harvests = []

    def fake_harvest(root, headless=False, echo=print):
        harvests.append(headless)
        write_cookie_file(root, "name=fresh")
        return "name=fresh"

    monkeypatch.setattr(cli.cookiejar, "harvest", fake_harvest)
    client = cli._ensure_client("https://e.example", tmp_path, echo=lambda *a: None)
    assert client.cookie == "name=fresh"
    assert harvests == [True]


def test_ensure_client_accepts_a_working_cookie_without_harvesting(monkeypatch, tmp_path):
    monkeypatch.delenv("BIRON_COOKIE", raising=False)
    write_cookie_file(tmp_path, "name=good")
    monkeypatch.setattr(
        cli, "BironClient",
        lambda **kwargs: FakeStatusClient(statuses={"name=good": 200}, **kwargs),
    )
    monkeypatch.setattr(
        cli.cookiejar, "harvest",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not harvest")),
    )
    client = cli._ensure_client("https://e.example", tmp_path, echo=lambda *a: None)
    assert client.cookie == "name=good"


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
