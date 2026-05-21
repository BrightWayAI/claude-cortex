# Changelog

All notable changes to the Cortex Plugin are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions match `plugin.json`.

## [Unreleased]

## [4.11.0] — Structural discipline: taxonomy + write-time orphan check + cleanup section K (2026-05-20)

Closes the loop on the user's question — "will the structure be improved for future users so they don't end up with random nodes?" v4.10.x was retroactive (relink existing memory). v4.11.0 is **proactive** — prevents new memory from drifting back into the disconnected pattern.

### Added — prescriptive node taxonomy

- New `references/node-taxonomy.md` — explicit rules for what node type to use when. Covers 8 types: user / client / person / company / topic / workstream / bizdev / domain-root. Plus reserved subdirs `infra/` and `archive/`.
- Decision rules: 8 questions in priority order ("Is this about a specific person? a paying engagement? a prospect? an initiative? a company? a subject area? infrastructure? a persistent area of YOUR work?") — first match wins.
- Anti-patterns documented: don't conflate prospect with client; don't dump knowledge into a mega-node; don't create ad-hoc top-level directories; don't create nodes without wikilink connections.
- Naming conventions: kebab-case; firstname-lastname for persons with company-hint disambiguation; descriptive slugs for workstreams.

### Added — `/remember` Step 1 consults the taxonomy

- Step 1 ("Detect the target node") rewritten to apply the taxonomy's decision rules before creating a new node. Old colon-prefix conventions (`client:acme`, `bizdev:stripe`) marked deprecated; new content follows the prescriptive taxonomy directly.
- Default fallback when nothing matches cleanly: `topic/<slug>`. No more ad-hoc top-level directories.

### Added — `/remember` Step 3.4 orphan warning for new nodes

- After Step 3 creates a NEW node file, check the outbound wikilink count.
- If outbound < 2 AND content mentions named entities (capitalized "First Last" patterns, capitalized companies, recognized topics) NOT wikilinked, surface a one-shot prompt: "Heads up: <node> has <N> wikilinks but mentions <entity 1>, <entity 2>, <entity 3>. Convert?" — yes / no / skip-always-this-session.
- Autonomy-aware: `auto` mode converts silently using the `/relink-memory` heuristic; `suggest` (default) surfaces the prompt; `confirm` adds emphasis.
- Skips: already-existing node updates (only fires on first-write of new nodes); `staged/` content (drafts); explicit `--no-orphan-check` flag; truly solo content (no named entities).

### Added — `/cleanup` Section K — structurally-isolated nodes

- Scans memory for nodes with **zero outbound AND zero inbound wikilinks** (excludes system files like DASHBOARD, CLAUDE.md, index.md, hot.md, log.md, user.md).
- Per-isolated-node prompt: relink (try to convert plain-text mentions) / archive (move to `memory/archive/`) / merge (into another node) / keep (legitimate solo note; suppress 90 days) / skip.
- Cap 10 per `/cleanup` run to prevent fatigue.
- Different from existing Section G (orphan-detection by dashboard-presence and recency) — Section K checks **graph connectivity** specifically.

### Why this matters

v4.10.0 fixed wikilink emission rules. v4.10.1 fixed DASHBOARD, first-name expansion, and person cross-linking. But all of those were *retroactive* — they fix accumulated mess in existing memory.

v4.11.0 is *proactive*: the taxonomy prevents ad-hoc node placement, the orphan warning prevents disconnected node creation, and Section K periodically audits structural health. Together they ensure new users don't drift into the same disconnected mess that required `/relink-memory` to clean up.

This matters across Nucleus, not just the graph view:
- **memory-librarian quality** depends on consistent node structure
- **mining accuracy** depends on canonical paths the agents can route to
- **daily-brief context loading** depends on `[[person/]]` and `[[client/]]` patterns
- **cross-plugin reads** (lead-engine, weekly-outreach, client-status) all assume the taxonomy

### How users apply it

- **New users:** automatically. Fresh installs start with the taxonomy; new content follows it from the first `/remember`.
- **Existing users:** run `/relink-memory --rerun` to apply v4.10.1's retroactive fixes (DASHBOARD regen, first-name expansion, person cross-links), then `/cleanup` to surface any remaining isolated nodes via Section K. After that, structural discipline holds going forward.

## [4.10.1] — Wikilink density: DASHBOARD hub + first-name expansion + person cross-links (2026-05-20)

Patch to v4.10.0. Real-user dogfooding showed three remaining issues after the initial wikilink fix:

1. **DASHBOARD.md had zero outbound wikilinks** even though it's the conceptual central hub. Pre-v4.10.1 dashboards used `### node-id` section headers (markdown), not `[[node-id]]` wikilinks. In Obsidian's graph view, DASHBOARD appeared as an isolated island while every active node radiated from somewhere else.

2. **First-name-only references missed by relink.** Files mentioning "Erica Hruby" once and "Erica" three more times had only the full-name match converted. Subsequent bare-first-name occurrences stayed as plain text.

3. **Person pages didn't cross-link to other persons.** Graduated pages linked to clients and brightway-profile but not to colleagues mentioned in the same source contexts. Result: graph looked like spoke-clusters around each client, not a network fabric between people.

### Fixed — DASHBOARD wikilink emission

- `commands/remember.md` Dashboard File Format template updated. Every `[node-id]` reference in the active-nodes table, P0 list, Waiting On, Recent Knowledge, Stale Threads, Dormant Nodes, Isolated Notes, and Active People rows now uses `[[wikilinks]]`. Section headers stay as `###` markdown but the references inside use wikilinks.
- `commands/relink-memory.md` adds new Step 2.5 — detects pre-v4.10.1-style DASHBOARDs (< 5 wikilinks, ≥ 3 `###` node-id section headers in Active Nodes) and regenerates them with wikilinks. Idempotent.

### Fixed — first-name expansion in relink heuristic

- `commands/relink-memory.md` Step 3 updated. After matching a full-name occurrence ("Erica Hruby") in a file, scan the same file for bare first-name occurrences ("Erica") and wikilink them. Constraints: first name must be unambiguous in this file (no two persons share it), word-boundary regex required, minimum 3-character match, contextually consistent.

### Fixed — person-to-person cross-linking

- `commands/relink-memory.md` Step 7 updated. During person-page synthesis, scan source nodes for OTHER persons mentioned in the same contexts (PEOPLE blocks, Recent Interactions, Open Threads, Changelog lines). For each other person with an existing page, add to `## Linked entities` under `Other people: [[person/<slug>]]`. Limit 10 cross-links per page.
- Reciprocal back-linking: when adding "Mary Kate" to Erica's Linked Entities, also add "Erica" to Mary Kate's Linked Entities. Avoids one-way edges. Idempotent.
- New cross-linking pass on `/relink-memory --rerun` — back-fills person-to-person edges on existing person pages that were graduated before v4.10.1.

