"""Manage the site's human.json (https://codeberg.org/robida/human.json).

The file at the repo root declares this site's human authorship and lists
vouches for other human-authored sites. Driven from ./human.sh:

    ./human.sh add domain.com      # vouch for a site (no duplicates)
    ./human.sh revoke domain.com   # withdraw a vouch
    ./human.sh renew domain.com    # refresh a vouch's date
    ./human.sh list                # show current vouches
"""

import argparse
import datetime
import json
import pathlib
import sys
import urllib.parse

SPEC_VERSION = "0.1.1"
SITE_URL = "https://eve.gd"
DEFAULT_PATH = pathlib.Path(__file__).resolve().parent.parent / "human.json"


def canonical_url(site):
    """Normalize a bare domain or URL to a canonical https URL."""
    site = site.strip()
    if "://" not in site:
        site = "https://" + site
    parts = urllib.parse.urlsplit(site)
    return urllib.parse.urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", "")
    )


def load(path=DEFAULT_PATH):
    """Read human.json; return a fresh skeleton if the file is absent."""
    path = pathlib.Path(path)
    if not path.exists():
        return {"version": SPEC_VERSION, "url": SITE_URL, "vouches": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(data, path=DEFAULT_PATH):
    """Write human.json as pretty-printed JSON."""
    pathlib.Path(path).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )


def _find(data, site):
    target = canonical_url(site)
    for vouch in data.get("vouches", []):
        if canonical_url(vouch["url"]) == target:
            return vouch
    return None


def add_vouch(data, site, date):
    """Add a vouch for site dated date. False if already vouched."""
    if _find(data, site) is not None:
        return False
    data.setdefault("vouches", []).append(
        {"url": canonical_url(site), "vouched_at": date}
    )
    return True


def revoke_vouch(data, site):
    """Remove the vouch for site. False if not vouched."""
    vouch = _find(data, site)
    if vouch is None:
        return False
    data["vouches"].remove(vouch)
    return True


def renew_vouch(data, site, date):
    """Refresh the vouched_at date for site. False if not vouched."""
    vouch = _find(data, site)
    if vouch is None:
        return False
    vouch["vouched_at"] = date
    return True


def main(argv=None):
    """CLI entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(
        prog="human.sh", description="Manage human.json vouches."
    )
    parser.add_argument("command", choices=["add", "revoke", "renew", "list"])
    parser.add_argument("site", nargs="?", help="bare domain or full URL")
    parser.add_argument("--file", default=DEFAULT_PATH, help="path to human.json")
    parser.add_argument("--date", help="vouch date (YYYY-MM-DD); defaults to today")
    args = parser.parse_args(argv)

    if args.command != "list" and not args.site:
        parser.error(f"'{args.command}' requires a site")

    date = args.date or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    data = load(args.file)

    if args.command == "list":
        for vouch in data.get("vouches", []):
            print(f"{vouch['url']}  (vouched {vouch['vouched_at']})")
        return 0

    if args.command == "add":
        if not add_vouch(data, args.site, date):
            print(f"Already vouched: {canonical_url(args.site)}", file=sys.stderr)
            return 1
        action = "Vouched for"
    elif args.command == "revoke":
        if not revoke_vouch(data, args.site):
            print(f"No vouch found for: {canonical_url(args.site)}", file=sys.stderr)
            return 1
        action = "Revoked vouch for"
    else:
        if not renew_vouch(data, args.site, date):
            print(f"No vouch found for: {canonical_url(args.site)}", file=sys.stderr)
            return 1
        action = "Renewed vouch for"

    save(data, args.file)
    print(f"{action} {canonical_url(args.site)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
