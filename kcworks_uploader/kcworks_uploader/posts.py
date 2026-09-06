"""Reading and interpreting Jekyll posts from the eve.gd blog."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import yaml

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DATED_SLUG_RE = re.compile(r"\A(\d{4})-(\d{2})-(\d{2})-(.+)\Z")
LIQUID_RE = re.compile(r"{%.*?%}|{{.*?}}", re.DOTALL)


@dataclass
class Post:
    """A parsed Jekyll post: front matter fields plus the markdown body."""

    path: Path
    title: str
    date: str  # ISO YYYY-MM-DD
    doi: str | None = None  # bare form, e.g. "10.59348/mjvdw-w0051"
    tags: list[str] = field(default_factory=list)
    body: str = ""
    last_modified: str | None = None  # ISO YYYY-MM-DD


def parse_post(path: Path) -> Post:
    """Parse a Jekyll post file into a Post.

    The DOI is normalised to its bare form (no https://doi.org/ prefix); the
    date is normalised to an ISO YYYY-MM-DD string, falling back to the date
    encoded in the filename when the front matter has none.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path} has no YAML front matter")
    front_matter = yaml.safe_load(match.group(1)) or {}
    title = front_matter.get("title")
    if not title:
        raise ValueError(f"{path} has no title in its front matter")
    return Post(
        path=path,
        title=str(title),
        date=_normalise_date(front_matter.get("date"), path),
        doi=_bare_doi(front_matter.get("doi")),
        tags=[str(tag) for tag in front_matter.get("tags") or []],
        body=text[match.end():],
        last_modified=_modified_date(front_matter.get("last_modified_at")),
    )


def post_slug(path: Path) -> str:
    """The post's slug: the filename without its extension."""
    return Path(path).stem


def canonical_url(slug: str, base: str = "https://eve.gd") -> str:
    """The canonical published URL for a post slug.

    ``2026-08-28-some-title`` becomes ``https://eve.gd/2026/08/28/some-title/``
    (matching the site's ``/:year/:month/:day/:title/`` permalink).
    """
    match = DATED_SLUG_RE.match(slug)
    if not match:
        raise ValueError(f"Slug {slug!r} does not start with a YYYY-MM-DD date")
    year, month, day, title = match.groups()
    return f"{base}/{year}/{month}/{day}/{title}/"


def site_slug(slug: str) -> str:
    """The site's on-disk name for a slug: the URL-escaped form with every
    run of characters outside [A-Za-z0-9._-] collapsed to a hyphen.

    Mirrors the blog's OgImage.slug convention, under which the PDF and OG
    derivatives of a post with non-ASCII characters in its name are cached
    (e.g. ``gerät`` becomes ``ger-C3-A4t``)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", quote(slug))


def find_pdf(repo_root: Path, slug: str) -> Path:
    """Locate the built PDF edition for a post.

    Prefers ``.pdf_cache`` and falls back to ``_site/PDF``, trying the
    bare slug and then its site_slug form in each. Raises
    FileNotFoundError when none exists.
    """
    repo_root = Path(repo_root)
    names = dict.fromkeys([f"{slug}.pdf", f"{site_slug(slug)}.pdf"])
    candidates = [
        directory / name
        for directory in (repo_root / ".pdf_cache", repo_root / "_site" / "PDF")
        for name in names
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"No PDF edition found for {slug!r} (looked in "
        + " and ".join(str(c) for c in candidates)
        + "); run `jekyll build` to generate it"
    )


def first_paragraph(body: str) -> str:
    """A plain-text rendering of the first real paragraph of a post body.

    Skips Liquid tags, headings and images; unwraps markdown links and
    emphasis; collapses internal whitespace.
    """
    for block in re.split(r"\n\s*\n", body):
        text = LIQUID_RE.sub("", block)
        text = re.sub(r"<[^>]+>", "", text)
        if not text.strip() or text.lstrip().startswith("#"):
            continue
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[*_`]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            return text
    return ""


def _normalise_date(value, path: Path) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and re.match(r"\A\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    match = DATED_SLUG_RE.match(path.stem)
    if match:
        year, month, day, _ = match.groups()
        return f"{year}-{month}-{day}"
    raise ValueError(f"Cannot determine a publication date for {path}")


def _bare_doi(value) -> str | None:
    if not value:
        return None
    return re.sub(r"\Ahttps?://(dx\.)?doi\.org/|\Adoi:", "", str(value).strip())


def _modified_date(value) -> str | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()[:10] or None


def find_blog_root(start: Path) -> Path | None:
    """The nearest ancestor (or start) holding a _config.yml, or None."""
    start = Path(start).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "_config.yml").is_file():
            return candidate
    return None


def blog_collection(blog_root: Path) -> str | None:
    """The blog-wide KC Works collection (`kcworks_collection` in
    _config.yml), or None when unset."""
    config = Path(blog_root) / "_config.yml"
    if not config.is_file():
        return None
    value = (yaml.safe_load(config.read_text(encoding="utf-8")) or {}).get(
        "kcworks_collection"
    )
    return str(value) if value else None


def pending_posts(posts_dir: Path) -> list[Path]:
    """Every post with no kcworks: front-matter deposit, in filename
    order — the queue for a backfill run."""
    pending = []
    for path in sorted(Path(posts_dir).glob("*.md")):
        match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
        front_matter = yaml.safe_load(match.group(1)) if match else None
        if not (front_matter or {}).get("kcworks"):
            pending.append(path)
    return pending


def record_deposit(path: Path, url: str) -> None:
    """Stamp `kcworks: <url>` into a post's front matter, leaving every
    other byte of the file untouched; a post that already carries a
    kcworks: entry is left alone."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path} has no YAML front matter")
    if (yaml.safe_load(match.group(1)) or {}).get("kcworks"):
        return
    insert_at = match.end(1)
    path.write_text(
        f"{text[:insert_at]}\nkcworks: {url}{text[insert_at:]}",
        encoding="utf-8",
    )


def update_deposit(path: Path, url: str) -> None:
    """Point a post's kcworks: front-matter entry at url, replacing any
    existing value (record_deposit, by contrast, leaves one alone); a
    post without the entry gains it."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path} has no YAML front matter")
    fm = match.group(1)
    new_fm, count = re.subn(
        r"^kcworks:[^\n]*$", f"kcworks: {url}", fm, count=1, flags=re.MULTILINE
    )
    if count:
        path.write_text(
            text[: match.start(1)] + new_fm + text[match.end(1):],
            encoding="utf-8",
        )
    else:
        record_deposit(path, url)


def deposited_records(posts_dir: Path) -> list[tuple[Path, str]]:
    """(post path, record id) for every post with a kcworks: front-matter
    deposit URL, in filename order."""
    records = []
    for path in sorted(Path(posts_dir).glob("*.md")):
        match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
        if not match:
            continue
        url = (yaml.safe_load(match.group(1)) or {}).get("kcworks")
        if url:
            records.append((path, str(url).rstrip("/").rsplit("/", 1)[-1]))
    return records
