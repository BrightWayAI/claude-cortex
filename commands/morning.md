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

## Step 0.5 — Memory diff review (v4.12.0+; race-aware in v4.12.2+)

If memory-as-git is enabled, surface what changed in memory overnight BEFORE walking the listen draft. The diff is your safety net — it catches anything that crept into memory unintentionally (auto-commits, /listen merges from a prior /morning, off-hours /remember runs).

Check whether `<config-root>/memory/.git/` exists.
- **If not** → skip silently (memory-as-git not enabled).
- **If exists** → proceed.

### Step 0.5.0 — Pre-flight checks (v4.12.2+)

Before computing the diff, three safety checks:

```
cd <config-root>/memory

# Check 1: HEAD~1 must exist (handles first-day-of-memory-as-git case cleanly)
if ! git rev-parse --verify HEAD~1 2>/dev/null:
  Surface: "Memory-as-git is fresh — no prior commit to diff against. First diff will appear after the next /end-day."
  Continue to Step 1.

# Check 2: working tree must be clean (handles failed /end-day Step 5.8 case)
dirty_count = git status --porcelain | wc -l
if dirty_count > 0:
  Surface: "⚠ Uncommitted memory changes from yesterday — looks like /end-day Step 5.8 may have failed. Files dirty:
    <show first 10 lines of `git status --porcelain`>
  Options:
    (c)ommit-now: stage + commit with message 'Recovery from prior /end-day'
    (i)nspect: show full status + diff, then re-prompt
    (s)kip: continue to Step 1 without diff review (the dirty state remains)"
  On `c`: git add . && git commit -m "Recovery commit from prior /end-day Step 5.8 failure (committed by /morning Step 0.5)"
  On `i`: render `git status` + `git diff` paginated, then re-prompt
  On `s`: continue to Step 1; the diff review for today's HEAD~1..HEAD will reflect the most-recent successful commit (which may be from 2+ days ago).

# Check 3: /listen must not be mid-write (race avoidance)
if exists <config-root>/memory/staged/queues/listen-in-progress:
  Read its content (format: "<iso8601-started>|<expected-completion>")
  if now < expected_completion + 2min grace:
    Surface: "Overnight /listen is still running (started <X> min ago). Memory diff may be mid-update. Wait 2 min and re-run /morning, or skip diff review now and review later?"
    On wait: exit /morning entirely with "Re-run when /listen finishes."
    On skip: continue without diff, with note "Skipped diff review — /listen mid-write."
  else:
    Treat as stale marker; remove and proceed.
```

### Step 0.5.1 — Compute and render the diff

```
HEAD_prev_date = git log -1 --format=%cd --date=short HEAD~1

If HEAD_prev_date == today_local (no overnight commit happened, e.g., /end-day ran twice today):
  Surface: "No memory commit since today's last close. Skipping diff review."
  Continue to Step 1.

Else:
  Compute git diff HEAD~1..HEAD --stat:
    - Files changed (count by directory: client/, person/, topic/, workstream/, bizdev/, team/, etc.)
    - Insertions / deletions per file

  Surface a summary block:
    "Memory changed since yesterday's commit (<HEAD_prev_date>):
       - <N> client nodes updated (<slug list, max 5>)
       - <M> person pages added (<slug list>)
       - <K> topic nodes modified
       - <total> insertions, <total> deletions across <files> files

     ⚠ Diff content includes raw memory text (person names, conversation snippets, decision rationales). If you're screen-sharing or screen-recording this session, the diff will expose that content.

     Open the diff? (y / skim / skip)"

  On `y`:
    Display git diff HEAD~1..HEAD paginated (50 lines at a time, with q-to-skip).
  On `skim`:
    Display file-level summary only (already shown above) plus the first 5 lines of each changed file's diff hunk.
  On `skip`:
    Continue to Step 1 without rendering.
```

The diff IS the review surface. The user can spot bad commits before they compound into wrong context for the day's sessions. If something looks wrong, `git revert HEAD` rolls back the last day's commit.

**Why this runs before Step 1 (the listen draft walk):** the diff captures what HAS landed (post-commit); the listen draft captures what's STAGED (pre-commit). User reviews HEAD first to know what they're already living with, then reviews proposals to decide what else to add.

If `cortex.user-context.md` has `memory_as_git.morning_diff: false`, skip this step (some users prefer to check diffs out-of-band via Obsidian's Git plugin).

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

1. `python3 scripts/cortex_cli.py reindex --memory-root <config-root>/memory` — regenerates `memory/index.md`. Quick — no model calls.
2. `python3 scripts/cortex_cli.py refresh-hot --memory-root <config-root>/memory --trigger morning` — regenerates `memory/hot.md` per `references/hot-cache.md`. Also quick.

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
