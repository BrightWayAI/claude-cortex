---
name: log-writer
description: Internal Cortex primitive for a locked, atomic operations-log append.
metadata:
  codex-status: partial
---

# Cortex log-writer primitive

This is not a user-facing skill. A parent workflow supplies `op_name`,
`summary`, and optional `body`; format the timestamp in the identity time zone.

Resolve `<config-root>` with `scripts/lib/config_root.py`. Any write to
`<config-root>/memory/log.md` must use `scripts/cortex_cli.py` or the existing
`scripts/lib/atomic_write.py` and `scripts/lib/locking.py` implementation. Never
use a bare shell append or direct model edit. If the parent cannot express the
complete append through those shared utilities, return the formatted proposed
entry without writing it and mark the chronicle step degraded.

Log failure is best-effort and must not retroactively fail a parent's completed
main operation.
