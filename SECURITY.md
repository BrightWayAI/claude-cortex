# Security Policy

This document describes what Cortex actually does with your filesystem,
network access, and external accounts — not an idealized or aspirational
description. If a claim here stops matching the implementation, that's a bug
in this document; please report it the same way you'd report a security
issue (see below).

## Core local-memory workflows vs. optional integrations

Cortex has two tiers of behavior:

- **Core memory workflows** (`/remember`, `/recall`, `/note`, `/learn`,
  `/search`, `/forget`, `/cleanup`, `/reindex`) —
  read and write **only** plain-text Markdown files under `<config-root>/`
  (default `~/Documents/Claude/`; see `references/core-contract.md` §1 for
  full resolution rules, including your own `~/Documents/ClaudeCortex/`
  pointer setup). These do not require network access and function fully
  without any sibling plugin installed.
- **Optional integrations** (`/listen`, `/morning`, `/end-day --full`,
  `/research-gaps`, `/setup-obsidian`, `/setup-sources`, and anything that
  reads calendar/inbox/Slack/transcript/CRM data) reach outside the local
  filesystem. These are described in detail below — do not assume "Cortex"
  as a whole is local-only just because the core workflows are.

## What Cortex reads and writes on your filesystem

- `<config-root>/memory/**` — node files, index, hot cache, dashboard,
  staged drafts, logs. Read and written by core workflows.
- `<config-root>/archive/**` — raw calendar/inbox/Slack/drive/transcript
  content pulled by `/listen`. **This is the most sensitive data Cortex
  stores on disk** — verbatim content from external systems, immutable
  once written (see `references/archive-layout.md`).
- `<config-root>/briefs/**` — daily brief snapshots (optional, if the
  briefing sibling plugin is in use).
- `<config-root>/.cortex/config-root`, `~/.cortex/config-root`,
  `~/Documents/.claude-plugin-config-root` — pointer files read to resolve
  `<config-root>` itself. Never written except by explicit setup steps.
- Lock files (`<config-root>/memory/.lock`) and atomic-write temp files
  (`<file>.tmp-<random>` created transiently next to the target during a
  write, then renamed over it or removed on failure) — see
  `references/core-contract.md` §11 and `scripts/lib/locking.py`,
  `scripts/lib/atomic_write.py`. These never persist past a successful or
  failed write; a `.lock` file older than its staleness window is
  reclaimed automatically, not left as manual cleanup.
- Cortex does **not** access files outside `<config-root>/` (and this
  repository's own `tests/` fixture directories during development) as
  part of any documented workflow.

## Scripts and code execution

As of this refactor, Cortex is **not** purely model-instructions-in-markdown.
`scripts/cortex_cli.py` and the modules under `scripts/lib/` are real Python
code, invoked via shell by `/remember` and `/note` (and, going forward,
other mutating commands as they're wired — see `references/core-contract.md`
§11) to perform locking, atomic writes, and index/hot-cache regeneration.
This code:

- Only ever touches paths inside the `--memory-root` it's given, and
  rejects any path that would resolve outside it (`scripts/lib/node_paths.py`).
- Performs no network access, no shelling out to other programs, and no
  execution of content read from memory files as code.
- Is covered by the fixture-based test suite under `tests/` (`python3
  scripts/check_repo.py` runs both repo validation and this test suite).

## Web research and network access

`/research-gaps` uses web search to fill gaps it identifies in memory. This
sends a search query (which may reference node content, e.g. a topic or
company name) to a third-party search provider, and reads back results,
which are staged in `memory/staged/research-drafts/` for your review before
merging into active memory. This is optional — skipping it (or not having
web search available) degrades to "no gap research performed," never a
failure of core memory.

## External connectors and possible external reads/writes

`/listen` (and the mining agents it invokes) can read from calendar, email
inbox metadata, Slack, and meeting transcripts, depending on which
connectors are configured — see `references/capability-matrix.md` for the
`connector.*` capabilities and their per-host implementation. These are
**reads** from third-party services into `<config-root>/archive/`; Cortex
core does not write back to any of them. A sibling plugin (e.g. a
HubSpot-style CRM integration) may perform external **writes**
(`connector.crm.write`), but that capability is owned entirely by the
sibling plugin, not by Cortex core, and does not execute unless that plugin
is installed and configured.

## Raw archive and staged-draft sensitivity

`<config-root>/archive/` and `<config-root>/memory/staged/` (especially
`staged/commit-drafts/`, which quotes raw archive content) are classified
as **sensitive** under `references/core-contract.md` §13 — they contain
verbatim third-party content (email bodies, Slack messages, transcripts),
not the distilled, user-reviewed summaries that live in `memory/*.md` once
committed. Treat them accordingly: don't sync them to a public git remote,
don't paste them into an external tool, don't assume they're safe just
because the rest of `<config-root>/` is fine to share.

## Artifact state and clipboard/paste paths

Cowork's artifact APIs (`artifact.read`/`artifact.update` in the capability
matrix) let `/end-day` maintain a persistent "today's brief" artifact and
support a clipboard-paste fallback path for brief state. This is a
Cowork-specific enhancement — it does not exist in Claude Code, and core
memory workflows do not depend on it. Pasted content follows the same
sensitivity rules as any other memory content it ends up in.

