from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.hot_cache_generator import (  # noqa: E402
    generate_and_write_hot_cache,
    render_hot_cache,
)


def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class RenderHotCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)
        self.today = date(2026, 6, 10)
        self.now = datetime(2026, 6, 10, 8, 0)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_includes_changelog_entries_within_window(self) -> None:
        _write(
            self.memory_root,
            "client/acme.md",
            "# client/acme\n\n## Changelog\n- 2026-06-09 — Kim confirmed the deadline\n"
            "- 2025-01-01 — ancient entry, out of window\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertIn("Kim confirmed the deadline", output)
        self.assertNotIn("ancient entry", output)

    def test_excludes_changelog_entries_outside_window(self) -> None:
        _write(
            self.memory_root,
            "client/acme.md",
            "# client/acme\n\n## Changelog\n- 2026-05-01 — too old\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertIn("nothing logged", output)

    def test_includes_recent_decisions(self) -> None:
        _write(
            self.memory_root,
            "workstream/q3-outbound.md",
            "# workstream/q3-outbound\n\n"
            "[workstream/q3-outbound] DECISION (2026-06-08): going with plan B "
            "[confirmed:2026-06-08]\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertIn("going with plan B", output)

    def test_excludes_old_decisions(self) -> None:
        _write(
            self.memory_root,
            "workstream/q3-outbound.md",
            "# workstream/q3-outbound\n\n"
            "[workstream/q3-outbound] DECISION (2020-01-01): ancient decision "
            "[confirmed:2020-01-01]\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertNotIn("ancient decision", output)

    def test_includes_open_threads(self) -> None:
        _write(
            self.memory_root,
            "client/acme.md",
            "# client/acme\n\n## Open threads\n- [P0] finalize contract\n"
            "- [WAITING:sarah] awaiting signature\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertIn("finalize contract", output)
        self.assertIn("awaiting signature", output)

    def test_excludes_private_proposals_staged_and_archive(self) -> None:
        _write(
            self.memory_root,
            "staged/commit-drafts/draft.md",
            "## Changelog\n- 2026-06-09 — should not appear\n",
        )
        _write(
            self.memory_root,
            "archive/old.md",
            "## Changelog\n- 2026-06-09 — should not appear either\n",
        )
        _write(
            self.memory_root,
            "proposals/alice/2026-06-09/p1.md",
            "## Changelog\n- 2026-06-09 — proposed only\n",
        )
        _write(
            self.memory_root,
            "me/user.md",
            "## Changelog\n- 2026-06-09 — private only\n",
        )
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertNotIn("should not appear", output)
        self.assertNotIn("proposed only", output)
        self.assertNotIn("private only", output)

    def test_trigger_is_recorded(self) -> None:
        output = render_hot_cache(self.memory_root, self.today, self.now, trigger="listen")
        self.assertIn("by listen", output)

    def test_empty_memory_root_does_not_crash(self) -> None:
        output = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertIn("# Hot cache", output)
        self.assertIn("nothing logged", output)

    def test_output_stable_across_repeated_renders(self) -> None:
        _write(
            self.memory_root, "client/acme.md", "# client/acme\n\n## Changelog\n- 2026-06-09 — stable entry\n"
        )
        first = render_hot_cache(self.memory_root, self.today, self.now)
        second = render_hot_cache(self.memory_root, self.today, self.now)
        self.assertEqual(first, second)


class GenerateAndWriteHotCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_writes_file_and_releases_lock(self) -> None:
        path = generate_and_write_hot_cache(
            self.memory_root, today=date(2026, 6, 10), now=datetime(2026, 6, 10, 8, 0)
        )
        self.assertTrue(path.exists())
        self.assertFalse((self.memory_root / ".lock").exists())


if __name__ == "__main__":
    unittest.main()
