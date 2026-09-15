# Architecture

Cortex is a **markdown-instruction plugin with shared deterministic utilities**. Claude, ChatGPT Work, or Codex reads thin skill adapters and canonical commands, while every memory mutation uses the shared Python CLI/library against one memory directory.

## High-level flow

```
User invokes /remember, $remember, or a matching skill
        │
        ▼
Host adapter loads commands/<name>.md
        │
        ▼
Host follows the canonical workflow and capability binding
        │
        ▼
scripts/cortex_cli.py performs locked, atomic memory mutations
        │
        ▼
Filesystem: <config-root>/memory/
        ├── DASHBOARD.md      ← master index
        ├── <prefix>/         ← e.g. client/, strategy/
        │   └── <node>.md    ← one file per node id
        └── archive/          ← archived nodes
```

## Repository layout

| Path | Role |
|------|------|
| `commands/*.md` | Cowork slash commands. May reference Cowork-only directory tools. |
| `skills/*/SKILL.md` | Portable generated Agent Skills wrapping canonical workflows. |
| `.agents/skills/*/SKILL.md` | Generated Codex project-discovery copies of the portable skills. |
| `plugin.json` | Portable Agent Plugins manifest and Codex hook binding. |
| `.codex-plugin/plugin.json` | OpenAI compatibility overlay; the portable root remains canonical. |
| `hooks/session_start.py` | Read-only, bounded Codex session-start recall. |
| `mcp.json` | Portable local MCP binding for ChatGPT Work and Codex. |
| `adapters/chatgpt_work/` | Bounded MCP tools; all mutations delegate to the shared CLI. |
| `scripts/configure_cortex.py` | Confirmation-oriented first-run setup for the shared config-root pointer and minimal memory nucleus. |
| `.codex/agents/*.toml` | Read-only Codex bindings for supported roles. |
| `.claude-plugin/plugin.json` | Plugin name, version, description for the Cowork marketplace. |
| `.claude/commands/*.md` | Optional Claude Code copies of commands (no Cowork MCP calls). |

Every command has a **generated paired skill** so “save this,” `/remember`, and `$remember` resolve to the same canonical workflow. Host-specific differences live in `references/capability-matrix.md`, not in forked workflow logic.

Cloud ChatGPT Work adds one transport boundary:

```text
ChatGPT Work / Codex
        |
        | Agent Skills + MCP tool calls
        v
adapters/chatgpt_work/server.py
        |
        | bounded reads or subprocess argv/stdin (never shell=True)
        v
scripts/cortex_cli.py + scripts/lib/*
        |
        v
resolved <config-root>/memory
```

Local Work launches the server over stdio from `mcp.json`. Cloud Work reaches
the same local process through Secure MCP Tunnel. Public HTTPS deployment is a
separate production concern because private memory requires per-user OAuth and
storage isolation.

## Memory model

- **Node** — A logical project or theme (e.g. `client:acme-corp`, `strategy:pricing`). Maps to one markdown file under `memory/`.
- **Living summary** — Replaced each session; short status for the node.
- **Changelog (`LOG`)** — Append-only lines per session.
- **Knowledge entries** — INSIGHT, LESSON, MODEL, GOTCHA, RECIPE, CORRECTION; highest long-term value.
- **DASHBOARD.md** — Aggregates active nodes, P0 actions, recent knowledge, and stale-thread hints for fast `/recall` with no arguments.

## Versioning and releases

- **Version** is synchronized across `.claude-plugin/plugin.json`, root
  `plugin.json`, `.codex-plugin/plugin.json`, and
  `adapters/chatgpt_work/codex-plugin.json`; it should match release tags and
  [CHANGELOG.md](../CHANGELOG.md).
- ChatGPT workspace distribution and release-owner checks are documented in
  [ORGANIZATION_DISTRIBUTION.md](ORGANIZATION_DISTRIBUTION.md).
- Pushing to `main` may trigger downstream marketplace notification (see `.github/workflows/notify-marketplace.yml`); coordinate with maintainers before merging release-sensitive changes.

## Further reading

- [CONTRIBUTING.md](../CONTRIBUTING.md) — how to change commands, parity rules, and PR checklist.
- [SECURITY.md](../SECURITY.md) — filesystem scope and how to report issues.
