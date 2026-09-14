from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.repo_checks import (  # noqa: E402
    check_internal_references,
    check_skill_directory_has_command_or_documented_exception,
    check_skill_name_matches_directory,
    check_taxonomy_regressions,
    check_version_agreement,
)


def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class SkillNameCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_matching_name_passes(self) -> None:
        _write(self.root, "skills/learn/SKILL.md", "---\nname: learn\ndescription: x\n---\nbody\n")
        self.assertEqual(check_skill_name_matches_directory(self.root), [])

    def test_mismatched_name_flagged(self) -> None:
        _write(self.root, "skills/learn/SKILL.md", "---\nname: learning\ndescription: x\n---\nbody\n")
        findings = check_skill_name_matches_directory(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "skill-name-mismatch")

    def test_missing_name_field_flagged(self) -> None:
        _write(self.root, "skills/learn/SKILL.md", "---\ndescription: x\n---\nbody\n")
        findings = check_skill_name_matches_directory(self.root)
        self.assertEqual(findings[0].rule, "skill-name-missing")


class InternalReferenceCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_valid_reference_passes(self) -> None:
        _write(self.root, "references/decay-model.md", "content\n")
        _write(
            self.root,
            "commands/remember.md",
            "See `references/decay-model.md` for details.\n",
        )
        self.assertEqual(check_internal_references(self.root), [])

    def test_broken_reference_flagged(self) -> None:
        _write(
            self.root,
            "commands/remember.md",
            "See `references/does-not-exist.md` for details.\n",
        )
        findings = check_internal_references(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "broken-internal-reference")
        self.assertEqual(findings[0].line, 1)


class TaxonomyRegressionCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_banned_phrase_in_canonical_doc_flagged(self) -> None:
        _write(self.root, "commands/remember.md", "There are now **four** knowledge types.\n")
        findings = check_taxonomy_regressions(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "taxonomy-drift")

    def test_historical_changelog_mention_in_readme_is_not_flagged(self) -> None:
        _write(self.root, "README.md", "### v2.1.0\n- Knowledge-first redesign with six knowledge types\n")
        # README.md is intentionally out of scope for this check (historical changelog).
        self.assertEqual(check_taxonomy_regressions(self.root), [])

    def test_clean_canonical_doc_passes(self) -> None:
        _write(self.root, "commands/remember.md", "There are seven canonical knowledge types.\n")
        self.assertEqual(check_taxonomy_regressions(self.root), [])


class SkillCoverageCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_command_with_matching_skill_passes(self) -> None:
        _write(self.root, "commands/note.md", "content\n")
        _write(self.root, "skills/note/SKILL.md", "content\n")
        self.assertEqual(check_skill_directory_has_command_or_documented_exception(self.root), [])

    def test_command_without_skill_flagged(self) -> None:
        _write(self.root, "commands/reindex.md", "content\n")
        findings = check_skill_directory_has_command_or_documented_exception(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "missing-skill-coverage")

    def test_documented_exception_not_flagged(self) -> None:
        _write(self.root, "commands/reindex.md", "content\n")
        findings = check_skill_directory_has_command_or_documented_exception(
            self.root, frozenset({"reindex"})
        )
        self.assertEqual(findings, [])


class VersionAgreementCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_matching_versions_pass(self) -> None:
        _write(self.root, ".claude-plugin/plugin.json", '{"version": "4.13.2"}')
        _write(self.root, "CHANGELOG.md", "## [4.13.2] — 2026-07-07\n- stuff\n")
        self.assertEqual(check_version_agreement(self.root), [])

    def test_mismatched_versions_flagged(self) -> None:
        _write(self.root, ".claude-plugin/plugin.json", '{"version": "4.13.2"}')
        _write(self.root, "CHANGELOG.md", "## [4.13.1] — 2026-07-01\n- stuff\n")
        findings = check_version_agreement(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "version-mismatch")


if __name__ == "__main__":
    unittest.main()
