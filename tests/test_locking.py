from __future__ import annotations

import os
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.locking import (  # noqa: E402
    LockTimeoutError,
    MemoryLock,
    acquire_lock_for_external_section,
    release_lock_for_external_section,
)


class MemoryLockTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.lock_path = self.root / ".lock"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_acquire_and_release(self) -> None:
        lock = MemoryLock(self.lock_path)
        lock.acquire()
        self.assertTrue(self.lock_path.exists())
        lock.release()
        self.assertFalse(self.lock_path.exists())

    def test_context_manager_releases_on_exception(self) -> None:
        with self.assertRaises(ValueError):
            with MemoryLock(self.lock_path):
                raise ValueError("boom")
        self.assertFalse(self.lock_path.exists())

    def test_two_writers_competing_second_times_out(self) -> None:
        first = MemoryLock(self.lock_path, timeout=0.3, poll_interval=0.01)
        second = MemoryLock(self.lock_path, timeout=0.3, poll_interval=0.01)
        first.acquire()
        try:
            with self.assertRaises(LockTimeoutError):
                second.acquire()
        finally:
            first.release()

    def test_two_writers_competing_second_succeeds_after_first_releases(self) -> None:
        first = MemoryLock(self.lock_path, timeout=1.0, poll_interval=0.01)
        second = MemoryLock(self.lock_path, timeout=1.0, poll_interval=0.01)
        first.acquire()

        def release_after_delay() -> None:
            time.sleep(0.1)
            first.release()

        threading.Thread(target=release_after_delay).start()
        second.acquire()  # should not raise — waits for release
        second.release()

    def test_stale_lock_is_reclaimed_automatically(self) -> None:
        # Simulate an abandoned lock: write it directly and backdate mtime.
        self.lock_path.write_text("dead-host:12345\nabc\n")
        old_time = time.time() - 3600
        os.utime(self.lock_path, (old_time, old_time))

        lock = MemoryLock(self.lock_path, timeout=1.0, stale_after=60.0)
        lock.acquire()  # should reclaim, not time out
        self.assertTrue(self.lock_path.exists())
        lock.release()
        self.assertFalse(self.lock_path.exists())

    def test_fresh_lock_is_not_reclaimed(self) -> None:
        self.lock_path.write_text("live-host:999\nabc\n")
        lock = MemoryLock(self.lock_path, timeout=0.2, stale_after=60.0, poll_interval=0.01)
        with self.assertRaises(LockTimeoutError):
            lock.acquire()

    def test_release_does_not_delete_a_lock_reclaimed_by_someone_else(self) -> None:
        # A holds the lock, but its record is artificially made to look stale
        # and B reclaims it. A's release() must not delete B's live lock.
        a = MemoryLock(self.lock_path, timeout=1.0, stale_after=0.05, poll_interval=0.01)
        a.acquire()
        time.sleep(0.1)  # let A's lock become "stale" by the staleness window

        b = MemoryLock(self.lock_path, timeout=1.0, stale_after=0.05, poll_interval=0.01)
        b.acquire()  # reclaims A's now-stale lock

        a.release()  # must be a no-op: token mismatch
        self.assertTrue(self.lock_path.exists(), "A's release must not remove B's live lock")

        b.release()
        self.assertFalse(self.lock_path.exists())

    def test_idempotent_release(self) -> None:
        lock = MemoryLock(self.lock_path)
        lock.acquire()
        lock.release()
        lock.release()  # must not raise
        self.assertFalse(self.lock_path.exists())

    def test_only_one_of_many_concurrent_acquirers_holds_at_a_time(self) -> None:
        counter = {"active": 0, "max_active": 0}
        counter_lock = threading.Lock()

        def worker() -> None:
            lock = MemoryLock(self.lock_path, timeout=5.0, poll_interval=0.005)
            lock.acquire()
            try:
                with counter_lock:
                    counter["active"] += 1
                    counter["max_active"] = max(counter["max_active"], counter["active"])
                time.sleep(0.02)
                with counter_lock:
                    counter["active"] -= 1
            finally:
                lock.release()

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(counter["max_active"], 1)
        self.assertFalse(self.lock_path.exists())


class ExternalSectionLockTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.lock_path = self.root / ".lock"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_acquire_then_release_across_separate_calls(self) -> None:
        acquire_lock_for_external_section(self.lock_path)
        self.assertTrue(self.lock_path.exists())
        released = release_lock_for_external_section(self.lock_path)
        self.assertTrue(released)
        self.assertFalse(self.lock_path.exists())
        self.assertFalse(Path(str(self.lock_path) + ".owner").exists())

    def test_second_acquire_blocks_until_release(self) -> None:
        acquire_lock_for_external_section(self.lock_path, timeout=0.2)
        with self.assertRaises(LockTimeoutError):
            acquire_lock_for_external_section(self.lock_path, timeout=0.2, stale_after=60.0)

    def test_release_without_prior_acquire_is_a_safe_noop(self) -> None:
        released = release_lock_for_external_section(self.lock_path)
        self.assertFalse(released)

    def test_release_does_not_delete_lock_reclaimed_by_someone_else(self) -> None:
        acquire_lock_for_external_section(self.lock_path, stale_after=0.05)
        time.sleep(0.1)
        # Someone else reclaims the now-stale lock via the normal context manager.
        other = MemoryLock(self.lock_path, stale_after=0.05, timeout=1.0)
        other.acquire()

        released = release_lock_for_external_section(self.lock_path)
        self.assertFalse(released, "must not report success releasing a lock it no longer owns")
        self.assertTrue(self.lock_path.exists(), "must not delete the other holder's live lock")

        other.release()


if __name__ == "__main__":
    unittest.main()