## Memory-as-git and remote risks

If `memory-as-git` is enabled (`<config-root>/memory/.git/` exists),
`<config-root>/memory/` becomes a git repository, maintained per
`references/memory-gitignore-template.md`. Two variants exist:

- **local-only** (default, no remote configured) — safe as long as you
  never add a remote; everything not explicitly excluded is tracked in a
  local-only history.
- **remote-safe** (chosen once you configure `memory_as_git.remote`) —
  additionally excludes PII-dense files (`triage-log.md`,
  `dismissed-proposals.log`, symlinked `*.user-context.md`) before any push.

**If you add a git remote to your memory repository, everything tracked in
it — which is most of your distilled personal/business context — is pushed
there.** Cortex does not warn you again after initial setup; treat adding a
remote as a deliberate decision with real data-sharing consequences, not a
routine git operation.

## Cloud-sync risks

Nothing in Cortex prevents `<config-root>/` from living inside a
cloud-synced folder (iCloud Drive, Dropbox, OneDrive, etc.) if that's where
`~/Documents/` happens to sync from on your machine. If it does, everything
described above as "local" is also subject to that cloud provider's own
storage, retention, and access policies — including `archive/`'s raw
third-party content. This is outside Cortex's control; it's a property of
where you've pointed `<config-root>` and how your OS is configured.

## `.gitignore` audit

The **plugin repository's** own `.gitignore` only excludes Python build
artifacts (`__pycache__/`, `*.pyc`) — it has no relationship to your
personal memory data, which lives outside this repository entirely.

The **generated `.gitignore` templates for your `<config-root>`**
(`references/gitignore-template.md` for `<config-root>/.gitignore`,
`references/memory-gitignore-template.md` for
`<config-root>/memory/.gitignore` under memory-as-git) are consistent with
each other as of this refactor: both exclude `archive/`, `staged/`, and the
lock file (`.lock` — corrected from a stale `.write-lock` reference found
during this audit). If you hand-edit either template, keep the sensitivity
table in `references/gitignore-template.md` as the source of truth for what
belongs excluded.

## Data deletion, archival, and recovery

- `/forget --archive` moves a node to `memory/archive/<slug>.md` —
  reversible by moving the file back; not a delete.
- `/forget` without `--archive` is a genuine delete of the node file. There
  is no undo beyond your own git history or backups, if any.
- `<config-root>/archive/` (the raw source substrate) is immutable once
  written per day; deleting a day's directory is a manual, user-initiated
  action outside any Cortex command.
- Cortex performs no automatic data deletion. Decay/staleness
  classification (`references/decay-model.md`) only changes how content is
  *surfaced*, never deletes it.

## Supported versions

| Version | Supported |
|---------|-----------|
| 4.x     | Yes       |
| 3.x     | Yes       |
| < 3.0   | No        |

## Reporting a vulnerability

If you discover a security issue — for example, a command or script that
could be manipulated to read or write outside `<config-root>`, a lock or
atomic-write bypass, or a path-traversal case not caught by
`scripts/lib/node_paths.py` — please report it **privately**:

1. **GitHub private vulnerability reporting**: Go to the repo's **Security**
   tab → **Report a vulnerability**.
2. **Email**: security@brightwayai.com

Please **do not** open a public issue for security problems. We will
acknowledge reports within 72 hours and aim to publish a fix within 7 days
for confirmed issues.
