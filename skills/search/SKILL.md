---
name: search
description: >
  Search across all working memory for knowledge, decisions, people, or topics.
  Auto-fires when a user asks "how does [X] work", "any gotchas with [X]",
  "what did we learn about [topic]", "when did we decide [X]", "what's the
  trick for [X]", "have we seen this before", "what's blocked right now",
  "what are my P0s", or "did we ever figure out [X]". Also fires on "what do
  we know about [person/topic/technology]".
---

See commands/search.md for the full workflow.

When this skill fires automatically:

- Parse query type: knowledge, decision, person, topic, artifact, blocker, action

- For knowledge queries, prioritize INSIGHT/LESSON/MODEL/GOTCHA/RECIPE/CORRECTION
  entries over raw log mentions

- Zero results → suggest the topic hasn't been committed yet, offer /learn or
  /note to capture what the user knows now

- Keep snippets short, link to /recall for full context
