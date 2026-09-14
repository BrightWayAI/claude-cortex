# Capability matrix (Phase 6)

Canonical workflows (`commands/*.md`, `skills/*/SKILL.md`, `references/*.md`)
must describe what they need in terms of the **logical capabilities** below,
never a specific tool name, MCP server, model name, or "Task tool" syntax.
Host adapters (Claude Code, Cowork, a future Codex adapter) translate a
capability into whatever mechanism that host actually offers.

If a canonical file names a concrete tool (e.g. `mcp__cowork__request_cowork_directory`,
"the Task tool", `subagent_type="memory-librarian"`), that is host leakage and
should be rewritten to reference a capability name from this table instead,
with the concrete tool name pushed into the per-host column here.

## Capabilities

### `filesystem.read` / `filesystem.write`

| | |
|---|---|
| Required or optional | Required |
| Claude Code | Native filesystem access via the Read/Write/Edit/Bash tools. |
| Cowork | `mcp__cowork__request_cowork_directory(path=<config-root>)`, then native fs once granted. |
| Behavior when unavailable | Fatal — memory cannot function without this. Explain and stop; never fabricate memory content in its place. |
| Reads/writes external state | No (local disk only). |
| Confirmation policy | Cowork requires one-time user approval per directory; Claude Code requires none (sandboxed to the working directory / explicitly granted paths). |

### `filesystem.atomic_replace`

| | |
|---|---|
| Required or optional | Required for any mutating workflow. |
| Claude Code | `scripts/lib/atomic_write.py` (`atomic_write`/`safe_append`), invoked via `scripts/cortex_cli.py`. |
| Cowork | Same underlying utility — Cowork's model shells out to the same repo scripts via its filesystem access; no separate implementation. |
| Behavior when unavailable | Fatal for mutating workflows — fall back to `filesystem.write` is explicitly disallowed once a node file exists, since it risks partial writes. |
| Reads/writes external state | No. |
| Confirmation policy | None beyond the workflow's own user-facing confirmation step. |

### `filesystem.lock`

| | |
|---|---|
| Required or optional | Required for any mutating workflow. |
| Claude Code | `scripts/lib/locking.py` (`MemoryLock`), invoked via `scripts/cortex_cli.py`. |
| Cowork | Same utility, same mechanism — the lock file lives in `<config-root>/memory/.lock` on shared disk, so it coordinates across hosts regardless of which one is writing. |
| Behavior when unavailable | Fatal for mutating workflows. A workflow must not write without acquiring this. |
| Reads/writes external state | No. |
| Confirmation policy | None; surfaces a wait/timeout message to the user only on contention (see `references/core-contract.md` §11). |

### `user.confirm`

| | |
|---|---|
| Required or optional | Required wherever a workflow calls for it (e.g. destructive `/forget`, ambiguous node routing). |
| Claude Code | A message in the conversation asking the user to respond. |
| Cowork | Same — a chat turn. |
| Behavior when unavailable | N/A — this capability is definitionally always available in an interactive session. In fully unattended/autonomous runs (e.g. `/listen`), workflows must not depend on it and must instead stage a proposal for later confirmation. |
| Reads/writes external state | No. |
| Confirmation policy | This *is* the confirmation mechanism. |

### `web.search`

| | |
|---|---|
| Required or optional | Optional (used by `/research-gaps`). |
| Claude Code | `WebSearch`/`WebFetch` tools. |
| Cowork | Equivalent built-in web tools, or an MCP web-search server if configured. |
| Behavior when unavailable | Degrade predictably — skip web-sourced findings, tell the user research was skipped, don't fabricate sources. |
| Reads/writes external state | Reads (queries a third-party service; queries themselves leave the local machine). |
| Confirmation policy | None required by default; a workflow may choose to confirm before sending a query that contains sensitive node content (see `references/core-contract.md` §13 privacy tiers). |

### `connector.calendar.read` / `connector.mail.read` / `connector.transcripts.read`

