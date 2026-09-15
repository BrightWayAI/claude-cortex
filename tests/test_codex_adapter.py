from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = ROOT / "hooks" / "session_start.py"
SPEC = importlib.util.spec_from_file_location("cortex_session_start", HOOK_PATH)
assert SPEC and SPEC.loader
session_start = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(session_start)


class CodexSessionStartTests(unittest.TestCase):
    def test_env_root_wins_over_pointer_and_reads_only_fixture_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            env_root = base / "env-root"
            pointer_root = base / "pointer-root"
            (home / ".cortex").mkdir(parents=True)
            (home / ".cortex" / "config-root").write_text(str(pointer_root), encoding="utf-8")
            (env_root / "memory").mkdir(parents=True)
            (env_root / "memory" / "hot.md").write_text("# Hot\nfixture decision", encoding="utf-8")
            (env_root / "memory" / "user.md").write_text("# User\nfixture preference", encoding="utf-8")

            context = session_start.build_context(
                home=home,
                environ={"CORTEX_CONFIG_ROOT": str(env_root)},
            )

            self.assertIn(str(env_root), context)
            self.assertIn("fixture decision", context)
            self.assertIn("fixture preference", context)
            self.assertNotIn(str(pointer_root), context)

    def test_vendor_neutral_pointer_precedes_legacy_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            preferred = base / "preferred"
            legacy = base / "legacy"
            (home / ".cortex").mkdir(parents=True)
            (home / "Documents").mkdir(parents=True)
            (home / ".cortex" / "config-root").write_text(str(preferred), encoding="utf-8")
            (home / "Documents" / ".claude-plugin-config-root").write_text(
                str(legacy), encoding="utf-8"
            )

            result = session_start.resolve_for_host(home=home, environ={})

            self.assertEqual(preferred, result.path)
            self.assertEqual("~/.cortex/config-root pointer", result.source)

    def test_context_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            root = base / "cortex"
            (root / "memory").mkdir(parents=True)
            (root / "memory" / "hot.md").write_text("x" * 10_000, encoding="utf-8")

            context = session_start.build_context(
                home=home,
                environ={"CORTEX_CONFIG_ROOT": str(root)},
                max_chars=1_000,
            )

            self.assertLessEqual(len(context), 1_030)
            self.assertIn("CORTEX SESSION RECALL", context)

    def test_missing_recall_files_is_nonfatal_and_does_not_create_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            root = base / "does-not-exist"

            context = session_start.build_context(
                home=home,
                environ={"CORTEX_CONFIG_ROOT": str(root)},
            )

            self.assertIn("No recall files were readable", context)
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
