---
name: log-writer
description: >
  Centralized writer for `<config-root>/memory/log.md` — the unified append-only
  chronicle of audit-worthy Nucleus operations (v4.7.1+, centralized in v4.7.2).

  Auto-fires when ANOTHER cortex command finishes its main work and needs to
  append a log entry. Not invoked by the user directly; invoked by /listen,
  /morning, /end-day, /end-week, /reindex, /research-gaps,
  /merge-research-draft, /cleanup, /rehearse at their respective "Log to
  chronicle" steps.

  Inputs: op_name (the command name, e.g., "listen"), summary (the one-line
  description for the entry). Optionally body (1-2 line context block).

  Output: appends one entry to `<config-root>/memory/log.md`. Creates the file
  with the standard header if it doesn't exist. Never modifies prior entries.

  Format is defined here in one place. If the format changes, this skill
  updates; callers don't need to change their instruction strings.
---

# log-writer

Centralized append-only writer for the Nucleus operations chronicle.

## When fired

By another cortex command at the end of its main workflow, when that command needs to log its completion. Callers include:

- `/listen` Step 7.5
- `/morning` Step 4.5
- `/end-day` Step 5.7
- `/end-week` Step 5.7
- `/reindex` Step 5.5
- `/research-gaps` Step 4.5
- `/merge-research-draft` Step 4.5
- `/cleanup` Step 4.7
- `/rehearse` Step 4.5
- (future) `/forget` and `/remember --full` may opt in

This skill is **not** auto-fired by user utterances or trigger phrases. It's a programmatic primitive called from other commands.

## Inputs

The calling command provides:
- `op_name` (required): the command name without the leading slash. E.g., `listen`, `morning`, `end-day`.
- `summary` (required): one-line description of what this run accomplished. Should be informative enough to be useful when grepped months later.
- `body` (optional): 1-2 line context block indented under the entry. Used rarely; only when the summary needs unpacking.
- `timestamp` (optional): override the timestamp. Default is current local time in the user's identity time zone.

## Procedure

1. **Resolve `<config-root>`** via the standard pattern (`~/Documents/.claude-plugin-config-root`).
2. **Determine timestamp.** If `timestamp` was provided, use it. Otherwise read `<config-root>/identity.md` for time zone and use current local time. Format: `YYYY-MM-DD HH:MM` (minute precision; no seconds).
3. **Ensure the log file exists.** Path: `<config-root>/memory/log.md`. If missing, create with this header:

   ```markdown
   # Memory log

   _Append-only chronicle of audit-worthy Nucleus operations. Cortex writes; humans read. See `references/log-chronicle.md` for the spec._

   ```

4. **Compose the entry.** Format:

   ```markdown

   ## [<timestamp>] <op_name> | <summary>
   ```

   If `body` was provided, append it on the next line, indented (4 spaces):

   ```markdown

   ## [<timestamp>] <op_name> | <summary>
       <body line 1>
       <body line 2>
   ```

5. **Append.** Open the file in append mode, write the entry. Never read-and-rewrite — that would invite race conditions if two scheduled commands fire simultaneously.

6. **Best-effort.** If the write fails (disk full, permissions, etc.), the caller's main work must NOT be marked failed. Log-writer returns a status to the caller; the caller continues regardless.

## Format consistency

All callers produce entries with the same structure:

```markdown
## [YYYY-MM-DD HH:MM] <op_name> | <one-line summary>
```

If this format ever needs to change (e.g., add structured fields, add an op-type prefix), update this skill in one place. Callers' instructions just say "invoke log-writer with op_name=X, summary=Y" — they don't repeat the format string.

## What this skill does NOT do

- Does not modify or delete prior log entries. Append-only.
- Does not enforce retention. That's the caller's job or the user's via `cortex.user-context.md` `log_chronicle.max_entries` (future).
- Does not deduplicate. If two commands log the same op at the same minute, both entries are written.
- Does not interpret `summary` or `body` — opaque strings to log-writer.
- Does not fire on user trigger phrases. Programmatic invocation only.
- Does not log itself. There's no "## log-writer fired" entry; the log is for audit-worthy *user* operations, not internal plumbing.
