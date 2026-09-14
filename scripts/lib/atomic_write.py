"""Atomic write and safe-append primitives for Cortex memory files.

Implements core-contract.md §11: writers must never leave a reader able to
observe a partially written file, and a failure mid-write must not corrupt
the original.
"""
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write `content` to `path` atomically (write-temp-then-rename).

    On any failure, the temp file is removed and the original `path` (if it
    existed) is left completely untouched. Safe to retry — calling this
    repeatedly with the same content is idempotent (no diff after the
    first successful write).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp-{uuid4().hex}")
    try:
        tmp_path.write_text(content, encoding=encoding)
        # os.replace is atomic on POSIX and Windows when src/dst share a
        # filesystem, which they do here since tmp_path is a sibling of path.
        os.replace(tmp_path, path)
    except BaseException:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def atomic_move(src: Path, dest: Path) -> None:
    """Move `src` to `dest` atomically within the same filesystem.

    Used for archive/merge operations (e.g. `/forget --archive` moving a
    node file into `memory/archive/`). `os.replace` is atomic and works
    across directories on the same filesystem; the caller is responsible
    for holding a lock around this and any related section edits.
    """
    src = Path(src)
    dest = Path(dest)
    if not src.exists():
        raise FileNotFoundError(f"cannot move: source does not exist: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dest)


def delete_node_file(path: Path) -> None:
    """Delete `path` if it exists. Idempotent — deleting twice is not an error."""
    path = Path(path)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def safe_append(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Append `content` to `path`, creating it if absent.

    Uses a single `open(..., "a")` + fsync so the append itself is a single
    write syscall from the OS's perspective for reasonably small payloads.
    Callers performing multiple related appends, or appends that must not
    interleave with a concurrent writer, must hold a MemoryLock (see
    scripts/lib/locking.py) around the whole operation — this function alone
    only guarantees the single write is not corrupted, not mutual exclusion
    across processes.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding=encoding) as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
