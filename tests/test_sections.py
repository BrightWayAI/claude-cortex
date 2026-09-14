from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.sections import (  # noqa: E402
    append_to_section,
    get_section,
    prepend_to_section,
    replace_section,
)


class GetSectionTests(unittest.TestCase):
    def test_extracts_body_between_headings(self) -> None:
        text = "# node\n\n## Summary\nold summary\n\n## Knowledge\nsome knowledge\n"
        self.assertEqual(get_section(text, "## Summary"), "old summary\n\n")

    def test_last_section_extends_to_end_of_file(self) -> None:
        text = "# node\n\n## Knowledge\nentry one\nentry two\n"
        self.assertEqual(get_section(text, "## Knowledge"), "entry one\nentry two\n")

    def test_missing_heading_returns_none(self) -> None:
        text = "# node\n\n## Summary\nsomething\n"
        self.assertIsNone(get_section(text, "## Open threads"))

    def test_malformed_file_with_no_headings_returns_none(self) -> None:
        text = "just some free text with no structure at all"
        self.assertIsNone(get_section(text, "## Summary"))


class ReplaceSectionTests(unittest.TestCase):
    def test_replaces_body_leaving_other_sections_untouched(self) -> None:
        text = (
            "# node\n\n## Summary\nold summary\n\n## Knowledge\n[node] INSIGHT: kept\n"
        )
        result = replace_section(text, "## Summary", "new summary\n")
        self.assertIn("new summary", result)
        self.assertNotIn("old summary", result)
        self.assertIn("[node] INSIGHT: kept", result)

    def test_appends_new_section_when_heading_absent(self) -> None:
        text = "# node\n\n## Summary\nsomething\n"
        result = replace_section(text, "## Open threads", "- [P0] do the thing\n")
        self.assertIn("## Open threads", result)
        self.assertIn("- [P0] do the thing", result)
        self.assertIn("## Summary", result)  # untouched

    def test_handles_completely_empty_file(self) -> None:
        result = replace_section("", "## Summary", "first summary\n")
        self.assertIn("## Summary", result)
        self.assertIn("first summary", result)

    def test_handles_malformed_partial_node_file(self) -> None:
        # No frontmatter, no top-level heading, garbled content.
        text = "some partial garbage\n### random subheading with no parent\nstuff\n"
        result = replace_section(text, "## Summary", "recovered summary\n")
        self.assertIn("some partial garbage", result)  # original content preserved
        self.assertIn("## Summary", result)
        self.assertIn("recovered summary", result)


class AppendToSectionTests(unittest.TestCase):
    def test_appends_after_existing_entries(self) -> None:
        text = "# node\n\n## Changelog\n- 2026-01-01: first entry\n"
        result = append_to_section(text, "## Changelog", "- 2026-01-02: second entry")
        self.assertIn("- 2026-01-01: first entry", result)
        self.assertIn("- 2026-01-02: second entry", result)
        # First entry still precedes the second (append-only ordering).
        self.assertLess(
            result.index("first entry"),
            result.index("second entry"),
        )

    def test_creates_section_if_absent(self) -> None:
        text = "# node\n\n## Summary\nsomething\n"
        result = append_to_section(text, "## Changelog", "- 2026-01-01: created")
        self.assertIn("## Changelog", result)
        self.assertIn("- 2026-01-01: created", result)

    def test_does_not_clobber_unrelated_sections(self) -> None:
        text = (
            "# node\n\n## Summary\nkeep me\n\n## Changelog\n- old entry\n\n"
            "## Notes\nuser-authored free text that must survive\n"
        )
        result = append_to_section(text, "## Changelog", "- new entry")
        self.assertIn("keep me", result)
        self.assertIn("user-authored free text that must survive", result)
        self.assertIn("- old entry", result)
        self.assertIn("- new entry", result)


class PrependToSectionTests(unittest.TestCase):
    def test_prepends_newest_first(self) -> None:
        text = "# node\n\n## Changelog\n[node] LOG 2026-01-01 — first note\n"
        result = prepend_to_section(text, "## Changelog", "[node] LOG 2026-01-02 — second note")
        self.assertLess(
            result.index("second note"),
            result.index("first note"),
        )

    def test_creates_section_if_absent(self) -> None:
        text = "# node\n\n## Summary\nsomething\n"
        result = prepend_to_section(text, "## Changelog", "[node] LOG 2026-01-01 — created")
        self.assertIn("## Changelog", result)
        self.assertIn("created", result)


if __name__ == "__main__":
    unittest.main()
