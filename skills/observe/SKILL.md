---
name: observe
description: Adapt to explicit user preferences and corrections during the current session.
metadata:
  codex-status: partial
---

# Cortex observation behavior

During the current conversation, adapt to explicit preferences, corrections,
domain facts, and relationship context without interrupting the user's work.
Do not make speculative personality or emotional assessments.

Observation alone never writes memory and is not evidence that a commit ran.
Persist an observation only through the canonical `commands/remember.md`
workflow (Codex: `$remember`), using `scripts/cortex_cli.py` for every memory
mutation. Direct corrections have the highest capture priority; inferred
patterns require repeated evidence and user review.
