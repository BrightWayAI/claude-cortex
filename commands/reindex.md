---
description: Regenerate `<config-root>/memory/index.md` — the catalog of every memory node grouped by type with decay-state flags. Deterministic and zero-LLM. Runs in seconds. Use when memory has changed outside of `/end-day` / `/cleanup` and you want the catalog refreshed now.
---

# /reindex

You are regenerating the memory catalog.

This command is fast and side-effect-free outside of `<config-root>/memory/index.md` itself. No model calls. No node edits.

---

## Step 0 — Resolve config root

Standard platform-aware Step 0:
- Read `~/Documents/.claude-plugin-config-root` to get the config root path.
- **Cowork:** call `mcp__cowork__request_cowork_directory(path=<config-root>)` to mount.
- **Claude Code:** filesystem access is direct.

If `<config-root>/memory/` doesn't exist, say so and stop. Don't create it — that's `/setup-identity`'s job.

---

## Step 1 — Read decay config

Read `<config-root>/memory/.decay-config.md`. If missing or malformed, fall back to defaults (`threshold_fresh: 60`, `threshold_dormant: 180`, `threshold_cold: 365`; type_modifiers per `references/decay-model.md`).

---

## Step 2 — Walk and classify

Per `references/memory-index.md`:

1. Walk `<config-root>/memory/` recursively.
2. Skip `index.md`, `archive/`, `.research-drafts/`, dot-prefixed directories.
3. Group each file by its directory: `user.md` → User profile; `client/*.md` → Clients; `person/*.md` → People (skip `person/archive/`); `company/*.md` → Companies; `topic/*.md` → Topics; `bizdev/*.md` → Bizdev; `<other-dir>/*.md` → that section; root-level `*.md` not in system allowlist → Domain notes.
4. Per file: extract descriptor (first H1, fallback to first non-empty body line, cap 80 chars). Find max `[confirmed:YYYY-MM-DD]` date. Compute days_since_confirmed.
5. Classify: Fresh / Stale / Dormant / Cold per the decay formula in `references/memory-index.md`. Apply `decay_profile` front-matter override if present.
6. Count active vs. demoted entries by checking section boundaries (`## Demoted knowledge`).
7. Count archive contents (person/archive/, archive/).

---

## Step 3 — Render

Render the catalog markdown per the template in `references/memory-index.md`:

```markdown
# Memory index

_Last updated: <today HH:MM>. Auto-maintained by cortex; do not hand-edit._
_Total nodes: <N> (<X> client, <Y> person, ...)._

## User profile
- [[user]] — <descriptor>. _<state>. Confirmed <date>._

## Clients
- [[client/<slug>]] — <descriptor>. _<state>._
...
```

Within each group, sort by state (Fresh → Stale → Dormant → Cold) then alphabetically.

Append demoted/archived summary footer:

```markdown
## Demoted knowledge (preserved for context)
<N> demoted entries across <M> nodes — see individual node `## Demoted knowledge` sections.

## Archived
<P> archived person pages in `memory/person/archive/` — last archived <date>.
<K> archived nodes in `memory/archive/` — last archived <date>.
```

---

## Step 4 — Write

Overwrite `<config-root>/memory/index.md` with the rendered content.

---

## Step 5 — Clean up queue marker

If `<config-root>/memory/.reindex-queue` exists, delete it. The marker only exists when prior `/remember` calls deferred a regeneration.

---

## Step 5.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `reindex`
- **summary:** `<N> nodes catalogued (<X> fresh, <Y> stale, <Z> dormant, <W> cold). <D> demoted entries across <M> nodes.`

---

## Step 6 — Report

One-line summary:

```
Indexed <N> nodes (<X> fresh, <Y> stale, <Z> dormant, <W> cold). Demoted: <D> entries across <M> nodes. Archived: <A> person pages, <K> nodes.
```

If counts are surprising (e.g., a sudden jump in cold nodes), note it: "Heads up — <count> entries crossed into Dormant since last index. Consider `/rehearse` or `/cleanup`."

---

## What this command does NOT do

- Does not edit any node files.
- Does not delete anything outside the queue marker.
- Does not call WebSearch, WebFetch, or any LLM.
- Does not prompt the user. Runs end-to-end without input.
