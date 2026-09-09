import textwrap

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


# --- deposit_post ----------------------------------------------------------


class FakeClient:
    def __init__(self):
        self.deposits = []

    def deposit(self, collection_url, xml):
        self.deposits.append((collection_url, xml))
        return {"eprintid": 58012, "url": "https://eprints.bbk.ac.uk/id/eprint/58012/"}


def test_deposit_post_sends_pdf_and_markdown(tmp_path):
    repo = make_repo(tmp_path)
    post_path = add_post(repo, "2026-09-01-eligible.md")
    client = FakeClient()
    receipt = deposit_post(
        client, post_path, "https://eprints.bbk.ac.uk/sword-app/deposit/inbox"
    )
    assert receipt["eprintid"] == 58012
    collection_url, xml = client.deposits[0]
    assert collection_url.endswith("/deposit/inbox")
    assert b"2026-09-01-eligible.md" in xml
    assert b"2026-09-01-eligible.pdf" in xml
    assert b"https://eve.gd/2026/09/01/eligible/" in xml
