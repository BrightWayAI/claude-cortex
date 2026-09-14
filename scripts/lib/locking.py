"""Cross-process filesystem lock for Cortex memory mutation.

Implements core-contract.md §11: every workflow that mutates memory must
acquire this lock before its first read-modify-write step and release it on
success, failure, interruption, or early exit. Coordinates across processes
and hosts purely through the shared filesystem — no in-memory host state.
"""
from __future__ import annotations

import os
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

DEFAULT_STALE_AFTER = 120.0  # seconds
DEFAULT_TIMEOUT = 10.0  # seconds
DEFAULT_POLL_INTERVAL = 0.05  # seconds


class LockTimeoutError(Exception):
    """Raised when a lock could not be acquired before `timeout` elapsed."""


@dataclass
class MemoryLock:
    """An exclusive lock scoped to a single lock file.

    Typical usage acquires one lock per memory root for the duration of a
    mutating workflow:

        lock = MemoryLock(memory_root / ".lock")
        with lock:
            ... read-modify-write ...

    Stale-lock recovery: if the existing lock file is older than
    `stale_after` seconds, it is treated as abandoned (e.g. left behind by a
    killed process) and reclaimed automatically — no manual cleanup required.
    Ownership is tracked with a random token written into the lock file, so a
    lock holder never removes a *different* lock that was created by whoever
    reclaimed it as stale out from under it.
    """

    lock_path: Path
    timeout: float = DEFAULT_TIMEOUT
    stale_after: float = DEFAULT_STALE_AFTER
    poll_interval: float = DEFAULT_POLL_INTERVAL
    owner: str = ""

    def __post_init__(self) -> None:
        self.lock_path = Path(self.lock_path)
        if not self.owner:
            self.owner = f"{socket.gethostname()}:{os.getpid()}"
        self._token: str | None = None

    def acquire(self) -> None:
        payload_owner = self.owner
        deadline = time.monotonic() + self.timeout
        while True:
            token = uuid4().hex
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, f"{payload_owner}\n{token}\n".encode("utf-8"))
                finally:
                    os.close(fd)
                self._token = token
                return
            except FileExistsError:
                if self._reclaim_if_stale():
                    continue
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(
                        f"could not acquire lock at {self.lock_path} within "
                        f"{self.timeout}s (held by another process)"
                    )
                time.sleep(self.poll_interval)

    def _reclaim_if_stale(self) -> bool:
        try:
            age = time.time() - self.lock_path.stat().st_mtime
        except FileNotFoundError:
            # Released between our failed create and this check — retry create.
            return True
        if age <= self.stale_after:
            return False
        try:
            self.lock_path.unlink()
        except FileNotFoundError:
            pass
        return True

    def release(self) -> None:
        if self._token is None:
            return
        try:
            content = self.lock_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self._token = None
            return
        # Only remove the lock file if it is still the one we created. If a
        # different token is present, our lock was reclaimed as stale by
        # another process while we still thought we held it — removing it
        # now would delete someone else's live lock.
        if self._token in content:
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass
        self._token = None

    def __enter__(self) -> "MemoryLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


def acquire_lock_for_external_section(
    lock_path: Path, timeout: float = DEFAULT_TIMEOUT, stale_after: float = DEFAULT_STALE_AFTER
) -> str:
    """Acquire a lock that will be released by a *separate* process invocation
    (e.g. `lock-acquire` then some non-CLI steps like `git commit` then
    `lock-release`, each a distinct `cortex_cli.py` call).

    The normal MemoryLock context manager can't be used for this because its
    ownership token only exists in that one process's memory. This function
    persists the token to a sidecar file (`<lock_path>.owner`) next to the
    lock, written only by whichever call actually wins acquisition, so a
    later `release_lock_for_external_section` call can prove ownership.

    Returns the acquired token.
    """
    lock = MemoryLock(lock_path, timeout=timeout, stale_after=stale_after)
    lock.acquire()
    sidecar = Path(str(lock_path) + ".owner")
    sidecar.write_text(lock._token or "", encoding="utf-8")
    return lock._token or ""


def release_lock_for_external_section(lock_path: Path) -> bool:
    """Release a lock previously acquired via `acquire_lock_for_external_section`.

    Returns True if released, False if there was nothing to release (already
    released, or never acquired by this mechanism) — never raises on a
    missing lock or sidecar, since release must be safe to call from a
    failure/cleanup path.
    """
    sidecar = Path(str(lock_path) + ".owner")
    try:
        token = sidecar.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return False

    try:
        current_content = lock_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        current_content = ""
    still_owns = token in current_content

    lock = MemoryLock(lock_path)
    lock._token = token
    lock.release()
    try:
        sidecar.unlink()
    except FileNotFoundError:
        pass
    return still_owns
