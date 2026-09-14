from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import cortex_cli  # noqa: E402


class CortexCliTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name) / "memory"
        self.memory_root.mkdir()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_append_section_creates_node_and_section(self) -> None:
        rc = cortex_cli.main(
            [
                "append-section",
                "--memory-root",
                str(self.memory_root),
                "person/sarah-chen.md",
                "## Changelog",
                "- 2026-01-01: created",
            ]
        )
        self.assertEqual(rc, 0)
        content = (self.memory_root / "person" / "sarah-chen.md").read_text()
        self.assertIn("## Changelog", content)
        self.assertIn("- 2026-01-01: created", content)

    def test_append_section_preserves_existing_content(self) -> None:
        target = self.memory_root / "topic" / "ai-governance.md"
        target.parent.mkdir(parents=True)
        target.write_text("# topic/ai-governance\n\n## Summary\nExisting summary.\n")

        rc = cortex_cli.main(
            [
                "append-section",
                "--memory-root",
                str(self.memory_root),
                "topic/ai-governance.md",
                "## Changelog",
                "- 2026-02-01: note added",
            ]
        )
        self.assertEqual(rc, 0)
        content = target.read_text()
        self.assertIn("Existing summary.", content)
        self.assertIn("- 2026-02-01: note added", content)

    def test_replace_section_overwrites_only_named_section(self) -> None:
        target = self.memory_root / "client" / "acme.md"
        target.parent.mkdir(parents=True)
        target.write_text(
            "# client/acme\n\n## Summary\nold summary\n\n## Knowledge\n[client/acme] INSIGHT: kept\n"
        )

        rc = cortex_cli.main(
            [
                "replace-section",
                "--memory-root",
                str(self.memory_root),
                "client/acme.md",
                "## Summary",
                "new summary text",
            ]
        )
        self.assertEqual(rc, 0)
        content = target.read_text()
        self.assertIn("new summary text", content)
        self.assertNotIn("old summary", content)
        self.assertIn("[client/acme] INSIGHT: kept", content)

    def test_stdin_payload_supported(self) -> None:
        import io

        old_stdin = sys.stdin
        sys.stdin = io.StringIO("piped content\n")
        try:
            rc = cortex_cli.main(
                [
                    "replace-section",
                    "--memory-root",
                    str(self.memory_root),
                    "hiring.md",
                    "## Summary",
                    "-",
                ]
            )
        finally:
            sys.stdin = old_stdin
        self.assertEqual(rc, 0)
        content = (self.memory_root / "hiring.md").read_text()
        self.assertIn("piped content", content)

    def test_path_traversal_is_rejected_and_writes_nothing(self) -> None:
        rc = cortex_cli.main(
            [
                "append-section",
                "--memory-root",
                str(self.memory_root),
                "../../etc/passwd",
                "## Changelog",
                "malicious",
            ]
        )
        self.assertEqual(rc, 1)
        # Nothing should exist outside the memory root as a result.
        self.assertFalse((self.memory_root.parent.parent / "etc" / "passwd").exists())

    def test_lock_is_released_after_successful_mutation(self) -> None:
        cortex_cli.main(
            [
                "append-section",
                "--memory-root",
                str(self.memory_root),
                "hiring.md",
                "## Changelog",
                "- entry",
            ]
        )
        self.assertFalse((self.memory_root / ".lock").exists())


    def test_lock_acquire_then_release_roundtrip(self) -> None:
        rc = cortex_cli.main(["lock-acquire", "--memory-root", str(self.memory_root)])
        self.assertEqual(rc, 0)
        self.assertTrue((self.memory_root / ".lock").exists())

        rc = cortex_cli.main(["lock-release", "--memory-root", str(self.memory_root)])
        self.assertEqual(rc, 0)
        self.assertFalse((self.memory_root / ".lock").exists())

    def test_lock_acquire_times_out_if_already_held(self) -> None:
        cortex_cli.main(["lock-acquire", "--memory-root", str(self.memory_root)])
        rc = cortex_cli.main(
            ["lock-acquire", "--memory-root", str(self.memory_root), "--timeout", "0.2"]
        )
        self.assertEqual(rc, 1)
        cortex_cli.main(["lock-release", "--memory-root", str(self.memory_root)])

    def test_write_file_overwrites_flat_file(self) -> None:
        target = self.memory_root / "staged" / "queues" / "reindex"
        target.parent.mkdir(parents=True)
        target.write_text("2026-06-01 10:00 touched: client/acme\n2026-06-02 09:00 touched: person/x\n")

        rc = cortex_cli.main(
            [
                "write-file",
                "--memory-root",
                str(self.memory_root),
                "staged/queues/reindex",
                "2026-06-02 09:00 touched: person/x\n",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(target.read_text(), "2026-06-02 09:00 touched: person/x\n")

    def test_write_file_rejects_traversal(self) -> None:
        rc = cortex_cli.main(
            ["write-file", "--memory-root", str(self.memory_root), "../../etc/passwd", "malicious"]
        )
        self.assertEqual(rc, 1)

    def test_append_line_creates_flat_file(self) -> None:
        rc = cortex_cli.main(
            [
                "append-line",
                "--memory-root",
                str(self.memory_root),
                "staged/skip-logs/rehearse.md",
                "entry-ref skipped 2026-06-10 — defer for at least 30 days",
            ]
        )
        self.assertEqual(rc, 0)
        content = (self.memory_root / "staged" / "skip-logs" / "rehearse.md").read_text()
        self.assertIn("entry-ref skipped 2026-06-10", content)

    def test_append_line_appends_without_disturbing_existing_lines(self) -> None:
        target = self.memory_root / "staged" / "queues" / "reindex"
        target.parent.mkdir(parents=True)
        target.write_text("2026-06-01 10:00 touched: client/acme\n")
        cortex_cli.main(
            [
                "append-line",
                "--memory-root",
                str(self.memory_root),
                "staged/queues/reindex",
                "2026-06-02 09:00 touched: person/sarah-chen",
            ]
        )
        lines = target.read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("client/acme", lines[0])
        self.assertIn("sarah-chen", lines[1])

    def test_append_line_rejects_traversal(self) -> None:
        rc = cortex_cli.main(
            ["append-line", "--memory-root", str(self.memory_root), "../../etc/passwd", "malicious"]
        )
        self.assertEqual(rc, 1)

    def test_move_node_relocates_file_and_releases_lock(self) -> None:
        src = self.memory_root / "client" / "acme.md"
        src.parent.mkdir(parents=True)
        src.write_text("content\n")

        rc = cortex_cli.main(
            [
                "move-node",
                "--memory-root",
                str(self.memory_root),
                "client/acme.md",
                "archive/acme.md",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertFalse(src.exists())
        self.assertEqual((self.memory_root / "archive" / "acme.md").read_text(), "content\n")
        self.assertFalse((self.memory_root / ".lock").exists())

    def test_move_node_rejects_traversal(self) -> None:
        rc = cortex_cli.main(
            [
                "move-node",
                "--memory-root",
                str(self.memory_root),
                "client/acme.md",
                "../../etc/passwd",
            ]
        )
        self.assertEqual(rc, 1)

    def test_delete_node_removes_file_and_releases_lock(self) -> None:
        target = self.memory_root / "client" / "acme.md"
        target.parent.mkdir(parents=True)
        target.write_text("content\n")

        rc = cortex_cli.main(
            ["delete-node", "--memory-root", str(self.memory_root), "client/acme.md"]
        )
        self.assertEqual(rc, 0)
        self.assertFalse(target.exists())
        self.assertFalse((self.memory_root / ".lock").exists())

    def test_delete_node_rejects_traversal(self) -> None:
        rc = cortex_cli.main(
            ["delete-node", "--memory-root", str(self.memory_root), "../../etc/passwd"]
        )
        self.assertEqual(rc, 1)

    def test_reindex_subcommand_generates_index(self) -> None:
        (self.memory_root / "client").mkdir()
        (self.memory_root / "client" / "acme.md").write_text("# client/acme\n\n## Summary\nkept\n")
        rc = cortex_cli.main(["reindex", "--memory-root", str(self.memory_root)])
        self.assertEqual(rc, 0)
        self.assertTrue((self.memory_root / "index.md").exists())

    def test_refresh_hot_subcommand_generates_hot_cache(self) -> None:
        rc = cortex_cli.main(["refresh-hot", "--memory-root", str(self.memory_root), "--trigger", "listen"])
        self.assertEqual(rc, 0)
        content = (self.memory_root / "hot.md").read_text()
        self.assertIn("by listen", content)


if __name__ == "__main__":
    unittest.main()
