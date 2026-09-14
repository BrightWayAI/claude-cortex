# Contributing to Cortex Plugin

Thanks for your interest in improving Cortex! This guide covers what you need to know before submitting a PR.

## How the repo is organized

```
commands/          Canonical command workflows (host-neutral; Cowork loads these directly)
skills/            Cowork skill files — auto-fire versions of commands
.claude/commands/  GENERATED Claude Code slash commands — do not hand-edit (see below)
.claude-plugin/    Plugin metadata (plugin.json)
.github/           CI workflows, issue/PR templates
docs/              Architecture notes
references/        Canonical contract and workflow reference docs (see core-contract.md)
scripts/           Deterministic utilities and validation (see scripts/lib/)
```

Every command in `commands/` has a matching skill in `skills/`. If you change a command's behavior, update its skill counterpart too.

**`commands/<name>.md` is the single source of truth.** `.claude/commands/<name>.md` is mechanically generated from it by `scripts/generate_claude_commands.py` — the only difference is the top usage line, which is rewritten to Claude Code's `$ARGUMENTS` placeholder convention. Never hand-edit a file under `.claude/commands/`; your edit will be silently overwritten (and CI will flag the file as stale if you forget to regenerate). Only the 9 commands listed in `scripts/lib/command_sync.py`'s `COMMAND_ADAPTER_NAMES` currently have a generated Claude Code counterpart — see `references/core-contract.md` for how the rest are exposed via natural-language auto-fire.

## Development workflow

1. **Fork** the repo and create a feature branch from `main`.
2. Make your changes (see guidelines below).
3. Open a PR against `BrightWayAI/claude-cortex:main`.

## What to check before submitting

- [ ] **Command ↔ skill parity** — changes to a command file are reflected in the corresponding skill.
- [ ] **`.claude/commands/` regeneration** — if you change a command's behavior in `commands/` for one of the 9 adapted commands, run `python3 scripts/generate_claude_commands.py --write` and commit the result. `scripts/check_repo.py` fails the build if you forget.
- [ ] **`plugin.json` version** — bump the version in `.claude-plugin/plugin.json` when your change is user-visible (new command, behavior change, storage format change). Patch for fixes, minor for features.
- [ ] **README** — if you add or change a command, update the README command table and changelog section.
- [ ] **CHANGELOG.md** — add an entry under `## [Unreleased]` describing your change.
- [ ] **Frontmatter** — every command and skill file starts with YAML frontmatter (`---` delimiters) containing at least a `description` field. Keep it accurate.

## Writing command files

Command files are markdown instructions that Claude follows at runtime. They are **not** traditional code. A few conventions:

- **Step-numbered structure** — use `## Step N — Title` headings so Claude can follow sequentially.
- **Storage path** — refer to `<config-root>` and `<config-root>/memory` (resolved per `references/core-contract.md` §1). Don't hardcode `~/Documents/Claude` in new canonical content; that's the backward-compatible *default*, not the only valid location.
- **Per-host branches stay inline, in the canonical file** — e.g. "**Cowork**: use `mcp__cowork__request_cowork_directory`... / **Claude Code**: direct filesystem access." Don't fork a separate file to express this; write the branch once in `commands/<name>.md` and let the generator carry it into `.claude/commands/`.
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

This verifies `plugin.json` parses; that every `commands/*.md`, `skills/*/SKILL.md`, and `.claude/commands/*.md` file has valid YAML frontmatter with a `description` field; skill `name` fields match their directory; internal file references resolve; the knowledge taxonomy hasn't drifted; command/skill coverage is complete or documented as an exception; `plugin.json`/`CHANGELOG.md` versions agree; `.claude/commands/` is in sync with its canonical source; and the fixture-based unit test suite under `tests/` passes.

## Reporting issues

Use the issue templates:

- **Bug report** — include which platform (Cowork / Claude Code), which command, and what you expected vs. what happened.
- **Feature request** — describe the use case and which command or workflow it affects.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind, be constructive.

## Questions?

Open a Discussion or tag the maintainers in an issue. We're happy to help you get started.
