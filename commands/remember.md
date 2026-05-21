---
description: Commit this conversation to working memory. Extracts knowledge, decisions, insights, open threads, and next actions — then writes a living summary and changelog entry for the detected project node. Also flushes any observations accumulated by the passive learning engine. Can run in full mode (user-triggered) or silent mode (auto-triggered at conversation end).
---

# /remember

You are committing this conversation to Claude's working memory. Work through the following steps precisely.

---

## Mode Detection

This command runs in one of two modes:

### Full mode (default — user triggered /remember explicitly)
- Complete extraction with all steps below
- Confirmation output at the end
- User sees what was committed

### Silent mode (auto-triggered at conversation end)
- Same extraction logic, but NO confirmation output
- Triggered when the conversation is ending (farewell signals detected)
- Skip if the conversation was trivial (no decisions, no knowledge, no meaningful observations)
- Exception: if creating a NEW node, briefly mention: "Noted — started tracking [node-id]."
- Always commit user observations (corrections, preferences) even from trivial conversations — these are never wasted

---

## Step 0 — Cheap-tier commit triage (v4.2+)

Before running the full Sonnet-tier extraction below, run a cheap Haiku-class classifier on the conversation to decide whether to commit at all and, if yes, which nodes are affected. This keeps per-commit cost predictable as commit volume grows.

### A — Classifier prompt

Send the last ~30 conversation turns (or the whole conversation if shorter) to a Haiku-tier model with this prompt:

