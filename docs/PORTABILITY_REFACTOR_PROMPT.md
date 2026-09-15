# Cortex stabilization and portability refactor prompt

Use this entire document as the prompt for a Claude Code session opened at the Cortex repository root.

---

You are improving the Cortex repository. Your immediate goal is to make the existing Claude implementation coherent, reliable, secure, and maintainable. Your longer-term goal is to make Cortex portable to Codex and other agent hosts without maintaining separate copies of its core behavior.

Do not begin by adding Codex-specific files. First create a host-neutral core with clean Claude adapters. Other hosts should eventually be able to reuse the same storage contract, workflows, deterministic utilities, and validation suite.

## Working principles

1. Preserve user data and backward compatibility.
2. Treat the repository as the only authorized write scope.
3. Do not read, modify, migrate, initialize, or test against the user's real `~/Documents/Claude/`, Cortex, Nucleus, Obsidian, CRM, email, Slack, transcript, or other personal data.
4. Use temporary fixtures inside the repository or an OS temporary directory for tests.
5. Do not delete, archive, rewrite, or rename existing public interfaces without a documented compatibility path.
6. Do not commit, push, publish, release, alter marketplace state, or modify user-level Claude/Codex configuration unless the user explicitly asks.
7. Preserve unrelated work already present in the worktree.
8. Prefer reversible, reviewable changes.
9. Do not claim a workflow is deterministic if it only exists as model instructions. Deterministic behavior must be implemented and tested as code.
10. Keep reasoning and semantic synthesis in agent workflows; move path resolution, locking, file mutation, rendering, indexing, and validation into deterministic utilities.
11. Core specifications must use host-neutral language. Claude-, Cowork-, Codex-, MCP-, model-, or connector-specific details belong in adapters or capability declarations.
12. Explicit user instructions take precedence over this refactor prompt.

## Desired end state

Cortex should have four clear layers:

```text
Host adapters
  Claude commands, Claude hooks, Claude agents, future Codex adapters
        ↓
Canonical workflows
  Skills and reusable workflow specifications
        ↓
Deterministic memory operations
  Root resolution, locks, atomic writes, indexing, validation, migrations
        ↓
Portable data contract
  Markdown node schema, metadata, links, archive, staging, configuration
```

The portable data contract and canonical workflows must not depend on a particular model vendor or tool name. A host adapter may translate a capability such as `filesystem.read` into the tools available in that host.

## Phase 0 — Audit before editing

Inspect the entire repository, including hidden configuration directories. Use repository search and targeted reads rather than assumptions.

Produce a concise audit covering:

- Every command, skill, agent, hook, manifest, reference, script, and documentation surface.
- Command-to-skill coverage and intentional exceptions.
- Differences between `commands/` and `.claude/commands/`.
- Broken or ambiguous internal references.
- Hardcoded storage paths versus `<config-root>` usage.
- Knowledge taxonomy and node-schema inconsistencies.
- All workflows that mutate memory and whether they acquire and release a lock.
- All references to Claude-, Cowork-, model-, tool-, artifact-, MCP-, connector-, or plugin-specific behavior.
- Claims in README, architecture, contributing, and security documentation that no longer match implementation.
- Validation gaps in `scripts/check_repo.py` and CI.
- Dependencies on sibling Nucleus plugins that are required, optional, or undocumented.
- Current version sources and any version mismatches.

Run the existing validation before editing and record the baseline. Do not treat a passing validator as proof that the repository is healthy.

Before implementing broad structural changes, summarize the intended file changes and compatibility strategy. Continue autonomously when the safe path is clear; stop only for a choice that would materially alter public behavior or user data compatibility.

## Phase 1 — Define canonical contracts

Create or consolidate a host-neutral Cortex contract. Choose a clear location such as `CORTEX.md` or `references/core-contract.md`. Do not duplicate the complete contract across multiple host instruction files.

The contract must define:

- Configuration-root resolution.
- Memory-directory layout.
- Node identifiers and node-to-file mapping.
- Canonical knowledge types.
- User-observation types.
- Required and optional node sections.
- Wikilink rules.
- Timestamp and timezone rules.
- Append-only versus replaceable sections.
- Staging and archive behavior.
- Locking and atomic-write requirements.
- Conflict and concept-drift behavior.
- Privacy classifications.
- Backward-compatibility rules for legacy colon-prefixed nodes and legacy knowledge types.
- Capability names used by workflows, such as filesystem read/write, search, web research, connector queries, subagent delegation, and interactive confirmation.

