import pathlib, json, base64, frontmatter
from frontmatter.default_handlers import SafeLoader

def _binary(loader, node):
    d = base64.b64decode(loader.construct_scalar(node))
    try: return d.decode("utf-8")
    except UnicodeDecodeError: return d.decode("latin-1")
SafeLoader.add_constructor("!binary", _binary)

cfg = json.loads(pathlib.Path("sequoia.json").read_text()) if pathlib.Path("sequoia.json").exists() else {}
POSTS = pathlib.Path(cfg.get("contentDir", "_posts"))
IMAGES = pathlib.Path(cfg.get("imagesDir", "images"))
FIELD = (cfg.get("frontmatter") or {}).get("coverImage", "ogImage")
base = IMAGES.name

for md in POSTS.rglob("*"):
    if md.suffix.lower() not in {".md", ".markdown", ".mdx"}:
        continue
    post = frontmatter.load(md)
    og = post.get(FIELD)
    if not isinstance(og, str) or not og or og.startswith(("http://", "https://")):
        continue
    if base in pathlib.PurePosixPath(og).parts:        # already prefixed
        continue
    if (IMAGES / og).exists():                          # real file lives at images/<og>
        post[FIELD] = f"{base}/{og}"                    # e.g. post_images/x.png -> images/post_images/x.png
        md.write_text(frontmatter.dumps(post), encoding="utf-8")
        print(f"{md.name}: {og} -> {base}/{og}")
    else:
        print(f"UNRESOLVED {md.name}: {FIELD}={og} (not found under {IMAGES})")
