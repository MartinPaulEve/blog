"""Manage the /pictures page (wraps _data/pictures.yml).

Each entry pairs an image under /images/ with a description and a
suggested credit line; the pictures/index.md template renders the
cards from the data file, so this tool is the only thing that needs
to edit it. `add` also renders a web-sized JPEG preview into
images/pictures-previews/ (the originals run to several megabytes)
and records the original's pixel size and weight for display.

Run through ./pictures.sh, which supplies the uv incantation:

    ./pictures.sh add                 # interactive wizard
    ./pictures.sh edit [filename]     # amend description/credit
    ./pictures.sh remove [filename]   # drop an image from the page
    ./pictures.sh list                # show current entries
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMAGES_DIR = "/images"
PREVIEWS_DIR = "/images/pictures-previews"
PREVIEW_MAX_WIDTH = 700
PREVIEW_QUALITY = 85
DEFAULT_CREDIT = "Photo: Martin Paul Eve, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)"


def data_file(root):
    return os.path.join(root, "_data", "pictures.yml")


def load_pictures(path):
    """Return the list of picture entries from the YAML data file."""
    import yaml

    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def save_pictures(path, entries):
    """Write the entries back to the YAML data file."""
    import yaml

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Images offered for re-use on /pictures/. Managed by\n")
        f.write("# ./pictures.sh (add/edit/remove/list); do not edit by hand.\n")
        yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False, width=1000)


def normalize_file(name):
    """Return the site-absolute path for an image file name."""
    name = name.strip()
    if name.startswith("/"):
        return name
    return f"{IMAGES_DIR}/{name}"


def find_picture(entries, name):
    """Return the entry whose file matches name, or None."""
    target = normalize_file(name)
    for e in entries:
        if e.get("file") == target:
            return e
    return None


def add_picture(entries, file, description, credit, **extra):
    """Return a new entries list with the picture appended."""
    if not description.strip():
        raise ValueError("description must not be blank")
    if not credit.strip():
        raise ValueError("credit must not be blank")
    target = normalize_file(file)
    if find_picture(entries, target):
        raise ValueError(f"{target} is already on the pictures page")
    entry = {"file": target, "description": description.strip(), "credit": credit.strip()}
    entry.update({k: v for k, v in extra.items() if v is not None})
    return list(entries) + [entry]


def update_picture(entries, file, description=None, credit=None):
    """Return a new entries list with the named picture amended."""
    target = normalize_file(file)
    out = []
    found = False
    for e in entries:
        if e.get("file") == target:
            e = dict(e)
            if description is not None and description.strip():
                e["description"] = description.strip()
            if credit is not None and credit.strip():
                e["credit"] = credit.strip()
            found = True
        out.append(e)
    if not found:
        raise ValueError(f"{target} is not on the pictures page")
    return out


def remove_picture(entries, file):
    """Return (new entries list, removed entry)."""
    target = normalize_file(file)
    removed = find_picture(entries, target)
    if removed is None:
        raise ValueError(f"{target} is not on the pictures page")
    return [e for e in entries if e is not removed], removed


def preview_path(file):
    """Return the site-absolute preview path for an image file."""
    stem = os.path.splitext(os.path.basename(normalize_file(file)))[0]
    return f"{PREVIEWS_DIR}/{stem}.jpg"


def generate_preview(src, dest, max_width=PREVIEW_MAX_WIDTH):
    """Render a web-sized JPEG preview of src at dest; returns (w, h) written."""
    from PIL import Image

    with Image.open(src) as img:
        if img.width > max_width:
            height = round(img.height * max_width / img.width)
            img = img.resize((max_width, height), Image.LANCZOS)
        if img.mode not in ("RGB", "L"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
            img = background
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        img.save(dest, "JPEG", quality=PREVIEW_QUALITY, optimize=True, progressive=True)
        return img.size


def image_info(src):
    """Return {"width", "height", "filesize"} for an image on disk."""
    from PIL import Image

    with Image.open(src) as img:
        width, height = img.size
    return {"width": width, "height": height, "filesize": os.path.getsize(src)}


def _fs_path(root, site_path):
    return os.path.join(root, site_path.lstrip("/"))


def _prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default or "")


def _choose(entries, name, verb):
    if name:
        return name
    if not entries:
        print("The pictures page is empty.", file=sys.stderr)
        return None
    print(f"Which picture would you like to {verb}?")
    for i, e in enumerate(entries, 1):
        print(f"  {i}. {os.path.basename(e['file'])} — {e['description']}")
    choice = input("Number or file name: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(entries):
        return entries[int(choice) - 1]["file"]
    return choice or None


def _format_size(nbytes):
    if nbytes >= 1024 * 1024:
        return f"{nbytes / (1024 * 1024):.1f} MB"
    return f"{nbytes / 1024:.0f} kB"


def cmd_add(args):
    entries = load_pictures(data_file(args.root))
    file = args.file or _prompt("Image file name (in images/)")
    if not file:
        print("No file given.", file=sys.stderr)
        return 1
    target = normalize_file(file)
    src = _fs_path(args.root, target)
    if not os.path.exists(src):
        print(f"No such image: {src}", file=sys.stderr)
        return 1
    if find_picture(entries, target):
        print(f"{target} is already on the pictures page (try edit).", file=sys.stderr)
        return 1

    description = args.description or _prompt("Description of the image")
    credit = args.credit or _prompt("Suggested credit line", default=DEFAULT_CREDIT)
    info = image_info(src)
    try:
        entries = add_picture(
            entries, target, description, credit,
            preview=preview_path(target), **info,
        )
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    pw, ph = generate_preview(src, _fs_path(args.root, preview_path(target)))
    save_pictures(data_file(args.root), entries)
    print(
        f"Added {target} ({info['width']}x{info['height']}, "
        f"{_format_size(info['filesize'])}; preview {pw}x{ph})."
    )
    return 0


def cmd_edit(args):
    entries = load_pictures(data_file(args.root))
    file = _choose(entries, args.file, "edit")
    if not file:
        return 1
    current = find_picture(entries, file)
    if current is None:
        print(f"{normalize_file(file)} is not on the pictures page.", file=sys.stderr)
        return 1
    description = args.description
    credit = args.credit
    if description is None and credit is None:
        description = _prompt("Description", default=current["description"])
        credit = _prompt("Suggested credit line", default=current["credit"])
    try:
        entries = update_picture(entries, file, description=description, credit=credit)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    save_pictures(data_file(args.root), entries)
    print(f"Updated {normalize_file(file)}.")
    return 0


def cmd_remove(args):
    entries = load_pictures(data_file(args.root))
    file = _choose(entries, args.file, "remove")
    if not file:
        return 1
    try:
        entries, removed = remove_picture(entries, file)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    if not args.yes:
        answer = input(f"Remove {removed['file']} from the page? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Nothing changed.")
            return 1
    preview = removed.get("preview")
    if preview:
        fs_preview = _fs_path(args.root, preview)
        if os.path.exists(fs_preview):
            os.remove(fs_preview)
    save_pictures(data_file(args.root), entries)
    print(f"Removed {removed['file']} (the original image file is untouched).")
    return 0


def cmd_list(args):
    entries = load_pictures(data_file(args.root))
    if not entries:
        print("The pictures page is empty.")
        return 0
    for e in entries:
        size = ""
        if e.get("width"):
            size = f" ({e['width']}x{e['height']}, {_format_size(e.get('filesize', 0))})"
        print(f"{e['file']}{size}")
        print(f"    {e['description']}")
        print(f"    credit: {e['credit']}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add an image to the pictures page")
    p_add.add_argument("--file", help="image file name (in images/)")
    p_add.add_argument("--description", help="description of the image")
    p_add.add_argument("--credit", help="suggested credit line")
    p_add.set_defaults(func=cmd_add)

    p_edit = sub.add_parser("edit", help="amend an image's description/credit")
    p_edit.add_argument("file", nargs="?", help="image file name")
    p_edit.add_argument("--description", help="new description")
    p_edit.add_argument("--credit", help="new credit line")
    p_edit.set_defaults(func=cmd_edit)

    p_remove = sub.add_parser("remove", help="take an image off the pictures page")
    p_remove.add_argument("file", nargs="?", help="image file name")
    p_remove.add_argument("--yes", action="store_true", help="skip confirmation")
    p_remove.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list", help="show the pictures page entries")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
