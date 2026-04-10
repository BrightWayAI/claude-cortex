---
name: timeline
description: >
  Show a chronological timeline of activity across all projects or a single
  project. Auto-fires when a user asks "what have I been working on", "show me
  last week", "what happened this month", "give me a timeline of [project]",
  "what did we do on [project] recently", or "show my activity".
  Also triggers on "what's the arc of [project]" or "show me the history of [project]".
  NOTE: "weekly review" and "prep my status update" should route to /review, not /timeline.
  /timeline is raw chronology; /review is synthesized analysis.
---

See commands/timeline.md for the full workflow.

When this skill fires automatically:

- Determine scope: specific project or all projects

- Default to last 14 days if no date range specified

- Present entries chronologically, oldest to newest

- Include velocity assessment and arc summary

- For cross-project timelines, highlight which projects got the most attention

- If the user seems to be prepping a status update, offer to draft one from
  the timeline data

- If activity is stalling on a project, proactively note it

- Keep individual entries to one line — this is a scan view
