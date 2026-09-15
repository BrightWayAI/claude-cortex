from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.index_generator import generate_and_write_index, render_index  # noqa: E402


def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class RenderIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)
        self.today = date(2026, 6, 1)
        self.now = datetime(2026, 6, 1, 9, 30)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_classifies_client_and_person_nodes_into_sections(self) -> None:
        _write(
            self.memory_root,
            "client/acme.md",
            "# client/acme\n\n## Summary\nActive engagement.\n\n"
            "## Knowledge\n[client/acme] INSIGHT (2026-05-20): kept. [confirmed:2026-05-20]\n",
        )
        _write(
            self.memory_root,
            "person/sarah-chen.md",
            "# person/sarah-chen\n\n## Identity\n- Full name: Sarah Chen\n"
            "[confirmed:2026-05-25]\n",
        )
        output = render_index(self.memory_root, self.today, self.now)
        self.assertIn("## Clients", output)
        self.assertIn("[[client/acme]]", output)
        self.assertIn("## People", output)
        self.assertIn("[[person/sarah-chen]]", output)

    def test_excludes_private_proposals_staged_archive_and_system_files(self) -> None:
        _write(self.memory_root, "staged/commit-drafts/draft.md", "# draft\nshould not appear\n")
        _write(self.memory_root, "proposals/alice/2026-06-01/p1.md", "# proposal\nshould not appear\n")
        _write(self.memory_root, "me/user.md", "# private profile\nshould not appear\n")
        _write(self.memory_root, "archive/old-node.md", "# old\nshould not appear\n")
        _write(self.memory_root, "person/archive/gone.md", "# gone\nshould not appear\n")
        _write(self.memory_root, "DASHBOARD.md", "# Working World Dashboard\n")
        _write(self.memory_root, "client/acme.md", "# client/acme\n\n## Summary\nkept\n")

        output = render_index(self.memory_root, self.today, self.now)
        self.assertNotIn("draft", output)
        self.assertNotIn("proposal", output)
        self.assertNotIn("private profile", output)
        self.assertNotIn("old-node", output)
        self.assertNotIn("gone", output)
        self.assertIn("client/acme", output)
        # DASHBOARD appears only in the System section, not as a scanned node.
        self.assertIn("[[DASHBOARD]]", output)

    def test_domain_note_without_prefix_goes_to_domain_notes(self) -> None:
        _write(self.memory_root, "hiring.md", "# hiring\n\nHiring plan for 2026.\n")
        output = render_index(self.memory_root, self.today, self.now)
        self.assertIn("## Domain notes", output)
        self.assertIn("[[hiring]]", output)

    def test_decay_state_fresh_vs_cold(self) -> None:
        _write(
            self.memory_root,
            "topic/fresh-topic.md",
            "# topic/fresh-topic\n\nSomething.\n[confirmed:2026-05-25]\n",
        )
        _write(
            self.memory_root,
            "topic/cold-topic.md",
            "# topic/cold-topic\n\nSomething else.\n[confirmed:2024-01-01]\n",
        )
        output = render_index(self.memory_root, self.today, self.now)
        fresh_line = [ln for ln in output.splitlines() if "fresh-topic" in ln][0]
        cold_line = [ln for ln in output.splitlines() if "cold-topic" in ln][0]
        self.assertIn("Fresh", fresh_line)
        self.assertIn("Cold", cold_line)

    def test_correction_entries_never_decay(self) -> None:
        _write(
            self.memory_root,
            "topic/old-correction.md",
            "# topic/old-correction\n\n"
            "[topic/old-correction] CORRECTION (2020-01-01): old belief -> new belief. [confirmed:2020-01-01]\n",
        )
        output = render_index(self.memory_root, self.today, self.now)
        line = [ln for ln in output.splitlines() if "old-correction" in ln][0]
        self.assertIn("Fresh", line)

    def test_missing_confirmed_tag_falls_back_to_mtime(self) -> None:
        target = self.memory_root / "topic" / "no-tags.md"
        target.parent.mkdir(parents=True)
        target.write_text("# topic/no-tags\n\nJust prose, no tags.\n")
        # Should not raise, and should classify by mtime (recent -> Fresh).
        output = render_index(self.memory_root, self.today, self.now)
        self.assertIn("no-tags", output)

    def test_output_is_stable_across_repeated_renders(self) -> None:
        _write(self.memory_root, "client/acme.md", "# client/acme\n\n## Summary\nkept\n[confirmed:2026-05-20]\n")
        first = render_index(self.memory_root, self.today, self.now)
        second = render_index(self.memory_root, self.today, self.now)
        self.assertEqual(first, second)

    def test_empty_memory_root_does_not_crash(self) -> None:
        output = render_index(self.memory_root, self.today, self.now)
        self.assertIn("# Memory index", output)
        self.assertIn("Total nodes: 0", output)


class GenerateAndWriteIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_writes_index_file_and_releases_lock(self) -> None:
        _write(self.memory_root, "client/acme.md", "# client/acme\n\n## Summary\nkept\n")
        path = generate_and_write_index(
            self.memory_root, today=date(2026, 6, 1), now=datetime(2026, 6, 1, 9, 0)
        )
        self.assertTrue(path.exists())
        self.assertIn("client/acme", path.read_text())
        self.assertFalse((self.memory_root / ".lock").exists())


if __name__ == "__main__":
    unittest.main()
