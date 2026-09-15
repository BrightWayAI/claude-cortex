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
from scripts.generate_codex_skills import expected_files as expected_codex_skills  # noqa: E402
from scripts.check_release import audit_release  # noqa: E402

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

    portable_plugin_path = ROOT / "plugin.json"
    try:
        portable = json.loads(portable_plugin_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: invalid portable plugin.json: {e}", file=sys.stderr)
        return 1
    portable_required = ("$schema", "name", "version", "description", "license")
    portable_missing = [k for k in portable_required if k not in portable]
    if portable_missing:
        print(f"ERROR: portable plugin.json missing keys: {portable_missing}", file=sys.stderr)
        return 1
    expected_version = data.get("version")
    if portable.get("version") != expected_version:
        print("ERROR: portable and Claude plugin versions differ", file=sys.stderr)
        return 1

    mcp_path = ROOT / "mcp.json"
    try:
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: invalid portable mcp.json: {e}", file=sys.stderr)
        return 1
    if mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        print("ERROR: mcp.json has an unsupported or missing Agent Plugins schema", file=sys.stderr)
        return 1
    cortex_server = mcp.get("mcpServers", {}).get("cortex", {})
    if cortex_server.get("type") != "stdio" or not cortex_server.get("command"):
        print("ERROR: mcp.json must declare the local Cortex stdio server", file=sys.stderr)
        return 1

    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: invalid Cortex marketplace.json: {e}", file=sys.stderr)
        return 1
    entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == "cortex"]
    if len(entries) != 1:
        print("ERROR: marketplace.json must contain exactly one Cortex entry", file=sys.stderr)
        return 1
    source = entries[0].get("source", {})
    if source.get("source") != "local" or source.get("path") != "./":
        print("ERROR: Cortex marketplace entry must point to the portable plugin root", file=sys.stderr)
        return 1
    marketplace_source = ROOT / "adapters" / "chatgpt_work" / "marketplace.json"
    if marketplace_path.read_text(encoding="utf-8") != marketplace_source.read_text(encoding="utf-8"):
        print("ERROR: .agents/plugins/marketplace.json is stale", file=sys.stderr)
        return 1

    compatibility_path = ROOT / ".codex-plugin" / "plugin.json"
    compatibility_source = ROOT / "adapters" / "chatgpt_work" / "codex-plugin.json"
    if compatibility_path.read_text(encoding="utf-8") != compatibility_source.read_text(encoding="utf-8"):
        print("ERROR: .codex-plugin/plugin.json is stale", file=sys.stderr)
        return 1
    try:
        compatibility = json.loads(compatibility_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: invalid .codex-plugin/plugin.json: {e}", file=sys.stderr)
        return 1
    if compatibility.get("version") != expected_version:
        print("ERROR: OpenAI compatibility and Claude plugin versions differ", file=sys.stderr)
        return 1

    server_text = (ROOT / "adapters" / "chatgpt_work" / "server.py").read_text(encoding="utf-8")
    if "def cortex_configure(" not in server_text:
        print("ERROR: ChatGPT Work adapter is missing cortex_configure", file=sys.stderr)
        return 1
    for required_doc in ("docs/CHATGPT_WORK_SETUP.md", "docs/ORGANIZATION_DISTRIBUTION.md"):
        if not (ROOT / required_doc).is_file():
            print(f"ERROR: missing distribution documentation: {required_doc}", file=sys.stderr)
            return 1
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for private_file in (
        ".channels_cache_v2.json",
        ".users_cache.json",
        ".claude/settings.local.json",
        ".env",
        ".env.local",
    ):
        if private_file not in gitignore:
            print(f"ERROR: .gitignore must exclude {private_file}", file=sys.stderr)
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

    codex_skills = ROOT / ".agents" / "skills"
    if codex_skills.is_dir():
        for path in sorted(codex_skills.glob("*/SKILL.md")):
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

    stale_codex = []
    try:
        codex_expected = expected_codex_skills()
    except (OSError, ValueError) as exc:
        print(f"ERROR: could not derive Codex skills: {exc}", file=sys.stderr)
        stale_codex.append("<generation failed>")
    else:
        for path, expected in codex_expected.items():
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != expected:
                stale_codex.append(str(path.relative_to(ROOT)))
    if stale_codex:
        print(
            "ERROR: generated Agent Skills are stale for: " + ", ".join(stale_codex) +
            " — run `python3 scripts/generate_codex_skills.py --write`",
            file=sys.stderr,
        )
    else:
        print(f"OK: {len(codex_expected)} shared/Codex Agent Skill wrappers are in sync.")

    stale_agents = []
    agent_sources = ROOT / "adapters" / "codex" / "agents"
    installed_agents = ROOT / ".codex" / "agents"
    source_files = sorted(agent_sources.glob("*.toml"))
    installed_files = sorted(installed_agents.glob("*.toml"))
    if {p.name for p in source_files} != {p.name for p in installed_files}:
        stale_agents.append("<agent set differs>")
    for source in source_files:
        installed = installed_agents / source.name
        current = installed.read_text(encoding="utf-8") if installed.exists() else ""
        if current != source.read_text(encoding="utf-8"):
            stale_agents.append(source.stem)
    if stale_agents:
        print(
            "ERROR: .codex/agents/ is stale for: " + ", ".join(stale_agents),
            file=sys.stderr,
        )
    else:
        print(f"OK: .codex/agents/ is in sync for {len(source_files)} roles.")

    release_findings = audit_release(ROOT)
    for finding in release_findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    if release_findings:
        print(f"ERROR: release audit found {len(release_findings)} issue(s).", file=sys.stderr)
    else:
        print("OK: release audit found no common private-data leaks.")

    test_status = run_unit_tests()

    return 1 if (
        errors
        or findings
        or stale_adapters
        or stale_codex
        or stale_agents
        or release_findings
        or test_status
    ) else 0


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
