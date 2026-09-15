"""Read-only cap-violation scan for the summary-layer restructure (v4.16+).

Checks two things, both documented in the Nucleus Operating Model Refactor
Phase 2 spec:
  1. `## Current state` sections on restructured nodes: warn at 150 lines,
     fail at 200. This is the invariant /recall's default load boundary
     depends on (< 4K tokens per node by default).
  2. Always-loaded files (hot.md, CLAUDE.md, user.md): warn at 200 lines.

Pure and side-effect-free: never writes, never mutates. Callers (cortex_cli.py
check-caps, /cleanup Section M) render the returned violations however they
like.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CURRENT_STATE_WARN = 150
CURRENT_STATE_FAIL = 200
ALWAYS_LOADED_WARN = 200

ALWAYS_LOADED_NAMES = {"hot.md", "CLAUDE.md", "user.md"}

_CURRENT_STATE_HEADING = re.compile(r"^##\s+Current state\s*$", re.IGNORECASE)
_NEXT_HEADING_OR_DIVIDER = re.compile(r"^(##\s+\S|---\s*$)")


@dataclass(frozen=True)
class CapViolation:
    path: str
    kind: str  # "current-state" | "always-loaded"
    lines: int
    cap: int
    severity: str  # "warn" | "fail"

    def render(self) -> str:
        label = {
            "current-state": "Current state",
            "always-loaded": "always-loaded file",
        }[self.kind]
        return f"{self.severity.upper()}: {self.path} — {label} is {self.lines} lines (cap: {self.cap})"


def _count_current_state_lines(text: str) -> int | None:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _CURRENT_STATE_HEADING.match(line):
            start = i + 1
            break
    if start is None:
        return None
    count = 0
    for line in lines[start:]:
        if _NEXT_HEADING_OR_DIVIDER.match(line):
            break
        count += 1
    return count


def check_caps(memory_root: Path) -> list[CapViolation]:
    """Walk memory_root and return every cap violation found."""
    violations: list[CapViolation] = []

    for md_file in sorted(memory_root.rglob("*.md")):
        if any(part.startswith(".") for part in md_file.relative_to(memory_root).parts):
            continue
        if "staged" in md_file.relative_to(memory_root).parts:
            continue
        if "archive" in md_file.relative_to(memory_root).parts:
            continue

        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(md_file.relative_to(memory_root))

        if md_file.name in ALWAYS_LOADED_NAMES:
            total_lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            if total_lines >= ALWAYS_LOADED_WARN:
                violations.append(
                    CapViolation(rel, "always-loaded", total_lines, ALWAYS_LOADED_WARN, "warn")
                )
            continue

        cs_lines = _count_current_state_lines(text)
        if cs_lines is None:
            continue  # not a restructured node — no cap applies
        if cs_lines >= CURRENT_STATE_FAIL:
            violations.append(
                CapViolation(rel, "current-state", cs_lines, CURRENT_STATE_FAIL, "fail")
            )
        elif cs_lines >= CURRENT_STATE_WARN:
            violations.append(
                CapViolation(rel, "current-state", cs_lines, CURRENT_STATE_WARN, "warn")
            )

    return violations
