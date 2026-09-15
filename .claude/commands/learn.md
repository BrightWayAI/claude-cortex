---
description: Capture standalone knowledge without a full session commit. Alias for `/remember --knowledge <type>` (2026-09-15) — same behavior, kept as a separate command so existing muscle memory, schedules, and router intent mappings keep working.
---

# /learn $ARGUMENTS

`/learn` is an alias for `/remember --knowledge <type>`. Rewrite the invocation as `/remember --knowledge <type> [node] [content]` (infer `<type>` from content if the user omitted it, per that command's type-inference table) and follow that command's Knowledge mode workflow exactly — same parsing, same type inference, same storage, same concept-drift check, same confirmation. Do not duplicate the workflow here; `commands/remember.md` is the single source of truth.

```
/learn client:acme gotcha Their procurement team requires 3 vendor quotes even for renewals
```
is equivalent to
```
/remember --knowledge gotcha client:acme Their procurement team requires 3 vendor quotes even for renewals
```
