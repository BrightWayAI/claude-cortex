# Contributing to Cortex Plugin

Thanks for your interest in improving Cortex! This guide covers what you need to know before submitting a PR.

## How the repo is organized

```
commands/          Cowork (Claude Desktop) command files — loaded by the plugin system
skills/            Cowork skill files — auto-fire versions of commands
.claude-plugin/    Plugin metadata (plugin.json)
.github/           CI workflows, issue/PR templates
docs/              Architecture notes
```

Every command in `commands/` has a matching skill in `skills/`. If you change a command's behavior, update its skill counterpart too.

## Development workflow

1. **Fork** the repo and create a feature branch from `main`.
2. Make your changes (see guidelines below).
3. Open a PR against `BrightWayAI/claude-cortex:main`.

## What to check before submitting

- [ ] **Command ↔ skill parity** — changes to a command file are reflected in the corresponding skill.
- [ ] **`.claude/commands/` parity** — if you change a command's behavior in `commands/`, apply the same changes to `.claude/commands/`, using direct filesystem access instead of `mcp__cowork__request_cowork_directory`.
- [ ] **`plugin.json` version** — bump the version in `.claude-plugin/plugin.json` when your change is user-visible (new command, behavior change, storage format change). Patch for fixes, minor for features.
- [ ] **README** — if you add or change a command, update the README command table and changelog section.
- [ ] **CHANGELOG.md** — add an entry under `## [Unreleased]` describing your change.
- [ ] **Frontmatter** — every command and skill file starts with YAML frontmatter (`---` delimiters) containing at least a `description` field. Keep it accurate.

## Writing command files

Command files are markdown instructions that Claude follows at runtime. They are **not** traditional code. A few conventions:

- **Step-numbered structure** — use `## Step N — Title` headings so Claude can follow sequentially.
- **Storage path** — memory lives at `~/Documents/Claude/memory/`. Never hardcode an absolute path; use `~` or `%USERPROFILE%` with a note for cross-platform users.
- **Cowork directory access** — `commands/` files may call `mcp__cowork__request_cowork_directory` for folder mounting. This tool only exists in Cowork. Do not add it to `.claude/commands/` files (Claude Code has native fs access).
- **No fabrication** — commands should never tell Claude to make up memory. Only commit what was actually discussed.

## Commit messages

Use a short prefix:

| Prefix | When |
|--------|------|
| `feat:` | New command, skill, or user-visible behavior |
| `fix:` | Bug fix or correction |
| `docs:` | README, CHANGELOG, CONTRIBUTING, architecture docs |
| `chore:` | CI, templates, metadata, repo hygiene |

Example: `feat(remember): add git-aware context capture (Step 1b)`

## Local checks

Before opening a PR, run the same validation as CI:

```bash
python3 scripts/check_repo.py
```

This verifies `plugin.json` parses and that every `commands/*.md` and `skills/*/SKILL.md` file has valid YAML frontmatter with a `description` field.

## Reporting issues

Use the issue templates:

- **Bug report** — include which platform (Cowork / Claude Code), which command, and what you expected vs. what happened.
- **Feature request** — describe the use case and which command or workflow it affects.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind, be constructive.

## Questions?

Open a Discussion or tag the maintainers in an issue. We're happy to help you get started.
