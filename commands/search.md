---
description: Search across all working memory for knowledge, decisions, people, or topics. Supports "how does X work", "what did we learn about Y", "when did we decide Z", "any gotchas with X", and "what's my P0 list". Returns matching entries from any node.
---

# /search [query]

Cross-project, cross-type search across all working memory.

---

## Step 0 — Decide: delegate or run inline?

Before doing any work, decide whether to delegate to the `memory-librarian` subagent (in this plugin) or run inline.

**Delegate to memory-librarian when:**
- The query is broad — would touch 5+ memory files (e.g., "what do we know about cross-team coordination," "any gotchas across all clients," "patterns in stalled deals").
- The query is cross-node by nature — themes, patterns, cross-cutting topics.
- The user wants *synthesis* (a deduplicated answer with citations), not a raw list of hits.
- You'd otherwise have to read many memory files inline and bloat this conversation's context.

**Run inline (skip delegation) when:**
- The query targets a single known node — that's a `/recall` job, not `/search`. Tell the user: "Try `/recall [node]` instead — it's faster for single-node loads."
- The query is narrow and surgical — looking for a specific entry by exact phrase, single person profile, or one specific decision date.
- Memory has fewer than 5 active nodes total — delegation overhead isn't worth it.

### To delegate

Use the Task tool with `subagent_type="memory-librarian"` and pass:

- **query** — the user's question, verbatim
- **scope-hint** (optional) — if the user said "in the last 30 days," "across clients only," "lead-engine project specifically," etc., pass that

The agent returns a structured response with these sections:
- **Summary** — 3-5 sentences synthesizing what memory says
- **Source Entries** — bulleted list with file paths and dates
- **Open Threads** — unresolved questions or pending next actions tied to the topic
- **Confidence** — High / Medium / Low with rationale

Render the agent's response to the user largely as-is (Summary first, then Source Entries, then Open Threads). Then offer follow-ups per Step 4 below ("Want to update any of these?" / "Memory is thin on this — want to capture what you know now?").

If delegation fails or the agent isn't available, fall through to inline execution.

---

## Step 1 — Parse the query

| Query type | Examples | What to search |
|-----------|---------|----------------|
| **Knowledge** | "how does their approval process work", "what do we know about onboarding" | MODEL, INSIGHT, LESSON, RECIPE entries |
| **Gotcha** | "any gotchas with Acme's procurement", "watch out for" | GOTCHA entries |
| **Lesson** | "what went wrong with the rollout", "what worked for retention" | LESSON, CORRECTION entries |
| **Recipe** | "how do we handle enterprise proposals", "process for onboarding" | RECIPE entries |
| **Decision** | "when did we decide on pricing", "why did we choose that vendor" | DECISIONS in LOGs |
| **Person** | "what do we know about Kim" | PEOPLE + LOG mentions |
| **Topic** | "everything about our hiring process" | All entry types |
| **Artifact** | "where's that proposal", "find the deck" | ARTIFACTS in LOGs |
| **Blocker** | "what's blocked" | BLOCKERS in SUMMARYs |
| **Action** | "what's my P0 list" | NEXT ACTIONS in SUMMARYs + LOGs |
| **Question** | "what questions are open" | QUESTIONS + OPEN THREADS |

---

## Step 2 — Search memory

### How to Search

**Before searching**: Check if `~/Documents/Claude/memory/` is accessible.
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path="~/Documents/Claude")` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem.

If the directory cannot be accessed, explain that memory cannot be searched without this folder and stop.

1. Read `~/Documents/Claude/memory/DASHBOARD.md` to get the list of all nodes
2. For each active/warm node, read the node file and search for entries matching the query
3. Use the entry type headers (## Knowledge, ### Models, ### Gotchas, etc.) to quickly navigate to relevant sections
4. For person queries, search the ## People section of each node file
5. For action/blocker queries, search ## Next Actions and ## Open Threads sections
6. Compile and deduplicate results across all nodes

Search all entry types: SUMMARY, LOG, INSIGHT, LESSON, MODEL, GOTCHA, RECIPE, CORRECTION, PEOPLE, SIGNAL.

Note per match: node, entry type, date, relevant snippet.

---

## Step 3 — Present results

### For knowledge queries

Prioritize knowledge entries over logs:

```
## What we know about: "[query]" — [count] entries across [node count] projects

### Mental Models
[node-id] ([date]): [MODEL entry]

### Lessons
[node-id] ([date]): [LESSON entry]

### Gotchas
[node-id] ([date]): [GOTCHA entry]

### Recipes
[node-id] ([date]): [RECIPE entry]

### Corrections
[node-id] ([date]): [old] → [corrected]

### Also in session logs
[node-id] ([date]): [LOG snippet]
```

### For project-state queries

Unified actionable list:
```
## All [Blockers/P0 Actions] — [today's date]

**[node-id]**: [description]
```

### For general topic queries

Group by node, relevance-sorted:
```
## Search: "[query]" — [count] results

### [node-id] ([match count])
**[date]** [type]: [snippet]
```

---

## Step 4 — Offer follow-up

- Knowledge results: "Want to update any of these, or add new knowledge?"
- Sparse: "Memory is thin on this. Want to tell me what you know so I can commit it?"
- Decision: "Revisit this, or still standing?"
- Gotcha: "Want me to flag this automatically next time we work in [node]?"

---

## Behavior notes

- Case-insensitive, partial matching
- Zero results → topic hasn't been committed, offer `/learn` or `/note` to capture now
- Knowledge entries are first-class results, not secondary
- Don't fabricate — only surface what's in memory
