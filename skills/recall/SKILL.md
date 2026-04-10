---
name: recall
description: >
  Surface project memory, user profile, and knowledge into the current conversation.

  Auto-fires in THREE scenarios:

  1. EXPLICIT: User says /recall, "what do we know about [topic/project]", "remind me
     where we left off", "how does [thing] work", "any gotchas with [thing]",
     "what's the status of [project]", "catch me up on [project]". Also fires on
     "what have we learned about [topic]" or when a user references a project/topic
     and seems to expect prior knowledge.

  2. CONVERSATION START: At the beginning of every new conversation, BEFORE the user
     asks for anything, proactively load context. This means:
     - Read the user profile node to remember who they are and how they like to work
     - Check for active projects with stale threads or overdue P0s
     - If the user's first message references a specific project or topic, load that
       context immediately
     - If the user's first message is a greeting or general start, load the dashboard
       overview and surface anything that needs attention
     - Apply user preferences from the profile to your behavior immediately

  3. CONTEXTUAL: Mid-conversation when the user mentions a project, person, or topic
     that has memory — surface the relevant knowledge without being asked. Don't
     dump the full recall output, just weave in the relevant context naturally.
     Example: user mentions "Acme" → you know their procurement requires 3 quotes
     because it's in memory → mention it if relevant to the current discussion.
---

See commands/recall.md for the full workflow.

## Auto-recall behavior (NEW in v4)

The biggest change: `/recall` no longer waits for the user to ask. It runs
automatically at conversation start and contextually during conversation.

### Conversation start (auto-recall)

When a new conversation begins:

1. **Always load the user profile first** (`user` node — `~/Documents/Claude/memory/user.md`)
   - Apply known preferences immediately (communication style, response length, etc.)
   - This happens silently — don't announce "I've loaded your preferences"

2. **Assess the first message:**
   - If it references a specific project → full project recall (show it)
   - If it's a greeting or general start → load dashboard, surface attention items
   - If it's a direct question or task → load relevant context silently, weave in

3. **Proactive health surfacing:**
   - P0 actions overdue by 3+ days → mention them
   - Stale threads (3+ sessions without progress) → flag them
   - Dormant nodes coming back to life → note the gap
   - Recent cross-project signals → surface if relevant

4. **Output for auto-recall on greeting/start:**
   ```
   Welcome back. Here's what needs attention:

   **Overdue**
   - [P0 action] in [node] (due [date])

   **Stale**
   - [thread] in [node] — no progress in [count] sessions

   **Recent**
   - Last worked on [node] ([date]): [1-line summary]

   Which project are we picking up today?
   ```
   Keep this SHORT. Don't dump the full dashboard — just the attention items.
   If nothing needs attention, keep it even shorter: "All clear — what are we working on?"

### Contextual recall (mid-conversation)

When the user mentions a project, person, or topic that has memory:

- **Don't dump a recall block.** Weave relevant knowledge into your response naturally.
- Example: User says "I need to send the proposal to Acme" → you know from memory
  their procurement needs 3 quotes → say "Heads up — Acme's procurement requires
  3 vendor quotes even for renewals, so factor in 2 weeks lead time."
- Only surface knowledge that's RELEVANT to what they're doing right now.
- This is the difference between a tool and a brain: a brain connects context
  automatically, it doesn't wait to be queried.

### Legacy behavior (still supported)

- Project reference → single-project recall with knowledge entries prominent
- Person name → cross-project person profile
- Topic/keyword → topic-based knowledge recall
- "Where did we leave off" → most recent nodes, last session's open threads
- No context available → say so, ask if they want to share
- Knowledge entries surfaced prominently — they're the most valuable recall content
