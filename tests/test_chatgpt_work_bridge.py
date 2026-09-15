from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from adapters.chatgpt_work.bridge import CortexBridge, CortexBridgeError
from scripts.lib.node_paths import PathTraversalError


ROOT = Path(__file__).resolve().parent.parent


class ChatGPTWorkBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.config_root = self.base / "fixture-cortex"
        self.memory_root = self.config_root / "memory"
        self.memory_root.mkdir(parents=True)
        self.bridge = CortexBridge(
            home=self.home,
            environ={"CORTEX_CONFIG_ROOT": str(self.config_root)},
            repo_root=ROOT,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_status_and_default_recall_use_only_injected_fixture(self) -> None:
        (self.memory_root / "hot.md").write_text("fixture hot", encoding="utf-8")
        (self.memory_root / "user.md").write_text("fixture preference", encoding="utf-8")

        status = self.bridge.status()
        recalled = self.bridge.recall()

        self.assertEqual(str(self.config_root), status["config_root"])
        self.assertEqual(2, status["markdown_file_count"])
        self.assertIn("fixture hot", recalled["content"])
        self.assertIn("fixture preference", recalled["content"])

    def test_configure_requires_confirmation(self) -> None:
        fresh_target = self.base / "fresh-target"
        with self.assertRaisesRegex(CortexBridgeError, "Write refused"):
            self.bridge.configure(str(fresh_target), user_confirmed=False)
        self.assertFalse(fresh_target.exists())
        self.assertFalse((self.home / ".cortex" / "config-root").exists())

    def test_configure_initializes_fixture_and_shared_pointer(self) -> None:
        result = self.bridge.configure(str(self.config_root), user_confirmed=True)

        self.assertEqual(str(self.config_root), result["config_root"])
        self.assertEqual(
            f"{self.config_root}\n",
            (self.home / ".cortex" / "config-root").read_text(encoding="utf-8"),
        )
        self.assertTrue((self.memory_root / "DASHBOARD.md").is_file())

    def test_node_recall_supports_colon_ids_and_bounds_output(self) -> None:
        target = self.memory_root / "client" / "acme.md"
        target.parent.mkdir()
        target.write_text("# client/acme\n" + ("x" * 2_000), encoding="utf-8")

        recalled = self.bridge.recall("client:acme", max_chars=100)

        self.assertEqual("client/acme.md", recalled["path"])
        self.assertIn("[truncated by Cortex MCP bridge]", recalled["content"])

    def test_search_returns_relative_line_citations(self) -> None:
        target = self.memory_root / "strategy.md"
        target.write_text("# strategy\n\nGOTCHA: fiscal year starts in April\n", encoding="utf-8")

        result = self.bridge.search("fiscal year")

        self.assertEqual(1, result["hit_count"])
        self.assertEqual("strategy.md:3", result["hits"][0]["citation"])

    def test_search_does_not_follow_symlink_outside_memory(self) -> None:
        outside = self.base / "outside-secret.md"
        outside.write_text("never expose this fixture secret", encoding="utf-8")
        link = self.memory_root / "linked-secret.md"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlinks are unavailable on this platform")

        result = self.bridge.search("fixture secret")

        self.assertEqual([], result["hits"])

    def test_write_requires_confirmation(self) -> None:
        with self.assertRaisesRegex(CortexBridgeError, "Write refused"):
            self.bridge.add_note("strategy", "Do not write", user_confirmed=False)
        self.assertFalse((self.memory_root / "strategy.md").exists())

    def test_note_mutation_shells_out_to_shared_cli(self) -> None:
        result = self.bridge.add_note("client:acme", "Fixture confirmed", user_confirmed=True)

        text = (self.memory_root / "client" / "acme.md").read_text(encoding="utf-8")
        self.assertIn("## Changelog", text)
        self.assertIn("Fixture confirmed", text)
        self.assertIn("OK: wrote", result["cli_output"])

    def test_section_update_and_derived_generators_use_fixture_root(self) -> None:
        self.bridge.update_section(
            "strategy",
            "## Summary",
            "Fixture summary",
            mode="replace",
            user_confirmed=True,
        )
        self.bridge.reindex(user_confirmed=True)
        self.bridge.refresh_hot(user_confirmed=True)

        self.assertIn(
            "Fixture summary",
            (self.memory_root / "strategy.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((self.memory_root / "index.md").is_file())
        self.assertTrue((self.memory_root / "hot.md").is_file())

    def test_path_traversal_is_rejected_for_reads_and_writes(self) -> None:
        with self.assertRaises(PathTraversalError):
            self.bridge.recall("../outside.md")
        # Write validation is intentionally performed by the shared CLI and
        # returned through the bridge's stable error type.
        with self.assertRaisesRegex(CortexBridgeError, "outside memory root"):
            self.bridge.update_section(
                "../outside.md",
                "## Summary",
                "blocked",
                mode="replace",
                user_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