Resolve the current taxonomy disagreement. The repository currently contains both a newer four-type taxonomy and older six-type references. Select one canonical write format, document how legacy entries are read, and update all active workflows and documentation consistently. Do not rewrite real user memory as part of this repository refactor.

Add a short architecture decision record explaining why the selected contract is host-neutral and how future adapters should consume it.

## Phase 2 — Establish one source of truth for workflows

Eliminate behavioral drift between commands, skills, and host copies.

Preferred architecture:

```text
skills/<workflow>/SKILL.md
skills/<workflow>/references/workflow.md
commands/<workflow>.md
.claude/commands/<workflow>.md
```

- `skills/<workflow>/references/workflow.md` contains the canonical detailed workflow when the procedure is large.
- `SKILL.md` contains concise discovery metadata, activation boundaries, required inputs, and an explicit instruction to read the canonical workflow reference.
- Claude slash-command files are thin adapters that pass command arguments into the same canonical workflow.
- Host copies must be symlinked, generated, or mechanically validated. Do not maintain hand-edited behavioral duplicates.
- If symlinks would make packaging or Windows compatibility unreliable, add a deterministic generator plus a CI check that fails when generated files are stale.

Classify workflows explicitly:

- User-facing command and skill.
- Natural-language-only skill.
- Internal workflow primitive.
- Migration command.
- Host-specific integration.

Do not force artificial one-to-one pairing where it is not appropriate. Instead, maintain an explicit machine-readable or validated coverage map with reasons for exceptions.

Shorten skill descriptions. Each description should front-load the user goal, important trigger phrases, and key exclusions in roughly one or two sentences. Move detailed trigger lists, version history, failure modes, and implementation notes into the skill body. Keep the aggregate discovery metadata small enough for agent hosts with bounded skill-list context.

Ensure every referenced file uses a path that resolves relative to the referencing skill or uses a documented plugin-root mechanism supplied by the host adapter.

## Phase 3 — Standardize configuration-root resolution

Replace scattered hardcoded `~/Documents/Claude/...` behavior with one deterministic resolver.

Requirements:

1. Preserve the existing `~/Documents/Claude` default for backward compatibility unless a documented migration is explicitly chosen.
2. Support a vendor-neutral pointer or configuration key for future hosts.
3. Continue reading the legacy `~/Documents/.claude-plugin-config-root` pointer.
4. Define precedence unambiguously, for example:
   - Explicit workflow argument or project configuration.
   - New Cortex-specific pointer/configuration.
   - Legacy Claude pointer.
   - Backward-compatible default.
5. Expand `~` and platform-specific home paths deterministically.
6. Validate that resolved paths are absolute and safe before mutation.
7. Never use an unresolved environment variable, broad home directory, or filesystem root as a destructive target.
8. Return structured errors that host adapters can explain.

All commands and skills should refer to `<config-root>` and `<memory-root>` after resolution. Host-specific directory-mount or permission requests must occur only in the adapter layer.

Add unit tests for precedence, missing pointers, malformed pointers, Windows-style paths where supported, tilde expansion, and unsafe targets.

## Phase 4 — Make memory mutation deterministic and concurrency-safe

Inventory every workflow that can create, append, edit, overwrite, move, archive, merge, or delete memory content.

Create shared utilities for:

- Lock acquisition, ownership metadata, timeout, stale-lock handling, and guaranteed release.
- Atomic write-through-temporary-file-and-rename behavior.
- Safe append behavior.
- Node path validation.
- Reading and updating Markdown sections without clobbering unrelated content.
- Backup or rollback preparation for destructive operations.
- Index and hot-cache rendering.
- Queue and marker operations.
- Schema validation.

Every mutating workflow must use the same lock protocol, not merely mention the protocol in prose. Lock before the first relevant read-modify-write operation and release on success, failure, interruption, or early exit.

The lock must coordinate Claude, future Codex sessions, scheduled tasks, and other processes through the shared filesystem. It must not depend on in-memory host state.

Add tests for:

