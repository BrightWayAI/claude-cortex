---
description: Nightly autonomous ingest. Pulls yesterday's calendar / Gmail / Slack / transcripts / Drive activity into immutable `<config-root>/archive/YYYY-MM-DD/`, runs the mining agents (transcript-reviewer, conversation-miner, activity-miner) against the archive, and stages all proposed memory commits as a single draft at `<config-root>/memory/staged/commit-drafts/YYYY-MM-DD.md`. Refreshes `<config-root>/memory/hot.md`. Designed for unattended scheduled execution. Pair with `/morning` to review and merge the draft.
---

# /listen

You are running the overnight ingest pipeline. This command is **unattended by design** — no user gates, no interactive prompts. It runs to completion or fails gracefully.

The output is a single review-ready draft the user merges via `/morning` the next day. `/listen` itself never modifies active memory nodes.

---

## Step 0 — Resolve config root and target date

Standard config-root pattern.

## Step 0.5 — Privacy defaults (v4.7.2+)

Before pulling any external data, ensure `<config-root>/.gitignore` exists and contains the privacy-sensitive paths. This is defensive — `/listen` is about to write raw email / Slack / transcript content to `archive/`, and we don't want that committed to a git repo silently.

Logic:
1. Check whether `<config-root>/.gitignore` exists.
2. If it doesn't exist, write it with the full template from `references/gitignore-template.md`. Log to stdout: "Wrote `.gitignore` with privacy defaults — see `references/gitignore-template.md` for what's protected and why."
3. If it exists, check whether `archive/` and `memory/staged/commit-drafts/` are listed. If either is missing, append the missing patterns under a section: `# Added by cortex /listen first-run — privacy defaults`. Don't reorder or delete user content.
4. Cloud-sync warning: check whether `<config-root>/` lives inside common cloud-sync paths (`~/Library/Mobile Documents/com~apple~CloudDocs/` for iCloud, `~/Dropbox/`, `~/OneDrive*/`, `~/Google Drive/`). If it does, log one line: "Heads up — `<config-root>` is inside <provider>. `.gitignore` does NOT prevent cloud sync. See `references/gitignore-template.md` cloud-sync section for alternatives (local-only archive via symlink)."

This step never blocks. If file write fails, log the error and continue — privacy defaults are best-effort, not blocking.

