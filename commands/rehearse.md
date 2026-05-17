---
description: Active retention loop (v4.4+). Surfaces 3-5 aging knowledge entries — past the freshness threshold but not yet cold — and asks "still true? still useful?" per entry. User actions per entry: confirm (mark current) / update (edit inline then confirm) / demote (move to ## Demoted knowledge) / archive (move to archive/) / skip (defer to next rehearsal). The hippocampus-style consolidation pass that converts dormancy into either re-confirmation or removal. Default cadence: weekly via /end-week; run on demand any time.
---

# /rehearse

Active memory consolidation. Picks a small batch of aging knowledge entries and walks the user through each: confirm, update, demote, or archive. The unit of work is one entry — keep the cognitive load light.

Designed to be a 2-5 minute ritual once a week. Not a sweep, not a cleanup audit — those are `/cleanup`'s job. This is the explicit retention loop.

---

## Step 0 — Resolve config root + load decay thresholds

Resolve `<config-root>` via `~/Documents/.claude-plugin-config-root` (platform-aware Step 0 — see any setup command for the pattern).

Read `<config-root>/memory/.decay-config.md`. If missing, create with documented defaults from `references/decay-model.md` and continue. Extract:

- `threshold_fresh`, `threshold_dormant`, `threshold_cold`
- `type_modifiers` (per-entry-type multipliers; `CORRECTION: 0` means immune)
- `rehearse_batch_size` (default 5)
- `rehearse_min_age_days` (default 90 — don't rehearse what's barely past Fresh)

---

## Step 1 — Build candidate pool

Walk the memory directory:

1. List all active node files (skip `archive/`, skip `person/archive/`).
2. For each node, read its `decay_profile` front-matter (default `normal` if absent).
3. For each knowledge entry in the node's active sections (NOT `## Demoted knowledge`):
   - Parse the `[confirmed:YYYY-MM-DD]` tag (default to the entry's original commit date if absent)
   - Compute `age_days = today - confirmed_date`
   - If `age_days < rehearse_min_age_days` → skip (too new)
   - If entry type is CORRECTION → skip (immune to decay)
   - Compute `effective_threshold_fresh = threshold_fresh × type_modifier × decay_profile_multiplier`
   - If `age_days < effective_threshold_fresh` → skip (still Fresh)
   - Otherwise → add to candidate pool with metadata: `{node, type, age_days, last_recalled_days_ago, type_weight}`

4. Check `<config-root>/memory/.rehearse-queue.md` (created by `/cleanup` when user defers a Dormant entry to "rehearse"). Any entries listed there get **priority** in this run — surface them first.

---

## Step 2 — Select batch

From the candidate pool:

1. Sort by composite score: `age_days × type_weight × (1 / max(1, last_recalled_days_ago / 30))`
   - Older entries score higher
   - GOTCHA and RECIPE get a 1.5× type_weight bump (their decay matters more to operational quality)
   - Entries with very recent `[recalled:...]` activity score lower (they were just surfaced, less urgent to re-confirm)
2. Within the top scores, diversify across nodes — don't make all 5 entries from one node when other nodes have candidates. Round-robin nodes after the top score-rank.
3. Pick `rehearse_batch_size` (default 5).

If the pool is empty (no entries past their effective freshness threshold), output:

> "Memory is fresh — nothing past the rehearsal threshold today. Run again next week."

And exit cleanly.

---

## Step 3 — Walk the batch

Present each entry one at a time. Format:

```
[1 / 5] [<node-id>] <TYPE> — confirmed <N>d ago, last recalled <M>d ago

"<full entry text>"

Still true? Still useful?
  (c) confirm — mark current, will surface less frequently
  (u) update — edit inline, then confirm
  (d) demote — move to ## Demoted knowledge, keep readable
  (a) archive — move to archive section, deprioritize further
  (s) skip — leave as-is, will resurface in a later rehearsal
```

Per-entry behavior:

### confirm

Update the entry's `[confirmed:<today>]` tag in place. Leave `[recalled:...]` alone — `/rehearse` is a confirmation event, not a recall event (the user isn't surfacing the knowledge into a working conversation; they're maintaining its status).

### update

Drop into inline edit mode. Show the current entry text; let the user edit. On save:
- Replace the entry text in the node file
- Update `[confirmed:<today>]`
- Note in the changelog: `[node-id] LOG <today> — rehearsal-edit: refined <type> entry`

### demote

Move the entry to the node's `## Demoted knowledge` section (create if missing). Append the demotion metadata:

```
↳ demoted <today> by rehearse-action, reason: user judged stale during rehearsal
```

Preserve the original `[confirmed:...]` and `[recalled:...]` tags on the moved entry. The active section loses the entry; the demoted section gains it.

### archive

Same as demote in effect, but with a different metadata trail:

```
↳ archived <today> by rehearse-action — user removed from active rotation
```

The entry still lives in `## Demoted knowledge` (entry-level archive isn't a separate folder — it's still demoted, just with stronger user intent).

### skip

No file changes. Optionally, append the entry to `<config-root>/memory/.rehearse-skip-log.md` so the agent doesn't surface this same entry next week:

```
<entry-ref> skipped <today> — defer for at least 30 days
```

The skip log expires entries after 30 days, so they can resurface in a later rehearsal.

---

## Step 4 — Summarize

After the batch is processed:

```
Rehearsal complete. [N] confirmed, [M] updated, [K] demoted, [L] archived, [S] skipped.

Next rehearsal: pulls from the candidate pool again next week (or run /rehearse anytime).
```

If `/rehearse` was invoked by `/end-week` (Step 5 of that chain), surface the count back to the calling skill in a structured form so `/end-week`'s closing summary can include it.

---

## Step 4.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `rehearse`
- **summary:** `walked <N> entries. <C> re-confirmed, <D> demoted, <S> skipped (in skip-log for 30d).`

---

## Step 5 — Update .rehearse-queue.md

After the batch is processed, remove any successfully-handled entries from `<config-root>/memory/.rehearse-queue.md` (entries that `/cleanup` had previously deferred). Skipped entries stay in the queue and may be re-surfaced in the next rehearsal.

---

## Behavior rules

- **Small batch, high friction.** 5 entries max by default. Larger batches cause review-fatigue and the user starts hitting "skip all."
- **Diversify across nodes.** Don't make all 5 entries from one node; the rehearsal is about overall memory health, not one node's audit.
- **Never auto-act.** Every entry's disposition is user-chosen. No "demote all aged" shortcut here (that's `/cleanup`'s job).
- **No interruption mode.** This command is always user-invoked or invoked by `/end-week`. It does not auto-fire mid-conversation.
- **Telemetry (optional).** If `core-ops` is installed, log one line at completion: `skill: rehearse, batch_size, confirmed, updated, demoted, archived, skipped`.

## What this command is NOT for

- **Memory health audits** — that's `/cleanup`.
- **Bulk archiving** — also `/cleanup` (entry-level demote with the `select all dormant` flow).
- **Person-page management** — that's `/cleanup`'s section H.
- **One-off knowledge capture** — that's `/learn` or `/note` or `/remember`.

## Failure modes

- No candidate pool → "Memory is fresh — nothing past the rehearsal threshold today." Exits cleanly.
- `<config-root>/memory/.decay-config.md` missing → create with defaults, continue. Don't block.
- Entry text contains malformed tags → parse what's parseable, treat missing tags as "default to original commit date." Don't fail the run on a parse error.
- User abandons mid-batch (closes session, walks away) → no problem. Partial batch is fine; remaining entries surface in the next rehearsal naturally.

## When to run

- **Default cadence**: weekly, via `/end-week` chain
- **On demand**: any time the user feels memory drifting — "is what I know still right?"
- **After a major project ends**: lots of old project-state entries may be ready for demotion. Rehearsal converts them to demoted-knowledge cleanly.

## Cost

Zero model calls in the steady state. Everything is date arithmetic + file edits. The selection algorithm is local. The user makes the decisions.
