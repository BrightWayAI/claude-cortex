# Changelog

All notable changes to the Cortex Plugin are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions match `plugin.json`.

## [Unreleased]

### Fixed
- `.claude/commands/remember.md` now includes v4 features: silent mode, user observation extraction, user node writes, and dashboard template (parity with `commands/remember.md`).

## [4.0.0] — Always-On Learning

### Added
- **Passive observation engine** (`commands/observe.md`, `skills/observe/SKILL.md`) — silently learns user preferences, corrections, domain knowledge, and relationship context during every conversation. Never interrupts. Adapts in real-time. Flushes observations to memory at conversation end.
- **User profile node** (`user.md`) — persistent model of the user: communication preferences, working style, corrections, domain expertise, relationships, tool preferences. Carries across all projects and both platforms.
- **Auto-recall at conversation start** — loads user profile silently, checks for overdue P0s and stale threads, surfaces attention items in <=8 lines.
- **Auto-commit at conversation end** — detects farewell signals, silently commits decisions, knowledge, and observations. Skips trivial conversations.
- **Contextual recall mid-conversation** — when user mentions a known project/person/topic, surfaces 1-3 relevant knowledge entries naturally (no recall block).
- **Silent mode for `/remember`** — auto-triggered commits produce no output unless creating a new node.
- **Claude Code full support** (`claude-code/INSTRUCTIONS.md`, `claude-code/hooks.json`) — drop-in CLAUDE.md instructions and optional hooks for auto-recall/auto-commit in Claude Code.
- **Per-project config** (`.cortex.json`, `cortex.config.md`) — control capture aggressiveness (`aggressive`/`normal`/`minimal`), toggle auto behaviors, set default node, override memory path per project.
- **Dashboard template** — `DASHBOARD.md` now has a defined format (table-based Active Nodes, P0 list, Waiting On, Recent Knowledge, Stale Threads, Dormant Nodes).

### Changed
- `skills/remember/SKILL.md` — now auto-fires on farewell signals (conversation end), runs silent extraction, flushes user observations.
- `skills/recall/SKILL.md` — now auto-fires on conversation start and contextual mid-conversation mentions.
- `skills/search/SKILL.md` — disambiguated trigger phrases from `/recall` (search is cross-project; recall is single-node context).
- `skills/timeline/SKILL.md` — removed "weekly review" trigger (routes to `/review` instead).
- `commands/remember.md` — added user observation extraction (Section D), user node write step, confidence gating, silent mode, dashboard template.
- `commands/recall.md` — added Step 0 (always load user profile), auto-recall attention summary, contextual recall section.
- `commands/cleanup.md` — aligned staleness thresholds to 4-tier system (7/14/30 days) matching recall.md.
- All 9 command files — platform-aware directory access (Cowork `request_cowork_directory` vs Claude Code direct filesystem).
- `CLAUDE.md` — updated to v4 with always-on behaviors, user profile, per-project config.
- `plugin.json` — v4.0.0, updated description, added `platforms` field.

## [3.0.1]

### Added
- MIT `LICENSE` file (matches `plugin.json` license field).
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `CHANGELOG.md` as the canonical version history (README changelog remains a summary).
- GitHub issue templates (bug report, feature request) and pull request template.
- `docs/ARCHITECTURE.md` describing command/skill flow and memory layout.
- CI workflow **Validate** — JSON checks for `plugin.json`, frontmatter checks for command/skill markdown (and `.claude/commands` when present).
- `scripts/check_repo.py` used by CI.

## [3.0.0]

### Added
- **File-based storage** — memory now persists to `~/Documents/Claude/memory/` as markdown files.
- Two-tier structure: `DASHBOARD.md` for fast orientation + individual node files for detail.
- Node-to-file mapping: `client:acme-corp` → `memory/client/acme-corp.md`.
- Directories created dynamically from node prefixes — any prefix is valid.
- Every write operation updates both the node file and the dashboard.
- Archive support: `/forget --archive` moves files to `memory/archive/`.
- `/cleanup` now audits actual files on disk, detects orphaned entries and missing files.
- All 9 commands updated with explicit storage instructions.

## [2.2.0]

### Changed
- **Business-operator friendly** — all examples, taxonomy, and language updated for general business use (not just technical projects).
- Node conventions now lead with client work, bizdev, strategy, and ops.
- Added strategy/planning node type (`strategy:q2-growth`, `strategy:pricing`).
- All knowledge examples rewritten for business contexts (proposals, procurement, pricing, onboarding, retention).

## [2.1.0]

### Added
- **Knowledge-first redesign** — memory now captures insights, lessons, mental models, gotchas, recipes, and corrected beliefs as first-class entry types.
- `/learn` — quick knowledge capture without full session extraction.
- `/note` — one-liner capture for quick facts.
- `/review` — synthesized weekly digest with "Learned" as a prominent section.

### Changed
- `/recall` now surfaces knowledge entries prominently (not buried under project state).
- `/recall [topic]` — topic-based knowledge recall across all projects.
- `/search` redesigned to prioritize knowledge entries for "how/what/why" queries.
- `/remember` extraction expanded to cover both project state and knowledge categories.
- Knowledge entries preserved longer than logs during memory consolidation.

## [2.0.0]

### Added
- `/search`, `/forget`, `/timeline`, `/cleanup` commands.
- Priority system, staleness tracking, blocker tracking, people index.
- Genericized taxonomy, cross-project signals.

## [1.0.0]

### Added
- Initial release with `/remember` and `/recall`.