- Two writers competing for the same lock.
- Stale-lock recovery.
- Failure during a write.
- Idempotent retries.
- Simultaneous append operations.
- Attempts to traverse outside the memory root.
- Existing files containing unexpected but valid user-authored Markdown.
- Partial or malformed node files.

Do not use the user's real memory directory in any test.

## Phase 5 — Make deterministic claims true

Implement code for operations currently described as deterministic or zero-LLM, including at minimum:

- Memory index generation.
- Hot-cache generation.
- Root resolution.
- Locking.
- Repository validation.
- Any purely mechanical migrations retained as supported commands.

Use the repository's existing language and dependency footprint when reasonable. Avoid introducing a runtime dependency that materially complicates installation without explaining the tradeoff.

Keep generated output stable. Re-running an operation without source changes should produce no diff.

Provide `--dry-run` or equivalent preview behavior for migrations and destructive maintenance utilities.

## Phase 6 — Separate capabilities from host tools

Create a capability matrix for each workflow. Use logical capabilities rather than raw tool names:

```text
filesystem.read
filesystem.write
filesystem.atomic_replace
filesystem.lock
user.confirm
web.search
connector.calendar.read
connector.mail.read
connector.crm.write
connector.transcripts.read
subagent.delegate
artifact.read
artifact.update
scheduler.register
```

For each capability, document:

- Whether it is required or optional.
- Claude Code implementation.
- Cowork implementation.
- Behavior when unavailable.
- Whether it reads or writes external state.
- Required confirmation policy.

Remove direct Cowork MCP names, Claude tool names, Sonnet/Haiku assumptions, and `Task tool` syntax from canonical workflows. Put those translations in Claude adapters.

Do not silently substitute an expensive or side-effecting capability. Missing optional connectors should degrade predictably. Missing required capabilities should fail with an actionable explanation.

Separate Cortex core from broader Nucleus orchestration:

- Core memory commands must work without briefing, HubSpot, Granola, growth, ops, or other sibling plugins.
- Integration workflows may enhance behavior when those capabilities are present.
- Cross-plugin references must identify the owning plugin and must not look like missing local files.
- Required versions or contracts between plugins must be documented.

## Phase 7 — Repair Claude integration

After the host-neutral core is stable, make Claude the first adapter implementation.

### Claude Code

- Keep `CLAUDE.md` concise and adapter-focused.
- It should point to the canonical Cortex contract rather than duplicate it.
- Make `.claude/commands/` complete and mechanically synchronized.
- Review hooks against current Claude Code lifecycle semantics.
- Distinguish guaranteed behavior from best-effort model behavior.
- Do not claim the existing stop reminder guarantees auto-commit.
- Ensure direct filesystem workflows use the resolver and shared deterministic utilities.

### Cowork

- Keep directory-access requests and Cowork artifact calls inside the Cowork adapter.
- Ask for the narrowest directory scope that supports the chosen workflow.
- Keep the core memory workflows functional when artifact APIs or sibling plugins are absent.
- Document which artifact behavior is an enhancement rather than core memory behavior.

### Claude subagents

- Keep canonical role instructions model-neutral where possible.
- Put Claude model selection and allowed-tool syntax in the Claude agent adapter.
- Enforce read-only behavior mechanically where supported, not only through prose.
- Document fallback behavior when a subagent or connector is unavailable.

## Phase 8 — Correct security and privacy documentation

Rewrite the security documentation to describe actual behavior.

It must cover:

- Every directory Cortex may read or write.
- Commands or scripts Cortex may execute.
- Web research and network access.
- External connectors and possible external writes.
- Raw archive and staged-draft sensitivity.
- Artifact state and clipboard/paste paths.
- Memory-as-git behavior and remote risks.
- Cloud-sync risks.
- Sandbox and directory-permission expectations.
- Lock files and temporary files.
- Data deletion, archival, and recovery behavior.
- The difference between core local-memory workflows and optional integrations.

Audit `.gitignore` templates for contradictions. State clearly which files are tracked, ignored locally, excluded from remotes, or potentially synced by cloud-storage software.

Never describe Cortex as local-only when a selected workflow uses web search, connectors, remote git, or external APIs.

## Phase 9 — Strengthen validation and tests

Expand `scripts/check_repo.py` or replace it with a clearer validation suite while preserving a simple entry command.

Validation must check:

