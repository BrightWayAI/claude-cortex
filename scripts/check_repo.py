#!/usr/bin/env python3
"""Validate plugin.json and YAML frontmatter on command/skill files."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.command_sync import COMMAND_ADAPTER_NAMES, derive_claude_command  # noqa: E402
from scripts.lib.repo_checks import run_all_checks  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Commands that are intentionally skill-less: pure deterministic/migration
# entrypoints with no natural-language workflow to wrap. See docs/PORTABILITY_REFACTOR_PROMPT.md
# Phase 0 audit and references/core-contract.md.
SKILL_COVERAGE_EXCEPTIONS = frozenset(
    {"merge-research-draft", "migrate-staged-substrates", "reindex"}
)


def run_unit_tests() -> int:
    """Run the fixture-based deterministic-utility test suite under tests/."""
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    if not result.wasSuccessful():
        print("ERROR: unit tests failed", file=sys.stderr)
        return 1
    print(f"OK: {result.testsRun} unit tests passed.")
    return 0


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

    findings = run_all_checks(ROOT, SKILL_COVERAGE_EXCEPTIONS)
    for f in findings:
        print(f"ERROR: {f}", file=sys.stderr)
    if findings:
        print(f"ERROR: {len(findings)} repo-check finding(s).", file=sys.stderr)
    else:
        print("OK: repo checks (skill names, internal references, taxonomy, "
              "skill coverage, version agreement) passed.")

    stale_adapters = []
    for name in COMMAND_ADAPTER_NAMES:
        canonical_path = ROOT / "commands" / f"{name}.md"
        generated_path = ROOT / ".claude" / "commands" / f"{name}.md"
        expected = derive_claude_command(canonical_path.read_text(encoding="utf-8"))
        current = generated_path.read_text(encoding="utf-8") if generated_path.exists() else ""
        if current != expected:
            stale_adapters.append(name)
    if stale_adapters:
        print(
            "ERROR: .claude/commands/ is stale for: " + ", ".join(stale_adapters) +
            " — run `python3 scripts/generate_claude_commands.py --write`",
            file=sys.stderr,
        )
    else:
        print(f"OK: .claude/commands/ is in sync for {len(COMMAND_ADAPTER_NAMES)} generated commands.")

    test_status = run_unit_tests()

    return 1 if (errors or findings or stale_adapters or test_status) else 0


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