Determine target date:
- **No argument** → yesterday in identity time zone (most common case; default for scheduled runs at e.g. 11pm or 6am).
- `/listen --date YYYY-MM-DD` → that date.
- `/listen --backfill N` → run the pipeline once per day for the last N days that don't yet have archives. Each day produces its own draft.
- `/listen --remine YYYY-MM-DD` → skip the source-pull phase; only re-run mining against an existing archive. Produces `staged/commit-drafts/<date>-remine-<seq>.md` (doesn't overwrite the original).

If `<config-root>/archive/<target_date>/` already exists AND mode is not `--rewrite` or `--remine`, log "Archive for <date> already exists; skipping pull. Use --remine to re-run mining or --rewrite to force re-pull." and exit with status 0. **Do not silently overwrite a prior archive — it's the immutable substrate.**

---

## Step 1 — Pull yesterday's substrate (skipped in --remine)

For each enabled note source per `<config-root>/plugins/cortex.user-context.md` and `/setup-sources`:

### Calendar (Calendar MCP)
Pull events where start_date matches `target_date` in the user's time zone. Skip blocked time and personal events. Write to `<config-root>/archive/<target_date>/calendar.md` per the format in `references/archive-layout.md`.

### Gmail (Gmail MCP)
Gmail search: `after:<target_date> before:<target_date+1> (to:me OR cc:me)` AND the user is not the most recent sender on the thread. Cap at 50 threads. Default privacy: metadata + 200-char snippet only. If `listen.inbox.full_body: true` is set in user-context, include full message body. Write to `archive/<target_date>/inbox.md`.

### Slack (Slack MCP — optional)
For each channel the user has joined, pull messages from `target_date` where (a) the user was @mentioned, or (b) the user authored the message. Cap 100 messages total. Write to `archive/<target_date>/slack.md` grouped by channel.

### Drive (Drive MCP — optional)
For each watched folder per user-context, list files modified or created on `target_date`. Metadata only. Write to `archive/<target_date>/drive.md`.

### Transcripts (per-adapter)
For each configured note source per `/setup-sources` and `agents/lib/note-source-adapters.md`:
- Granola: query Granola API for meetings dated `target_date`.
- Gemini: query Gemini meetings.
- Fireflies / Otter: same.
- Generic Drive folder: walk the configured transcript folder for files created on `target_date`.

For each transcript found, write `archive/<target_date>/transcripts/<meeting-id>-<slug>.md` with front-matter (source adapter, original ID, title, participants, date) and the transcript body.

### Failures
Each source-pull failure is logged to `archive/<target_date>/_index.md` under `## Errors`. Do not abort the whole pipeline on a single source failure — proceed with what was successfully pulled.

---

## Step 2 — Write the archive index

After all sources complete, write `archive/<target_date>/_index.md`:

```markdown
# Archive index — <target_date>

Generated by /listen at <ISO timestamp>.

## Counts
- Calendar events: <N>
- Inbox threads: <N>
- Slack mentions: <N>
- Drive changes: <N>
- Transcripts: <N>

## Sources pulled
- Calendar MCP: ok | skipped | error
- Gmail MCP: ok | skipped | error
- Slack MCP: ok | skipped | error
- Drive MCP: ok | skipped | error
- Granola adapter: ok (<N> meetings) | skipped | error
- ...

## Errors
- (none) or list with retry hints
```

This file is the canonical "what did /listen accomplish" record.

---

## Step 3 — Run mining agents against the archive

Now mine the archive into proposed memory commits. All three agents run **read-only against the archive** and **read-only against active memory** — they propose, they never write to nodes directly.

### Transcript review
Invoke `transcript-reviewer` agent with:
- Scope: `<config-root>/archive/<target_date>/transcripts/`
- Cross-reference: active person pages + open threads on project/client nodes
- Output: proposed knowledge entries (INSIGHT, MODEL, GOTCHA, LESSON), proposed commitments (to / from others), proposed person-page updates.

### Conversation mining
Invoke `conversation-miner` agent with:
- Scope: Cowork session metadata for `target_date` (via session-info MCP if available)
- Cross-reference: active project nodes
- Output: proposed knowledge entries, proposed user-observation updates.

### Activity mining
Invoke `activity-miner` agent with:
- Scope: `archive/<target_date>/calendar.md`, `inbox.md`, `slack.md`, `drive.md`
- Cross-reference: active person + client + topic nodes
- Output: proposed person-page entries (interactions, status), proposed open-thread updates, proposed commitment captures.

All three agents return structured proposal lists. Aggregate them.

---

## Step 4 — Stage the commit draft

Write all proposals to a single file: `<config-root>/memory/staged/commit-drafts/<target_date>.md`.

Structure:

```markdown
# Commit draft — <target_date>

Generated by /listen at <ISO timestamp>.
Total proposals: <N> across <M> nodes.

## Summary
- <P> proposed knowledge entries
- <Q> proposed person-page updates
- <R> proposed commitments
- <S> proposed thread updates / closures

## Proposals

### Proposal 1 — <node>: <one-line summary>
- **Type:** INSIGHT | MODEL | GOTCHA | LESSON | RECIPE | CORRECTION | person-update | thread-update | commitment
- **From:** transcript-reviewer | conversation-miner | activity-miner
- **Source:** archive/<target_date>/<file> (line <N> or section <X>)
- **Proposed content:**
  > <verbatim or near-verbatim text to add>
- **Target placement:** `<node-path>` · section `<section-name>`
- **Confidence:** high | medium | low
- **Conflicts:** <list of existing entries on the same node this might supersede / contradict; or "none">

### Proposal 2 ...
```

Sort by priority (Critical / High / Medium / Low) within type. Group by source agent for transparency.

This file is what `/morning` walks the user through. It is **not** active memory — it's a draft for review.

---

## Step 5 — Refresh `<config-root>/memory/hot.md`

Invoke the hot-cache regeneration logic per `references/hot-cache.md`. Pure file walk + filter + render. Zero LLM cost.

After this step, the morning's `/recall` auto-fire will load the freshest possible context including yesterday's activity.

---

## Step 6 — Telemetry (optional)

If `core-ops` is installed, log one line via `/log-agent-run`:
```
skill: listen, date: <target_date>, archive_size_bytes: <N>, proposals_count: <M>, runtime_ms: <T>
```

---

## Step 7 — Retention tail (weekly)

Once per week (e.g., when `target_date` is Sunday), additionally:
- Compress `archive/YYYY-MM-DD/` directories older than 30 days into monthly tarballs at `archive/YYYY-MM.tar.gz`. Use OS-native compression (tar / gzip).
- Do NOT delete tarballs > 180 days old silently. Prompt-style retention requires user interaction; `/listen` skips it.

If today is not Sunday, skip Step 7.

---

## Step 7.5 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `listen`
- **summary:** `archived <target_date> (<events> events, <inbox> inbox, <mentions> mentions, <transcripts> transcripts, <errors> errors). <P> proposals staged.`

The log-writer creates `log.md` if missing, writes the timestamped entry, and returns a best-effort status. If the write fails, continue — don't fail the `/listen` run on an audit-log error.

---

## Step 8 — Exit

Print a one-line summary to stdout (visible to scheduled-task logs):

```
/listen <target_date> complete: <N> proposals staged in staged/commit-drafts/<target_date>.md. Run /morning to review.
```

Exit with status 0 on success; non-zero only on hard failures (config-root missing, all sources failed, etc.).

---

## Behavior rules

- **No interactive prompts.** `/listen` is designed for cron. Errors go to the archive's `_index.md`, not to the user.
- **Idempotent on the archive.** Re-running for the same date without `--rewrite` is a no-op.
- **Privacy-conservative.** Default to metadata-only for inbox / Slack. Full bodies only with explicit opt-in via user-context.
- **Never modify active memory.** Proposals stage to `staged/commit-drafts/`. The user gates the merge.
- **Skip silently when empty.** If a date had zero source data (weekend, vacation), still write a minimal `_index.md` noting zero activity. Don't stage an empty draft — skip the draft entirely and log "no activity to mine."
- **Honor adapter health.** If `/setup-sources` flagged an adapter as unhealthy in its last health-check, skip that adapter's pull and note in `_index.md`.

---

## Scheduling

Recommended schedule (register via `/register-schedules` in core-ops):

```yaml
- name: listen-nightly
  cron: "0 23 * * *"          # 11pm local
  command: /listen
  args: ""
```

Alternative early-morning schedule (if user prefers proposals to be fresh at start of day rather than waiting overnight):

```yaml
- name: listen-early-am
  cron: "0 5 * * 1-5"          # 5am weekdays
  command: /listen
  args: ""
```

Both work. The 11pm version means the proposals exist by the time the user wakes up; the 5am version means they're as fresh as possible.

---

## What this command does NOT do

- Does not modify active memory.
- Does not invoke `gap-researcher` (web research) — that's `/research-gaps`.
- Does not invoke the brief, the dashboard, or anything user-facing.
- Does not run mining synchronously with the user (that's what `/end-day` is for).
- Does not chain into `/morning` — they're separate commands by design.
- Does not skip `--remine` runs based on `_index.md` errors; re-mining is always allowed against an existing archive.
