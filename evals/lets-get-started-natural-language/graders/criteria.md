---
type: llm
weight: 1
---

The user gave a generic first-time-setup cue with no explicit command and no mention of
"nucleus" or "start" by name. A successful response still recognizes this as an
onboarding request — given no other Nucleus context in-session, "let's get started"
maps to the `start-nucleus` walker (identity → voice → sources → Obsidian → per-plugin
setup → diagnostics → optional schedules) and begins it, or at minimum offers it as the
clear first move rather than asking a vague clarifying question. A failing response
ignores the request, treats it as unrelated small talk, or invents an unrelated workflow.
