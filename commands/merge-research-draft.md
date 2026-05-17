---
description: Walk through the most recent `.research-drafts/` file and merge findings into active memory one at a time. Each finding gets accept / reject / defer / edit. Accepted findings are written to the relevant node with `[confirmed:today]`. Rejected findings go to the skip-log. The merge command does not invoke `gap-researcher` — the draft must already exist (produced by `/research-gaps`).
---

# /merge-research-draft

You are merging research findings into active memory. The draft has already been written by `/research-gaps`. Your job is to walk the user through each finding and apply the chosen action.

---

## Step 0 — Resolve config root and find the draft

Standard config-root resolution.

Locate the most recent draft: list `<config-root>/memory/.research-drafts/*.md` sorted by mtime descending. Pick the newest non-archived file.

If no draft exists: "No research draft found. Run `/research-gaps` first to generate one." Stop.

If the user passed an argument (e.g., `/merge-research-draft 2026-05-09`), look for that specific date and abort if not found.

If `--discard` is the argument, move the draft to `.research-drafts/archive/<date>-discarded.md` and exit. No merge.

---

## Step 1 — Parse the draft

Each `### Gap N: ...` section is one finding. For each:
- Capture the node path.
- Capture the existing entry (or "no entry — new").
- Capture the proposed update with its action type (replace / merge / add / archive).
- Capture findings, sources, and confidence rating.

---

## Step 2 — Walk findings interactively

For each finding, render compactly:

```
[Gap 1 of 5] person/sarah-chen — Thin entity. Confidence: high.

Current entry: "VP Eng at Acme. (no other detail)"
Proposed update: REPLACE with:
  - Role: VP Engineering at Acme Corp (confirmed via LinkedIn [1], Acme press release [2])
  - Tenure: started May 2024 (per LinkedIn)
  - Prior: Senior Eng Manager, Initrode (2021-2024)
  - Public talks: "Scaling agentic teams" — Acme AI Summit 2026 [3]

Sources:
  [1] https://linkedin.com/in/sarah-chen-...
  [2] https://acme.example/press/2024-05-...
  [3] https://acme-summit.example/sessions/...

(a)ccept / (r)eject / (e)dit / (d)efer / (s)kip-remaining
```

Capture the choice:

### `accept`
- Apply the proposed update to the node:
  - REPLACE: overwrite the existing entry with the new content.
  - MERGE: append new bullets to the existing entry, preserving prior structure.
  - ADD: insert as a new entry alongside existing entries.
  - ARCHIVE (orphan only): move the file to `memory/archive/<rel-path>`.
- Add a `[confirmed:<today>]` tag to the new content.
- Append a changelog entry to the node: `[confirmed:today] research-gaps merge: <one-line summary>`.
- Move on to the next finding.

### `reject`
- Append to `<config-root>/memory/.research-skip-log.md`: `<today YYYY-MM-DD> rule:<N> node:<path> "<signal>" — user rejected merge`.
- Move on.

### `edit`
- Render the proposed update in an editable form (the user types changes inline).
- Apply the edited version on confirmation.

### `defer`
- Leave the finding in the draft. Move on.

### `skip-remaining`
- Stop walking. Remaining findings stay in the draft for next session.

---

## Step 3 — Finalize the draft

After walking (or hitting skip-remaining):

- If all findings were accepted, rejected, or archived: move the draft to `.research-drafts/archive/<date>-merged.md`.
- If any findings remain in defer/skip state: leave the draft in place with merged/rejected sections crossed out (`~~...~~`) so the user knows what's still pending. Subsequent `/merge-research-draft` runs skip crossed-out sections automatically.

---

## Step 4 — Refresh index

After any node writes, run the indexer (per `skills/indexer/SKILL.md`) to refresh `memory/index.md`. Or, if many findings just merged, queue a deferred refresh by appending to `.reindex-queue` and let `/end-day` pick it up — the user can decide via "Refresh index now? (y/N)" prompt.

---

## Step 4.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `merge-research-draft`
- **summary:** `walked <T> findings from <date>-research-gaps.md. <A> accepted, <R> rejected, <D> deferred.`

---

## Step 5 — Report

```
Merge complete.
- Accepted: <N> findings → <K> nodes updated, <P> changelog entries written.
- Rejected: <M> findings → skip-log updated.
- Deferred: <D> findings → still in draft.
- Index: <refreshed | queued for next /end-day>.
```

---

## What this command does NOT do

- Does not invoke `gap-researcher`. Operates on existing drafts only.
- Does not auto-accept findings, regardless of confidence rating. Every merge is user-gated.
- Does not modify the draft file other than crossing out merged/rejected sections.
- Does not call WebSearch / WebFetch. The research already happened.
