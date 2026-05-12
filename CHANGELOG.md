# Changelog

All notable changes to the Cortex Plugin are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions match `plugin.json`.

## [Unreleased]

## [4.2.0] — Second-brain v2 Phases 3-6 (2026-05-12)

### Added — Person pages (Phase 3)
- **`memory/person/<firstname-lastname>.md`** — new directory and schema for canonical per-contact pages. Identity / Relationship / Recent interactions / Open threads / Notes / Linked entities. Schema documented in `CLAUDE.md`.
- **Usage-graduated, not mention-graduated.** Six triggers create a page (contact-researcher dossier, 3+ recalls, project-setup primary contact, time-log billing role, explicit `[ENTITY:person]` tag, 3+ calendar meetings in 30 days). Casual mentions stay in project-node PEOPLE indices.
- **`memory/.person-recall-counter.json`** — JSON map tracking recall count per slug. After 3 recalls without a page, `/recall` offers to graduate.
- **`/recall person:<slug>`** — new query form renders the full person page when it exists; falls back to legacy cross-project profile when it doesn't.
- **`/remember` Step 3 D.1 person-page graduation logic** — detects triggers, creates pages with pre-filled content from the conversation, or appends Recent interactions to existing pages. Never overwrites Identity / Notes / Linked entities without explicit confirmation.
- **memory-librarian agent** — now checks `memory/person/<slug>.md` first for person-shaped queries; falls back to project-node ## People sections only if no page exists.
- **DASHBOARD.md** — new `## Active People` section (top 10 graduated pages, sorted by Last updated).

### Added — Cheap-tier commit triage (Phase 4)
- **`/remember` Step 0** — Haiku-class classifier decides `commit: true | false` plus affected node list before any Sonnet synthesis runs. Trivial conversations cost ~$0.001 (classifier only); substantive conversations skip the classifier overhead and proceed normally.
- **`memory/triage-log.md`** — append-only audit log of triage decisions. User reviews weekly for false-negatives.
- **`skills/observe/SKILL.md`** — auto-commit flush now always runs `/remember` Step 0. CORRECTION-type observations bypass the classifier and always commit to `user.md`.
- **Bypass rules** — explicit `/remember <node-id>` invocations and conversations with `[ENTITY:person]` tags skip Step 0 (user is asserting commit-worthiness).

### Changed — `/end-day` orchestration chain (Phase 5)
- **Rewrote `commands/end-day.md`** as a five-step chain with user gates:
  1. Inbox triage for tomorrow (delegates to `inbox-triage` plugin if installed; falls back to lighter Gmail search otherwise)
  2. Transcript-reviewer agent surfaces uncaptured commitments → per-item user gate to convert to CRM task / cortex P0 / skip
  3. Cortex auto-commit with Phase 4 cheap-tier triage
  4. Three reflective prompts (biggest done / blockers / one thing to move tomorrow) — answers also append to today's brief markdown snapshot
  5. Pre-stage tomorrow's brief artifact via `daily-brief` plugin (skipped if not installed)
- **Default-wait on gates.** If no user response within ~10s, conservative default is chosen. The chain never blocks.

### Added — Guardrails (Phase 6)
- **`/cleanup` orphan / isolated-note detection** — section G in the cleanup audit. Flags nodes with no incoming/outgoing links and last updated > 30 days ago. Per-orphan suggestion: archive / merge into candidate / keep standalone. Surfaces in DASHBOARD.md's new `## Isolated Notes` section.
- **`/cleanup` person-page maintenance** — section H. Flags dormant (no contact 12+ months), stale-interaction (entries > 90 days that haven't been archived to the page's archive section), and premature-graduation pages.
- **`/recall` duplicate-topic surfacing** — Haiku-tier semantic match on topic queries. If an existing node summary is plausibly about the same topic, surface "Note: `<node>` may already cover this. Read that first?" before the regular topic answer.

### Why this matters
Phases 3-6 of SECOND-BRAIN-V2-SPEC. Brings cortex from project-state memory to a relationship-and-cost-aware knowledge graph. Person pages make "who is this in 5 seconds before a meeting" possible. Cheap-tier triage keeps per-commit cost predictable as commit volume grows. `/end-day` ties the day's work into a single ritual. Guardrails prevent silent drift into noise.

Phase 2 (inbox-triage as a separate plugin) was deliberately skipped — `daily-brief`'s built-in Gmail fallback for section 2 is sufficient for now.

## [4.1.3] — Platform-agnostic Step 0 (2026-05-12)

### Changed
- **`/setup-identity` and `/setup-voice` Step 0 instructions are now platform-agnostic.** Every `request_cowork_directory(...)` call is wrapped in a conditional: "In Cowork, call `request_cowork_directory(...)`. In Claude Code (or any environment with direct filesystem access), no mount is needed." This lets the same plugin source serve both Cowork and Claude Code without two divergent code paths.

### Why this matters
Phase 0 of SECOND-BRAIN-V2-SPEC. Removes the implicit Cowork-only assumption that was forcing Claude Code users to debug mount calls that don't exist in their runtime. Future plugins (daily-brief, end-day, etc.) inherit this convention.

### Fixed
- `.claude/commands/remember.md` now includes v4 features: silent mode, user observation extraction, user node writes, and dashboard template (parity with `commands/remember.md`).

## [4.1.0] — Config-root awareness

### Added
- **`/setup-identity` and `/setup-voice` now honor `~/Documents/.claude-plugin-config-root`**, a single-line text pointer file at the user-level home that records the user-chosen plugin config root (set by any marketplace plugin's first-time setup, including these two commands). When the pointer exists, identity and voice files are written to `<config-root>/identity.md` and `<config-root>/voice.md` respectively. When the pointer does not exist, both commands either fall back to a pre-existing legacy default at `~/Documents/Claude/` or prompt the user to pick a config root.
- **Step 0** added to both commands: resolve the canonical file path before any read or write. Documented variables `<identity-path>` and `<voice-path>` for downstream references inside each command body.

### Why this matters
The other plugins in this marketplace previously tried to write per-plugin config to their own folder (read-only under Cowork's mount), which failed silently. The refactor across all plugins centralizes user-writable config under a user-chosen folder. Cortex was already writing to a writable user-level path, but adopting the same pointer means cortex's identity and voice files live alongside the other plugins' per-plugin configs when the user picks a non-default config root — and the convention is generic enough that any user (not just the original maintainer) can install or fork this marketplace.

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
