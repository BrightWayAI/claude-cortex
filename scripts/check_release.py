#!/usr/bin/env python3
"""Audit the shareable repository surface for common private-data leaks."""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SENSITIVE_BASENAMES = frozenset(
    {
        ".channels_cache_v2.json",
        ".users_cache.json",
        ".env",
        ".env.local",
    }
)
SENSITIVE_PATHS = frozenset({".claude/settings.local.json"})
SKIP_DIRS = frozenset({".git", "__pycache__", ".venv", ".venv-chatgpt-work"})
PATTERNS = (
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "contains a private-key header",
    ),
    (
        "access-token",
        re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,})"
        ),
        "contains a value shaped like an access token",
    ),
    (
        "personal-absolute-path",
        re.compile(r"(?<!:)/Users/[A-Za-z0-9._-]+/"),
        "contains a macOS user-specific absolute path",
    ),
)


@dataclass(frozen=True)
class ReleaseFinding:
    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.rule}] {self.message}"


def shareable_paths(root: Path) -> list[Path]:
    """Return tracked plus non-ignored files, with an export-tree fallback."""
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0:
        names = [name for name in completed.stdout.split(b"\0") if name]
        return [root / name.decode("utf-8", errors="surrogateescape") for name in names]

    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    ]


def audit_release(root: Path = ROOT) -> list[ReleaseFinding]:
    """Scan only files that would be shared from this checkout."""
    findings: list[ReleaseFinding] = []
    for path in sorted(shareable_paths(root)):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            findings.append(
                ReleaseFinding(relative, 1, "symlink", "must be reviewed and replaced before release")
            )
            continue
        if path.name in SENSITIVE_BASENAMES or relative in SENSITIVE_PATHS:
            findings.append(
                ReleaseFinding(relative, 1, "sensitive-file", "must not be included in a release")
            )
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            findings.append(
                ReleaseFinding(relative, 1, "unreadable-file", f"could not audit file: {exc}")
            )
            continue
        if b"\0" in raw[:8192]:
            continue
        text = raw.decode("utf-8", errors="replace")
        for rule, pattern, message in PATTERNS:
            for match in pattern.finditer(text):
                findings.append(
                    ReleaseFinding(
                        relative,
                        text[: match.start()].count("\n") + 1,
                        rule,
                        message,
                    )
                )
    return findings


def main() -> int:
    findings = audit_release(ROOT)
    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    if findings:
        print(f"ERROR: release audit found {len(findings)} issue(s).", file=sys.stderr)
        return 1
    print("OK: release audit found no common secrets, private caches, or personal absolute paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
