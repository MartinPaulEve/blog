"""Draft persistence for the dry-run → POST confirmation flow.

A dry run must leave enough on disk that a later POST reply publishes
exactly what was previewed — the text and the original image bytes,
not a re-parse of the reply (which mail clients mangle). Each draft is
a directory: meta.json plus the attachment files.
"""

import json
import secrets
import shutil
from datetime import UTC, datetime
from pathlib import Path

DRAFT_TTL_DAYS = 30


def new_draft_id(rand=None) -> str:
    """A fresh 8-hex-character draft id (``rand`` injectable for tests)."""
    return (rand() if rand else secrets.token_hex(8))[:8]


def save_draft(
    drafts_dir: Path,
    draft_id: str,
    text: str,
    images: list,
    sender: str,
    message_id: str,
    now=None,
) -> Path:
    """Persist a draft; returns its directory.

    ``images`` is [{"data", "mime", "alt", "filename"}] as produced by
    extract.collect_images; the bytes land in files, meta.json carries
    everything else.
    """
    now = now or datetime.now(UTC)
    directory = Path(drafts_dir) / draft_id
    directory.mkdir(parents=True, exist_ok=True)
    stored = []
    for seq, image in enumerate(images, 1):
        name = f"image-{seq}"
        (directory / name).write_bytes(image["data"])
        stored.append(
            {
                "file": name,
                "mime": image["mime"],
                "alt": image.get("alt", ""),
                "filename": image.get("filename", name),
            }
        )
    meta = {
        "text": text,
        "sender": sender,
        "message_id": message_id,
        "created": now.isoformat(),
        "images": stored,
    }
    _meta_path(drafts_dir, draft_id).write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8"
    )
    return directory


def load_draft(drafts_dir: Path, draft_id: str) -> dict | None:
    """The stored draft, or None when the id is unknown.

    Returns {"text", "sender", "message_id", "created", "images":
    [{"data", "mime", "alt", "filename"}]} with the image bytes read
    back in.
    """
    meta_path = _meta_path(drafts_dir, draft_id)
    if not meta_path.exists():
        return None
    meta = _read_json(meta_path)
    directory = meta_path.parent
    meta["images"] = [
        {
            "data": (directory / image["file"]).read_bytes(),
            "mime": image["mime"],
            "alt": image.get("alt", ""),
            "filename": image.get("filename", image["file"]),
        }
        for image in meta.get("images", [])
    ]
    return meta


def delete_draft(drafts_dir: Path, draft_id: str) -> None:
    """Remove a draft (idempotent: unknown ids are a no-op)."""
    shutil.rmtree(Path(drafts_dir) / draft_id, ignore_errors=True)


def prune_drafts(drafts_dir: Path, ttl_days: int = DRAFT_TTL_DAYS, now=None) -> list:
    """Delete drafts older than the TTL; returns the ids removed."""
    drafts_dir = Path(drafts_dir)
    if not drafts_dir.is_dir():
        return []
    now = now or datetime.now(UTC)
    removed = []
    for directory in sorted(drafts_dir.iterdir()):
        meta_path = directory / "meta.json"
        if not meta_path.is_file():
            continue
        created = datetime.fromisoformat(_read_json(meta_path)["created"])
        if (now - created).days >= ttl_days:
            delete_draft(drafts_dir, directory.name)
            removed.append(directory.name)
    return removed


def _meta_path(drafts_dir: Path, draft_id: str) -> Path:
    return Path(drafts_dir) / draft_id / "meta.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