### How to apply

Users on v4.10.0 should run `/relink-memory --rerun` after upgrading to v4.10.1. The rerun:
1. Detects + regenerates pre-v4.10.1 DASHBOARD with wikilinks.
2. Re-scans memory with first-name expansion enabled.
3. Cross-links existing person pages.

Expected outcome on a 30-node memory with ~12 person pages: DASHBOARD becomes the central hub with ~10-20 outbound edges. First-name references convert (~20-50 additional wikilinks). Person pages add ~3-8 cross-links each (~50-100 additional edges).

Combined with v4.10.0, total graph edges should be 5-10× the pre-v4.10 baseline.

## [4.10.0] — Wikilink density: schema discipline + /relink-memory backfill (2026-05-20)

Real-user diagnostic: a memory scan against a user's `<config-root>/memory/` showed 28 wikilinks across 30 node files (~1 per file). Obsidian graph view was mostly disconnected. Root cause: cortex schemas used bare-bracket `[Name]` placeholders, not wikilink `[[name]]` syntax; mining agents emitted plain-text entity references; person-page graduation never fired in practice.

This release fixes all four parts. See `nucleus/docs/proposals/wikilink-density.md` for the full diagnosis.

### Added — canonical wikilink rule in CLAUDE.md

New section in cortex CLAUDE.md formalizes the wikilink convention:
- Every entity reference in memory uses `[[<type>/<slug>]]` syntax (e.g., `[[person/sarah-chen]]`, `[[client/acme]]`, `[[workstream/q3-outbound]]`).
- If a node file exists for the entity → emit the wikilink. If not → emit bare name + increment `memory/.person-mention-counts.json` for graduation tracking.
- Applies across PEOPLE entries, knowledge entries, changelogs, open threads, DECISION `Affected:` fields, workstream `Linked entities:`, DASHBOARD, index.md.
- Bare-bracket notation in cortex docs (`[Name]`, `[role]`, `[context]`) is **template placeholder syntax**, not output syntax. Don't confuse template brackets with wikilink brackets — they're visually similar but semantically opposite.

### Updated — schema documents now use wikilinks

- `commands/remember.md` Step 2 PEOPLE template + Step 3 People Index template both updated to `[[person/<slug>]] ([role]) — [context]. Also in: [[<other-node-id>]]`.
- Person-page schema's `## Linked entities` section template updated to wikilink form.
- Wikilink rule explicitly cross-referenced in mining-agent specs (transcript-reviewer, conversation-miner, activity-miner, memory-librarian inherit via cortex CLAUDE.md context).

### Added — `/end-day` Step 3.7: passive person-page graduation

After Step 3 commits land, scan `<config-root>/memory/.person-mention-counts.json` for names with ≥ 3 mentions across ≥ 2 nodes that don't have a person page yet. Surface a one-line graduation prompt (capped at 3 per `/end-day` to prevent fatigue). On accept: synthesize a person page from all source nodes + relink the source nodes to use `[[person/<slug>]]`. On "never": suppress this name from future prompts.

### Added — `/relink-memory` retroactive command

New `commands/relink-memory.md` + `skills/relink-memory/SKILL.md`. The load-bearing fix for existing memory that predates v4.10.

What it does:
1. Builds an entity registry by walking `memory/` (every existing node file → its target wikilink + display-name variants from `# Title` lines, slug expansion, aliases).
2. Scans every node file for plain-text mentions of known entities NOT already inside `[[...]]`. Counts and contextualizes each.
3. Identifies person-name strings without person pages that meet the graduation threshold (≥ 3 mentions across ≥ 2 nodes OR ≥ 5 total).
4. Surfaces a single proposal with conversion + graduation counts.
5. User picks: accept-all / links-only / select (per-entity gate) / graduate-only / cancel.
6. On accept: edits file contents (plain-text → wikilink), synthesizes person pages from source contexts, refreshes index.md and hot.md.

Idempotent per the v4.8.1 migration pattern. Gated by `memory/.migration-wikilink-relink-done` marker. `--rerun` forces re-scan.

Conflict handling: name collisions (two persons → same slug) get the CLAUDE.md disambiguation rule. Partial matches require word-boundary + ≥ 3-character match. Case-insensitive proper-noun match preserves original casing in wikilink display.

Token cost: ~$0.10-0.50 per run depending on graduation count.

### Added — migrations.md entry

`references/migrations.md` now lists `wikilink-relink (v4.10+)` as an active migration with command, marker, and rerun behavior documented.

### Added — router intent rows (in nucleus-router v0.2.1)

Router routes "relink my memory", "fix my wikilinks", "my graph is disconnected", "back-fill the wikilinks", "graduate the people in my memory" → `/relink-memory`.

### Why this matters

Before v4.10, memory worked but the graph view didn't. With the wikilink rule canonical + mining emitting wikilinks + `/end-day` graduating people automatically + `/relink-memory` back-filling existing memory, the Obsidian graph view becomes a real navigable network of your operating world. Expected outcome on a 30-node memory: edges go from ~28 to ~150-400 after one `/relink-memory --accept-all` run.

### Downstream distribution

