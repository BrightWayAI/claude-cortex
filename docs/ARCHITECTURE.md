# Architecture

Cortex is a **markdown-instruction plugin**: there is no runtime binary. Claude reads command and skill files as prompts, then reads and writes files under a single memory directory on disk.

## High-level flow

```
User invokes /remember (or a skill auto-fires)
        │
        ▼
Cowork loads commands/<name>.md  OR  Claude Code loads .claude/commands/<name>.md
        │
        ▼
Claude follows step-by-step instructions (extract state, format entries, write files)
        │
        ▼
Filesystem: ~/Documents/Claude/memory/
        ├── DASHBOARD.md      ← master index
        ├── <prefix>/         ← e.g. client/, strategy/
        │   └── <node>.md    ← one file per node id
        └── archive/          ← archived nodes
```

## Repository layout

| Path | Role |
|------|------|
| `commands/*.md` | Cowork slash commands. May reference Cowork-only directory tools. |
| `skills/*/SKILL.md` | Cowork skills: natural-language triggers that mirror command behavior. |
| `.claude-plugin/plugin.json` | Plugin name, version, description for the Cowork marketplace. |
| `.claude/commands/*.md` | Optional Claude Code copies of commands (no Cowork MCP calls). |

Every command has a **paired skill** with aligned behavior so “save this” and `/remember` stay consistent.

## Memory model

- **Node** — A logical project or theme (e.g. `client:acme-corp`, `strategy:pricing`). Maps to one markdown file under `memory/`.
- **Living summary** — Replaced each session; short status for the node.
- **Changelog (`LOG`)** — Append-only lines per session.
- **Knowledge entries** — INSIGHT, LESSON, MODEL, GOTCHA, RECIPE, CORRECTION; highest long-term value.
- **DASHBOARD.md** — Aggregates active nodes, P0 actions, recent knowledge, and stale-thread hints for fast `/recall` with no arguments.

## Versioning and releases

- **Version** lives in `.claude-plugin/plugin.json` and should match release tags and [CHANGELOG.md](../CHANGELOG.md).
- Pushing to `main` may trigger downstream marketplace notification (see `.github/workflows/notify-marketplace.yml`); coordinate with maintainers before merging release-sensitive changes.

## Further reading

- [CONTRIBUTING.md](../CONTRIBUTING.md) — how to change commands, parity rules, and PR checklist.
- [SECURITY.md](../SECURITY.md) — filesystem scope and how to report issues.