> System: You are a memory-commit triage classifier for a personal working-memory system. Decide:
>
> 1. **Is this conversation commit-worthy?** Were decisions made, knowledge shared, corrections given, or entities mentioned in a way that should update existing memory nodes? Greetings, scheduling pings, and trivial Q&A without takeaways are NOT commit-worthy.
> 2. **If yes, which nodes are affected?** Return only nodes that need updating. Don't over-attribute. Use the user's existing node namespace (you'll be told what nodes exist).
>
> Existing node namespace (truncated to active set from DASHBOARD.md): <list of active node ids>
>
> Output exactly one JSON object on a single line, no other text:
>
> `{"commit": true, "nodes": ["client:acme-corp", "person:sarah-chen"], "reason": "<one line>"}`
>
> or
>
> `{"commit": false, "reason": "<one line>"}`
>
> Rules:
> - Always include any user-observation work (corrections, preferences) as commit-worthy AT MINIMUM to the `user` node, even if no project nodes apply. So if the user corrected your approach, `commit: true, nodes: ["user"]`.
> - Person-page graduation triggers (explicit `[ENTITY:person]` tag, contact-researcher dossier produced this session, etc.) → include `person:<slug>` in nodes.
> - When in doubt, lean conservative: `commit: false` is preferred over a noisy commit. The user reviews `triage-log.md` weekly to catch false-negatives.

### B — Decision routing

Parse the classifier's response. If parsing fails (malformed JSON, model timeout), default to `commit: true, nodes: ["<detected project node>"]` so we don't silently lose a substantive conversation.

- **`commit: false`** → log one entry to `<config-root>/memory/triage-log.md` (format below), return silently. Do not run Steps 1-5. The conversation contributes nothing to memory beyond this audit line.
- **`commit: true`** → log one entry to `triage-log.md` (with the node list), then proceed to Step 1 but **pass the node list forward** so Step 1's project-detection is informed (not overridden) by the classifier's call.

### C — Triage log format

Append to `<config-root>/memory/triage-log.md` (create file if missing). Format:

```markdown
# Triage Log

_Auto-appended by cortex's two-stage commit triage. Audit weekly for false-negatives (commit:false when a real decision was made) and over-attribution (commit:true with too many nodes)._

## YYYY-MM-DD HH:MM
- Decision: [commit | skip]
- Nodes: [list, or omit if skip]
- Reason: <one-line from classifier>
- Conversation context: <one-line synthesized from your own read of the turns — what the conversation was about>
```

### D — Cost discipline

The Haiku call is the only model call until classification completes. If `commit: false`, Steps 1-5 (Sonnet synthesis) never run. Expected cost per `/remember` invocation:
- Trivial conversations: ~$0.001 (Haiku classifier only)
- Substantive conversations: previous cost + ~$0.001 (negligible overhead)

Total Sonnet cost drops 30-50% measured weekly when ~30-40% of conversations are trivial.

### E — When to bypass Step 0

User-invoked `/remember` with an explicit node argument (e.g., `/remember client:acme-corp`) bypasses Step 0 entirely — the user is asserting commit-worthiness. Silent mode and auto-fire commits still run Step 0.

Also bypass Step 0 if the conversation contains an explicit `[ENTITY:person]` tag with a new person — that's a strong-enough graduation signal to commit unconditionally.

---

## Step 1 — Detect the project node

Scan the full conversation and identify which project(s) this session belongs to.

Check Claude's existing memory for any established project nodes first. If a matching node exists, use it. If the session covers something genuinely new, create a new node using kebab-case.

**Node naming conventions:**
- Client work: prefix with `client:` (`client:acme-corp`, `client:northstar`)
- Business development: `bizdev` or `bizdev:[target]` (`bizdev:stripe-partnership`)
- Internal ops: use a descriptive slug (`company-ops`, `brand`, `hiring`, `finance`)
- Products/services: use the product name (`crm-dashboard`, `onboarding-program`)
- Strategy/planning: `strategy:[topic]` (`strategy:q2-growth`, `strategy:pricing`)
- Learning/study: `learning:[topic]` (e.g. `learning:sales-ops`, `learning:ai-tools`)
- Domain knowledge: `domain:[area]` (e.g. `domain:tax-law`, `domain:healthcare-compliance`)
- Research/exploration: `research:[topic]` (`research:competitor-landscape`)
- Infrastructure/tooling: `infra` or `infra:[system]`
- Personal: `personal` or `personal:[topic]`

If the session spans multiple nodes, you'll commit to each one separately in Step 3.

---

## Step 1b — Capture git context (if available)

If the conversation involves code or a git repository, capture the development context:

1. **Current branch**: Record the branch name being worked on
2. **Recent commits**: Note the last 3-5 commit messages from this session (if any)
3. **Uncommitted changes**: Summarize what's staged or modified (high-level, not full diffs)
4. **Related branches**: Note any branches mentioned (feature branches, PRs, upstream)

Include this as a `GIT CONTEXT` block in the changelog entry:
```
[node-id] LOG YYYY-MM-DD — title: ... | Git: branch [branch-name], [count] commits ([summary])
```

Skip this step entirely if the session doesn't involve code or version control.

---

## Step 2 — Extract structured memory

Pull from two categories: **what changed** (project state) and **what was learned** (knowledge).

Not every session will have entries in every category. A pure learning/exploration session may have nothing in "project state" — that's fine. Extract what's actually there.

### A. Project State (what changed)

```
DECISIONS MADE:
- What was definitively resolved, chosen, or agreed upon
- Include reasoning if non-obvious

OPEN THREADS:
- Things started but not finished
- Questions raised but unanswered
- Ideas flagged for later
- Mark each: [FRESH], [ONGOING], or [STALE]

BLOCKERS:
- Anything actively preventing progress
- Dependencies on people, systems, or information
- Include who/what is blocking and since when

ARTIFACTS:
- Documents created, decks built, spreadsheets drafted (include filenames/paths)
- External resources, URLs, or references worth keeping
- Emails sent, proposals delivered, contracts shared, campaigns launched

NEXT ACTIONS:
- Explicitly stated or implied next steps
- Tag each with priority:
  - [P0] — Do immediately
  - [P1] — Do soon / this week
  - [P2] — Do eventually
  - [WAITING:person/thing] — Blocked on someone/something specific
```

### B. Knowledge (what was learned)

```
INSIGHTS:
- New understanding gained during this session
- "Aha" moments, reframes, or realizations
- Connections spotted between previously unrelated things
- Example: "Realized our churn isn't a product problem — it's an onboarding problem. Customers who complete setup in week 1 retain at 92%."

LESSONS LEARNED:
- Things tried that worked → why they worked
- Things tried that failed → why they failed, what to do instead
- Mistakes made → what the correct approach is
- Example: "Tried sending proposals same-day — close rate dropped. Waiting 48 hours with a tailored deck closes 3x better."

MENTAL MODELS:
- How something works, explained for future reference
- Business processes, decision frameworks, domain rules, workflows
- "The way X actually works is..."
- Example: "Their approval process: department head → finance review → VP sign-off → procurement. Skip finance and it stalls for weeks."

GOTCHAS & PITFALLS:
- Specific traps or non-obvious behaviors in processes, tools, or relationships
- Things that look like they should work but don't
- Surprising rules, undocumented requirements, edge cases
- Example: "Their fiscal year starts in April, not January — all budget conversations need to reference Q1 as April-June."

PATTERNS & RECIPES:
- Techniques or approaches that proved effective
- Reusable solutions to specific types of problems
- Workflows or processes worth repeating
- Example: "For getting executive buy-in: lead with the metric they own, show the gap, propose one action, name the timeline."

CORRECTED BELIEFS:
- Assumptions that turned out to be wrong
- Previous understanding that was updated or reversed
- Example: "Previously assumed they were price-sensitive — actually they have budget, they just need ROI framing to get internal approval."

DECISIONS (v4.9+):
- A choice made — forward-looking commitment, not a retrospective lesson
- Cues: "we decided," "I'm going with," "settled on," "going forward we'll," "the call is," "made the call to"
- Required fields when captured:
  - **What was decided:** the choice
  - **When:** YYYY-MM-DD
  - **Why:** reasoning at the time
  - **Affected:** wikilinked entities affected by the decision
  - **Revisit when:** trigger condition for re-evaluation ("if vendor raises prices," "annually," "if we hire a 3rd person") — or "n/a" if no specific trigger
  - **Status:** active (default), superseded, revisit-now
- Format inline:
  - `DECISION [confirmed:YYYY-MM-DD] <one-line decision>`
  - `  - What was decided: ...`
  - `  - When: YYYY-MM-DD`
  - `  - Why: ...`
  - `  - Affected: [[entity]], [[entity]]`
  - `  - Revisit when: ...`
  - `  - Status: active`
- DECISIONs decay slowly (1.5× modifier) — they stay relevant longer than INSIGHTs. They supersede via concept-drift detection (a later DECISION on the same topic moves the earlier one to Demoted knowledge with `↳ superseded by: ...`).
- Example: "DECISION [confirmed:2026-05-15] Going with Pipedrive over HubSpot for the firm's CRM. **Why:** Pipedrive's pricing scales better at our size; HubSpot's marketing automation is more than we need. **Affected:** [[client/acme]], [[bizdev]]. **Revisit when:** if we hit 5+ active sales pipelines, re-evaluate. **Status:** active."

CONTEXT & BACKGROUND:
- Domain knowledge needed to understand this project or topic
- Terminology, acronyms, or jargon defined
- Historical context: why things are the way they are
- Constraints or requirements that shape decisions
```

### C. Cross-cutting

```
CROSS-PROJECT SIGNALS:
- Anything with implications for a different node
- Knowledge that applies across projects
- "The caching pattern here would solve the performance issue in [other-node]"

PEOPLE:
- Anyone who came up: name, role, context
- What they know or own relative to this project
- Tag with other nodes they appear in
- If the user explicitly tagged someone with [ENTITY:person] in the conversation, that's an
  explicit graduation trigger (#5 from the schema in CLAUDE.md) — record the slug.

QUESTIONS FOR NEXT TIME:
- Things to investigate, test, or verify
- Research to do before the next session
- Hypotheses to confirm or reject
```

### D. User Observations (from passive learning engine)

```
PREFERENCES:
- Communication style signals (terse vs. detailed, options vs. decisions)
- Tool/platform preferences expressed or demonstrated
- Working style patterns (batching, time-of-day, delegation)
- Vocabulary and framing they use and expect

CORRECTIONS:
- Anything the user corrected about your approach
- Implicit corrections (they ignored your suggestion and did it differently)
- Format: [what was wrong] → [what they wanted] → [why, if given]

DOMAIN CONTEXT:
- Facts about their company, team, industry shared in passing
- How their processes/systems work
- Constraints they operate under
```

These observations are ALWAYS extracted, even in silent mode. They go to the `user` node, not project nodes (unless the observation is project-specific domain knowledge).

---

## Step 3 — Write to memory

### Storage Location

Memory is stored in `~/Documents/Claude/memory/`.

**Before writing**: Check if `~/Documents/Claude/memory/` is accessible.
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path="~/Documents/Claude")` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem. Create it with `mkdir -p` if it doesn't exist.

If the directory cannot be accessed, explain that memory cannot be persisted without this folder and stop.

1. Determine the file path from the node ID:
   - If node has a prefix (e.g., `client:acme-corp`): `memory/{prefix}/{slug}.md`
   - If no prefix (e.g., `hiring`): `memory/{node-id}.md`
2. If the directory doesn't exist, create it
3. If the node file doesn't exist, create it with the standard template (see Node File Format below)
4. If the node file exists, READ it first, then update the relevant sections
5. After writing the node file, ALWAYS update `memory/DASHBOARD.md`:
   - Replace or add the node's living summary in the Active Nodes section
   - Update the Unified P0 Actions list
   - Update Waiting On if applicable
   - Add any new knowledge entries to Recent Knowledge (keep last 7 days only)
   - Update the "Last updated" timestamp

#### Dashboard File Format

If `DASHBOARD.md` doesn't exist, create it with this template:

```markdown
# Working World Dashboard
> Last updated: YYYY-MM-DD