| | |
|---|---|
| Required or optional | Optional — only used by `/listen` and sibling-plugin-fed ingest. |
| Claude Code | Provided by an MCP connector or a sibling Nucleus plugin, if configured. Not implemented in this repo. |
| Cowork | Same — via whatever connector integration Cowork has configured. |
| Behavior when unavailable | `/listen` skips the source, notes it as unavailable in `_index.md` (see `references/archive-layout.md`), and continues with whatever sources it does have. Never fatal. |
| Reads/writes external state | Reads (pulls from a third-party calendar/mail/transcript service). |
| Confirmation policy | One-time authorization at connector setup time (outside this repo's scope); no per-run confirmation. |

### `connector.slack.read`

| | |
|---|---|
| Required or optional | Optional — used by `/listen` to pull mentions and authored messages into `archive/YYYY-MM-DD/slack.md`. |
| Claude Code / Cowork | Provided by a Slack MCP server if configured. |
| Behavior when unavailable | `/listen` skips Slack for that day's archive, notes it in `_index.md` as skipped, and continues with other sources. Never fatal. |
| Reads/writes external state | Reads. |
| Confirmation policy | One-time authorization at connector setup; no per-run confirmation. |

### `connector.drive.read`

| | |
|---|---|
| Required or optional | Optional — used by `/listen` to pull file changes in watched folders into `archive/YYYY-MM-DD/drive.md`. |
| Claude Code / Cowork | Provided by a Drive MCP server if configured. |
| Behavior when unavailable | `/listen` skips Drive for that day's archive, notes it in `_index.md` as skipped, and continues. Never fatal. |
| Reads/writes external state | Reads. |
| Confirmation policy | One-time authorization at connector setup; no per-run confirmation. |

### `connector.crm.read`

| | |
|---|---|
| Required or optional | Optional — used by `activity-miner` for deal-stage/lifecycle/task-closure events. |
| Claude Code / Cowork | Provided by a CRM MCP server if configured (e.g. HubSpot: `search_crm_objects`, `get_crm_objects`, `search_properties`). |
| Behavior when unavailable | `activity-miner` skips the CRM source and continues with mail/calendar (see its per-connector triage gate). Never fatal. |
| Reads/writes external state | Reads. |
| Confirmation policy | One-time authorization at connector setup; no per-run confirmation. |

### `connector.crm.write`

| | |
|---|---|
| Required or optional | Optional, and out of scope for core Cortex — this is a sibling-plugin (HubSpot-style) capability referenced by cross-plugin documentation, not implemented here. |
| Claude Code / Cowork | Provided entirely by the sibling plugin; Cortex core never writes to a CRM directly. |
| Behavior when unavailable | No effect on core memory workflows — this capability doesn't gate anything in this repo. |
| Reads/writes external state | Writes (to an external CRM). |
| Confirmation policy | Owned by the sibling plugin, not documented here. |

### `subagent.delegate`

| | |
|---|---|
| Required or optional | Optional — an efficiency choice for broad/cross-node queries (e.g. `/search` Step 0). |
| Claude Code | The `Agent` tool with a named subagent type (e.g. `memory-librarian`). |
| Cowork | The `Task` tool with `subagent_type="memory-librarian"`. |
| Behavior when unavailable | Fall through to inline execution — read the relevant files directly instead of delegating. Never treat delegation as required. |
| Reads/writes external state | No (delegates to another local agent instance). |
| Confirmation policy | None. |

### `artifact.read` / `artifact.update`

| | |
|---|---|
| Required or optional | Optional — Cowork-specific enhancement (e.g. paste-path / brief-state bridging). |
| Claude Code | Not applicable; Claude Code has no artifact layer distinct from the filesystem. |
| Cowork | Cowork artifact APIs. |
| Behavior when unavailable | Core memory workflows must work with this capability entirely absent — it is documented as an enhancement, never a dependency, per Phase 6 of the portability refactor. |
| Reads/writes external state | No (local to the host session). |
| Confirmation policy | None beyond the host's own artifact-access model. |

### `scheduler.register`

| | |
|---|---|
| Required or optional | Optional — used by `/listen`'s nightly cron framing and similar unattended triggers. |
| Claude Code | No native scheduler; the user runs `/listen` manually or wires an external cron to invoke it. |
| Cowork | Cowork's own scheduled-task mechanism, if configured. |
| Behavior when unavailable | The workflow remains available as an on-demand command; only the "runs automatically overnight" framing doesn't apply. |
| Reads/writes external state | No (registers a local trigger). |
| Confirmation policy | One-time setup confirmation when the schedule is first registered. |

## How to use this table

- A canonical workflow file should say "requires `subagent.delegate`" or "degrades if `web.search` is unavailable," not "use the Task tool" or "call `mcp__cowork__request_cowork_directory`."
- When you find a canonical file naming a concrete tool, replace it with a reference to this table's capability name, and (if the host-specific detail is worth keeping) fold it into this table's per-host column instead.
- This table is descriptive of the current two hosts (Claude Code, Cowork). A future Codex adapter adds a column by extending each capability's per-host rows — it does not require changes to canonical workflow files, which is the entire point of routing through capability names instead of tool names.