- Real YAML frontmatter parsing.
- Required skill `name` and `description` fields.
- Skill directory/name agreement.
- Manifest schema and version agreement.
- All internal file references.
- Command/skill coverage and documented exceptions.
- Generated-file or symlink freshness.
- Canonical taxonomy references.
- Prohibited hardcoded storage paths outside compatibility fixtures/docs.
- Prohibited host-specific tool names in canonical layers.
- Every mutating workflow's lock declaration or deterministic mutation entrypoint.
- Duplicate or conflicting workflow identifiers.
- Aggregate skill-discovery metadata size.
- Documentation command tables generated from or validated against canonical metadata.
- Security documentation presence and version-sensitive claims.

Add fixture-based tests for the deterministic memory utilities. CI must run validation and tests on pull requests.

Keep the validator's output actionable: show the file, line where possible, violated rule, and expected correction.

## Phase 10 — Prepare—but do not prematurely implement—other hosts

Create a portability readiness document describing how another host would integrate Cortex through:

- A durable instruction entrypoint.
- Skill discovery and explicit invocation.
- Lifecycle hooks.
- Filesystem permission configuration.
- Logical capability adapters.
- Subagent role translation.
- Plugin packaging.
- Scheduled tasks.

For Codex specifically, the future mapping is expected to use:

- `AGENTS.md` for durable project guidance.
- Agent Skills as the canonical workflow format.
- `$skill-name` or natural-language invocation rather than depending on identical slash commands.
- Codex hooks for session-start recall and carefully designed stop/session-end behavior.
- Codex sandbox writable roots for the shared memory directory.
- Codex custom-agent configuration for translated specialist roles.
- A portable Agent Plugins manifest for distribution.

Document this mapping, but do not duplicate workflows into Codex-specific files during the Claude stabilization phase unless the user explicitly expands the scope.

## Documentation requirements

Update README, architecture, contributing, security, configuration, and changelog documentation so they agree with the implementation.

Documentation must not use stale counts such as “all 10 commands.” Generate or validate command tables from canonical metadata where possible.

Clearly distinguish:

- Current behavior.
- Optional behavior.
- Planned behavior.
- Deprecated behavior.
- Migration-only behavior.

Remove historical implementation commentary from active instructions when it does not affect runtime behavior. Keep release history in the changelog.

## Compatibility requirements

The refactor is acceptable only if:

- Existing Markdown memory remains readable.
- Existing `~/Documents/Claude` installations continue to resolve by default.
- Legacy `.claude-plugin-config-root` pointers continue to work.
- Existing node identifiers resolve to the same files.
- Legacy knowledge types remain readable even if new writes use a consolidated taxonomy.
- Existing Claude slash-command names continue to work or have an explicit compatibility wrapper.
- Destructive operations remain user-gated unless the user has explicitly configured a documented autonomy policy.
- Core workflows function without optional Nucleus plugins.
- No test touches real user memory or external services.

## Definition of done

Do not declare completion until all of the following are true:

1. There is one documented canonical storage and schema contract.
2. There is one canonical detailed workflow per capability.
3. Claude command and skill adapters cannot silently drift.
4. Every memory mutation uses shared deterministic locking and safe-write utilities.
5. Deterministic index/cache/migration claims are backed by tested code.
6. Active workflows use one root resolver.
7. Active documentation uses one knowledge taxonomy.
8. Canonical layers contain no undeclared host-specific tool or model assumptions.
9. Security documentation matches actual filesystem, network, connector, command, git, and cloud-sync behavior.
10. Internal references resolve or are explicitly identified as cross-plugin references.
11. The validation suite catches the drift and inconsistencies that existed before this refactor.
12. Existing validation and the new test suite pass.
13. The final diff contains no unrelated modifications.
14. A portability-readiness document explains how Codex or another host can reuse the core without copying it.

## Final handoff

At completion, report:

- The resulting architecture.
- The files added, changed, generated, or intentionally retained.
- Compatibility decisions.
- Deterministic utilities and their tests.
- Validation commands and results.
- Remaining Claude-specific limitations.
- Remaining work before a Codex adapter can be added.
- Any risks that require real-memory testing, clearly separated from tests already completed with fixtures.

Lead with the outcome. Cite concrete files and validation evidence. Do not claim real-world memory compatibility was tested unless the user separately authorized testing against a sanitized copy of their data.

