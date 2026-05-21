---
description: Interactive morning routine. Reads the most-recent `<config-root>/memory/staged/commit-drafts/` file (produced overnight by `/listen`), walks the user through each proposal (accept / reject / edit / defer), applies accepted proposals to active memory nodes, refreshes hot.md and the memory index, and optionally chains into `/brief`. The JARVIS morning.
---

# /morning

You are running the user's morning routine. Overnight, `/listen` ingested yesterday's substrate and staged a draft of proposed memory commits. Your job is to walk that draft with the user efficiently — accept what's right, reject what isn't, capture edits, and hand off to the brief.

---

## Step 0 — Resolve config root and find the draft

Standard config-root pattern.

Locate the most-recent draft: list `<config-root>/memory/staged/commit-drafts/*.md` sorted by date descending (use the date in the filename, not mtime).

- **No draft found** → "No `/listen` draft to merge. Did `/listen` run last night? Recent runs:" → list any `archive/<date>/_index.md` from the last 3 days. Offer to run `/listen` now for yesterday. Otherwise exit.
- **Draft exists** → continue.

If the user passed `--date YYYY-MM-DD`, merge that specific draft instead of the latest.

If the user passed `--discard`, move the latest draft to `staged/commit-drafts/archive/<date>-discarded.md` and exit without merging.

---

## Step 1 — Show the overnight summary

```
Good morning. Overnight /listen ingested yesterday:

  <N> calendar events
  <M> inbox threads (you in To/Cc)
  <K> Slack mentions
  <L> Drive changes
  <T> transcripts (<adapter1>: <count>, <adapter2>: <count>, ...)

Proposals staged: <P> total
  - <a> knowledge entries (INSIGHT / MODEL / GOTCHA / LESSON / RECIPE / CORRECTION)
  - <b> person-page updates
  - <c> commitment captures (to/from others)
  - <d> thread updates / closures

Sources status: <K> ok, <U> skipped/missing, <E> errors
(see archive/<date>/_index.md for details if errors)

Ready to walk through the proposals? (y/n/skim)
```

- `y` (default) → Step 2 (walk one at a time)
- `n` → exit, leave draft in place for later
- `skim` → render every proposal as a one-line summary, no per-proposal gates; user picks numbers to dig into

---

## Step 2 — Walk proposals interactively

Group proposals by priority (Critical / High / Medium / Low) and within priority by source agent.

For each proposal:

```
[Proposal N of P] <node-path> — <type> from <agent>
  Confidence: <high | medium | low>
  Source: archive/<date>/<file> · <section/line>
  Conflicts: <list or "none">

  Current state in `<node-path>`:
  > <verbatim quote of relevant existing entry, or "no entry — new">

  Proposed:
  > <verbatim proposed content>

  (a)ccept / (r)eject / (e)dit / (d)efer / (s)kip-remaining
```

### `accept`
- Apply the proposal to the target node per its `Type`:
  - **Knowledge entry** → append to the appropriate `## Knowledge → ### Insights / Models / Gotchas / Lessons / Recipes / Corrections` section with `[confirmed:today]` tag.
  - **Person-update** → append to `## Recent interactions` or `## Notes` on the person page; create page if needed (graduate the contact per v4.2 rules).
  - **Commitment** → append to `## Open threads` (for ones the user owes) or `## Waiting on` (for ones others owe the user).
  - **Thread-update** → modify the named open thread (status change, append note, or close).
- Append a `## Changelog` entry to the node: `[YYYY-MM-DD] /morning merge: <one-line summary> — proposed by <agent>`.
- Check for conflicts via the v4.4 concept-drift detector. If the proposal conflicts with an existing entry, prompt: "This contradicts the existing entry '<...>'. Supersede the old / Keep both / Skip the new?" Default: keep both.

### `reject`
- Append to `<config-root>/memory/staged/skip-logs/research.md` (or a new `staged/skip-logs/morning-reject.md` if we want to keep these separate): `<today> proposal:<type>@<node> "<signal>" — rejected from /listen draft <date>`.
- Move on.

### `edit`
- Render the proposed content as editable text. User types in changes. Apply the edited version on confirmation.

### `defer`
- Leave the proposal in the draft. Move on.

### `skip-remaining`
- Stop walking. Remaining proposals stay in the draft for the next session.

---

## Step 3 — Finalize the draft

After walking:

- If all proposals were accepted / rejected / archived: move the draft to `staged/commit-drafts/archive/<date>-merged.md`.
- If any proposals remain in defer state: leave the draft in place, with merged / rejected sections marked `~~struck out~~` so the next session skips them. Subsequent `/morning` runs on the same draft pick up where you left off.

---

## Step 4 — Refresh hot.md and memory index

After any node writes:

1. Run the `indexer` skill (per `skills/indexer/SKILL.md`) to regenerate `memory/index.md`. Quick — no model calls.
2. Refresh `memory/hot.md` per `references/hot-cache.md`. Also quick.

Both happen unconditionally so the morning ends with fresh substrate.

---

## Step 4.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `morning`
- **summary:** `merged <a> / <total> proposals from <draft-date> draft. <r> rejected, <d> deferred. hot.md + memory/index.md refreshed.`

---

## Step 5 — Report and offer brief handoff

```
Morning merge complete.

  Accepted: <a> proposals → <k> nodes updated, <p> changelog entries written
  Rejected: <r> proposals → reject-log updated
  Deferred: <d> proposals → still in draft

  hot.md: refreshed (<w> words)
  memory/index.md: refreshed (<n> nodes catalogued)

Run /brief to start the day with today's working surface? (y/N)
```

- `y` → invoke `/brief` for today.
- `n` → exit.

---

## Behavior rules

- **No silent merges.** Every proposal accepted is explicitly confirmed by the user.
- **Conflict-aware.** Run v4.4 drift detection on every knowledge-entry accept. Surface contradictions; never silently supersede.
- **Idempotent.** Re-running `/morning` on a partially-walked draft picks up where the last session stopped.
- **Skim mode is real.** Users who don't want to one-by-one walk should still be able to glance the proposals and accept-all-high-confidence. Skim mode renders one-line summaries and offers `accept-all-high`, `accept-all`, `select`, `reject-all` shortcuts.
- **Privacy-aware.** The draft cites the archive (`archive/<date>/<file>`). Don't surface raw archive content unless the user asks to expand a proposal's source quote.

---

## When this is NOT the right command

- **No `/listen` draft exists.** This command exits gracefully; you don't need to run `/listen` interactively to use cortex.
- **Mid-day captures.** Use `/remember`.
- **Memory health audits.** Use `/cleanup`.
- **Web research for gaps.** Use `/research-gaps`.
- **End-of-day reflection.** Use `/end-day`.

---

## What this command does NOT do

- Does not invoke `/listen` (the draft must already exist).
- Does not modify the archive — `archive/` is immutable.
- Does not auto-accept high-confidence proposals (even in skim mode, the user types `accept-all-high` explicitly).
- Does not call WebSearch / WebFetch. The mining already happened overnight.
- Does not run `/brief` without user confirmation.
