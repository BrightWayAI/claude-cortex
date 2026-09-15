from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_release import audit_release


class ReleaseAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_accepts_shareable_fixture(self) -> None:
        (self.root / "README.md").write_text("Use ~/Documents/Cortex.\n", encoding="utf-8")
        self.assertEqual([], audit_release(self.root))

    def test_rejects_private_cache_filename(self) -> None:
        (self.root / ".users_cache.json").write_text("{}", encoding="utf-8")
        self.assertEqual("sensitive-file", audit_release(self.root)[0].rule)

    def test_rejects_token_shaped_value(self) -> None:
        token = "sk-" + "1234567890abcdefghijklmnop"
        (self.root / "oops.txt").write_text(token, encoding="utf-8")
        self.assertEqual("access-token", audit_release(self.root)[0].rule)

    def test_rejects_personal_absolute_path(self) -> None:
        personal_path = "/Users/" + "alice/Documents/private"
        (self.root / "oops.txt").write_text(personal_path, encoding="utf-8")
        self.assertEqual("personal-absolute-path", audit_release(self.root)[0].rule)


if __name__ == "__main__":
    unittest.main()
