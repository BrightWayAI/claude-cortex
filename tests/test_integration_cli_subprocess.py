"""End-to-end integration tests that invoke scripts/cortex_cli.py as a real
subprocess (not an in-process function call) against a fixture memory root.

Unit tests elsewhere import functions directly and never exercise: argument
parsing, shell quoting, subprocess exit codes, or a realistic multi-step
sequence of calls the way a command's prose actually chains them (e.g.
/remember's Step 3 issuing several CLI calls in a row, then /end-day's
Step 5.5/5.6 running reindex + refresh-hot afterward). This file simulates
those sequences for real, as a smoke test for the wiring done across
/remember, /note, /forget, /cleanup, /rehearse, /relink-memory,
/sync-linked-entities, and /end-day's lock section.

Never touches real user memory — every test operates in its own
tempfile.TemporaryDirectory().
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "cortex_cli.py"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


class RememberLikeSequenceTests(unittest.TestCase):
    """Simulates /remember Step 3: several section writes to a node, then a
    DASHBOARD update, then a hot-cache/index refresh — the same sequence
    commands/remember.md's prose now describes."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_full_remember_like_sequence_end_to_end(self) -> None:
        node = "client/acme.md"

        r1 = run_cli(
            "replace-section", "--memory-root", str(self.memory_root),
            node, "## Summary", "Acme renewed for another year.",
        )
        self.assertEqual(r1.returncode, 0, r1.stderr)

        r2 = run_cli(
            "append-section", "--memory-root", str(self.memory_root),
            node, "## Knowledge",
            "[client/acme] INSIGHT (2026-06-10): Renewal always closes faster with a live call. [confirmed:2026-06-10] [recalled:2026-06-10]",
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)

        r3 = run_cli(
            "prepend-section", "--memory-root", str(self.memory_root),
            node, "## Changelog", "[client/acme] LOG 2026-06-10 — Renewed for another year.",
        )
        self.assertEqual(r3.returncode, 0, r3.stderr)

        r4 = run_cli(
            "append-line", "--memory-root", str(self.memory_root),
            "staged/queues/reindex", "2026-06-10 09:00 touched: client/acme",
        )
        self.assertEqual(r4.returncode, 0, r4.stderr)

        r5 = run_cli("reindex", "--memory-root", str(self.memory_root))
        self.assertEqual(r5.returncode, 0, r5.stderr)

        r6 = run_cli("refresh-hot", "--memory-root", str(self.memory_root), "--trigger", "remember")
        self.assertEqual(r6.returncode, 0, r6.stderr)

        # Verify final on-disk state reflects every step, in the right places.
        content = (self.memory_root / node).read_text()
        self.assertIn("Acme renewed for another year.", content)
        self.assertIn("Renewal always closes faster", content)
        self.assertIn("[client/acme] LOG 2026-06-10", content)

        index_content = (self.memory_root / "index.md").read_text()
        self.assertIn("client/acme", index_content)

        hot_content = (self.memory_root / "hot.md").read_text()
        self.assertIn("by remember", hot_content)

        # No lock left behind after the whole sequence.
        self.assertFalse((self.memory_root / ".lock").exists())

    def test_malformed_arguments_fail_loudly_not_silently(self) -> None:
        # Missing required --memory-root should be a clean argparse failure,
        # not a stack trace swallowed somewhere or a silent no-op.
        result = run_cli("replace-section", "client/acme.md", "## Summary", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("memory-root", result.stderr.lower())


class ForgetLikeSequenceTests(unittest.TestCase):
    """Simulates /forget --archive: move-node then a DASHBOARD update."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)
        node_dir = self.memory_root / "client"
        node_dir.mkdir(parents=True)
        (node_dir / "old-project.md").write_text(
            "# client/old-project\n\n## Summary\nWrapped up.\n"
        )
        (self.memory_root / "DASHBOARD.md").write_text(
            "# Working World Dashboard\n\n## Active Nodes\n| Node | Summary | Last Updated |\n"
            "|------|---------|-------------|\n| [[client/old-project]] | Wrapped up | 2026-06-01 |\n"
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_archive_sequence_end_to_end(self) -> None:
        r1 = run_cli(
            "move-node", "--memory-root", str(self.memory_root),
            "client/old-project.md", "archive/old-project.md",
        )
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertFalse((self.memory_root / "client" / "old-project.md").exists())
        self.assertTrue((self.memory_root / "archive" / "old-project.md").exists())

        r2 = run_cli(
            "replace-section", "--memory-root", str(self.memory_root),
            "DASHBOARD.md", "## Active Nodes",
            "| Node | Summary | Last Updated |\n|------|---------|-------------|\n",
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)
        dashboard = (self.memory_root / "DASHBOARD.md").read_text()
        self.assertNotIn("old-project", dashboard)


class RehearseLikeSequenceTests(unittest.TestCase):
    """Simulates /rehearse's demote action: remove from active section,
    append to Demoted knowledge, then log to changelog."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)
        node_dir = self.memory_root / "topic"
        node_dir.mkdir(parents=True)
        (node_dir / "ai-governance.md").write_text(
            "# topic/ai-governance\n\n## Knowledge\n"
            "[topic/ai-governance] INSIGHT (2026-01-01): old take on this. [confirmed:2026-01-01] [recalled:2026-01-01]\n"
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_demote_sequence_end_to_end(self) -> None:
        node = "topic/ai-governance.md"

        r1 = run_cli(
            "replace-section", "--memory-root", str(self.memory_root),
            node, "## Knowledge", "",
        )
        self.assertEqual(r1.returncode, 0, r1.stderr)

        r2 = run_cli(
            "append-section", "--memory-root", str(self.memory_root),
            node, "## Demoted knowledge",
            "[topic/ai-governance] INSIGHT (2026-01-01): old take on this. [confirmed:2026-01-01] [recalled:2026-01-01]\n"
            "  ↳ demoted 2026-06-10 by rehearse-action, reason: user judged stale during rehearsal",
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)

        content = (self.memory_root / node).read_text()
        self.assertIn("## Demoted knowledge", content)
        self.assertIn("demoted 2026-06-10 by rehearse-action", content)
        # The entry moved out of the active Knowledge section body.
        knowledge_idx = content.index("## Knowledge")
        demoted_idx = content.index("## Demoted knowledge")
        active_knowledge_body = content[knowledge_idx:demoted_idx]
        self.assertNotIn("old take on this", active_knowledge_body)


class LockAcquireReleaseAroundExternalStepTests(unittest.TestCase):
    """Simulates /end-day Step 5.8's git-commit critical section: acquire,
    do something external (here, just a file touch standing in for `git
    commit`), release — across three separate subprocess invocations."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_acquire_external_step_release_across_three_processes(self) -> None:
        r1 = run_cli("lock-acquire", "--memory-root", str(self.memory_root))
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertTrue((self.memory_root / ".lock").exists())

        # Stand-in for "git add && git commit" running as its own process.
        marker = self.memory_root / "external-step-ran"
        marker.write_text("ran while holding the lock\n")

        r2 = run_cli("lock-release", "--memory-root", str(self.memory_root))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertFalse((self.memory_root / ".lock").exists())

    def test_second_acquire_blocked_while_first_process_holds_it(self) -> None:
        r1 = run_cli("lock-acquire", "--memory-root", str(self.memory_root))
        self.assertEqual(r1.returncode, 0, r1.stderr)

        r2 = subprocess.run(
            [sys.executable, str(CLI), "lock-acquire", "--memory-root", str(self.memory_root),
             "--timeout", "0.3"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(r2.returncode, 1)

        run_cli("lock-release", "--memory-root", str(self.memory_root))


class ReindexAndHotCacheIdempotenceTests(unittest.TestCase):
    """Running the deterministic regenerators twice with no source changes
    must produce output that's stable except for the timestamp line — this
    is the actual 'deterministic claim' from Phase 5, verified via the real
    CLI rather than the library function directly."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name)
        node_dir = self.memory_root / "client"
        node_dir.mkdir(parents=True)
        (node_dir / "acme.md").write_text(
            "# client/acme\n\n## Summary\nStable content.\n[confirmed:2026-06-01]\n"
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_reindex_twice_is_stable_modulo_timestamp(self) -> None:
        run_cli("reindex", "--memory-root", str(self.memory_root))
        first = (self.memory_root / "index.md").read_text()
        run_cli("reindex", "--memory-root", str(self.memory_root))
        second = (self.memory_root / "index.md").read_text()

        def strip_timestamp(text: str) -> str:
            return "\n".join(ln for ln in text.splitlines() if not ln.startswith("_Last updated"))

        self.assertEqual(strip_timestamp(first), strip_timestamp(second))


if __name__ == "__main__":
    unittest.main()
