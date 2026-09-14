from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.command_sync import COMMAND_ADAPTER_NAMES, derive_claude_command, is_stale  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class DeriveClaudeCommandTests(unittest.TestCase):
    def test_rewrites_bracket_args_to_dollar_arguments(self) -> None:
        canonical = "---\ndescription: x\n---\n\n# /note [node] [content]\n\nbody\n"
        result = derive_claude_command(canonical)
        self.assertIn("# /note $ARGUMENTS", result)
        self.assertNotIn("[node] [content]", result)

    def test_only_rewrites_the_first_heading(self) -> None:
        canonical = (
            "---\ndescription: x\n---\n\n# /note [node] [content]\n\n"
            "See also `# /note [node]` in an example block.\n"
        )
        result = derive_claude_command(canonical)
        self.assertEqual(result.count("$ARGUMENTS"), 1)
        self.assertIn("`# /note [node]` in an example block", result)

    def test_body_is_otherwise_byte_identical(self) -> None:
        canonical = "---\ndescription: x\n---\n\n# /search [query]\n\nUnchanged body.\nMore lines.\n"
        result = derive_claude_command(canonical)
        self.assertIn("Unchanged body.\nMore lines.\n", result)

    def test_is_stale_true_when_generated_differs(self) -> None:
        canonical = "# /note [node]\nbody\n"
        self.assertTrue(is_stale(canonical, "# /note [node]\nbody\n"))

    def test_is_stale_false_when_generated_matches(self) -> None:
        canonical = "# /note [node]\nbody\n"
        generated = derive_claude_command(canonical)
        self.assertFalse(is_stale(canonical, generated))


class RealRepoAdaptersAreInSyncTests(unittest.TestCase):
    """Guards against re-drift: fails if commands/*.md and .claude/commands/*.md
    diverge again without regenerating."""

    def test_all_adapters_match_their_canonical_source(self) -> None:
        for name in COMMAND_ADAPTER_NAMES:
            canonical_path = ROOT / "commands" / f"{name}.md"
            generated_path = ROOT / ".claude" / "commands" / f"{name}.md"
            with self.subTest(name=name):
                expected = derive_claude_command(canonical_path.read_text(encoding="utf-8"))
                actual = generated_path.read_text(encoding="utf-8")
                self.assertEqual(
                    actual,
                    expected,
                    f".claude/commands/{name}.md is stale — run "
                    "`python3 scripts/generate_claude_commands.py --write`",
                )


if __name__ == "__main__":
    unittest.main()
