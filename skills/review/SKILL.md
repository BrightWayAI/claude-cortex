---
name: review
description: >
  Generate a synthesized weekly review. Auto-fires when a user says "weekly
  review", "what did I accomplish this week", "summarize my week", "weekly
  roundup", "what happened this week", "prep my status update", or "end of
  week review". Also fires on "what have I learned recently" or "give me a
  digest of recent activity".
---

See commands/review.md for the full workflow.

When this skill fires automatically:

- Default to the last 7 days unless the user specifies a range

- Synthesize, don't just list — group by theme (progress, learned, stuck,
  decided, coming up, connections)

- Highlight the "Learned" section prominently — this is what makes the review
  more than a status report

- Call out 1-3 notable items that might get lost in the noise

- Offer to format for sharing (Slack/email) or to commit reflections
