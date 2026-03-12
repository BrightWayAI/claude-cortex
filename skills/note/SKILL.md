---
name: note
description: >
  Quick one-liner capture. Auto-fires when a user says "note that [fact]",
  "jot down that...", "quick note:", "FYI for the record:", "just happened:",
  or any brief factual statement the user clearly wants persisted but doesn't
  warrant a full /remember or typed /learn entry. Also fires if the user says
  "log this" followed by a short statement.
---

See commands/note.md for the full workflow.

When this skill fires automatically:

- Identify the project node from context

- Append a lightweight LOG entry

- Confirm in one line

- If the content sounds like a knowledge entry (gotcha, lesson, model), suggest
  upgrading to /learn: "This sounds like a gotcha — want me to /learn it for
  easier recall later?"

- Minimum friction. Don't slow the user down.
