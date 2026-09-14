"""Deterministic repository validation rules for scripts/check_repo.py.

Each check operates on an arbitrary repo root (never the real user's
`~/Documents/Claude`) so it can be exercised against small fixture trees in
tests/test_repo_checks.py as well as against this repository itself.

Each finding reports (file, line, rule, message) so output is actionable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

INTERNAL_REF_RE = re.compile(
    r"`((?:references|commands|skills|scripts|agents)/[A-Za-z0-9_\-./]+\.(?:md|py))`"
)

BANNED_TAXONOMY_PHRASES = (
    "four canonical types",
    "four knowledge types",
    "six knowledge types",
    "there are now **four** knowledge types",
)

HARDCODED_PATH_RE = re.compile(r"~/Documents/Claude(?!Cortex)\b")


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.file}:{self.line}: [{self.rule}] {self.message}"


def _iter_markdown(root: Path, *dirs: str) -> list[Path]:
    out = []
    for d in dirs:
        base = root / d
        if not base.exists():
            continue
        out.extend(sorted(base.rglob("*.md")))
    return out


def check_skill_name_matches_directory(root: Path) -> list[Finding]:
    """Every skills/<dir>/SKILL.md must declare `name: <dir>` in frontmatter."""
    findings: list[Finding] = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return findings

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        dir_name = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*(.+?)\s*$", text, re.MULTILINE)
        rel = str(skill_md.relative_to(root))
        if not match:
            findings.append(
                Finding(rel, 1, "skill-name-missing", "SKILL.md frontmatter has no `name:` field")
            )
            continue
        declared = match.group(1).strip()
        if declared != dir_name:
            line_no = text[: match.start()].count("\n") + 1
            findings.append(
                Finding(
                    rel,
                    line_no,
                    "skill-name-mismatch",
                    f"frontmatter name '{declared}' does not match directory '{dir_name}'",
                )
            )
    return findings


def check_internal_references(root: Path) -> list[Finding]:
    """Every backtick-quoted repo-relative .md/.py reference must exist."""
    findings: list[Finding] = []
    scan_dirs = ("commands", "skills", "references", ".claude", "agents")
    for path in _iter_markdown(root, *scan_dirs):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in INTERNAL_REF_RE.finditer(line):
                ref = m.group(1)
                if not (root / ref).exists():
                    findings.append(
                        Finding(
                            rel,
                            lineno,
                            "broken-internal-reference",
                            f"references `{ref}`, which does not exist in the repo",
                        )
                    )
    return findings


def check_taxonomy_regressions(root: Path) -> list[Finding]:
    """Guard against reintroducing the four-type/six-type taxonomy claims.

    Scoped to canonical/instructional docs only (commands, skills,
    references, CLAUDE.md, agents) — historical CHANGELOG.md entries and
    README.md's changelog section describe what was *actually* true at an
    earlier version and must not be rewritten to satisfy this check.
    """
    findings: list[Finding] = []
    candidates = _iter_markdown(root, "commands", "skills", "references", "agents", ".claude")
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        candidates.append(claude_md)
    for path in sorted(candidates):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        rel = str(path.relative_to(root))
        for lineno, line in enumerate(text.splitlines(), start=1):
            line_lower = line.lower()
            for phrase in BANNED_TAXONOMY_PHRASES:
                if phrase in line_lower:
                    findings.append(
                        Finding(
                            rel,
                            lineno,
                            "taxonomy-drift",
                            f"reintroduces a superseded taxonomy claim ('{phrase}'); "
                            "canonical taxonomy is the 7 types in CLAUDE.md / references/core-contract.md §4",
                        )
                    )
    return findings


def check_skill_directory_has_command_or_documented_exception(
    root: Path, documented_exceptions: frozenset[str] = frozenset()
) -> list[Finding]:
    """Every commands/<name>.md should have a skills/<name>/SKILL.md, or be
    explicitly listed as an exception (internal primitive / migration-only)."""
    findings: list[Finding] = []
    commands_dir = root / "commands"
    skills_dir = root / "skills"
    if not commands_dir.exists():
        return findings
    for cmd in sorted(commands_dir.glob("*.md")):
        name = cmd.stem
        if name in documented_exceptions:
            continue
        if not (skills_dir / name / "SKILL.md").exists():
            findings.append(
                Finding(
                    str(cmd.relative_to(root)),
                    1,
                    "missing-skill-coverage",
                    f"commands/{name}.md has no skills/{name}/SKILL.md and is not a "
                    "documented exception",
                )
            )
    return findings


def check_version_agreement(root: Path) -> list[Finding]:
    """plugin.json version must match the top CHANGELOG.md entry's version."""
    import json

    findings: list[Finding] = []
    plugin_path = root / ".claude-plugin" / "plugin.json"
    changelog_path = root / "CHANGELOG.md"
    if not plugin_path.exists() or not changelog_path.exists():
        return findings

    try:
        plugin_version = json.loads(plugin_path.read_text(encoding="utf-8")).get("version")
    except json.JSONDecodeError:
        return findings

    changelog_text = changelog_path.read_text(encoding="utf-8")
    match = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", changelog_text, re.MULTILINE)
    if not match:
        return findings
    changelog_version = match.group(1)

    if plugin_version != changelog_version:
        findings.append(
            Finding(
                "CHANGELOG.md",
                changelog_text[: match.start()].count("\n") + 1,
                "version-mismatch",
                f"top CHANGELOG entry is {changelog_version} but "
                f".claude-plugin/plugin.json version is {plugin_version}",
            )
        )
    return findings


def run_all_checks(root: Path, documented_skill_exceptions: frozenset[str] = frozenset()) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_skill_name_matches_directory(root))
    findings.extend(check_internal_references(root))
    findings.extend(check_taxonomy_regressions(root))
    findings.extend(check_skill_directory_has_command_or_documented_exception(root, documented_skill_exceptions))
    findings.extend(check_version_agreement(root))
    return findings
