"""Derive a Claude Code slash-command adapter from its canonical workflow file.

Implements Phase 2 of the portability refactor: `commands/<name>.md` is the
single source of truth for a workflow. `.claude/commands/<name>.md` is a
mechanically generated view of the same content — the only difference is the
top-level usage line, which uses Claude Code's `$ARGUMENTS` placeholder
convention instead of the bracket-style `[node] [content]` placeholders used
in the Cowork-oriented canonical docs. Nothing else is allowed to diverge; if
it needs to, that's a sign the content should change in the canonical file,
not be forked here.
"""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(# /(?P<name>[a-zA-Z0-9_-]+))(?P<rest>.*)$", re.MULTILINE)

# Names with a documented, intentionally-generated .claude/commands/ counterpart.
COMMAND_ADAPTER_NAMES = (
    "cleanup",
    "forget",
    "learn",
    "note",
    "recall",
    "remember",
    "search",
)


def derive_claude_command(canonical_text: str) -> str:
    """Return the generated `.claude/commands/<name>.md` content.

    Rewrites only the first `# /<name> ...` heading line to use `$ARGUMENTS`;
    everything else is passed through byte-for-byte.
    """

    def _replace(match: re.Match[str]) -> str:
        return f"# /{match.group('name')} $ARGUMENTS"

    return HEADING_RE.sub(_replace, canonical_text, count=1)


def is_stale(canonical_text: str, generated_text: str) -> bool:
    return derive_claude_command(canonical_text) != generated_text
