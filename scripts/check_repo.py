#!/usr/bin/env python3
"""Validate plugin.json and YAML frontmatter on command/skill files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(plugin_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: invalid plugin.json: {e}", file=sys.stderr)
        return 1

    required = ("name", "version", "description", "license")
    missing = [k for k in required if k not in data]
    if missing:
        print(f"ERROR: plugin.json missing keys: {missing}", file=sys.stderr)
        return 1

    checked = 0
    errors = 0

    for path in sorted((ROOT / "commands").glob("*.md")):
        errors += check_markdown(path)
        checked += 1

    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        errors += check_markdown(path)
        checked += 1

    claude_cmds = ROOT / ".claude" / "commands"
    if claude_cmds.is_dir():
        for path in sorted(claude_cmds.glob("*.md")):
            errors += check_markdown(path)
            checked += 1

    print(f"OK: plugin.json valid; {checked} markdown files checked.")
    return 1 if errors else 0


def check_markdown(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        print(f"ERROR: {path.relative_to(ROOT)}: must start with YAML frontmatter (---)", file=sys.stderr)
        return 1
    end = text.find("\n---\n", 4)
    if end == -1:
        print(f"ERROR: {path.relative_to(ROOT)}: unclosed frontmatter", file=sys.stderr)
        return 1
    front = text[4:end]
    if not re.search(r"^description:\s*.+", front, re.MULTILINE):
        print(f"ERROR: {path.relative_to(ROOT)}: frontmatter must include non-empty description", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
