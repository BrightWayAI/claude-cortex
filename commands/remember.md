---
description: Commit this conversation to working memory. Extracts knowledge, decisions, insights, open threads, and next actions — then writes a living summary and changelog entry for the detected project node. Run at the end of any conversation worth remembering.
---

# /remember

You are committing this conversation to Claude's working memory. Work through the following steps precisely.

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

QUESTIONS FOR NEXT TIME:
- Things to investigate, test, or verify
- Research to do before the next session
- Hypotheses to confirm or reject
```

---

## Step 3 — Write to memory

### Storage Location

Memory is stored in `~/Documents/Claude/memory/`.

**Before writing**: Check if `~/Documents/Claude/memory/` is accessible. If not, use the `request_cowork_directory` tool to request access:

```
mcp__cowork__request_cowork_directory(path="~/Documents/Claude")
```

The user will see an approval prompt. Wait for the mount to succeed before proceeding. If the user declines, explain that memory cannot be persisted without this folder and stop.

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
[node] PEOPLE: Name (role) — context. Also in: [other nodes]

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

```
[node-id] INSIGHT (YYYY-MM-DD): [the insight, compressed but precise]
```
```
[node-id] LESSON (YYYY-MM-DD): [what was tried] → [what happened] → [the takeaway]
```
```
[node-id] MODEL (YYYY-MM-DD): [how something works, 1-3 sentences]
```
```
[node-id] GOTCHA (YYYY-MM-DD): [the trap and how to avoid it]
```
```
[node-id] RECIPE (YYYY-MM-DD): [technique name] — [when to use] → [how to do it]
```
```
[node-id] CORRECTION (YYYY-MM-DD): [old belief] → [corrected understanding]
```

**Quality bar**: Only write knowledge entries for things that are genuinely reusable. The test: "Would future-me benefit from this surfacing automatically?"

### D. People Index (append or update)

```
[node-id] PEOPLE: [Name] ([role]) — [context]. Also in: [other-node-ids]
```

### E. Cross-Project Signals (if applicable)

```
[other-node-id] SIGNAL from [source-node-id] (YYYY-MM-DD): [the implication]
```

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

Respond with:
1. **Node(s)** written to
2. **Living summary** (for verification)
3. **Knowledge captured** — list INSIGHT/LESSON/MODEL/GOTCHA/RECIPE/CORRECTION entries
4. **Open threads** with staleness
5. **Blockers** (if any)
6. **Next actions** — P0 → P1 → P2 → WAITING
7. **Cross-project signals** (if any)
8. **Knowledge updates** — prior entries invalidated, reinforced, or corrected
9. **Unanswered questions** carried forward

Keep tight. Skimmable in 20 seconds.

---

## Memory hygiene

- **Living summaries**: Always replace, never duplicate
- **Logs**: Append only, never modify past entries
- **Knowledge entries**: Update if understanding evolves. CORRECTION supersedes original. Remove outdated entries.
- **Memory full**: Consolidate old LOGs first. Knowledge entries should be preserved longest — they're the most reusable content.
- **Dormant nodes**: Note `[DORMANT → ACTIVE]` if reviving after 14+ days
- **Staleness**: Open threads 3+ sessions without progress → [STALE]
