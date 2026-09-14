#!/usr/bin/env python3
"""Regenerate .claude/commands/*.md from the canonical commands/*.md files.

Usage:
    python3 scripts/generate_claude_commands.py --write   # regenerate on disk
    python3 scripts/generate_claude_commands.py --check   # exit 1 if stale (CI)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.command_sync import COMMAND_ADAPTER_NAMES, derive_claude_command, is_stale  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate files on disk")
    mode.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args(argv)

    stale = []
    for name in COMMAND_ADAPTER_NAMES:
        canonical_path = ROOT / "commands" / f"{name}.md"
        generated_path = ROOT / ".claude" / "commands" / f"{name}.md"

        canonical_text = canonical_path.read_text(encoding="utf-8")
        expected = derive_claude_command(canonical_text)

        if args.write:
            generated_path.parent.mkdir(parents=True, exist_ok=True)
            generated_path.write_text(expected, encoding="utf-8")
            print(f"wrote {generated_path.relative_to(ROOT)}")
        else:
            current = generated_path.read_text(encoding="utf-8") if generated_path.exists() else ""
            if current != expected:
                stale.append(name)

    if args.check:
        if stale:
            print(
                "ERROR: .claude/commands/ is stale for: " + ", ".join(stale) +
                " — run `python3 scripts/generate_claude_commands.py --write`",
                file=sys.stderr,
            )
            return 1
        print(f"OK: .claude/commands/ is in sync for {len(COMMAND_ADAPTER_NAMES)} commands.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
