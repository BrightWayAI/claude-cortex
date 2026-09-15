---
type: llm
weight: 1
---

The user only said a plain greeting with no question and no explicit command. Because
`morning` is deliberately kept model-invocable specifically to fire on "good morning"
phrasing (the required daily touch), a successful response treats this greeting alone as
enough signal to run the cortex `morning` workflow and present a memory-grounded
morning-context summary. A failing response replies with only a generic greeting back,
or waits for a follow-up question before doing anything.
