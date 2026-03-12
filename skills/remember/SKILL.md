---
name: remember
description: >
  Commit a conversation to working memory — extracts both project state and
  knowledge (insights, lessons, mental models, gotchas, recipes, corrections).
  Auto-fires when a user says /remember, "save this conversation", "commit this
  to memory", "log this session", or signals they're wrapping up. Also triggers
  if the user asks Claude to "remember" something specific about a project,
  decision, or piece of knowledge.
---

See commands/remember.md for the full workflow.

When this skill fires automatically:

- If the user said "remember that X" → determine if X is project state (decision,
  action) or knowledge (insight, gotcha, model). Commit to the appropriate entry
  type in the relevant node.

- If the user is wrapping up → offer: "Want me to commit this session to memory?"
  If they agree, run full extraction covering both project state AND knowledge.

- If mid-conversation → checkpoint: commit what's happened so far. Note
  `[CHECKPOINT]` in the changelog.

- If the conversation was purely exploratory/learning (no decisions or actions) →
  focus extraction on the Knowledge section. It's totally valid to commit a
  session that only produced INSIGHT/LESSON/MODEL entries with no project state.

- If multiple projects → commit to each separately, flag cross-project signals.

- If new node → note `[NEW NODE]` in changelog, write thorough initial summary.

Key extraction targets:
1. Decisions, open threads, blockers, artifacts, next actions (project state)
2. Insights, lessons, mental models, gotchas, recipes, corrections (knowledge)
3. Cross-project signals and people
4. Questions for next time
