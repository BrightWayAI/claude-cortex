from __future__ import annotations

import sys
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.atomic_write import atomic_move, atomic_write, delete_node_file, safe_append  # noqa: E402


class AtomicWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_creates_new_file(self) -> None:
        target = self.root / "node.md"
        atomic_write(target, "hello\n")
        self.assertEqual(target.read_text(), "hello\n")

    def test_no_temp_files_left_behind_on_success(self) -> None:
        target = self.root / "node.md"
        atomic_write(target, "hello\n")
        leftovers = list(self.root.glob("*.tmp-*"))
        self.assertEqual(leftovers, [])

    def test_idempotent_retry_produces_no_diff(self) -> None:
        target = self.root / "node.md"
        atomic_write(target, "same content\n")
        first = target.read_text()
        atomic_write(target, "same content\n")
        second = target.read_text()
        self.assertEqual(first, second)

    def test_original_untouched_on_failure_during_write(self) -> None:
        target = self.root / "node.md"
        atomic_write(target, "original\n")

        with mock.patch("pathlib.Path.write_text", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                atomic_write(target, "corrupted\n")

        self.assertEqual(target.read_text(), "original\n")
        leftovers = list(self.root.glob("*.tmp-*"))
        self.assertEqual(leftovers, [])

    def test_creates_parent_directories(self) -> None:
        target = self.root / "person" / "sarah-chen.md"
        atomic_write(target, "# person/sarah-chen\n")
        self.assertEqual(target.read_text(), "# person/sarah-chen\n")


class SafeAppendTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_creates_file_if_absent(self) -> None:
        target = self.root / "log.md"
        safe_append(target, "line one\n")
        self.assertEqual(target.read_text(), "line one\n")

    def test_preserves_existing_unrelated_content(self) -> None:
        target = self.root / "log.md"
        target.write_text("# Existing user-authored heading\n\nSome free-form prose.\n")
        safe_append(target, "- appended line\n")
        content = target.read_text()
        self.assertIn("# Existing user-authored heading", content)
        self.assertIn("Some free-form prose.", content)
        self.assertTrue(content.endswith("- appended line\n"))

    def test_simultaneous_appends_do_not_corrupt_or_interleave(self) -> None:
        target = self.root / "log.md"
        target.write_text("")
        n_threads = 8
        n_writes = 25

        def worker(idx: int) -> None:
            for i in range(n_writes):
                safe_append(target, f"thread-{idx}-write-{i}\n")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        lines = target.read_text().splitlines()
        self.assertEqual(len(lines), n_threads * n_writes)
        # No line should be a mangled/interleaved fragment of two writes.
        for line in lines:
            self.assertRegex(line, r"^thread-\d+-write-\d+$")
        # Every expected line is present exactly once.
        expected = {f"thread-{i}-write-{j}" for i in range(n_threads) for j in range(n_writes)}
        self.assertEqual(set(lines), expected)


class AtomicMoveTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_moves_file_to_new_location(self) -> None:
        src = self.root / "client" / "acme.md"
        src.parent.mkdir(parents=True)
        src.write_text("content\n")
        dest = self.root / "archive" / "acme.md"
        atomic_move(src, dest)
        self.assertFalse(src.exists())
        self.assertEqual(dest.read_text(), "content\n")

    def test_creates_destination_parent_directories(self) -> None:
        src = self.root / "client" / "acme.md"
        src.parent.mkdir(parents=True)
        src.write_text("content\n")
        dest = self.root / "archive" / "deep" / "nested" / "acme.md"
        atomic_move(src, dest)
        self.assertEqual(dest.read_text(), "content\n")

    def test_raises_if_source_missing(self) -> None:
        with self.assertRaises(FileNotFoundError):
            atomic_move(self.root / "missing.md", self.root / "dest.md")


class DeleteNodeFileTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_deletes_existing_file(self) -> None:
        target = self.root / "node.md"
        target.write_text("content\n")
        delete_node_file(target)
        self.assertFalse(target.exists())

    def test_idempotent_on_missing_file(self) -> None:
        target = self.root / "missing.md"
        delete_node_file(target)  # must not raise
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
