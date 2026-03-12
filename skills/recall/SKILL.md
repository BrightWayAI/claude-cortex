---
name: recall
description: >
  Surface project memory and knowledge into the current conversation. Auto-fires
  when a user says /recall, "what do we know about [topic/project]", "remind me
  where we left off", "how does [thing] work", "any gotchas with [thing]",
  "what's the status of [project]", "catch me up on [project]", or starts a
  conversation assuming shared context. Also fires on "what have we learned
  about [topic]" or when a user references a project/topic and seems to expect
  prior knowledge.
---

See commands/recall.md for the full workflow.

When this skill fires automatically:

- Project reference → single-project recall with knowledge entries prominent
- Person name → cross-project person profile
- Topic/keyword → topic-based knowledge recall (models, gotchas, lessons, recipes)
- "Where did we leave off" → most recent node(s), last session's open threads
- Starting fresh → offer dashboard: "Want me to pull up your working world?"
- No context available → say so, ask if they want to share what you should know
- Stale threads or overdue P0s → flag proactively

Knowledge entries (INSIGHT, MODEL, GOTCHA, RECIPE, LESSON, CORRECTION) should
be surfaced prominently — they're often the most valuable thing to recall.
