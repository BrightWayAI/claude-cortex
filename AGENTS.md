# Cortex — Codex handoff

This is the durable instruction entrypoint for Codex sessions working in
this repository, or working against Cortex memory from any other directory
once `<config-root>` is resolved. It exists because you (Codex) are about
to be introduced as a second host alongside Claude Code/Cowork, sharing the
same memory.

**Do not duplicate workflow content into this file.** It points at the
canonical, host-neutral sources; it does not re-describe them. If something
here conflicts with the files it points to, those files win — this is a
map, not the territory.

## Read these first, in order

1. **`references/core-contract.md`** — the single canonical definition of
   config-root resolution, memory layout, node schema, the 7-type knowledge
   taxonomy, wikilink rules, locking/atomic-write requirements, privacy
   tiers, and backward-compatibility guarantees. Everything else assumes
   you've read this.
2. **`references/capability-matrix.md`** — the logical capabilities
   (`filesystem.read`, `web.search`, `subagent.delegate`, etc.) that
   canonical workflows reference instead of naming a specific tool. Your
   job as the Codex adapter is to map each capability to whatever Codex
   actually offers, and to document degrade behavior for the ones you
   don't have.
3. **`docs/PORTABILITY_READINESS.md`** — the Codex-specific mapping table
   (`AGENTS.md` ↔ `CLAUDE.md`, Agent Skills ↔ `commands/*.md`, etc.) and,
   critically, the **Known gaps** and **Risks that would require testing
   against real memory** sections. Read those before assuming anything here
   is more finished than it is.

## What already exists and is safe to use as-is

- **`scripts/cortex_cli.py`** — a plain Python CLI, no Claude-specific
  dependencies. Shell out to it exactly the way `commands/*.md` files
  already do: `python3 scripts/cortex_cli.py <subcommand> --memory-root
  <config-root>/memory ...`. This is the actual mechanism that acquires the
  shared lock, writes atomically, and releases — using it is not optional
  for any memory mutation. See `references/core-contract.md` §11.
- **`scripts/lib/*.py`** — the underlying deterministic utilities (locking,
  atomic writes, section editing, decay classification, index/hot-cache
  generation, node-path validation, repo checks). All are plain Python,
  fixture-tested under `tests/`, with no Claude/Cowork dependency. Import
  them directly if you're writing Codex-side tooling instead of shelling
  out.
- **`commands/*.md`** — the canonical workflow specs. These are the
  workflows themselves; a Codex Agent Skill for e.g. `/remember` should be
  a thin wrapper that reads and follows `commands/remember.md`, the same
  relationship `.claude/commands/remember.md` has to it (see
  `scripts/generate_claude_commands.py` for exactly how thin — Codex's
  equivalent doesn't have to be auto-generated, but should be similarly
  non-divergent).
- **The config-root pointer chain.** To share memory with an existing
  Claude Code/Cowork setup, read (in this order): `CORTEX_CONFIG_ROOT` env
  var → `~/.cortex/config-root` file → legacy
  `~/Documents/.claude-plugin-config-root` file → `~/Documents/Claude`
  default. Whoever set up Claude Code already resolves to one of these; use
  the same one rather than inventing a Codex-specific pointer.

## What does not exist yet — do not assume it does

- **No Codex Agent Skills, custom-agent configs, or Agent Plugins manifest
  exist in this repo.** Building them is explicitly out of scope for the
  refactor that produced this file (see
  `docs/PORTABILITY_REFACTOR_PROMPT.md`) — they're future work, not
  something you should find and are missing due to error.
- **Most mutating commands are wired to `cortex_cli.py`, not all.**
  `/remember`, `/note`, `/forget`, `/cleanup`, `/rehearse`,
  `/relink-memory`, `/sync-linked-entities`, and `/end-day`'s index/hot-cache/
  lock steps use it. Anything not listed there may still describe its
  writes in prose only — check the specific `commands/<name>.md` file
  before assuming a write path is code-backed.
- **The `agents/*.md` role files (memory-librarian, conversation-miner,
  activity-miner, transcript-reviewer, gap-researcher) are Claude/Cowork
  role definitions**, annotated with "Host binding note" callouts pointing
  at the capability each one needs, but not yet translated into Codex
  custom-agent config. `conversation-miner` in particular mines Cowork's
  own session history — there is no Codex equivalent, and it should not be
  ported.
- **Model-tier language** (e.g. "a low-cost/fast-tier model, Claude
  adapter: Haiku") appears throughout `commands/*.md` for cost-tiering
  decisions. Substitute Codex's own equivalent cheap/fast model where the
  workflow calls for one; don't skip the tiering distinction, it exists for
  real cost reasons documented inline.

## Testing and validation

Before trusting any change you make in this repo, run:

```
python3 scripts/check_repo.py
```

This runs frontmatter validation, the repo-check suite (skill naming,
broken internal references, taxonomy drift, command/skill coverage,
version agreement), the `.claude/commands/` freshness check, and the full
fixture-based test suite under `tests/` (unit tests import
`scripts/lib/*.py` directly; `tests/test_integration_cli_subprocess.py`
invokes `scripts/cortex_cli.py` as a real subprocess against fixture memory
roots — read that file for worked examples of full command sequences, e.g.
what `/remember` actually does end-to-end). None of this touches real user
memory; if you add tests, keep it that way — always operate against
`tempfile.TemporaryDirectory()`.

## If you're about to write a Codex adapter

Come back to `docs/PORTABILITY_READINESS.md`'s Codex-specific mapping table
and Known gaps section — it was written for exactly this moment, with more
detail than fits here. The short version: translate capabilities, don't
copy tool names; make Codex's workflow wrapper as thin as
`.claude/commands/*.md` is; and do not touch real user memory during
development — use fixtures, the same discipline this whole refactor was
built under.
