---
type: llm
weight: 1
---

The user only said a natural greeting and a natural-language question — they never typed `/morning` or any other slash command. A successful response recognizes this as a request for the cortex `morning` workflow and acts on it directly: it reads or references cortex memory (hot cache, DASHBOARD, active nodes, priorities/open threads/people) and presents a morning-context summary, without first asking the user to type an explicit command. A failing response either ignores the request, asks "did you mean /morning?" instead of just running it, or produces a generic greeting with no memory context at all.
