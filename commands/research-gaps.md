---
description: Autonomous gap-finder + web research for memory. Scans `<config-root>/memory/` for seven gap types (thin entity, stale fact, contradiction, orphan, under-cited claim, decision gap, sparse domain), researches the highest-priority gaps via the open web (≥2 sources per claim), and writes findings to a draft file for user review. Never modifies active memory directly.
---

# /research-gaps

You are running an active maintenance loop on the second brain. This command complements the passive decay model (v4.4) by proactively finding weak spots and proposing fixes.

Two phases: **scan** (deterministic + cheap-tier classifier) and **research** (web-based, user-gated). All findings land in a single draft file for the user to merge selectively via `/merge-research-draft`.

---

## Step 0 — Resolve config root

Standard platform-aware Step 0:
- Read `~/Documents/.claude-plugin-config-root`.
- Cowork: `mcp__cowork__request_cowork_directory(path=<config-root>)`. Claude Code: direct.

---

## Step 1 — Scan for gaps

Apply all rules from `references/gap-detection-rules.md`:

1. **Thin entity** — `person/*.md` or `company/*.md` with ≤1 active entry but ≥3 inbound refs.
2. **Stale fact in active rotation** — INSIGHT/MODEL/LESSON past `threshold_dormant` on a node referenced by Fresh nodes in the last 30 days.
3. **Contradiction within a node** — opposing active claims (cheap-tier classifier; budgeted to ~100 Haiku calls).
4. **Orphan node** — zero inbound wikilinks AND no confirmation in 90 days.
5. **Under-cited high-confidence claim** — `[high-confidence]` tag with no source attribution.
6. **Decision gap** — `## Open threads` / `## Next Actions` entry with a past date and no resolution.
7. **Sparse domain** — root-level domain with ≤3 entries, no updates in 60 days, ≥5 inbound refs.

If the user passed a scope argument (e.g., `/research-gaps person`, `/research-gaps client/acme`), restrict the scan to that subpath / category.

Compose the gap list as YAML (see `gap-detection-rules.md` output format). Sort by priority (Critical → High → Medium → Low), then by inbound-reference count within priority.

---

## Step 2 — Present the gap list

Render the list to the user:

```
Found N gaps:

CRITICAL
  1. Contradiction in `topic/agentic-pricing` — two active entries make opposing claims about 2026 pricing benchmarks.

HIGH
  2. Thin entity: `person/sarah-chen` — 1 active entry, 4 inbound refs.
  3. Stale fact: `topic/ai-governance` — "EU AI Act takes effect 2025" confirmed 218d ago; still actively referenced.
  4. Decision gap: `client/acme` — "decide on stack by 2026-04-15" past date by 31 days; no resolution captured.

MEDIUM
  5. Orphan: `topic/agentic-pricing-old` — no inbound links, no confirmation in 142 days.
  6. Under-cited claim: `topic/llm-economics` — entry tagged [high-confidence] with no source.

LOW
  7. Sparse domain: `studio.md` — 2 entries, last updated 71d ago, 6 inbound refs.

Per-gap actions:
- research-now: have gap-researcher pull web sources
- skip: ignore this run (next run will re-flag if still present)
- mark-ok: log this gap as known-and-OK; suppress for 90 days
- archive-node: only for orphan rule — propose archive
- ask-me: only for decision-gap rule — render the question for you to answer

Reply with comma-separated numbered actions: e.g., "1: research-now, 2: research-now, 4: ask-me, 5: archive-node, 7: skip"
```

Wait for user input.

---

## Step 3 — Process per-gap actions

For each user-specified action:

### `research-now`
Add this gap to the queue for the `gap-researcher` subagent.

### `skip`
Note it but do nothing. Will resurface on next `/research-gaps` if still present.

### `mark-ok`
Append a line to `<config-root>/memory/.research-skip-log.md`:
```
<today YYYY-MM-DD> rule:<N> node:<path> "<signal>" — user marked OK
```
Suppress this exact (rule, node) pair for 90 days on future scans.

### `archive-node` (orphan only)
Propose archive: "Move `<node>` to `memory/archive/` (preserves the file; just relocates). Confirm?" If yes, move the file; otherwise treat as skip.

### `ask-me` (decision-gap only)
Render the open thread inline and ask: "Was this decided? If so, what was the outcome?" Capture the answer and write it back to the node's `## Changelog` as a `[confirmed:today]` entry. This rule does not involve `gap-researcher`.

---

## Step 4 — Invoke gap-researcher (if any gaps were queued for research)

Cap: 5 gaps per run by default. If the user queued more, ask: "You queued <N> for research. The default cap is 5 to avoid runaway runs. Research all <N>, or first 5?" Default to 5.

Invoke the `gap-researcher` subagent with the queued list. Agent returns a structured summary (see `agents/gap-researcher.md`) and the path to the draft file.

If the subagent reports `status: aborted` or `average_confidence: low`, surface that to the user immediately: "Research returned low-confidence findings — recommend manual review of `<draft-path>` before any merge."

---

## Step 4.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `research-gaps`
- **summary:** `scanned <N> nodes, found <G> gaps. Researched <R> (<H> high confidence, <M> medium, <L> low). Draft at .research-drafts/<date>-research-gaps.md.`

---

## Step 5 — Surface the draft path and next steps

```
Draft written: <config-root>/memory/.research-drafts/<date>-research-gaps.md

To merge: run /merge-research-draft to walk through each finding (accept/reject/defer).
To skip merging now: the draft persists; rerun /merge-research-draft any time.
To discard the draft entirely: delete the file or run /merge-research-draft --discard.
```

End the command. The draft is the artifact; the user merges separately.

---

## Optional: triggered from /end-week

`/end-week` (cortex v4.5+) offers `/research-gaps` as optional Step 6. When invoked from there:
- Skip the user prompt at Step 2 — render the gap list inline and ask "Research the top 5? (y/n/select)"
- On `y`, queue the top 5 by priority and proceed.
- On `n`, exit without writing a draft.
- On `select`, hand off to interactive Step 2.

The end-week integration is purely additive; running `/research-gaps` standalone always uses the full interactive path.

---

## Schedule

Default: weekly, Saturday morning, scope `all`. Optional registration in `core-ops/references/schedules.md`:

```yaml
- name: research-gaps-weekly
  cron: "0 9 * * 6"   # Saturday 9am local
  command: /research-gaps
  args: ""
```

Skip if the user hasn't opted into scheduled tasks via core-ops.

---

## What this command does NOT do

- Does not modify active memory. All findings stage to `.research-drafts/`.
- Does not run `gap-researcher` without the user choosing research-now on at least one gap.
- Does not handle merge. That's `/merge-research-draft`.
- Does not write the draft if no gaps are found. Reports clean and exits.
- Does not deep-research private individuals (gap-researcher enforces the privacy rule).
