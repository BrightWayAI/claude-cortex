---
description: Search across all working memory for knowledge, decisions, people, or topics. Supports "how does X work", "what did we learn about Y", "when did we decide Z", "any gotchas with X", and "what's my P0 list". Returns matching entries from any node.
---

# /search [query]

Cross-project, cross-type search across all working memory.

---

## Step 1 — Parse the query

| Query type | Examples | What to search |
|-----------|---------|----------------|
| **Knowledge** | "how does auth work", "what do we know about caching" | MODEL, INSIGHT, LESSON, RECIPE entries |
| **Gotcha** | "any gotchas with Lambda", "watch out for" | GOTCHA entries |
| **Lesson** | "what went wrong with migration", "what worked for X" | LESSON, CORRECTION entries |
| **Recipe** | "how do we debug X", "process for Y" | RECIPE entries |
| **Decision** | "when did we decide on pricing" | DECISIONS in LOGs |
| **Person** | "what do we know about Kim" | PEOPLE + LOG mentions |
| **Topic** | "everything about authentication" | All entry types |
| **Artifact** | "where's that spreadsheet" | ARTIFACTS in LOGs |
| **Blocker** | "what's blocked" | BLOCKERS in SUMMARYs |
| **Action** | "what's my P0 list" | NEXT ACTIONS in SUMMARYs + LOGs |
| **Question** | "what questions are open" | QUESTIONS + OPEN THREADS |

---

## Step 2 — Search memory

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
