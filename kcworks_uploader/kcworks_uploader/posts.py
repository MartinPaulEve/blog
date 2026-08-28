"""Reading and interpreting Jekyll posts from the eve.gd blog."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

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


def find_pdf(repo_root: Path, slug: str) -> Path:
    """Locate the built PDF edition for a post.

    Prefers ``.pdf_cache/<slug>.pdf`` and falls back to
    ``_site/PDF/<slug>.pdf``. Raises FileNotFoundError when neither exists.
    """
    repo_root = Path(repo_root)
    candidates = [
        repo_root / ".pdf_cache" / f"{slug}.pdf",
        repo_root / "_site" / "PDF" / f"{slug}.pdf",
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
