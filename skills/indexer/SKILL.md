---
disable-model-invocation: true
name: indexer
description: Internal Cortex alias that regenerates the deterministic memory index.
metadata:
  codex-status: partial
---

# Cortex indexer primitive

Prefer the public `$reindex` workflow and read `commands/reindex.md` completely.
Resolve `<config-root>` with `scripts/lib/config_root.py`, then run only:

```bash
python3 scripts/cortex_cli.py reindex --memory-root <config-root>/memory
```

Do not hand-edit `index.md` or delete a reindex queue marker directly. Queue
cleanup remains unavailable until the canonical workflow provides a shared
CLI/library operation for it.
