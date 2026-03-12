---
name: learn
description: >
  Capture standalone knowledge without a full session commit. Auto-fires when
  user says "remember that X works like Y", "good to know that...", "TIL",
  "I just realized...", "note to self about [technical thing]", "the trick is...",
  "gotcha:", "watch out for...", "the way X works is...", or "I was wrong about X".
  Also fires when the user discovers something mid-conversation and it sounds
  like knowledge worth preserving (a gotcha, mental model, technique, or
  corrected assumption) but a full /remember would be overkill.
---

See commands/learn.md for the full workflow.

When this skill fires automatically:

- Identify the knowledge type from the content (model, gotcha, lesson, recipe,
  correction, or insight)

- Identify the most relevant project node from conversation context

- Write a single knowledge entry — no changelog, no full extraction

- Check for conflicts with existing knowledge entries in that node

- Confirm briefly: what was committed, to which node, as what type

- If the user is mid-conversation and seems to be in flow, keep the
  confirmation minimal — don't break their focus with a long report
