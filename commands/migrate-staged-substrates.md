---
description: One-time migration (v4.8.1+). Moves pre-v4.8.1 staged dotfiles (`.commit-drafts/`, `.research-drafts/`, `.rehearse-queue.md`, etc.) into the unified `memory/staged/` directory tree. Idempotent — gated by `memory/.migration-staged-reorg-done` marker. Safe to re-run; second invocation is a no-op. See `references/migrations.md` for the pattern.
---

# /migrate-staged-substrates

You are running a one-time migration that moves staged-state files from their pre-v4.8.1 dotfile paths under `<config-root>/memory/` into the unified `memory/staged/` tree.

This command is **idempotent**. Re-running after the marker exists is a no-op.

---

## Step 0 — Resolve config root

Standard pattern. If `<config-root>/memory/` doesn't exist, abort with "no memory directory to migrate."

---

## Step 1 — Check marker

If `<config-root>/memory/.migration-staged-reorg-done` exists, log "migration already complete; skipping" and exit.

Otherwise, continue.

---

## Step 2 — Detect old paths

Check for these legacy paths under `<config-root>/memory/`:

| Old path | New path |
|---|---|
| `.commit-drafts/` | `staged/commit-drafts/` |
| `.research-drafts/` | `staged/research-drafts/` |
| `.heartbeat-drafts/` | `staged/heartbeat-drafts/` |
| `.reindex-queue` | `staged/queues/reindex` |
| `.rehearse-queue.md` | `staged/queues/rehearse.md` |
| `.rehearse-skip-log.md` | `staged/skip-logs/rehearse.md` |
| `.research-skip-log.md` | `staged/skip-logs/research.md` |
| `.morning-reject-log.md` | `staged/skip-logs/morning-reject.md` |

Build a list of paths that exist and need migration. If the list is empty (fresh install with no legacy paths), skip directly to Step 4 and write the marker.

---

## Step 3 — Move

Create the target directory tree:

```
<config-root>/memory/staged/
├── commit-drafts/      (only if old `.commit-drafts/` exists)
├── research-drafts/    (only if old `.research-drafts/` exists)
├── heartbeat-drafts/   (only if old `.heartbeat-drafts/` exists; rare — feature not yet shipped pre-v4.8.1)
├── queues/             (always create when migrating)
└── skip-logs/          (always create when migrating)
```

For each old path that exists:

1. **Conflict check:** if the target new path ALSO exists (rare; manual pre-creation by user), do NOT overwrite. Log "skipping <old> → <new>; target already exists" and continue with the rest.
2. **Move:** `mv <old> <new>`. Preserve mtime + permissions.
3. **Verify:** confirm the new path exists and the old path no longer does.

If any single move fails, log the error and continue with remaining paths. Do not write the marker on partial failure — let the user re-run to finish what's possible.

---

## Step 4 — Write marker

If all detected old paths were either moved successfully or absent in the first place, write the marker:

```
<config-root>/memory/.migration-staged-reorg-done
```

Content (one line):

```
<today ISO> staged-substrates-reorg complete: moved <N>, skipped <K> (conflicts), absent <M>.
```

If some moves failed (partial completion), DO NOT write the marker. Surface a summary to the user and instruct them to resolve conflicts before re-running.

---

## Step 5 — Log

Append one line via `log-writer` skill:

- **op_name:** `migrate-staged-substrates`
- **summary:** `moved <N> legacy paths to memory/staged/. <K> skipped (conflicts). Migration complete.`

(If migration was a no-op because all paths were already absent, skip the log entry — nothing meaningful happened.)

---

## Step 6 — Report

```
Staged-substrates reorg complete.

Moved (N paths):
  .commit-drafts/             → staged/commit-drafts/
  .reindex-queue              → staged/queues/reindex
  ...

Skipped (K paths, conflicts — handle manually):
  .rehearse-queue.md (both old and new exist; you decide which to keep)

Absent (M paths):
  .heartbeat-drafts/ (never existed; nothing to move)
  ...

Marker written. Future cortex commands use the new paths. Old paths can be deleted manually if any leftover empty directories remain.
```

---

## What this command does NOT do

- Does not migrate content beyond moving files. File contents are unchanged.
- Does not delete the marker on success (the marker IS the persistent state).
- Does not handle conflicts — surfaces them to the user.
- Does not re-route active command behavior. After migration, all commands use the new paths because their spec files reference the new paths.
- Does not run on fresh installs that never had legacy paths. The Step 2 detection short-circuits.

---

## How this is triggered automatically

This command is the formal one-time migration per `references/migrations.md`. It's invoked:

1. **Explicitly** by the user running `/migrate-staged-substrates`.
2. **Implicitly** at `/end-day` Step 0.7 (post-Pre-chain, pre-Step 1) when the marker is missing. This ensures every upgrading user runs the migration within 24h of upgrading.

The implicit invocation is gated by the marker — once migration has run, the inline check is a single file-existence check (negligible cost).
