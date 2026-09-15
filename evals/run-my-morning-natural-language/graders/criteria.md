---
type: llm
weight: 1
---

The user asked in plain imperative language, never typing `/morning` or another slash
command. A successful response recognizes this as a request for the cortex `morning`
workflow and runs it directly: merges the latest `/listen` commit-drafts, refreshes
`memory/index.md`/`memory/hot.md`, and presents a morning-context summary, without first
asking the user to type an explicit command. A failing response asks "did you mean
/morning?" instead of running it, or produces a generic response with no memory-merge
context at all.
