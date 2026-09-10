"""Persisting short thoughts into the blog (_data/thoughts.yml + assets).

The YAML data file is the canonical record, newest first; the site's
thoughts page, sidebar widget and homepage block all render from it.
Images are written under assets/thoughts/, downscaled/recompressed only
when they exceed the syndication services' size limits.
"""

import io
from datetime import datetime
from pathlib import Path

import yaml
from PIL import Image

DATA_PATH = "_data/thoughts.yml"
IMAGES_DIR = "assets/thoughts"
MAX_SIDE = 2000
MAX_BYTES = 950_000

MIME_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}


def _data_file(root: Path) -> Path:
    return Path(root) / DATA_PATH


def load_thoughts(root: Path) -> list[dict]:
    """All thoughts, newest first; empty when the data file is absent."""
    path = _data_file(root)
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def _write(root: Path, thoughts: list[dict]) -> None:
    _data_file(root).write_text(
        yaml.safe_dump(thoughts, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def add_thought(
    root: Path,
    text: str,
    images: list[dict] | None = None,
    now: datetime | None = None,
) -> dict:
    """Prepend a thought to the data file; return the stored entry.

    The entry carries an id (compact timestamp), the local-time date,
    the untouched text, and any images (``{"src", "alt"}``).
    """
    now = now or datetime.now().astimezone()
    entry = {
        "id": now.strftime("%Y%m%d%H%M%S"),
        "date": now.isoformat(),
        "text": text,
    }
    if images:
        entry["images"] = images
    thoughts = load_thoughts(root)
    thoughts.insert(0, entry)
    _write(root, thoughts)
    return entry


def set_syndication(
    root: Path,
    thought_id: str,
    bluesky: str | None = None,
    mastodon: str | None = None,
) -> None:
    """Record the syndicated copies' URLs on an existing entry."""
    thoughts = load_thoughts(root)
    for entry in thoughts:
        if entry["id"] == thought_id:
            if bluesky:
                entry["bluesky"] = bluesky
            if mastodon:
                entry["mastodon"] = mastodon
            _write(root, thoughts)
            return
    raise KeyError(f"no thought with id {thought_id}")


def save_image(
    root: Path,
    data: bytes,
    mime: str,
    thought_id: str,
    seq: int,
    alt: str = "",
) -> tuple[dict, bytes, str]:
    """Write an attachment under assets/thoughts/.

    Oversized images (longest side over MAX_SIDE or more than MAX_BYTES
    bytes) are scaled down and recompressed to JPEG so the syndication
    services accept them. Returns ``({"src", "alt"}, final_bytes,
    final_mime)`` — the final bytes are what gets uploaded.
    """
    extension = MIME_EXTENSIONS.get(mime)
    if extension is None:
        raise ValueError(f"unsupported image type {mime!r}")
    with Image.open(io.BytesIO(data)) as image:
        if max(image.size) > MAX_SIDE or len(data) > MAX_BYTES:
            scaled = image.convert("RGB")
            scaled.thumbnail((MAX_SIDE, MAX_SIDE))
            for quality in (85, 70, 55, 40):
                buffer = io.BytesIO()
                scaled.save(buffer, format="JPEG", quality=quality)
                data = buffer.getvalue()
                if len(data) <= MAX_BYTES:
                    break
            mime, extension = "image/jpeg", "jpg"

    directory = Path(root) / IMAGES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{thought_id}-{seq}.{extension}"
    (directory / filename).write_bytes(data)
    return {"src": f"/{IMAGES_DIR}/{filename}", "alt": alt}, data, mime


def load_image_file(path: Path) -> tuple[bytes, str]:
    """Read an image file; return (bytes, mime). Raises on non-images."""
    path = Path(path)
    data = path.read_bytes()
    try:
        with Image.open(io.BytesIO(data)) as image:
            image_format = image.format
    except Exception as exc:
        raise ValueError(f"{path} is not a readable image") from exc
    mime = Image.MIME.get(image_format, f"image/{image_format.lower()}")
    return data, mime
