---
description: Regenerate `<config-root>/memory/index.md` — the catalog of every memory node grouped by type with decay-state flags. Deterministic and zero-LLM. Runs in seconds. Use when memory has changed outside of `/end-day` / `/cleanup` and you want the catalog refreshed now.
---

# /reindex

You are regenerating the memory catalog.

This command is fast and side-effect-free outside of `<config-root>/memory/index.md` itself. No model calls. No node edits.

The algorithm (walk, classify by decay state, render, write) is implemented in `scripts/lib/index_generator.py` and `scripts/lib/decay.py`, fixture-tested in `tests/test_index_generator.py`. This file no longer re-describes that algorithm for the model to execute by hand — see `references/memory-index.md` if you need the spec the code implements.

---

## Step 0 — Resolve config root

Standard platform-aware Step 0 per `references/core-contract.md` §1:
- Resolve `<config-root>` (env var → `~/.cortex/config-root` → legacy `~/Documents/.claude-plugin-config-root` → default).
- **Cowork:** call `mcp__cowork__request_cowork_directory(path=<config-root>)` to mount.
- **Claude Code:** filesystem access is direct.

If `<config-root>/memory/` doesn't exist, say so and stop. Don't create it — that's `/setup-identity`'s job.

---

## Step 1 — Regenerate

```
python3 scripts/cortex_cli.py reindex --memory-root <config-root>/memory
```

This single call reads `.decay-config.md` (or falls back to documented defaults), walks the tree, classifies every node's decay state, renders the catalog, and overwrites `<config-root>/memory/index.md` atomically under lock. It does not touch anything else, including `staged/queues/reindex`.

---

## Step 2 — Clean up queue marker

If `<config-root>/memory/staged/queues/reindex` exists, delete it. The marker only exists when prior `/remember` calls deferred a regeneration.

---

## Step 2.5 — Cap check (v4.16+, Nucleus Operating Model Refactor Phase 2 step 2.3)

```
python3 scripts/cortex_cli.py check-caps --memory-root <config-root>/memory
```

Read-only, deterministic (`scripts/lib/cap_check.py`). Warns at 150 / fails at 200 lines for any node's `## Current state` section; warns at 200 lines for always-loaded files (`hot.md`, `CLAUDE.md`, `user.md`). Include any output in Step 4's report. A non-zero exit means at least one FAIL — surface it prominently, but don't block the rest of reindexing on it.

---

## Step 3 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `reindex`
- **summary:** counts parsed from the regenerated `index.md`'s `_Total nodes:` line, e.g. `<N> nodes catalogued (<X> fresh, <Y> stale, <Z> dormant, <W> cold).`

---

## Step 4 — Report

Read the regenerated `index.md`'s header line and report it back in one line:

```
Indexed <N> nodes (<X> fresh, <Y> stale, <Z> dormant, <W> cold).
```

Append the Step 2.5 cap-check output if non-clean, e.g.: `Cap check: 1 FAIL, 2 WARN — see above.` Omit the line entirely when caps are clean.

If counts are surprising (e.g., a sudden jump in cold nodes), note it: "Heads up — <count> entries crossed into Dormant since last index. Consider `/rehearse` or `/cleanup`."

---

## What this command does NOT do

- Does not edit any node files.
- Does not delete anything outside the queue marker.
- Does not call WebSearch, WebFetch, or any LLM.
- Does not prompt the user. Runs end-to-end without input.
