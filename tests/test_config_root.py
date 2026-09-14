"""Fixture-based tests for scripts/lib/config_root.py.

Never touches a real user's filesystem or real $HOME — every test builds
its own temp directory and passes it in as `home`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.config_root import ConfigRootError, resolve_config_root  # noqa: E402


class ConfigRootResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.home = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_pointer(self, rel_path: str, content: str) -> None:
        p = self.home / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    # --- precedence ---------------------------------------------------

    def test_default_when_nothing_present(self) -> None:
        result = resolve_config_root(home=self.home)
        self.assertEqual(result.path, self.home / "Documents" / "Claude")
        self.assertEqual(result.source, "default (~/Documents/Claude)")

    def test_legacy_pointer_used_when_new_pointer_absent(self) -> None:
        self._write_pointer(
            "Documents/.claude-plugin-config-root", str(self.home / "Documents" / "ClaudeCortex")
        )
        result = resolve_config_root(home=self.home)
        self.assertEqual(result.path, self.home / "Documents" / "ClaudeCortex")
        self.assertIn("legacy", result.source)

    def test_new_pointer_wins_over_legacy_pointer(self) -> None:
        self._write_pointer(
            "Documents/.claude-plugin-config-root", str(self.home / "Documents" / "OldTarget")
        )
        self._write_pointer(".cortex/config-root", str(self.home / "NewTarget"))
        result = resolve_config_root(home=self.home)
        self.assertEqual(result.path, self.home / "NewTarget")
        self.assertEqual(result.source, "~/.cortex/config-root pointer")

    def test_env_var_wins_over_both_pointer_files(self) -> None:
        self._write_pointer(".cortex/config-root", str(self.home / "PointerTarget"))
        self._write_pointer(
            "Documents/.claude-plugin-config-root", str(self.home / "LegacyTarget")
        )
        result = resolve_config_root(
            home=self.home, environ={"CORTEX_CONFIG_ROOT": str(self.home / "EnvTarget")}
        )
        self.assertEqual(result.path, self.home / "EnvTarget")
        self.assertEqual(result.source, "CORTEX_CONFIG_ROOT env var")

    def test_explicit_override_wins_over_everything(self) -> None:
        self._write_pointer(".cortex/config-root", str(self.home / "PointerTarget"))
        result = resolve_config_root(
            home=self.home,
            environ={"CORTEX_CONFIG_ROOT": str(self.home / "EnvTarget")},
            explicit=str(self.home / "ExplicitTarget"),
        )
        self.assertEqual(result.path, self.home / "ExplicitTarget")
        self.assertEqual(result.source, "explicit override")

    def test_project_config_override_used_when_no_explicit_arg(self) -> None:
        result = resolve_config_root(
            home=self.home,
            project_config={"config_root": str(self.home / "ProjectTarget")},
        )
        self.assertEqual(result.path, self.home / "ProjectTarget")
        self.assertEqual(result.source, "explicit override")

    def test_explicit_arg_wins_over_project_config(self) -> None:
        result = resolve_config_root(
            home=self.home,
            project_config={"config_root": str(self.home / "ProjectTarget")},
            explicit=str(self.home / "ArgTarget"),
        )
        self.assertEqual(result.path, self.home / "ArgTarget")

    # --- missing / malformed pointers ----------------------------------

    def test_missing_pointers_falls_through_to_default(self) -> None:
        # No files written at all — every tier should report "not found"/"not set".
        result = resolve_config_root(home=self.home, environ={})
        self.assertEqual(result.source, "default (~/Documents/Claude)")

    def test_malformed_new_pointer_is_a_hard_error_not_a_skip(self) -> None:
        self._write_pointer(".cortex/config-root", "   ")  # empty/whitespace-only
        self._write_pointer(
            "Documents/.claude-plugin-config-root", str(self.home / "Documents" / "ClaudeCortex")
        )
        with self.assertRaises(ConfigRootError) as ctx:
            resolve_config_root(home=self.home)
        self.assertIn(".cortex/config-root", str(ctx.exception))
        # Must NOT silently fall through to the legacy pointer.
        self.assertNotIn("ClaudeCortex", str(ctx.exception))

    def test_malformed_env_var_is_a_hard_error(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, environ={"CORTEX_CONFIG_ROOT": "relative/path"})

    def test_relative_path_is_rejected(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, explicit="not/absolute")

    def test_empty_explicit_override_is_rejected(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, explicit="   ")

    # --- unsafe targets --------------------------------------------------

    def test_filesystem_root_is_rejected(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, explicit="/")

    def test_bare_home_directory_is_rejected(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, explicit=str(self.home))

    # --- tilde expansion ---------------------------------------------------

    def test_tilde_expands_against_injected_home_not_real_home(self) -> None:
        result = resolve_config_root(home=self.home, explicit="~/Documents/ClaudeCortex")
        self.assertEqual(result.path, self.home / "Documents" / "ClaudeCortex")

    def test_bare_tilde_is_rejected_as_bare_home(self) -> None:
        with self.assertRaises(ConfigRootError):
            resolve_config_root(home=self.home, explicit="~")

    # --- windows-style paths -------------------------------------------

    def test_windows_style_absolute_path_accepted_syntactically(self) -> None:
        result = resolve_config_root(home=self.home, explicit=r"C:\Users\zach\Cortex")
        self.assertEqual(str(result.path), r"C:\Users\zach\Cortex")

    def test_windows_style_forward_slash_variant_accepted(self) -> None:
        result = resolve_config_root(home=self.home, explicit="C:/Users/zach/Cortex")
        self.assertEqual(str(result.path), "C:/Users/zach/Cortex")

    # --- idempotence -------------------------------------------------------

    def test_resolution_is_stable_across_repeated_calls(self) -> None:
        self._write_pointer(".cortex/config-root", str(self.home / "Stable"))
        first = resolve_config_root(home=self.home)
        second = resolve_config_root(home=self.home)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
