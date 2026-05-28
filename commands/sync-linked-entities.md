---
description: After a node has been meaningfully changed, walk its Linked Entities section and check linked nodes for drift — status flips, stale summaries, contradictions. Surface drift candidates as proposed updates; never auto-edit linked nodes. Use after status changes ("X deal closed-lost"; "Y reframed as keep-warm") to keep the network consistent. Closes the cross-artifact drift gap surfaced during the inaugural /network-rebalance walk 2026-05-28.
---

# /sync-linked-entities

Cross-artifact drift detector. When a node's status or framing changes, OTHER nodes in the network often need updates to stay consistent — but the system has no built-in mechanism to propagate. This command bridges that gap by walking a source node's `## Linked Entities` section and surfacing drift candidates in those linked nodes.

**Read-only against linked nodes.** Never auto-edits. Surfaces proposed updates; user accepts/rejects per row.

---

## When to use

- After a meaningful status change to a node (deal closed-lost, person reframed, engagement wound down, workstream completed)
- After `/network-rebalance` writes frontmatter changes to person pages
- As a routine sweep when running `/cleanup` (manual invocation from cleanup Step 2)
- On a node a user is actively editing (the natural-language trigger via skill)

Not for:
- Auto-editing linked nodes (this command is surfacing, not mutating)
- Bulk operations across all nodes (use `/cleanup` for that pattern)
- One-way relink (use `/relink-memory` for adding `[[wikilinks]]` to bare-text mentions)

---

## Step 0 — Resolve config root

Standard config-root pattern. Need read access to `<config-root>/memory/`.

---

## Step 1 — Identify the source node

The user can invoke this command in three ways:

### A. Explicit arg

```
/sync-linked-entities person/rob-buelow
/sync-linked-entities bizdev:vector-solutions
/sync-linked-entities client/holt-riptoes
```

Resolve the path: `memory/<prefix>/<slug>.md`. If the file doesn't exist, surface "Source node not found" and exit.

### B. From a recent edit (smart default)

If no arg, check `<config-root>/memory/.git/` (if memory-as-git enabled): the most recently committed node OR currently uncommitted modified node becomes the source. If multiple, surface a numbered list and ask which.

If memory-as-git not enabled, fall back to mtime-sorted listing of recent person/, client/, bizdev/, workstream/ files. Top 5; user picks.

### C. From natural-language reference

Via the skill (`skills/sync-linked-entities/SKILL.md`): if the user just edited or discussed a node in conversation, the skill resolves the source from context.

---

## Step 2 — Walk linked entities

Read the source node. Find its `## Linked Entities` section (or `## Linked entities`, both casings). Parse out the wikilinked entries:

- `[[person/sarah-chen]]`
- `[[client/acme]]`
- `[[bizdev/vector-solutions]]`
- `[[workstream/q3-outbound]]`
- `[[topic/ai-governance]]`
- `[[brightway-profile]]` (root-level node)

For each, resolve to a file path. Skip if the file doesn't exist (surface as broken-link candidate in the report).

---

## Step 3 — Drift detection per linked node

For each linked node, run lightweight drift checks:

### Check 1 — Status / temperature contradiction

Compare key status fields between source and linked:

- **Person ↔ client:** if person page says `tier: dormant` but client node lists them as active primary contact → flag.
- **Person ↔ bizdev:** if bizdev node summary says "active pursuit" but person page says `tier: operational + intent: keep_warm` → flag.
- **Person ↔ workstream:** if workstream `status: completed` but person's open threads include items from that workstream → flag.
- **Client ↔ workstream:** if client engagement ended (LOG entry "engagement wrapped") but workstream linked to it is still `status: active` → flag.
- **DECISION revisit:** if the source node has a recent DECISION supersede and the linked node references the old decision in its content → flag.

### Check 2 — Stale summary

Compare the linked node's Summary timestamp / last-updated date against the source node's. If source was modified TODAY and linked's Summary was last touched >14 days ago, AND the linked node references the source by wikilink (so the dependency is real), flag as potential staleness.

Lightweight heuristic — false-positives are fine; this surfaces candidates, doesn't auto-edit.

### Check 3 — Open threads / WAITING items pointing at the source

Scan linked node's Open Threads / Next Actions sections for items referencing the source node. If the source has resolved them (the source's own open threads no longer contain them, or the source's status indicates the issue is closed), flag those linked open threads as candidates to close.

Example: source `person/rob-buelow.md` Open Threads no longer has "Vector proposal — pending option selection," but `bizdev/vector-solutions.md` Next Actions still has "Wait for Rob's option selection." Flag for closure.

### Check 4 — Frontmatter intent / tier compatibility

If source is a person page with `relationships:` frontmatter and the linked nodes are bizdev/client/workstream nodes:

- Source `tier: operational + intent: keep_warm` on a person who's a primary client contact → the client node should probably reflect "client engagement wound down" or similar in its Summary.
- Source `intent: client_delivery` on a person → linked client node should be in active status.
- Source `intent: passive_visibility` (network-only) → linked bizdev node should not have active outreach scheduled.

