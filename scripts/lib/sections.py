"""Read and update named Markdown sections without clobbering the rest.

Implements core-contract.md §9 (append-only vs. replaceable sections) and
§11 (updating Markdown sections without touching unrelated content). Works
on plain text so it tolerates partial or malformed node files — a missing
heading is treated as "section absent," never an error.
"""
from __future__ import annotations

import re


def _section_pattern(heading: str) -> re.Pattern[str]:
    # Matches from a heading line up to (but not including) the next heading
    # of the same or shallower level, or end of file.
    level = len(heading) - len(heading.lstrip("#"))
    escaped = re.escape(heading.strip())
    return re.compile(
        rf"(?P<full>^{escaped}\s*$\n)(?P<body>.*?)(?=^#{{1,{level}}}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )


def get_section(text: str, heading: str) -> str | None:
    """Return the body text of `heading`'s section, or None if absent."""
    match = _section_pattern(heading).search(text)
    if match is None:
        return None
    return match.group("body")


def replace_section(text: str, heading: str, new_body: str) -> str:
    """Replace the body of `heading`'s section with `new_body`.

    If the heading is not present, the section is appended at the end of
    the document (with a leading blank line for separation) rather than
    raising — a malformed or partial node file should never block a write.
    """
    if not new_body.endswith("\n"):
        new_body += "\n"
    pattern = _section_pattern(heading)
    match = pattern.search(text)
    if match is None:
        separator = "" if text.endswith("\n\n") or not text.strip() else "\n"
        return f"{text.rstrip()}\n{separator}\n{heading.strip()}\n{new_body}"
    return text[: match.start("body")] + new_body + text[match.end("body") :]


def prepend_to_section(text: str, heading: str, line: str) -> str:
    """Insert `line` at the start of `heading`'s section (newest-first logs).

    Creates the section (appended at end of document) if it doesn't exist.
    Existing body content is preserved verbatim, after the new line.
    """
    if not line.endswith("\n"):
        line += "\n"
    body = get_section(text, heading)
    if body is None:
        return replace_section(text, heading, line)
    return replace_section(text, heading, line + body)


def append_to_section(text: str, heading: str, line: str) -> str:
    """Append `line` to the end of `heading`'s section (append-only sections).

    Creates the section (appended at end of document) if it doesn't exist.
    Existing body content is preserved verbatim; `line` is added after it.
    """
    if not line.endswith("\n"):
        line += "\n"
    body = get_section(text, heading)
    if body is None:
        return replace_section(text, heading, line)
    new_body = body if body.endswith("\n") or not body else body + "\n"
    return replace_section(text, heading, new_body + line)
