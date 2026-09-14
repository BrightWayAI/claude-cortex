from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.node_paths import (  # noqa: E402
    PathTraversalError,
    node_id_to_relative_path,
    resolve_node_path,
)


class ResolveNodePathTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self._tmpdir.name) / "memory"
        self.memory_root.mkdir()
        self.memory_root = self.memory_root.resolve()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_simple_relative_path_resolves_inside_root(self) -> None:
        result = resolve_node_path(self.memory_root, "person/sarah-chen.md")
        self.assertEqual(result, self.memory_root / "person" / "sarah-chen.md")

    def test_dotdot_traversal_outside_root_is_rejected(self) -> None:
        with self.assertRaises(PathTraversalError):
            resolve_node_path(self.memory_root, "../../etc/passwd")

    def test_dotdot_that_stays_inside_root_is_allowed(self) -> None:
        # person/../client/acme.md still resolves inside the root.
        result = resolve_node_path(self.memory_root, "person/../client/acme.md")
        self.assertEqual(result, self.memory_root / "client" / "acme.md")

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(PathTraversalError):
            resolve_node_path(self.memory_root, "/etc/passwd")

    def test_symlink_escape_is_rejected(self) -> None:
        outside = self.memory_root.parent / "outside.md"
        outside.write_text("secret")
        link = self.memory_root / "escape.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not supported in this environment")
        with self.assertRaises(PathTraversalError):
            resolve_node_path(self.memory_root, "escape.md")


class NodeIdToRelativePathTests(unittest.TestCase):
    def test_slash_form(self) -> None:
        self.assertEqual(node_id_to_relative_path("person/sarah-chen"), "person/sarah-chen.md")

    def test_legacy_colon_form_maps_identically_to_slash_form(self) -> None:
        self.assertEqual(
            node_id_to_relative_path("person:sarah-chen"),
            node_id_to_relative_path("person/sarah-chen"),
        )

    def test_unprefixed_root_node(self) -> None:
        self.assertEqual(node_id_to_relative_path("hiring"), "hiring.md")

    def test_empty_node_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            node_id_to_relative_path("   ")


if __name__ == "__main__":
    unittest.main()
