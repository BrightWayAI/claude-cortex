# Changelog

All notable changes to the Cortex Plugin are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions match `plugin.json`.

## [Unreleased]

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
