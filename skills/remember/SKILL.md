---
name: remember
description: >
  Commit a conversation to working memory — extracts both project state and
  knowledge (insights, lessons, mental models, gotchas, recipes, corrections),
  plus any observations accumulated by the passive learning engine.

  Auto-fires in THREE scenarios:

  1. EXPLICIT: User says /remember, "save this conversation", "commit this
     to memory", "log this session", or asks Claude to "remember" something
     specific about a project, decision, or piece of knowledge.

  2. CONVERSATION END: User signals they're wrapping up — "thanks", "that's all",
     "goodbye", "talk later", "I'm done", "signing off", "good night", "bye",
     "let's stop here", "wrap it up", or any farewell/closing language. In this
     case, run a SILENT auto-commit — don't ask permission, just commit what
     was learned. If the conversation was trivial (no decisions, no knowledge,
     no meaningful observations), skip the commit silently.

  3. SIGNIFICANT MOMENT: A major decision was just made, a critical piece of
     knowledge was shared, or a correction was given that should be captured
     immediately rather than risked to session loss. In this case, do a
     silent checkpoint — no announcement, no confirmation.
---

See commands/remember.md for the full workflow.

## Auto-commit behavior (NEW in v4)

The biggest change: `/remember` no longer requires the user to trigger it. It runs
automatically when conversations end.

### When the user explicitly triggers it
Full extraction with confirmation — same as v3 behavior.

### When the conversation is ending (auto-commit)
1. Detect farewell signals (see trigger list above)
2. Assess conversation value:
   - Were any decisions made? → commit
   - Was knowledge shared or learned? → commit
   - Were corrections given? → always commit (highest priority)
   - Were observations accumulated? → commit to user profile
   - Was it just small talk or a quick question? → skip silently
3. Run extraction in SILENT MODE:
   - No "Want me to commit this?" prompt
   - No confirmation output
   - Just commit and close
   - Exception: if the commit would create a NEW node, briefly mention it:
     "Noted — started tracking [node-id]."

### When a significant moment happens mid-conversation (checkpoint)
1. Silently checkpoint the decision/knowledge
2. Mark `[CHECKPOINT]` in the changelog
3. Continue the conversation without interruption
4. The end-of-conversation commit will include everything since the checkpoint

## What gets committed during auto-commit

Everything from the standard /remember extraction PLUS:
- **User observations** from the passive learning engine → written to `user` node
- **Corrections** given during the conversation → always captured
- **Preferences** expressed or demonstrated → written to `user` node

## Observation flush

During auto-commit, also flush accumulated observations:
1. Check for user-level observations (preferences, corrections, patterns)
2. Write to the `user` node (create if it doesn't exist)
3. Check for project-level observations (domain knowledge, relationship context)
4. Write to respective project nodes
5. Deduplicate against existing entries

## Legacy behavior (still supported)

- "remember that X" → determine if X is project state or knowledge, commit
- Mid-conversation checkpoint → note `[CHECKPOINT]` in changelog
- Purely exploratory session → focus on Knowledge section
- Multiple projects → commit to each, flag cross-project signals
- New node → note `[NEW NODE]` in changelog

## Key extraction targets
1. Decisions, open threads, blockers, artifacts, next actions (project state)
2. Insights, lessons, mental models, gotchas, recipes, corrections (knowledge)
3. User preferences, corrections, and patterns (observations)
4. Cross-project signals and people
5. Questions for next time
