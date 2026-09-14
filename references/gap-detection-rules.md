# Gap-detection rules (v4.5+)

Formal definitions of the gaps `/research-gaps` looks for. Each rule has:
- **What it detects** — the structural signal.
- **How to scan** — the file-level check (no LLM unless noted).
- **Priority** — Critical / High / Medium / Low (drives default ranking when the user asks "research the top N").
- **Notes** — caveats, false-positive risks.

The scanner walks `<config-root>/memory/` once and applies all rules in parallel. Pure file reads — no model calls during scan. (Contradiction detection optionally uses a cheap-tier classifier; see rule 3.)

---

## Rule 1 — Thin entity

**What:** A `person/*.md` or `company/*.md` node with **≤1 active knowledge entry** but **referenced by ≥3 other nodes** (via wikilinks or by-name mentions).

**How to scan:**
1. For each `person/<slug>.md` and `company/<slug>.md`:
   - Count active entries (entries outside `## Demoted knowledge` sections).
   - Count inbound references: grep across all other memory files for `[[person/<slug>]]` / `[[company/<slug>]]` / case-insensitive name matches (cap at 50 hits to avoid runaway).
2. Flag when active ≤ 1 AND inbound ≥ 3.

**Priority:** High.

**Notes:**
- A "name match" without a wikilink is weaker signal. Require ≥2 link-based refs OR ≥5 name-based mentions before flagging name-only hits.
- Newly created person pages (mtime < 7 days) are exempt — give the user time to populate.

---

## Rule 2 — Stale fact in active rotation

**What:** An INSIGHT, MODEL, or LESSON entry with `[confirmed:...]` past `threshold_dormant` AND the node it's on is in active rotation (mentioned in ≥1 Fresh-state node within the last 30 days).

**How to scan:**
1. For each node, find entries past `threshold_dormant` per `references/decay-model.md`.
2. For the parent node, check whether any other node with state=Fresh references it in the last 30 days (via wikilink scan).
3. Flag any (entry, node) pair meeting both.

**Priority:** High. These are the entries most likely to mislead the user — they're old, but the topic is still alive.

**Notes:**
- Excludes CORRECTION entries (immune to decay per decay-model).
- Excludes RECIPE entries (additive, slow-decay).

---

## Rule 3 — Contradiction within a node

**What:** Two active entries on the same node make opposing claims about the same thing.

**How to scan:** A low-cost/fast-tier model (Claude adapter: Haiku) reads pairs of active entries from the same node when:
- Both are typed INSIGHT, MODEL, or GOTCHA.
- Their `[confirmed:...]` dates differ by ≥7 days (recent flips don't count — they're naturally superseding via the v4.4 concept-drift detector).
- Their text similarity (cheap embedding or n-gram overlap) is ≥ 0.4 on key noun phrases.

For each candidate pair, ask the classifier: "Do these two entries make opposing claims about the same thing? Respond exactly: AGREE / CONTRADICT / UNRELATED." Flag CONTRADICT only.

**Priority:** Critical. Contradictions actively pollute future recall.

**Notes:**
- This is the only rule with a model cost. Budget: ~100 low-cost/fast-tier model calls per scan, capped. If a node has >20 active entries, sample 20 pairs by recency rather than checking all.
- A "supersedes" relationship marked by the v4.4 drift detector is not a contradiction — it's a resolved one. Skip those.

---

## Rule 4 — Orphan node

**What:** A node with **zero inbound wikilinks** AND **no `[confirmed:...]` tag in the last 90 days**.

**How to scan:**
1. For each node, grep across all other files for wikilink references.
2. If zero matches AND most-recent `[confirmed:...]` is > 90 days ago (or no confirmed tags at all and file mtime > 90 days), flag.

**Priority:** Medium. The node may still be useful as private notes; just isolated.

**Notes:**
- The user's own `user.md` is exempt (it's the root; nothing links to it).
- DASHBOARD.md and system files are exempt.
- `/research-gaps` proposes either archive or merge, not deletion.

---

## Rule 5 — Under-cited high-confidence claim

**What:** An entry tagged `[high-confidence]` (or equivalent), with no source / citation in the entry body.

**How to scan:**
1. Find entries containing `[high-confidence]` or `[confidence:high]` or similar.
2. Check whether the same entry contains any URL (https://...), explicit source attribution ("per <name>", "from <publication>"), or a `source:` field in front-matter.
3. Flag entries with no detectable source.

**Priority:** Medium-High. The confidence claim is unsupported.

**Notes:**
- Personal observations from the user ("I noticed X in our last call") are valid sources — but they should be explicitly attributed ("[observed:2026-04-12, call with Sarah]") rather than tagged high-confidence without provenance.

---

## Rule 6 — Decision gap (commitment past its date)

**What:** A `## Open threads` or `## Next Actions` entry on a client / project / bizdev node that mentions a date AND that date is past AND no follow-up entry resolves it.

**How to scan:**
1. For each project-shaped node, parse `## Open threads` and `## Next Actions`.
2. Regex for date patterns (`YYYY-MM-DD`, `MM/DD/YY`, "by Friday", "next week" — only resolve the unambiguous YYYY-MM-DD form in v0.1; defer fuzzy resolution).
3. Find entries with a date < today AND no subsequent changelog entry mentioning resolution / decision / closed.

**Priority:** High. Surfaces commitments the user dropped.

**Notes:**
- This is the only rule that primarily prompts the *user* rather than triggering research. The research phase asks: "Was a decision made on X? If so, what?"
- Output to the user is a list of unresolved commitments, with optional research if the decision might have been mentioned in news / public sources.

---

## Rule 7 — Sparse domain node

**What:** A root-level domain node (`memory/<name>.md` not in person/client/company/topic/) with ≤3 entries total AND no updates in 60 days AND ≥5 inbound references.

**How to scan:**
- Same as rule 1 (count entries, count inbound refs, check recency).

**Priority:** Low. Probably an early-stage scratch domain that the user paused capturing on.

**Notes:**
- The research phase for this rule synthesizes from inbound references rather than the open web ("here's what other nodes are saying about this domain; consolidate into a real entry?").

---

## Scanner output format

The scan produces an in-memory list of gaps with this shape:

```yaml
- rule: 1                              # rule number
  node: person/sarah-chen
  signal: "1 active entry, 4 inbound refs"
  priority: high
  default_research: yes                # whether the research phase should fire automatically
  user_action: "research-online"       # research-online | review-and-decide | merge-from-context

- rule: 6
  node: client/acme
  signal: "Open thread '2026-04-15 stack decision' past date by 31 days"
  priority: high
  default_research: no                 # decision gaps prompt user first
  user_action: "ask-user"
```

The `/research-gaps` command renders this as a numbered list, grouped by priority, with per-gap actions: research now / skip / mark-as-OK / archive node.
