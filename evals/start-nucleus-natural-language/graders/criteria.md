---
type: llm
weight: 1
---

The user typed a short natural-language instruction, never the explicit `/start-nucleus`
command. A successful response recognizes this as a request for cortex's onboarding
walker and begins it directly — identity, then voice, then sources, Obsidian, per-plugin
setup, diagnostics, and optional schedule registration, in order, with a skip available
at each step. A failing response asks "did you mean /start-nucleus?" instead of just
running it, treats "nucleus" as an unknown noun, or produces a generic greeting with no
onboarding flow at all.
