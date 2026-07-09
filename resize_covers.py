#!/usr/bin/env python3
"""Resize Sequoia cover images (ogImage) that exceed Bluesky's ~1MB blob limit.

Run from your blog root (where sequoia.json lives):
    uv run --with pillow --with python-frontmatter ./resize_covers.py

Each oversized image is shrunk in place under its original filename (so the
ogImage reference keeps working) and the original is kept alongside it with an
"_old" suffix, e.g. images/bookstack.jpg -> images/bookstack_old.jpg.
"""

import io
import json
import base64
import pathlib
import frontmatter
from frontmatter.default_handlers import SafeLoader
from PIL import Image, ImageOps

# --- config: read from sequoia.json, fall back to sensible defaults ---
ROOT = pathlib.Path(".")
cfg = {}
cfg_path = ROOT / "sequoia.json"
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())

CONTENT_DIR = ROOT / cfg.get("contentDir", "_posts")
IMAGES_DIR = ROOT / cfg.get("imagesDir", "images")
COVER_FIELD = (cfg.get("frontmatter") or {}).get("coverImage", "ogImage")

TARGET_BYTES = 990_000            # just under Bluesky's 1,000,000-byte limit
EXTS = {".md", ".markdown", ".mdx"}
SUFFIX_FMT = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
              ".webp": "WEBP", ".gif": "GIF"}


# Tolerate any stray Ruby !binary blobs still lurking in frontmatter
def _binary(loader, node):
    data = base64.b64decode(loader.construct_scalar(node))
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")
SafeLoader.add_constructor("!binary", _binary)


def resolve_image(og: str) -> pathlib.Path:
    """Mirror Sequoia's resolveImagePath for the imagesDir case."""
    base = IMAGES_DIR.name
    idx = og.find(base)
    if idx != -1:
        rel = og[idx + len(base):].lstrip("/\\")
    else:
        rel = pathlib.PurePosixPath(og).name
    return IMAGES_DIR / rel


def encode(im, fmt, quality):
    buf = io.BytesIO()
    if fmt in ("JPEG", "WEBP"):
        kwargs = dict(quality=quality, optimize=True)
        if fmt == "JPEG":
            kwargs["progressive"] = True
    else:  # PNG, GIF -> lossless
        kwargs = dict(optimize=True)
    im.save(buf, format=fmt, **kwargs)
    return buf.getvalue()


def shrink(im, fmt, target):
    """Return (bytes, note) under target, or (None, reason)."""
    im = ImageOps.exif_transpose(im)                 # bake orientation before dropping EXIF
    if fmt == "JPEG" and im.mode not in ("RGB", "L"):
        im = im.convert("RGB")

    scales = [1.0]
    s = 0.9
    while s > 0.25:
        scales.append(round(s, 3))
        s *= 0.85

    for scale in scales:
        if scale == 1.0:
            work = im
        else:
            w, h = im.size
            work = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        if fmt in ("JPEG", "WEBP"):
            for q in (90, 82, 74, 66, 58, 50, 42, 35):
                out = encode(work, fmt, q)
                if len(out) <= target:
                    return out, f"scale {scale:.2f}, quality {q}"
        else:
            out = encode(work, fmt, None)
            if len(out) <= target:
                return out, f"scale {scale:.2f}"
    return None, "still over target even at smallest size"


def main():
    if not CONTENT_DIR.exists():
        raise SystemExit(f"content dir not found: {CONTENT_DIR} (run from your blog root)")

    # collect unique cover images (an image reused by many posts is handled once)
    covers = {}
    for md in CONTENT_DIR.rglob("*"):
        if md.suffix.lower() not in EXTS:
            continue
        og = frontmatter.load(md).get(COVER_FIELD)
        if not isinstance(og, str) or not og or og.startswith(("http://", "https://")):
            continue
        img = resolve_image(og)
        covers.setdefault(img.resolve(), (img, md))

    resized = skipped = problems = 0
    for _, (img, referer) in sorted(covers.items()):
        if not img.exists():
            print(f"MISSING  {img}  (referenced by {referer.name})")
            problems += 1
            continue

        size = img.stat().st_size
        if size <= TARGET_BYTES:
            skipped += 1
            continue

        old = img.with_name(f"{img.stem}_old{img.suffix}")
        if old.exists():
            print(f"SKIP     {img.name}: backup {old.name} already exists")
            skipped += 1
            continue

        try:
            with Image.open(img) as im:
                fmt = im.format or SUFFIX_FMT.get(img.suffix.lower())
                if fmt is None:
                    raise ValueError(f"unknown image format for {img.suffix}")
                out, note = shrink(im, fmt, TARGET_BYTES)
        except Exception as e:
            print(f"FAIL     {img.name}: {e}")
            problems += 1
            continue

        if out is None:
            print(f"FAIL     {img.name}: {note}")
            problems += 1
            continue

        img.rename(old)              # keep the original as *_old
        img.write_bytes(out)         # shrunk file takes the original name
        print(f"RESIZED  {img.name}: {size/1e6:.2f}MB -> {len(out)/1e6:.2f}MB "
              f"({note}); original kept as {old.name}")
        resized += 1

    print(f"\nDone. resized {resized}, skipped {skipped}, problems {problems}.")


if __name__ == "__main__":
    main()