## Active Nodes
| Node | Summary | Last Updated |
|------|---------|-------------|
| [node-id] | [1-line living summary] | YYYY-MM-DD |

## Active People (v4.2+)
Top 10 graduated person pages sorted by Last updated desc.

| Person | Temperature | Last contact | Open threads | Page |
|--------|-------------|--------------|--------------|------|
| Sarah Chen | Active | 2026-05-10 | 2 | [person/sarah-chen](person/sarah-chen.md) |

## P0 Actions
- [P0] [node-id]: [action]

## Waiting On
- [WAITING:who] [node-id]: [what]

## Recent Knowledge (last 7 days)
- [node-id] [TYPE] (date): [entry]

## Stale Threads
- [node-id]: [thread] — open since [date]

## Dormant Nodes
- [node-id]: Last active [date]

## Isolated Notes (v4.2+)
Surfaced by `/cleanup`'s orphan-detection guardrail. Nodes with no incoming/outgoing links and last updated >30 days ago.
- [node-id]: Last updated [date] — suggest [archive / merge / keep]
```

#### Node File Format

```markdown
# {node-id}
> Last updated: YYYY-MM-DD

## Summary
[Living summary — replaced each session]

## Knowledge

### Models
[node] MODEL (date): [entry]

### Gotchas
[node] GOTCHA (date): [entry]

