---
name: cleanup
description: >
  Run maintenance on working memory. Auto-fires when a user says "clean up
  memory", "memory is getting cluttered", "consolidate my logs", "what's stale",
  "memory health check", or "run maintenance". Also triggers on "I'm running out
  of memory space" or "too many old entries".
---

See commands/cleanup.md for the full workflow.

When this skill fires automatically:

- Run the full audit: count entries, assess health, identify issues

- Present the health report before proposing any changes

- Propose specific, numbered actions for each issue found

- Never auto-execute — always get user approval

- Default to archive over delete for any content removal

- After cleanup, report what changed and suggest next cleanup date

- If memory is already clean, say so and skip to a brief health summary
