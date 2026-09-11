"""The pending-deposit ledger (_biron/deposited.yml).

SWORD deposits land in the review queue, not the live archive, so the
``biron:`` front-matter key is only stamped later by the _biron fetch
sweep once the record is public. Between those two moments this ledger
(post filename -> eprintid) is what stops a redeposit.
"""

import hashlib
from pathlib import Path

import yaml


def load_ledger(path: Path) -> dict:
    """The ledger as {filename: eprintid}; empty when the file is absent."""
    path = Path(path)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write(path: Path, ledger: dict) -> None:
    Path(path).write_text(
        yaml.safe_dump(ledger, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )


def record_deposit(path: Path, filename: str, eprintid: int) -> None:
    """Add one deposit to the ledger, creating the file when needed."""
    ledger = load_ledger(path)
    ledger[filename] = eprintid
    _write(path, ledger)


def file_digest(path: Path) -> str:
    """The sha256 hex digest of a file's bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_shipped(path: Path) -> dict:
    """The shipped-content ledger {filename: sha256}; {} when absent.

    Records what each deposited post's file hashed to when its BIROn
    record was last written, so `biron-update` can detect changed posts
    without querying the repository.
    """
    return load_ledger(path)


def record_shipped(path: Path, filename: str, digest: str) -> None:
    """Set one post's shipped digest, creating the file when needed."""
    shipped = load_shipped(path)
    shipped[filename] = digest
    _write(path, shipped)


def prune_ledger(path: Path, stamped: set[str]) -> list[str]:
    """Drop entries whose post now carries the biron: key; return them."""
    ledger = load_ledger(path)
    removed = sorted(name for name in ledger if name in stamped)
    if removed:
        for name in removed:
            del ledger[name]
        _write(path, ledger)
    return removed
