# Portability readiness

This document describes how a host other than Claude would integrate
Cortex, and specifically what a future Codex adapter would look like. It is
a readiness assessment, not an implementation — no Codex-specific files
exist in this repository as a result of this document, per the portability
refactor's explicit scope boundary (`docs/PORTABILITY_REFACTOR_PROMPT.md`).

## What already exists to build on

- **A host-neutral data contract and workflow spec** — `references/core-contract.md`
  defines config-root resolution, memory layout, node schema, knowledge
  taxonomy, locking, and append/replace semantics without naming Claude,
  Cowork, or any model.
- **Deterministic utilities usable from any host that can shell out to
  Python** — `scripts/lib/{locking,atomic_write,node_paths,sections,decay,
  index_generator,hot_cache_generator}.py`, fronted by `scripts/cortex_cli.py`.
  A host adapter doesn't need to reimplement locking or atomic writes; it
  shells out to the same CLI Claude Code uses.
- **A capability matrix** (`references/capability-matrix.md`) naming the
  logical operations a workflow needs, independent of tool syntax.
- **Canonical workflow specs** (`commands/*.md`) written in host-neutral
  language wherever this refactor reached them (see Known gaps below for
  what's left).

## Generic integration pattern for a new host

Any host integrating Cortex needs to provide, in its own idiom:

1. **A durable instruction entrypoint** — a file the host always loads at
   session start that points at `references/core-contract.md` instead of
   re-describing it (mirrors what `CLAUDE.md` now does for Claude).
2. **Skill discovery and explicit invocation** — a way to list and invoke
   the workflows in `commands/*.md` (or a host-native equivalent format
   generated from them, as `.claude/commands/` is via `scripts/generate_claude_commands.py`).
3. **Lifecycle hooks** — session-start recall (read `hot.md`, `user.md`,
   `DASHBOARD.md`) and session-end commit, translated into whatever hook
   mechanism the host provides.
4. **Filesystem permission configuration** — the host's own mechanism for
   granting read/write access to `<config-root>`, resolved via
   `scripts/lib/config_root.py`'s precedence chain (§1 of the contract) —
   in particular, honoring `CORTEX_CONFIG_ROOT` and `~/.cortex/config-root`
   so multiple hosts share one memory root without host-specific pointer
   files.
5. **Logical capability adapters** — a translation from each entry in
   `references/capability-matrix.md` to the host's actual tools/APIs, plus
   documented degrade behavior for optional capabilities.
6. **Subagent role translation** — the roles described in `agents/*.md`
   (memory-librarian, conversation-miner, activity-miner, gap-researcher,
   transcript-reviewer) translated into the host's own sub-agent/role
   configuration format.
7. **Plugin packaging** — a manifest in the host's own format, generated
   from or validated against `.claude-plugin/plugin.json` rather than
   hand-maintained separately.
8. **Scheduled tasks** — for hosts that support them, wiring `/listen` (or
   equivalent) to the host's own scheduler, with the `scheduler.register`
   capability documenting the degrade path (manual invocation) when absent.

## Codex-specific mapping

For Codex specifically, the future mapping is expected to use:

| Cortex concept | Codex mechanism |
|---|---|
| `CLAUDE.md` (durable instructions) | `AGENTS.md` |
| `commands/*.md` (canonical workflows) | Agent Skills — Codex's canonical workflow format |
| `.claude/commands/*.md` (slash-command adapter) | `$skill-name` or natural-language invocation — Codex does not require identical slash-command syntax |
| Claude Code hooks | Codex hooks for session-start recall; stop/session-end behavior needs careful design (see "Do not claim guaranteed behavior" below) |
| Claude Code native filesystem access | Codex sandbox writable roots configured to include the resolved `<config-root>` |
| `agents/*.md` roles | Codex custom-agent configuration |
| `.claude-plugin/plugin.json` | A portable Agent Plugins manifest |

None of this is implemented. Building it is future work; this table exists
so that work starts from an explicit mapping instead of guessing.

## Do not claim guaranteed behavior that isn't

Per `references/core-contract.md` and the working principles of this
refactor: a "stop reminder" or hook firing is host-provided best-effort
behavior, not a guarantee that auto-commit ran. Any adapter (Claude or
future Codex) must document this distinction explicitly rather than imply
that session-end memory capture is guaranteed. Deterministic guarantees
exist only for the code paths in `scripts/lib/` and `scripts/cortex_cli.py`
— locking, atomic writes, index/hot-cache generation — not for model-driven
steps like extraction or knowledge-typing.

## Known gaps before a Codex adapter could actually be built

These are the concrete blockers, not hypothetical ones:

1. **Most mutating commands aren't wired to the deterministic utilities
   yet.** Only `/remember` and `/note` call `scripts/cortex_cli.py`. Every
   other mutating command (`/end-day`, `/end-week`, `/listen`, `/morning`,
   `/cleanup`, `/forget`, `/rehearse`, `/relink-memory`,
   `/sync-linked-entities`) still describes its writes and its lock
   protocol in prose only. A Codex adapter inheriting these commands
   as-is would inherit the same "prose lock, no real code" gap this
   refactor found in the Claude implementation.
2. **The capability matrix is applied to `commands/*.md` and `agents/*.md`,
   not yet to `references/*.md`.** `commands/search.md`, `commands/end-day.md`,
   `commands/end-week.md` (removed "Task tool"/`subagent_type=`), and all
   five `agents/*.md` role files (frontmatter `tools:`/`model:` annotated as
   the Claude/Cowork binding; body prose naming MCP tools directly —
   `mcp__session_info__*`, `HubSpot MCP`, `Gmail MCP`, `WebSearch`/`WebFetch`
   — rewritten to name the capability first with the concrete tool as an
   implementation parenthetical) were fixed during this refactor. Added a
   missing `connector.crm.read` capability to the matrix in the process
   (only `connector.crm.write` existed before, but `activity-miner` reads
   CRM data). The broader sweep across `references/*.md` (`archive-layout.md`,
   `decay-model.md`, `gap-detection-rules.md`, `node-taxonomy.md`,
   `note-sources.md`) flagged in the Phase 0 audit has not been completed.
3. **`agents/*.md` still name a concrete model tier (`model: sonnet`) in
   frontmatter**, annotated as the Claude/Cowork binding rather than removed.
   `commands/remember.md` §C.2 also names "a Haiku-tier classifier" for the
   concept-drift check — this is a cost-tiering *decision*, not tool syntax,
   and rephrasing it as "a low-cost/fast-tier model" with the concrete choice
   pushed to the adapter layer has not been done.
4. **`conversation-miner`'s session-history capability
   (`connector.session_history.read`) is not yet in `references/capability-matrix.md`**
   — it's referenced from the agent file but the matrix doesn't have a formal
   entry for it, since it's Cowork-only with no cross-host equivalent
   (unlike the `connector.*` entries that already exist). Documented as a
   gap in the agent file itself rather than silently added to the matrix as
   if it applied broadly.
4. **No plugin manifest exists for any host but Claude.** `.claude-plugin/plugin.json`
   is Claude/Cowork-specific; there's no generator producing a portable
   manifest format yet.
5. **Hot-cache generation is partial.** `scripts/lib/hot_cache_generator.py`
   covers node-local sources (changelog, open threads, decisions) but not
   `<config-root>/briefs/` reflections or resolved `staged/commit-drafts/archive/`
   items — documented as a gap in `references/hot-cache.md`, not silently
   dropped, but still a real gap a Codex adapter would inherit.

## Risks that would require testing against real memory (not done here)

Everything in this refactor was validated against fixtures and temporary
directories only — no test in `tests/` touches `~/Documents/Claude`,
`~/Documents/ClaudeCortex`, or any other real user data, and none of this
work was run against a sanitized copy of real memory either. The following
would need real-memory testing before being trusted in production, and that
testing has explicitly **not** been done as part of this refactor:

- Whether `scripts/lib/index_generator.py`'s descriptor-extraction heuristic
  (`_descriptor()`) produces sensible output across the full variety of
  hand-authored node files that have accumulated over multiple cortex
  versions (v2.x through v4.13.x), including files with unusual front-matter
  or malformed sections.
- Whether the real `<config-root>/memory/` tree is large enough that
  `render_index`/`render_hot_cache`'s full-tree walk becomes a performance
  concern (fixtures used in testing are small, synthetic trees).
- Whether any real node file uses the legacy colon-prefixed filename form
  (`person:sarah-chen.md` as an actual filename, not just prose syntax) —
  this was never confirmed to exist in real data; the compatibility rule in
  `references/core-contract.md` §3 is written defensively but untested
  against an actual instance.
- Whether real `memory-as-git` repositories already have a committed
  `.write-lock`-based `.gitignore` entry that needs a one-time manual fix
  now that the canonical lock filename is `.lock` (this refactor fixed the
  *templates*, not any already-generated real `.gitignore` file).

Do not treat any of the above as validated. If real-memory testing is
wanted, it requires explicit authorization to work against a sanitized copy
of actual user data, which was out of scope for this session.