### Lessons
[node] LESSON (date): [entry]

### Recipes
[node] RECIPE (date): [entry]

### Insights
[node] INSIGHT (date): [entry]

### Corrections
[node] CORRECTION (date): [entry]

## People
[node] PEOPLE: [[person/<slug>]] (role) — context. Also in: [[<other-node>]], [[<other-node>]]

(v4.10+ wikilink rule: ALWAYS emit `[[person/<slug>]]` if a person page exists; if not, emit the bare name + flag for graduation tracking via `memory/.person-mention-counts.json`. Same applies to client / company / topic / workstream references in this entry.)

## Changelog
[node] LOG YYYY-MM-DD — title: content
(append-only, newest first)

## Open Threads
- [FRESH/ONGOING/STALE] [description]

## Next Actions
- [P0] [action]
- [P1] [action]
- [WAITING:who] [action]

## Signals
[node] SIGNAL from [other-node] (date): [implication]
```

### User Node — Observation Flush

**Before writing project data**, flush observations to the user profile node:

1. File path: `~/Documents/Claude/memory/user.md`
2. If it doesn't exist, create it with this template:

```markdown
# user
> Last updated: YYYY-MM-DD

## Communication Preferences

## Working Style

## Corrections

## Domain Expertise

## Relationships & Org Context

