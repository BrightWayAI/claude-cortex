---
name: observe
description: >
  Always-on passive learning engine. This skill does NOT wait for user triggers —
  it runs continuously in the background of every conversation. It silently detects
  user preferences, corrections, domain knowledge, workflow patterns, and relationship
  context. Never interrupts. Never announces itself. Just watches, learns, and adapts
  in real-time. Observations are flushed to memory when the conversation ends.

  This skill should be considered ALWAYS ACTIVE. It does not need a trigger phrase.
  Any conversation is an opportunity to learn about the user.
---

See commands/observe.md for the full specification.

## Always-on behavior

This skill is unique — it does not have trigger phrases because it is always running.
Every conversation is an observation opportunity. The skill operates in two modes:

### Mode 1: Real-time adaptation (during conversation)
When you notice any of the following, adapt your behavior immediately — don't wait
for a commit:

- User corrects your approach → adjust immediately and for the rest of the conversation
- User shows a preference (terse vs. detailed, options vs. decisions) → match it
- User is frustrated or stressed → simplify, be more direct, protect scope
- User is energized → match their pace, be more ambitious
- User shares domain context → incorporate it into your responses going forward

### Mode 2: Memory accumulation (for commit at end)
Silently note observations that should persist beyond this conversation:

**Always capture:**
- Direct corrections: "don't do X", "I prefer Y", "that's wrong"
- Explicit preferences: "I like...", "always...", "never..."
- Role/company/domain facts
- Relationship context: who is who, who owns what
- Process knowledge: how their org/team/company works

**Capture after 2+ signals:**
- Communication style (terse vs. verbose, formal vs. casual)
- Working patterns (batching, time-of-day preferences, task switching)
- Decision-making style (deliberative vs. fast, data-driven vs. intuitive)

**Never capture:**
- One-off moods (use for real-time adaptation only)
- Personality judgments
- Sensitive personal information unrelated to work

### Flush behavior
When the conversation ends (via /remember, auto-commit, or session close):
1. Commit user-level observations to the `user` node
2. Commit project-level observations to their respective nodes
3. Deduplicate against existing entries
4. Corrections always get committed — they're the highest-signal learning

### Cheap-tier commit triage (v4.2+)

Auto-commit at conversation end **always runs `/remember`'s Step 0 Haiku triage** (see `commands/remember.md` → Step 0). The flush behavior above is gated by the classifier's decision:

- **Classifier returns `commit: false`** → write one line to `triage-log.md`, skip the entire flush. **Exception**: if user observations include any CORRECTION-type signals, override to commit those to the `user` node regardless — corrections are always worth keeping (rule #4 above).
- **Classifier returns `commit: true`** → proceed with flush as documented, scoped to the classifier's `nodes` list.

The auto-commit path is where cost discipline matters most because it fires on every farewell signal. Most farewells follow trivial conversations. The triage step turns those into ~$0.001 audit lines instead of full Sonnet synthesis runs.

### Person-page graduation in auto-commit

If the conversation contains a graduation trigger for any person (explicit `[ENTITY:person]` tag, dossier just produced by `contact-researcher`, etc.), the auto-commit path follows `/remember` Step 3 D.1 to create the page. Mention-only references stay in project-node PEOPLE sections and do not auto-graduate.
