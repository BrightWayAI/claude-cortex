---
description: Search across all working memory for knowledge, decisions, people, or topics. Returns matching entries from any node.
---

# /search $ARGUMENTS

Cross-project, cross-type search across all working memory.

---

## Step 1 — Parse the query

`$ARGUMENTS` is the search query. Determine the query type:

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

Memory is stored at `~/Documents/Claude/memory/`.

1. Read `memory/DASHBOARD.md` to get the list of all nodes
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