Flag mismatches.

### Check 5 — Provenance freshness (if v4.12.0 DASHBOARD provenance is wired)

For each linked node mentioned in DASHBOARD active-state section, check the DASHBOARD line's `<!-- by:<cmd> @ <date> -->` provenance. If source has been recently modified but the DASHBOARD line for the linked node still carries an old provenance date, flag as DASHBOARD-drift candidate (likely needs DASHBOARD card refresh).

---

## Step 4 — Surface findings

Render a structured report. For each linked node with drift candidates, group findings together. Then offer per-candidate actions.

```
DRIFT SCAN — source: [[person/rob-buelow]] (modified 2026-05-28)
═══════════════════════════════════════════════════════════════

[[bizdev/vector-solutions]] — 3 drift candidates
  1. Status contradiction
     Source: tier=strategic + intent=content_share (closed-lost reframe)
     Linked: Summary says "Three engagement options at $175/hr blended... Today 5/12 11AM Teams call"
     → Linked Summary doesn't reflect closed-lost status
     Action: (u)pdate-linked-summary / (k)eep / (s)kip

  2. Open thread orphaned
     Source no longer has "Vector option selection pending" in Open Threads
     Linked has [FRESH 2026-05-12] "Today 5/12 11AM — Zach <> Rob progress + next-steps call"
     → Linked open thread refers to a now-completed event
     Action: (c)lose-on-linked / (k)eep / (s)kip

  3. Next-action stale
     Source intent shifted to content_share (no active BD)
     Linked has [P1] "Once Vector picks an option, produce SOW within 5 business days"
     → P1 is no longer relevant
     Action: (r)emove / (k)eep / (s)kip

[[bizdev/jacquie-moen]] — 1 drift candidate
  1. Stale summary
     Source modified 2026-05-28; linked Summary last touched 2026-04-13 (45 days)
     Source is jacquie's network referral target → linked may need a "Vector closed-lost; network reference still warm" note
     Action: (u)pdate-summary / (k)eep / (s)kip

[[client:holt-riptoes]] — no drift detected

═══════════════════════════════════════════════════════════════
SUMMARY: 4 drift candidates across 2 linked nodes (1 no-drift).
```

Walk each candidate; accept user input per-row.

**On `u` / `update-linked-summary` / `update-summary`:** open the linked node, draft a proposed update to the relevant section (Summary, status block, etc.) reflecting the new source-side reality. Show the diff. User confirms before writing.

**On `c` / `close-on-linked`:** mark the linked open thread as completed (add `[COMPLETED <today>]` prefix or move to a Closed Out section). User confirms.

**On `r` / `remove`:** remove the line from the linked node. User confirms.

**On `k` / `keep`:** suppress this candidate for 30 days. Log to `<config-root>/memory/staged/skip-logs/sync-linked.md` with `(source, linked, candidate-id, reason)`.

**On `s` / `skip`:** no action; re-surfaces on next `/sync-linked-entities` run.

---

## Step 5 — Update memory/log.md

Invoke `log-writer` skill with:
- **op_name:** `sync-linked-entities`
- **summary:** `Source: <source-node>. <N> linked nodes scanned. <K> drift candidates surfaced. <U> updated, <C> closed, <R> removed, <S> skipped.`

---

## Constraints

- **Read-only on linked nodes** by default. Writes only happen on explicit user approval per candidate.
- **Cap of 25 drift candidates per invocation.** If more, sort by severity (status-contradiction > orphaned-thread > stale-summary > frontmatter-mismatch > provenance-freshness) and surface the top 25 with "More candidates — re-run after addressing these."
- **Don't recurse.** If user updates a linked node, do NOT auto-run /sync-linked-entities on THAT node. User can re-invoke explicitly. Recursion would spiral.
- **No fabrication.** If the drift check is ambiguous (e.g., status contradiction without a clear resolution), surface as `(s)urface-only` — describe the contradiction but don't propose a specific update.
- **Skip-log respected.** Candidates suppressed via skip-log in the last 30 days don't re-surface.

---

## Edge cases

- **Source node has no `## Linked Entities` section** → surface "No linked entities found in source. This command works against the explicit Linked Entities section. Use `/cleanup` Section K (Structurally-isolated nodes) for broader connectivity analysis." Exit.
- **Linked entity wikilink doesn't resolve to an existing file** → flag as `## Broken Links` section at the end of the report. Offer (a)rchive-wikilink-mention / (s)kip.
- **Source modified within the last 60 seconds** → likely mid-edit. Surface "Source was just modified — give it a moment to settle, then re-run." Exit.
- **Memory-as-git not enabled and no other recent-modification signal** → in arg-mode A, proceed. In smart-default mode B, surface "Need a source node arg (or enable memory-as-git for auto-detection)."
- **All findings are `s`/skip** → no writes; just the log entry. Surface "0 changes applied. Re-run after addressing or use `/cleanup` Section L for DASHBOARD-side drift."