## Tool & Platform Preferences
```

3. Append new observations to the appropriate section:
   - Preferences → Communication Preferences or Working Style or Tool & Platform Preferences
   - Corrections → Corrections (always — these are highest priority)
   - Domain context → Domain Expertise
   - Relationship info → Relationships & Org Context

4. Before appending, check for duplicates or contradictions:
   - If new observation reinforces existing → skip (already captured)
   - If new observation contradicts existing → write a CORRECTION entry, remove the old one
   - If new observation is genuinely new → append

5. Update `DASHBOARD.md` with the user node's last-updated timestamp

**Confidence gating**: Only commit observations with reasonable confidence. A single offhand remark is a signal, not a fact. But direct corrections — always commit.

### A. Living Summary (replace if exists, create if new)

Format:
```
[node-id] SUMMARY (updated YYYY-MM-DD): [2-4 sentences — what this is, where it stands, what's known. Include top blocker/P0 if any. Include most important recent insight if learning-heavy.]
```

Keep under 400 characters.

### B. Changelog Entry (always append)

Format:
```
[node-id] LOG YYYY-MM-DD — [3-6 word title]: [decisions] | [insights/lessons] | [artifacts] | [next actions]
```

Keep under 500 characters. Skip empty categories.

### C. Knowledge Entries (append or update)

For significant, reusable knowledge, write dedicated entries. These persist longer than logs — they're the highest-value memory content.

#### C.0 Entry metadata convention (v4.3+)

Every knowledge entry carries three timestamps. The first is the original date the entry was committed. The second is the date the entry was last meaningfully touched (re-affirmed, edited, or referenced as evidence in a downstream commit). The third is the date the entry was last surfaced via `/recall` or returned by `memory-librarian`.

Encoded inline using key:value tags at the end of the entry line:

```
[node-id] <TYPE> (YYYY-MM-DD): <entry body>  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```

- The leading `(YYYY-MM-DD)` is the **original commit date** — set once at creation, never changed.
- `[confirmed:YYYY-MM-DD]` is the **last-confirmed-at** timestamp — updated whenever:
  - The user accepts a mining-layer proposal that references this entry (Pre-chain B + Step 2b)
  - A new commit explicitly reinforces this entry (e.g., new evidence for an existing INSIGHT)
  - The user re-confirms via a future v4.4 rehearsal prompt
- `[recalled:YYYY-MM-DD]` is the **last-surfaced-at** timestamp — updated whenever `memory-librarian` returns this entry in a Source Entries list or `/recall` renders it in a project view.

Both tags default to the original commit date if no later event has touched them.

These tags are the substrate for v4.4's forgetting/decay layer. **In v4.3 we write and maintain them but do not yet decay or demote based on them.** v4.4 reads these timestamps and decides which entries to demote, surface for rehearsal, or auto-archive.

Existing pre-v4.3 entries without tags are treated as if `confirmed:` and `recalled:` both equal the original commit date. No migration step needed — the absence of a tag is itself a legible default.

#### C.1 Entry formats

```
[node-id] INSIGHT (YYYY-MM-DD): [the insight, compressed but precise]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```
```
[node-id] LESSON (YYYY-MM-DD): [what was tried] → [what happened] → [the takeaway]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```
```
[node-id] MODEL (YYYY-MM-DD): [how something works, 1-3 sentences]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```
```
[node-id] GOTCHA (YYYY-MM-DD): [the trap and how to avoid it]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```
```
[node-id] RECIPE (YYYY-MM-DD): [technique name] — [when to use] → [how to do it]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```
```
[node-id] CORRECTION (YYYY-MM-DD): [old belief] → [corrected understanding]  [confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]
```

On new commit, both `confirmed` and `recalled` are set to the commit date.

**Quality bar**: Only write knowledge entries for things that are genuinely reusable. The test: "Would future-me benefit from this surfacing automatically?"

#### C.2 Concept-drift detection (v4.4+)

Before writing a new INSIGHT / MODEL / GOTCHA / LESSON entry, check whether it contradicts, supersedes, or meaningfully refines an existing entry on the same node. RECIPE entries are excluded from this check (recipes are additive techniques, not competing facts). CORRECTION entries already encode supersede explicitly via `[old belief] → [corrected understanding]` and don't need the check.

Process:

1. Read all entries of the same type from the target node's active sections (skip `## Demoted knowledge` and `## Archive`). If the node is brand new with no prior entries of this type, skip the drift check.
2. If there are more than 20 existing entries of the same type, scope to the most-recently-confirmed 20 (read each entry's `[confirmed:...]` tag; sort desc, take top 20). The drift check is most useful against recent beliefs; old beliefs that contradict are less likely to still be active.
3. Send to a Haiku-tier classifier:

   > "You are a concept-drift detector for working memory. New entry:
   > `<new entry text>`
   >
   > Existing entries of the same type on this node (most recent 20):
   > [1] `<entry text>`
   > [2] `<entry text>`
   > ...
   >
   > Does the new entry contradict, supersede, or meaningfully refine any of the existing entries? Output exactly:
   > `{supersedes: [<index>], relationship: 'contradicts' | 'supersedes' | 'refines', reason: '<one line>'}`
   > or
   > `{supersedes: null}`
   >
   > Rules:
   > - 'contradicts' = new entry asserts the opposite of the existing one
   > - 'supersedes' = new entry replaces the existing one with an updated version
   > - 'refines' = new entry sharpens or qualifies an existing one without replacing it
   > - Be conservative — only flag when the relationship is clear. Most new entries are additive, not superseding."

4. Parse the response. If `supersedes` is non-null:

   In FULL mode (user-triggered `/remember`):
   - Surface inline before writing:
     > "New entry: '<text>'
     >  Concept-drift detector flagged this against existing entry [<index>]: '<existing text>'
     >  Relationship: <contradicts | supersedes | refines>. Reason: <one line>.
     >
     >  How to handle?
     >  (s)upersede — move existing to ## Demoted knowledge; write new in its place
     >  (k)eep both — write new alongside; existing stays active
     >  (e)dit relationship — describe the relationship inline (e.g., "this is a refinement that should be cross-referenced, not a supersede")
     >  (skip) skip new entry — don't commit it"

   In SILENT mode (auto-commit at conversation end):
   - **Never auto-supersede in silent mode.** Silently demoting a held belief is too destructive for an unattended path. Instead: write the new entry alongside the old, append a `## Concept-drift flags` note to the changelog entry ("New entry on [node] may supersede [existing entry] — review via /rehearse"), and let the user resolve at the next `/recall` or `/rehearse`.

5. On user-chosen `supersede` action:
   - Move the existing entry to the node's `## Demoted knowledge` section (create if missing)
   - Append metadata under the demoted entry: `↳ demoted <today> by supersede` and `↳ superseded by: <new entry's first 60 chars>`
   - Write the new entry in the active section as normal
   - Preserve the old entry's `[confirmed:...]` and `[recalled:...]` tags

6. On `keep both` → write the new entry alongside; both stay active.

7. On `edit relationship` → drop into inline editing for the new entry. After save, write it normally without supersede.

8. On `skip new entry` → do not commit the new entry. Log to triage-log: "skipped new <type> on <node> — concept-drift conflict with existing entry, user declined."

Cost: one Haiku call per new knowledge entry that's being written to a node with > 0 prior entries of the same type. Typical commit writes 2-4 knowledge entries → 2-4 Haiku calls → ~$0.005 per `/remember` invocation. Negligible.

### D. People Index (append or update)

```
[node-id] PEOPLE: [[person/<slug>]] ([role]) — [context]. Also in: [[<other-node-id>]], [[<other-node-id>]]
```

**Wikilink rule (v4.10+):** Always emit `[[person/<slug>]]` if the person page exists at `<config-root>/memory/person/<slug>.md`. If no page exists yet, emit the bare name (e.g., `Kim Smith`) and update `<config-root>/memory/.person-mention-counts.json` — when a person hits ≥3 mentions across ≥2 nodes, the next `/end-day` Step 3 cheap-tier triage proposes graduation to a person page. Same wikilink rule applies to client / company / topic / workstream / domain references within this entry.

#### D.1 Person-page graduation (v4.2+)

After writing PEOPLE entries to project nodes, check each person against the graduation triggers from cortex's CLAUDE.md:

1. **Explicit `[ENTITY:person]` tag** in the conversation → graduate immediately. This is the strongest signal.
2. **Three or more `/recall` invocations** for this person (check `memory/.person-recall-counter.json`) → graduate.
3. **`contact-researcher` produced a dossier** earlier in this conversation (look for a recent run of that agent referencing this slug) → graduate; use the dossier as the page's initial Notes section.
4. **`project-setup` named them as primary contact** for a new engagement that's also being committed in this run → graduate.

To graduate:
1. Compute slug: `firstname-lastname` lowercased, hyphenated. Check for name collision: if `memory/person/<slug>.md` exists but is about a different person (different company / different email), prompt the user once to disambiguate; recommend appending a company hint (`<slug>-<company-slug>.md`).
2. Create `memory/person/<slug>.md` with the schema from CLAUDE.md. Pre-fill what you know from this conversation (Identity, Relationship line, first Recent interactions entry dated today). Leave unknown fields as `_(unknown — fill in next conversation)_`.
3. Add an "Active people" entry to DASHBOARD.md (see DASHBOARD format in section "Dashboard File Format" below).
4. If a recall counter entry exists for this slug, reset its count to `0` (the page now satisfies the trigger).

If a page **already exists** for this person, treat this run as an additive update:

- Append a new line to the page's **Recent interactions** section: `<today> — <conversation_or_activity_type> — <one-line summary>`. Don't duplicate; if an identical line already exists for today, skip.
- Update **Last meaningful contact** in the Relationship section.
- Update **Relationship temperature** if today's interaction crosses a threshold (e.g., from Cold → Warm after a meeting).
- Never overwrite **Notes**, **Identity**, or **Linked entities** without explicit user confirmation. If new identity info contradicts existing, surface the conflict and ask.
- Keep Recent interactions to the last 90 days; older entries get archived to the page's bottom under a `## Archive (>90 days)` section to keep the active surface readable.

Casual mentions (a name appearing in conversation without any of the graduation triggers above) **do not** create or update a person page. They stay in the project node's PEOPLE index.

### E. Cross-Project Signals (if applicable)

```
[other-node-id] SIGNAL from [source-node-id] (YYYY-MM-DD): [the implication]
```

---

## Step 3.5 — Queue an index refresh (v4.5+)

After all writes succeed, append a line to `<config-root>/memory/staged/queues/reindex`:

```
<today YYYY-MM-DD HH:MM> touched: <node-id>[, <node-id>, ...]
```

Create the file if it doesn't exist. Idempotent — multiple `/remember` calls just append more lines.

This step does NOT regenerate `<config-root>/memory/index.md`. That happens at the next `/end-day` Step 5.5, the next `/cleanup` Step 4.5, or an explicit `/reindex`. Synchronously regenerating on every `/remember` would chunk fast capture sessions.

If the reindex-queue file ever exceeds 200 lines, the next consumer of it (indexer) ignores the contents and just runs a full regeneration — the queue is a *hint*, not a critical record.

Silent mode (auto-commit) writes the queue line too. The next session's `/recall` auto-fire will trigger the next index refresh chain.

---

## Step 4 — Continuity check

Scan for:
- **Orphaned threads**: Still open from previous sessions, not addressed
- **Completed threads**: Previously open, now resolved
- **Escalated items**: P2s that should now be P0/P1
- **Invalidated knowledge**: New learning contradicts a prior INSIGHT/MODEL/GOTCHA → update or remove old entry
- **Reinforced knowledge**: New evidence strengthens a prior insight
- **Answered questions**: Prior "questions for next time" that got answered

---

## Step 5 — Confirm

### Full mode (user-triggered)

Respond with:
1. **Node(s)** written to
2. **Living summary** (for verification)
3. **Knowledge captured** — list INSIGHT/LESSON/MODEL/GOTCHA/RECIPE/CORRECTION entries
4. **Observations captured** — count of preferences, corrections, patterns written to user node
5. **Open threads** with staleness
6. **Blockers** (if any)
7. **Next actions** — P0 → P1 → P2 → WAITING
8. **Cross-project signals** (if any)
9. **Knowledge updates** — prior entries invalidated, reinforced, or corrected
10. **Unanswered questions** carried forward

Keep tight. Skimmable in 20 seconds.

### Silent mode (auto-triggered)

- Say nothing unless creating a new node
- If creating a new node: "Noted — started tracking [node-id]."
- If a critical correction was captured that changes future behavior, optionally note: "Got it — I'll [adjusted behavior] going forward."
- Otherwise: complete silence. The user shouldn't notice the commit happened.

---

## Memory hygiene

- **Living summaries**: Always replace, never duplicate
- **Logs**: Append only, never modify past entries
- **Knowledge entries**: Update if understanding evolves. CORRECTION supersedes original. Remove outdated entries.
- **Memory full**: Consolidate old LOGs first. Knowledge entries should be preserved longest — they're the most reusable content.
- **Dormant nodes**: Note `[DORMANT → ACTIVE]` if reviving after 14+ days
- **Staleness**: Open threads 3+ sessions without progress → [STALE]