- **Schema + mining + graduation changes:** ship as cortex code; every user updating to v4.10+ gets correct behavior automatically.
- **Retroactive `/relink-memory` command:** ships as code, but the user has to RUN it once against their own existing memory (each install's `<config-root>/memory/` is different). New users with empty memory don't need to run it (auto-detects empty state).

## [4.9.0] — Workstream nodes + DECISION knowledge type (2026-05-20)

Part of the Chief-of-Staff evolution (see `nucleus/docs/proposals/chief-of-staff-evolution.md`). Two new cortex primitives close real navigability gaps in the second brain.

### Added — `workstream/` node type

A workstream is an **ongoing initiative pipeline** that spans multiple projects, people, and topics — distinct from projects (specific engagements), topics (subject areas), and domains (persistent areas of work).

Examples: "Q3 outbound campaign," "BrightWay 2026 product strategy," "ops platform evaluation."

- New `references/workstream-schema.md` — formal schema with sections for current state, pinned context, recent activity, open loops, linked entities, and workstream-scoped knowledge.
- New `commands/start-workstream.md` + `skills/start-workstream/SKILL.md` — interview-driven workstream creation. Triggers: "start a workstream X", "I'm beginning work on X", "track X as a workstream".
- Workstreams default to `decay_profile: slow` (1.5× modifier on freshness thresholds) — they stay fresh longer than topic nodes.
- `memory-librarian` agent gains a new query path: workstream-shape queries ("what's happening with X initiative") route to `memory/workstream/<slug>.md` first.
- `indexer` skill + `references/memory-index.md` updated — new "Workstreams" section in `memory/index.md`, grouped by `status` front-matter (active first, paused after, completed at bottom).
- `hot.md` regeneration walks workstream nodes and surfaces active ones (last_active within 7d) in the "What I worked on" section.
- Storage layout in `CLAUDE.md` updated to show `memory/workstream/<slug>.md`.

### Added — `DECISION` knowledge entry type

Decisions become first-class memory entries alongside INSIGHT / MODEL / GOTCHA / LESSON / RECIPE / CORRECTION.

Why: decisions are **forward-looking commitments**, not retrospective lessons. They're worth surfacing when context changes (cheaper to re-evaluate a decision than rediscover it).

- New DECISION type with required fields: what, when, why, affected entities, **Revisit when** trigger, status (active / superseded / revisit-now).
- `/remember` Step 2 extraction updated — recognizes decision cues ("we decided", "I'm going with", "settled on", "going forward we'll", "the call is", "made the call to"). Prompts for the Revisit-when field when captured.
- DECISIONs decay slowly (1.5× modifier, same as RECIPE and workstream nodes). They supersede via concept-drift detection — a later DECISION on the same topic moves the earlier one to Demoted knowledge with `↳ superseded by: ...`.
- New `/cleanup` section J — DECISION revisit-trigger scan. Haiku-tier classifier checks whether each DECISION's `Revisit when` trigger appears to have fired in recent activity; surfaces flagged DECISIONs for user re-evaluation. Cap 10 per `/cleanup` run to prevent fatigue.
- `memory-librarian` ranks DECISIONs higher for strategy queries ("why are we using X", "what was our approach to Y").
- `hot.md` "Recent decisions" section is now properly typed — pulls DECISION entries from last 7 days, plus any with `Status: revisit-now` regardless of age. Never truncated even at word cap.
- `references/decay-model.md` updated — DECISION joins GOTCHA and RECIPE in the slow-decay tier.

### Schema documentation

- `references/workstream-schema.md` — workstream node format
- `commands/remember.md` Step 2 — DECISION extraction template + example
- `references/decay-model.md` — DECISION decay rules
- `CLAUDE.md` knowledge-taxonomy table — DECISION added with description

### Migration

- No migration required. Existing nodes continue to work; new workstream nodes are opt-in via `/start-workstream`. DECISION entries can be added to any node going forward; existing knowledge stays untyped.
- `/end-day` Pre-chain C from v4.8.1 (staged-substrates migration) is unaffected.

### Why this matters

The user identified two real navigability gaps in the second brain:
1. **Operators run ongoing initiatives** that don't fit project/topic/domain. Workstreams capture them with the right shape (current state, pinned context, open loops, linked entities).
2. **Decisions weren't first-class** — they got buried as changelog lines or retrospective lessons. With the DECISION type, every choice has a place to live with traceable reasoning + a re-evaluation trigger.

Together with the router evolution (nucleus-router v0.2.0), this is the Chief-of-Staff layer becoming real.

## [4.8.1] — Staged substrates reorg + migrations pattern doc (2026-05-20)

Cleanup pass 1 (per `nucleus/docs/proposals/cleanup-pass-1.md`). Pure clarity refactor — no behavioral changes for users post-migration.

### Changed — unified `memory/staged/` tree

Pre-v4.8.1, in-flight memory state lived in 8 different dotfile paths under `memory/`:
- `.commit-drafts/`, `.research-drafts/`, `.heartbeat-drafts/` (drafts)
- `.reindex-queue`, `.rehearse-queue.md` (queues)
- `.rehearse-skip-log.md`, `.research-skip-log.md`, `.morning-reject-log.md` (skip-logs)

These now consolidate under `<config-root>/memory/staged/`:

```
memory/staged/
├── commit-drafts/
├── research-drafts/
├── heartbeat-drafts/
├── queues/
│   ├── reindex
│   └── rehearse.md
└── skip-logs/
    ├── rehearse.md
    ├── research.md
    └── morning-reject.md
```

All 22 cortex files that previously referenced the old paths updated. CLAUDE.md storage layout updated.

### Added — migration command + pattern doc

- New `commands/migrate-staged-substrates.md` — one-time migration that detects pre-v4.8.1 dotfiles and moves them to the new layout. Idempotent; gated by `<config-root>/memory/.migration-staged-reorg-done` marker.
- New `references/migrations.md` — names the marker-gated one-time migration pattern, lists active migrations (scope-migration, decay-config-init, gitignore-privacy-defaults, staged-substrates-reorg, hot-cache-first-generation), provides template for adding new ones.
- `/end-day` gains **Pre-chain C** that invokes `/migrate-staged-substrates` if the marker is missing — ensures every upgrading user migrates within 24h.

### Why this matters
- Eight scattered dotfiles → one named tree. Easier to read, easier to gitignore (single `memory/staged/` entry replaces 8 individual exclusions).
- Future "staged state" features (e.g., `/sweep` heartbeat drafts in cortex v4.9+) drop into `staged/heartbeat-drafts/` without inventing new dotfiles.
- The migration pattern is now documented and named — future one-time data transforms follow a consistent shape.

### Migration safety
- `/migrate-staged-substrates` does conflict-checks; if both old and new paths exist (rare), it skips and surfaces a manual-resolve prompt rather than overwriting.
- Old `.commit-drafts/` / `.research-drafts/` paths remain in the gitignore template as legacy exclusions (defensive — in case any leftover files exist after migration).
- No content changes; pure path renames. Existing drafts continue to be reviewable by `/morning` and `/merge-research-draft`.

### Files updated in this pass
- 20 cortex command + skill + reference files had path references rewritten via sed
- CLAUDE.md (storage layout + slash-command table)
- References: archive-layout.md, hot-cache.md, log-chronicle.md, memory-index.md, gitignore-template.md
- New: commands/migrate-staged-substrates.md, references/migrations.md

### Coordinated with nucleus repo
- `nucleus/docs/proposals/cleanup-pass-1.md` (this cleanup's parent spec).
- `nucleus/docs/proposals/memory-as-git.md` (next-up: vault-as-git pattern).
- `nucleus/docs/proposals/sweep-heartbeat.md` (uses new `staged/heartbeat-drafts/` path).
- `nucleus/docs/contracts.md` (lists every cross-plugin file-format dependency with both old and new paths).
- nucleus README "Start here" callout added.

## [4.8.0] — /start-nucleus onboarding walker + /observe pruned (2026-05-16)

### Added — `/start-nucleus` foundational onboarding walker
- New `commands/start-nucleus.md` + `skills/start-nucleus/SKILL.md` — the "I just installed Nucleus, now what" command. Chains the essential setups in order:
  1. `/setup-identity` (if `identity.md` missing)
  2. `/setup-voice` (skip if user opts out of drafting)
  3. `/setup-sources` (skip if user has no note adapters)
  4. `/setup-obsidian` (recommended; user opts in)
  5. Per-plugin `/setup-*` for each detected installed plugin (daily-brief, lead-engine, weekly-outreach, referral-engine, news-curator, client-status, project-setup, time-tracking, writing-style, core-ops, weekly-alignment, bizdev-outreach)
  6. `/diagnose` (if core-ops installed)
  7. `/register-schedules` (optional, if core-ops installed)
- **Idempotent.** Detects completed setups via marker files; silently skips done steps. Re-running picks up where you left off. `--reset` (with per-file confirmation) walks from scratch.
- **Every step has a skip.** Nothing is mandatory beyond `/setup-identity` (and even that surfaces a warning rather than failing).
- **Honors autonomy slider.** `autonomy: /start-nucleus: auto` collapses the menu to "going through all setups now."
- Logs to `<config-root>/memory/log.md` via the `log-writer` skill at completion.
- Router (v0.1.4) added intent rows mapping "start nucleus", "let's get started", "set me up", "onboard me", "first time setup", "let's begin", "configure everything" → `/start-nucleus`.

### Removed — `/observe` slash command
- `commands/observe.md` deleted. The full spec consolidated into `skills/observe/SKILL.md` (which was always the canonical home — the command file's own description said "this is NOT a user-facing command — it is a background behavior").
- Passive observation continues unchanged via the always-on skill. No functional change.
- Router intent table updated (v0.1.4) to remove the "/observe" row. Trigger phrases like "passively observe X" / "watch for X" now route to no command — observation is always on, no command needed.
- Migration: if you typed `/observe` in a memory entry or script, it will no longer resolve. The behavior it described is still active; just no slash-command surface.

### Why this matters
- **/start-nucleus is the productization unblock.** Before this, a new user had to know about and run 5-9 setup commands in the right order. After this, they say "start nucleus" and the AI walks them. Critical for sharing Nucleus with operators who aren't power users.
- **Pruning /observe** removes a phantom command. The doc said it wasn't user-facing; now the catalog matches the doc.

## [4.7.2] — Wiring + privacy: autonomy gates, log centralization, gitignore defaults (2026-05-16)

### Added — `.gitignore` privacy defaults
- New `references/gitignore-template.md` — the canonical privacy gitignore + cloud-sync notes for `<config-root>/`. Documents what's protected (archive/, .commit-drafts/, .research-drafts/, queue markers, plugin runtime state, Obsidian local-only state) and what's still versioned (active node files, briefs, hot.md, log.md, identity/voice/VAULT).
- `/setup-identity` Step 3.5 (new) — writes `.gitignore` with privacy defaults if missing. Surfaces a one-line cloud-sync warning if `<config-root>/` is inside iCloud / Dropbox / OneDrive / Google Drive (since `.gitignore` doesn't apply to cloud sync).
- `/listen` Step 0.5 (new) — defensive check before pulling raw substrate. If `.gitignore` doesn't exist, creates it. If it exists but is missing `archive/` or `memory/.commit-drafts/`, appends them under a "Added by cortex /listen first-run" section. Idempotent.
- Cloud-sync caveat documented in the template — iCloud lacks selective sync; recommended pattern is symlinking `archive/` to `~/.cache/nucleus/archive/` (out of the synced directory) before the first `/listen` run.

### Added — autonomy wiring at command level (Karpathy Iron Man slider, take 2)
- `/forget` Step 3 — consults `autonomy` mode (default `confirm`). `auto` skips the gate; `confirm` per-effect prompts; `suggest` single yes/no.
- `/cleanup` Step 3 — consults mode (default `suggest`). `auto` executes all proposed actions inline; `confirm` walks per-item.
- `/setup-obsidian` Step 2 — consults mode (default `confirm`). `auto` skips the plan-and-confirm prompt.
- `references/autonomy.md` updated with "Where autonomy is currently wired (v4.7.2)" section documenting the three levels (router, command gates, future) and listing which commands are/aren't wired and why.

### Added — log centralization
- New `skills/log-writer/SKILL.md` — programmatic primitive invoked by other cortex commands at their "Log to chronicle" steps. Takes `op_name` + `summary` (and optional `body`, `timestamp`); writes one formatted entry to `<config-root>/memory/log.md`. Single source of truth for the log format.
- All 9 commands with Log steps (`/listen`, `/morning`, `/end-day`, `/end-week`, `/reindex`, `/research-gaps`, `/merge-research-draft`, `/cleanup`, `/rehearse`) updated to invoke `log-writer` with structured inputs instead of inlining the format string. If the chronicle format ever changes, only `log-writer` needs updating.

### Why this matters
- **Privacy defaults shipped.** First-run `/listen` no longer risks committing raw email / Slack / transcript content to git. Cloud-sync gap is documented for users to address.
- **Autonomy slider actually moves the needle.** Three high-traffic cortex commands now respect user-set autonomy preferences at their internal gates. `auto` mode for `/cleanup` lets scheduled cleanups run unattended; `auto` mode for `/forget` is hands-off for users who trust the operation.
- **Log format is now single-source-of-truth.** Future format changes won't require touching 9 command files.

## [4.7.1] — Karpathy patterns: memory/log.md chronicle + autonomy slider (2026-05-16)

### Added — `memory/log.md` chronicle
- New `references/log-chronicle.md` — formal spec for the unified append-only operations log at `<config-root>/memory/log.md`. Grep-friendly date prefixes (`## [YYYY-MM-DD HH:MM] <op> | <summary>`). Karpathy LLM-wiki `log.md` pattern.
- New `## Log` step appended to: `/listen` (Step 7.5), `/morning` (Step 4.5), `/end-day` (Step 5.7), `/end-week` (Step 5.7), `/reindex` (Step 5.5), `/research-gaps` (Step 4.5), `/merge-research-draft` (Step 4.5), `/cleanup` (Step 4.7), `/rehearse` (Step 4.5). Each appends one line at completion. No silent commands log; the log is for audit-worthy operations only.
- CLAUDE.md storage-layout section updated to mention `memory/log.md` and link to the spec.
- Optional retention controls via `<config-root>/plugins/cortex.user-context.md` (`log_chronicle.max_entries`, `log_chronicle.archive_yearly`).

### Added — per-command autonomy slider
- New `references/autonomy.md` — Karpathy Software 3.0 "Iron Man suit with autonomy sliders" pattern. Three modes per command: `auto` (no confirmation), `suggest` (default; suggest+confirm), `confirm` (extra-strict; confirm each material step).
- Default settings tuned to operational risk: `/recall`, `/search`, `/timeline`, `/reindex`, `/listen`, `/note`, `/diagnose` → `auto`. `/forget`, `/morning`, `/merge-research-draft`, `/lead-draft`, `/track-time`, `/generate-invoices`, `/setup-*` → `confirm`. Everything else → `suggest`.
- User override at `<config-root>/plugins/cortex.user-context.md` under `autonomy:` section. Per-command opt-in; users tune as trust develops.
- nucleus-router skill (v0.1.3) reads the autonomy section before suggesting confirmations. `auto` mode runs the command directly with a one-line "Running `/X` now" note. `confirm` mode adds emphasis to the suggestion.

### Why this matters
- The log chronicle gives a grep-friendly answer to "what did I do on date X" across every audit-worthy operation. Closes the last LLM-wiki pattern gap.
- The autonomy slider lets trust develop unevenly across capabilities. Commands you trust (`/note`, `/recall`) stop interrupting. Commands with blast radius (`/lead-draft`, `/generate-invoices`) stay gated.

## [4.7.0] — Overnight learning: /listen + /morning + hot.md (2026-05-16)

### Why this exists
Cortex was event-driven: passive observation during sessions, auto-commit at session close, mining triggered by `/end-day`. Nothing learned while the user slept. v4.7 adds the missing layer — a nightly ingest pipeline that pulls yesterday's substrate into an immutable archive, mines it autonomously, and stages proposals for a 2-minute morning review.

Inspired by Karpathy's LLM-wiki separation of `raw/` (immutable source room) and `wiki/` (LLM-owned knowledge), and by his `hot.md` rolling-buffer pattern for fast warm-start.

### Added — `/listen` nightly ingest pipeline
- New `commands/listen.md` + `skills/listen/SKILL.md` — unattended (no user gates).
- Pulls yesterday's calendar (Calendar MCP), inbox metadata (Gmail MCP), Slack mentions + authored messages, Drive activity in watched folders, and transcripts via the configured note-source adapters (Granola / Gemini / Fireflies / Otter / generic-Drive).
- Writes immutable substrate to `<config-root>/archive/YYYY-MM-DD/` per `references/archive-layout.md`. Each day has `calendar.md`, `inbox.md`, `slack.md`, `drive.md`, `transcripts/<id>-<slug>.md`, and `_index.md` (counts + source health + errors). Privacy-conservative defaults: metadata-only for inbox / Slack; full bodies opt-in.
- Runs `transcript-reviewer`, `conversation-miner`, `activity-miner` against the archive read-only. Stages all proposals to a single `<config-root>/memory/.commit-drafts/YYYY-MM-DD.md` file. Active memory is never modified.
- Modes: default (yesterday), `--date YYYY-MM-DD`, `--backfill N`, `--remine YYYY-MM-DD`, `--rewrite YYYY-MM-DD` (rare; force re-pull).
- Weekly retention tail (Sundays only) compresses archive directories older than 30 days into monthly tarballs. No silent deletion of >180-day tarballs.
- Recommended cron registration via core-ops `/register-schedules`: `0 23 * * *` (11pm local) or `0 5 * * 1-5` (5am weekdays).

### Added — `/morning` interactive merge + brief handoff
- New `commands/morning.md` + `skills/morning/SKILL.md` — the JARVIS morning routine.
- Reads the latest `.commit-drafts/` file. Renders an overnight summary (counts, sources status, proposal totals).
- Walks proposals interactively: each gets `accept / reject / edit / defer / skip-remaining`. `skim` mode renders one-liners and offers `accept-all-high`, `accept-all`, `select`, `reject-all` shortcuts.
- v4.4 drift detection runs on every knowledge-entry accept; conflicts prompt supersede / keep-both / skip.
- Idempotent — re-running on a partially-walked draft picks up where the last session left off. Merged / rejected sections marked `~~struck out~~`.
- After merge, refreshes `memory/index.md` and `memory/hot.md`, archives the fully-resolved draft to `.commit-drafts/archive/<date>-merged.md`.
- Optional handoff to `/brief` after merge: "Run /brief to start the day? (y/N)".

### Added — `memory/hot.md` rolling 7-day context cache
- New `references/hot-cache.md` — formal spec.
- Sections: what I worked on (last 7 days), active people, active threads, recent commitments (to others / from others), recent reflections, recent decisions. Verbatim citations from existing nodes — no synthesis, no judgment, zero LLM cost.
- Capped at 3000 words; truncates intelligently when over.
- Configurable via `<config-root>/plugins/cortex.user-context.md` (`hot_cache.enabled`, `window_days`, `word_cap`, `refresh_on`).
- **Read first by `/recall` auto-fire** at conversation start — every session opens warm.
- **Maintained by** `/listen` (nightly), `/morning` (after merge), `/end-day` Step 5.6.
- Graceful fallback: if `hot.md` is missing or disabled, `/recall` reverts to v4.6 behavior.

### Changed — `/recall` Step 0 + `/end-day` Step 5.6
- `/recall` auto-fire now loads `memory/hot.md` before `memory/user.md` (when present and enabled). Adds a pending-overnight-draft check that surfaces a one-line "Run /morning" hint if `.commit-drafts/` has unmerged content.
- `/end-day` quick chain gains Step 5.6 — refresh hot.md after index refresh, before close.

### Why this matters
- **The system actually learns while the user sleeps.** Wake up to a single 2-minute draft instead of a blank canvas.
- **Reproducible mining.** If a mining proposal was wrong, re-run `/listen --remine` against the same archive with different settings. The Karpathy immutable-`raw/` pattern.
- **Warm starts every session.** `/recall` no longer cold-loads context from scratch. The hot cache makes the AI feel like it already knows what's been going on.

### Coordinated with daily-brief v0.3.0+ and `/end-day` v4.6.0
- `/morning` can chain directly into `/brief` after merge.
- `/end-day`'s `## Reflection` writes feed `hot.md` via the cache refresh in Step 5.6.

## [4.6.0] — /end-day cleanup: quick-default + --full opt-in (2026-05-16)

### Why this exists
Real-user feedback: the v4.5 8-step `/end-day` chain felt like overhead on days without transcripts, inbox volume, or things to triage. The user gates fired even when nothing needed gating. This release reshapes `/end-day` so the default chain is the actionable spine and heavy work is opt-in.

### Changed — `/end-day` defaults to quick mode
- **Quick mode (default).** Runs Step 3 (cortex auto-commit with cheap-tier triage), Step 4 (reflective prompts), Step 5 (pre-stage tomorrow's brief), Step 5.5 (refresh memory index), Step 6 (close). 30s – 3 min.
- **Full mode (`/end-day --full`).** Adds Step 1 (inbox triage), Step 2 (transcript review), Step 2a (mining of non-transcript sources), Step 2b (unified review gate) before the quick chain. The full chain from v4.5. 10-15 min.
- **Auto-offer prompt.** In quick mode, before Step 3, run a fast pre-check counting today's transcripts and today's unread inbox where the user is To/Cc. If transcripts ≥ 2 OR inbox ≥ 5, surface a one-line prompt offering the full close. Default `no` after ~5s. If both are low, no prompt at all — no friction for nothing.
- **Step 4 reflection write target changed.** Reflection answers now append to today's brief markdown as a `## Reflection` section (was Section 7 in daily-brief v0.2.x; daily-brief v0.3.0 removed Section 7). Idempotent re-runs replace existing reflection content rather than duplicating. Tomorrow's `/brief` Section 6 reads from this section.
- **Step 5 inbox-triage handoff is now conditional.** Full mode passes Step 1 results to tomorrow's brief; quick mode lets the brief query Gmail itself in the morning. No shared-state requirement in quick mode.

### Why this matters
Most days are quiet days. The user gates on Steps 1 and 2 fired even when there was nothing to gate, training users to skim through empty motions. After v4.6 the chain auto-shrinks to the actionable spine and asks for more only when the data justifies it. Skipped-by-default steps stay available via `--full` for the days that need them.

### Coordinated with daily-brief v0.3.0
This release lands alongside daily-brief v0.3.0, which removes Section 7 (end-of-day prompts) from `/brief`. The `## Reflection` section written by `/end-day` Step 4 is the new contract between the two plugins — daily-brief reads it; cortex writes it.

## [4.5.0] — Legibility upgrade: memory index + research-gaps + Obsidian (2026-05-16)

### Why this exists
v4.3 (mining) made memory grow with the user. v4.4 (decay) made it forget gracefully. v4.5 makes memory **legible** and **self-improving**: a single auto-maintained catalog file gives a one-glance overview of the whole second brain, a new `/research-gaps` command actively finds and fills weak spots with web-sourced research (user-gated), and a new `/setup-obsidian` command makes `<config-root>/` a graph-viewable, mobile-readable Obsidian vault.

Part of the "Nucleus as JARVIS" initiative (Phase 1 finish + Phase 2 human UI). See nucleus repo `docs/proposals/cortex-v4.5-legibility.md` and `docs/proposals/obsidian-as-ui.md` for the design rationale.

### Added — `memory/index.md` (auto-maintained catalog)
- New `skills/indexer/SKILL.md` — deterministic, zero-LLM file walker. Reads every memory node, extracts descriptor + latest `[confirmed:...]` date, classifies decay state, renders a grouped catalog (user / clients / people / companies / topics / domain / bizdev / system). Writes `<config-root>/memory/index.md` wholesale.
- New `commands/reindex.md` — explicit invocation. Runs in seconds, no model calls, no node writes.
- New `references/memory-index.md` — formal spec covering walk rules, classification formula, output template, and refresh triggers.
- **`/end-day` Step 5.5** — auto-runs the indexer after Step 5 brief pre-stage; clears `.reindex-queue` marker.
- **`/cleanup` Step 4.5** — auto-runs the indexer if any Step 4 action touched memory.
- **`/remember` Step 3.5** — appends to `<config-root>/memory/.reindex-queue` after writes (does NOT run indexer synchronously; defers to the next `/end-day`).
- Storage-layout update in CLAUDE.md to include `index.md`, `.reindex-queue`, and `.research-drafts/`.

### Added — `/research-gaps` autonomous gap-fill
- New `commands/research-gaps.md` + `skills/research-gaps/SKILL.md` — active-maintenance loop complementing the v4.4 decay model. Scans `<config-root>/memory/` for seven gap types (thin entity, stale fact in active rotation, contradiction within a node, orphan, under-cited high-confidence claim, decision gap, sparse domain) per `references/gap-detection-rules.md`. Renders ranked gap list; user picks per-gap actions (research-now / skip / mark-ok / archive-node / ask-me).
- New `agents/gap-researcher.md` — subagent with `WebSearch`, `WebFetch`, file I/O scoped to `<config-root>/memory/.research-drafts/` only. Enforces ≥2-independent-sources rule per claim. Enforces private-individual privacy rule (verifiable professional facts only — no home location, family details, real-estate, social media beyond official professional profiles, speculation). Returns confidence-aware findings (high / medium / low). Cap of 25K WebFetch tokens per run; default 5-gap cap.
- New `commands/merge-research-draft.md` — interactive walk-through of the most recent `.research-drafts/` file. Each finding: accept / reject / edit / defer / skip-remaining. Accepts apply REPLACE / MERGE / ADD / ARCHIVE per the proposed action and stamp `[confirmed:today]`. Rejects log to `.research-skip-log.md` for 90-day suppression. Drafts archive to `.research-drafts/archive/` once fully resolved.
- New `references/gap-detection-rules.md` — formal scanner rules with priority, scan procedure, and false-positive caveats.
- **`/end-week` Step 5.5** — optional invocation of `/research-gaps` in chained mode (top-5 by priority, no per-gap prompts unless user chooses "select").

### Added — `/setup-obsidian` (config-only Obsidian vault scaffolding)
- New `commands/setup-obsidian.md` + `skills/setup-obsidian/SKILL.md` — writes `<config-root>/.obsidian/` workspace config (`app.json`, `core-plugins.json`, `daily-notes.json`) and a `VAULT.md` home page with Dataview-powered active-entity tables.
- New `references/obsidian-config-templates/` — bundled defaults for the four files written above.
- **Idempotent and non-destructive** — existing `.obsidian/` files and existing `VAULT.md` are preserved on re-run. Force-reset available via `/setup-obsidian --reset` with per-file confirmation.
- **Daily-brief integration is config-only.** `daily-notes.json` points the daily-notes folder at `<config-root>/briefs/` — daily-brief's existing markdown snapshots become Obsidian daily notes with zero plugin code change.
- **No external installs.** The command does not install Obsidian or community plugins. It lists recommended community plugins (Dataview, Tasks, Calendar, Periodic Notes) for the user to install through Obsidian's UI.

### Added — schema and trigger updates
- CLAUDE.md storage-layout, auto-fire triggers, and slash-command tables updated for `/reindex`, `/research-gaps`, `/merge-research-draft`, `/setup-obsidian`.

### Why this matters
- **Obsidian becomes a first-class human UI immediately.** `index.md` + `VAULT.md` + the existing wikilink convention give graph view, mobile access, and daily-note integration with zero plugin code.
- **Non-cortex agents can read memory cold via `index.md`** without loading `memory-librarian` — a one-file entry point for any future Nucleus plugin or one-off agent.
- **Active gap-filling complements passive decay.** v4.4 forgets; v4.5 asks "what's missing?" and proposes user-gated answers.
- **Productization-ready.** A new user can run `/setup-identity` → `/setup-voice` → `/setup-obsidian` and end up with a graph view of their own second brain in under five minutes.

## [4.4.0] — Forgetting / decay layer (2026-05-12)

### Why this exists
v4.3's mining layer ships the "perpetually learning" half of the second-brain vision. v4.4 ships the other half: forgetting, decay, and consolidation. Without it, cortex grows but never lets go — beliefs that get superseded silently linger, and "what do we know about X" returns mixed signal because the system can't tell fresh insight from stale.

### Added — Decay model
- **Knowledge entries pass through four states based on the age of `[confirmed:...]`**: Fresh → Stale → Dormant → Cold. State drives surfacing behavior but never deletes content.
- **`<config-root>/memory/.decay-config.md`** auto-created on first v4.4 run with documented defaults: `threshold_fresh: 60`, `threshold_dormant: 180`, `threshold_cold: 365` (days). Per-type modifiers (GOTCHA and RECIPE decay 1.5× slower; CORRECTION is immune). Per-node `decay_profile: fast | normal | slow` front-matter override stacks with type modifiers multiplicatively.
- **`references/decay-model.md`**: full spec covering read-time decay (via `/recall`), event-time decay (via `/cleanup` and `/rehearse`), state transitions, threshold computation, and rationale.

### Added — Decay-aware `/recall`
- Every entry surfaced by `/recall` is now state-classified inline. Stale entries render with `[stale-confidence]`; Dormant with `[dormant — last confirmed Nd ago]`; Cold with stronger flag.
- **Recall-time triage offer** at the end of explicit `/recall` runs (not auto-recall or contextual): re-confirm all / select per-entry / demote all dormant+cold / skip. Per-entry actions: confirm (update tag) / demote (move to `## Demoted knowledge`) / edit-then-confirm / skip.
- Demoted entries render after active sections in project-view and topic-view recall, de-emphasized and explicitly labeled.

### Added — Concept-drift detection in `/remember`
- Before writing a new INSIGHT / MODEL / GOTCHA / LESSON entry, a Haiku-tier classifier compares it against existing same-type entries on the same node (scoped to most-recent-20 by `[confirmed:...]` for cost).
- If the classifier flags `supersedes` / `contradicts` / `refines` → FULL mode prompts the user: supersede (move old to Demoted knowledge, write new in its place) / keep both / edit relationship / skip new entry.
- SILENT mode (auto-commit) never auto-supersedes — writes alongside and flags in changelog for review at next `/recall` or `/rehearse`. Silently demoting a held belief is too destructive for an unattended path.
- On `supersede`: old entry moves to the node's `## Demoted knowledge` section with metadata trail (`↳ demoted <today> by supersede`, `↳ superseded by: <new entry first 60 chars>`). Tags preserved on the moved entry.
- RECIPE excluded from the check (additive, not competing). CORRECTION already encodes supersede explicitly.

### Added — `/rehearse` command and skill
- New `commands/rehearse.md` and `skills/rehearse/SKILL.md` — active retention loop.
- Selects 3-5 aging entries past their freshness threshold but not yet cold. Walks the user through each: confirm / update / demote / archive / skip.
- Selection algorithm: composite score by age × type-weight, diversified across nodes. Entries from `<config-root>/memory/.rehearse-queue.md` (deferred by `/cleanup`) get priority.
- Skip-log at `<config-root>/memory/.rehearse-skip-log.md` suppresses skipped entries for 30 days so they don't immediately resurface.
- Default cadence: weekly via `/end-week` (new Step 3.5). Can run on demand any time.
- Cost: zero model calls in steady state — date arithmetic + file edits.

### Added — Decay-aware `memory-librarian`
- Freshness multiplier on relevance ranking: Fresh 1.0, Stale 0.85, Dormant 0.6, Cold 0.3. Older entries sink, never hidden.
- Skips `## Demoted knowledge` sections by default. Reads them only when the parent skill explicitly requests historical context (e.g., "what did we used to think about X").
- Surfaces aging in Confidence when > 30% of Source Entries are Dormant or Cold ("Most relevant memory on this is aging — consider `/rehearse` or fresh capture").

### Added — `/cleanup` deepening
- **Section H expanded** for person-page maintenance: cooling / dormant / cold-archive states drive concrete archive proposals. On accept, moves files from `memory/person/<slug>.md` to `memory/person/archive/<slug>.md`. `/recall person:<slug>` continues to find archived pages but flags them.
- **New section I — Dormant knowledge entries**: scans all active nodes for entries past `threshold_dormant`. Per-entry suggestion: rehearse (defer to `/rehearse` via the queue file) / demote / archive. Cold entries surface separately with stronger flags. CORRECTIONs are excluded (immune to decay).

### Added — `/end-week` chain integration
- **New Step 3.5 — Rehearse**: invokes `/rehearse` between `/review` (Step 3) and reflective prompts (Step 4). Exits cleanly if the candidate pool is empty.

### Added — CLAUDE.md schema updates
- New `Decay model` section pointing at `references/decay-model.md`
- New `Demoted knowledge convention` section documenting the per-node `## Demoted knowledge` format
- `/rehearse` added to auto-fire trigger table and slash command list

### Why this matters
Now the second-brain learns AND forgets. `/remember` adds, `/recall` flags aging, `/rehearse` consolidates, `/cleanup` audits, drift detection prevents silent belief-flipping. The system carries less stale weight over time without ever silently deleting content — every transition is user-gated or logged, and demoted entries stay readable for as long as the node exists.

The combination of v4.3 (mining) + v4.4 (decay) is the bidirectional learning the user asked for: "perpetually updating and learning (and in some cases forgetting or moving things to the back of my memory similarly to how the brain is always learning)."

## [4.3.0] — `/end-day` mining layer (2026-05-12)

### Added — Mining layer (the main change)
- **`/end-day` now mines beyond the current chat session.** Three read-only agents run in parallel at Step 2a after the existing transcript-review (Step 2):
  - **`transcript-reviewer` (expanded — was commitments-only)**: now returns TWO output streams — `commitments_delta` (unchanged) AND `learnings_delta` (decisions, insights, gotchas, models, relationship context, blockers, recipes, corrections). Reads notes from all configured sources via the new adapter pattern, not just Granola. Cross-source dedup merges the same meeting captured by multiple providers (e.g., Granola + Gemini) before extraction.
  - **`conversation-miner` (new)**: mines the user's other Cowork sessions in the time window. Excludes the current session, sessions already committed via `/remember`, sessions under ~4k tokens, and sessions tagged `[no-mine]`. Groups same-topic sessions before extraction so one insight surfacing in 3 sessions = 1 reinforced proposal, not 3 duplicates.
  - **`activity-miner` (new)**: mines CRM events (deal stage changes, lifecycle changes, task closures with outcome), sent email (user's own outbound decisions only), and calendar event metadata. Privacy guardrails: paraphrase always, hard-skip `[CONFIDENTIAL]` threads, no verbatim quotes of counterparties. Scoped to events, not extraction from CRM note bodies.
- **`code-miner` deferred to v4.4+** per user decision (low marginal value for consulting/ops-focused users).

### Added — Unified review gate (Step 2b)
- Merges all mining proposals across the three agents, dedupes against existing node content, groups by `target_node`, sorts by `confidence DESC, update_type`.
- One review gate per `/end-day` run instead of three. Modes: accept-all / select-per-node / edit-each / **high-confidence-only** / skip-all.
- **Cross-refs auto-expand inline** — when a proposal's `cross_ref` links to another proposal, the linked content renders as a "cross-ref →" line beneath it so the user reviews both in context.
- **New-node creation is explicit.** Proposals with `node_type: new` require a confirmation step (with inline Scope-section interview) before any content is accepted into them. Prevents silent taxonomy bloat.
- **Dismissed proposals are logged** at `<config-root>/memory/dismissed-proposals.log` (append-only, keyed by source-ref + content hash). Miners read this log at the head of every run and skip matching items within 7 days so dismissals don't re-surface tomorrow. After 7 days, re-surfacing is permitted.
- **30s gate timeout** with skip-all default (longer than the 10s elsewhere because the gate has more density and the user may actually be reviewing).

### Added — Source-agnostic note-source adapters
- **`agents/lib/note-source-adapters.md`**: prompt-only adapters for `granola`, `gemini` (drive-folder and gmail-search methods), `fireflies`, `otter`, `notion`, `drive-folder` (generic), `gmail-label` (generic), `custom` (free-form). Each adapter documents config schema, tools used, `fetch(time_window)` logic, and `health_check()`.
- **Adding a new provider is one new section in this file — no code change required.**
- **`<config-root>/plugins/cortex.note-sources.md`**: configured source list (markdown wrapper with a fenced YAML block). Per-source fields: `id`, `provider`, `label`, `enabled`, `scope` (`global` or `project:<node-id>`), `config`. Per-project scope lets a user run Fireflies only on one client and Granola everywhere else.

### Added — Node-routing model
- **Scope section convention on domain nodes.** Four fields: `Topics:`, `Aliases:`, `What goes here:`, `What does NOT go here:`. Used by miners to route extracted content correctly.
- **One-time migration in `/end-day` Pre-chain B**: detects domain-shaped nodes (root-level `.md` files plus first-level nodes in non-reserved subdirectories), synthesizes Scope drafts from existing content, prompts user to accept/edit/skip per node. Open-ended "create new domain nodes?" step after. Marker file `<config-root>/memory/.scope-migration-done` prevents re-prompting. Re-run via `/end-day --rerun-scope-migration`.
- **Generic detection — no hardcoded node names anywhere.** Migration scans whatever the user has.
- **`references/node-routing.md`** and **`references/note-sources.md`**: docs covering the routing algorithm and source config schema.

### Added — `/setup-sources` command
- New `commands/setup-sources.md` and `skills/setup-sources/SKILL.md` — standalone interview to configure note sources.
- Walks provider menu (Granola / Gemini / Fireflies / Otter / Notion / Drive-folder / Gmail-label / custom) and per-provider config questions.
- **Mandatory health-check on every new/updated source** — adapter's `health_check()` runs during setup; failures surface verbatim with options to fix/disable/remove. Loud failure at setup, not silent at `/end-day`.
- Supports `--health-check-only` and `--remove <source-id>` flags for maintenance.

### Added — v4.4 decay substrate
- **`[confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]` tags on every knowledge entry.** `confirmed:` updates when an entry is re-affirmed or referenced as evidence. `recalled:` updates when `/recall` surfaces the entry to the user. Pre-v4.3 entries are treated as if both default to the original commit date.
- **`/recall` updates the `recalled:` tag** on every entry it renders. Backfills tags on pre-v4.3 entries as it touches them.
- **`memory-librarian` returns tag values in Source Entries** so callers can update `recalled:` after consuming the list. Agent stays strictly read-only.
- **v4.3 maintains the tags but does not yet decay or demote.** v4.4 reads them.

### Changed
- `/remember` Step 3 C: knowledge-entry formats updated to include the `[confirmed:...] [recalled:...]` tag suffix
- `/end-day` Step 3: now accepts pre-routed accepted-proposals as a second input alongside the current-session content. Accepted proposals bypass the Haiku triage (the user just accepted them).
- `skills/end-day/SKILL.md` description rewritten to reflect the mining layer

### Why this matters
The earlier `/end-day` only auto-committed the current Cowork chat session. Most of the user's day happens elsewhere — Granola meetings, other Cowork sessions, CRM activity, sent email. None of that flowed into the right cortex nodes. The mining layer closes that gap with three read-only agents that route extracted content through a single unified review gate, scoped to actually-changed events and source-agnostic notes via the adapter pattern.

The `[confirmed/recalled]` tags ship as substrate for v4.4's forgetting/decay layer (coming next).

### v4.3 → v4.4 sequencing
v4.4 will be the forgetting half: decay weights on retrieval, concept-drift detection on contradicting entries, auto-archive of dormant person pages, periodic "still true?" rehearsal prompts. Builds on the substrate that lands in v4.3.

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
