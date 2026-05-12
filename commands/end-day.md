---
description: End-of-day orchestration ritual (v4.2+). Chains five steps with user gates between them — inbox triage for tomorrow, transcript review for uncaptured commitments, cortex auto-commit with Phase 4 cheap-tier triage, reflective prompts, and pre-stage tomorrow's brief artifact. Run once per work day, late afternoon. Takes 10-15 minutes including user-gated decisions.
---

# /end-day

End-of-day closing chain. Reads the day, captures commitments, updates memory with cost discipline, and pre-stages tomorrow so the morning has a working surface waiting.

This rewrite (v4.2) ties together the second-brain v2 phases — inbox triage, transcript review, person-page graduation via cheap-tier commit triage, daily-brief pre-stage. Each step has a user gate so the chain never blocks on something the user wants to defer.

Run once per work day, ideally 4-6pm. If a downstream plugin isn't installed (e.g., `daily-brief` not yet adopted), the chain skips that step silently and continues.

---

## Pre-chain — Resolve config root and identity

Resolve `<config-root>` via `~/Documents/.claude-plugin-config-root` (platform-aware Step 0 — see any setup command for the pattern). Read `<config-root>/identity.md` for time zone (defines "today" / "tomorrow").

Determine `today_local` and `tomorrow_local` (next business day: Mon-Thu → tomorrow; Fri → Monday; Sat/Sun → Monday).

---

## Step 1 — Inbox triage for tomorrow

**Goal:** surface threads that will need a reply tomorrow so they can populate tomorrow's brief.

Behavior:

- If the user has the `inbox-triage` plugin installed and its `/triage-inbox` command is available → invoke it. The skill returns the top 3-7 Needs-reply-today threads (the classifier doesn't distinguish "today" from "tomorrow" — it returns "needs a reply in the next 24h," which from a 5pm vantage means tomorrow morning).
- If `inbox-triage` is NOT installed → fall back to a lighter Gmail search: messages received today where the user is in To/Cc and hasn't replied. Cap at 7.
- Either way, **stash the result** in memory for Step 5's pre-stage call. Don't render it to the user yet.

### User gate after Step 1

> "Tomorrow's inbox triage shows [N] threads. Want to review them now, or wait until morning when the brief surfaces them?"

- "Review now" → render the list and pause for user reactions before proceeding to Step 2
- "Wait" (default if no response within ~10s in interactive mode) → continue to Step 2

---

## Step 2 — Transcript review for uncaptured commitments

**Goal:** surface commitments the user made today that aren't already in CRM tasks or cortex memory.

If the `transcript-reviewer` agent is available (cortex bundles it), invoke it with:
- `time-window: 1 day`
- `compare-against: HubSpot tasks owned by user + cortex DASHBOARD.md`

The agent returns a delta — only items missing from existing tracking, formatted as:

```
- [transcript: <meeting title> on <date>] You committed to: <one-line>
- ...
```

### User gate after Step 2

For each item in the delta, prompt:

> "Convert this to a CRM task / cortex P0 / both / skip?"

- **CRM task** → create via HubSpot MCP, due tomorrow (or a user-specified date), assigned to the user
- **Cortex P0** → append to the relevant project node's `## Next Actions` as `[P0]`
- **Both** → both side-effects
- **Skip** → no action, no log

If the delta is empty ("Nothing missing — all commitments already tracked"), confirm and continue. Don't pad.

---

## Step 3 — Cortex auto-commit with cheap-tier triage

**Goal:** capture the day's learnings, decisions, and observations to memory — without burning Sonnet tokens on trivial conversations.

Run `/remember` in silent mode. **Step 0 (cheap-tier triage) is mandatory here** — it's the whole reason this step is cost-disciplined.

- Classifier decides commit-worthiness and node list
- Synthesis runs only on affected nodes
- Trivial day (greetings + scheduling, no decisions) → `commit: false`, one line in `triage-log.md`, no Sonnet call
- Substantive day → normal flow, with the Phase 3 person-page graduation logic firing where relevant

User-observation CORRECTIONs always commit to the `user` node regardless of the classifier's decision (see `skills/observe/SKILL.md` for the override rule).

Confirm briefly to the user (not verbose):

> "Memory updated: [N] nodes touched, [M] knowledge entries committed, [K] person-page updates."

If the classifier returned `commit: false`, say: "Quiet day — nothing material to commit. Logged the audit line." and continue.

---

## Step 4 — Reflective prompts

**Goal:** capture the human-readable version of what mattered today, separate from the structured commits in Step 3.

Ask the user, conversationally, one at a time:

1. **"Biggest thing that got done today?"** — captured as a LESSON or INSIGHT depending on shape, written to the relevant project node.
2. **"What blocked you, if anything?"** — captured as a GOTCHA if structural, or as a BLOCKER on the project's open threads.
3. **"What's the one thing tomorrow has to move?"** — captured as a `[P0]` next-action on the relevant project node, dated tomorrow.

These three answers also feed Step 5's pre-stage as section-6 content of tomorrow's brief (yesterday's reflection, from tomorrow's perspective).

Keep conversational. If the user says "nothing major today," that's valid — skip to Step 5.

If the user provides answers, **append them to today's brief markdown snapshot** at `<config-root>/briefs/<today_local>.md` under section 7 (End-of-day prompts). This is the canonical write — it ensures the snapshot reflects what was actually captured, even if `daily-brief` isn't installed.

---

## Step 5 — Pre-stage tomorrow's brief

**Goal:** when tomorrow morning hits, the brief is already waiting.

If the `daily-brief` plugin is installed:

1. Invoke its `/brief` command with `target_date: tomorrow_local`.
2. Pass the inbox-triage results from Step 1 directly (so the brief doesn't re-query Gmail).
3. Pass today's reflection answers from Step 4 to populate tomorrow's section 6 (Yesterday's reflection).
4. The brief generator writes `<config-root>/briefs/<tomorrow_local>.md` and updates the Cowork artifact "Today's Brief" to tomorrow's data — or, if Cowork artifact tools aren't available (Claude Code), produces the markdown snapshot only with a clear notice.

### User gate after Step 5

> "Tomorrow's brief is staged. Want to review it now, or wait until morning?"

- "Review now" → render section summaries inline (don't dump full sections — that's what the artifact / snapshot is for)
- "Wait" (default) → confirm and close

If `daily-brief` is NOT installed, skip Step 5 entirely. The chain still produced value (triage results visible in chat, commitments converted, memory committed, reflections captured to today's snapshot).

---

## Step 6 — Close

Confirm completion briefly:

> "Day closed. [N] commitments converted, [M] memory entries, [K] person pages touched. Tomorrow's brief staged for [tomorrow_local]. See you tomorrow."

Adjust the count summary based on what actually ran (don't fabricate counts for skipped steps).

---

## Default behavior on user-gate timeouts

If the user is running this in a fire-and-forget mode (e.g., via a scheduled task, or they walked away), apply these defaults after ~10 seconds of no response:

- Step 1 gate → "Wait"
- Step 2 gate → "Skip" per item (don't auto-create CRM tasks without confirmation — that's destructive on the wrong side)
- Step 5 gate → "Wait"

The chain should never block. If the user is engaged, gates pause for input. If not, gates pick the conservative default and move on.

---

## Behavior rules

- **Conversational, not formal.** This is a reflection ritual.
- **Skip what doesn't apply.** Missing plugins → skip that step silently.
- **Don't over-capture.** Step 3's cheap-tier triage exists to prevent over-capture; respect its decisions.
- **Honor user gates.** Never auto-convert transcript commitments to CRM tasks without explicit per-item confirmation.
- **Pre-stage is opt-in default.** If `daily-brief` isn't installed, the chain ends after Step 4. No nag.
- **Telemetry (optional).** If core-ops is installed, log one line at completion: `skill: end-day, steps_run: [...], commits_count, runtime_ms`.

## What this command is NOT for

- **Mid-day check-ins.** Use `/recall [node]` or `/search`.
- **Long retrospectives.** Use `/end-week` or `/review`.
- **Session memory dumps.** That's `/remember`. `/end-day` is the *day's* rhythm.
- **Tomorrow's calendar blocking.** That's `plan-tomorrow`'s job (different verb, different output). If you want both this chain AND calendar blocks for tomorrow, run `/end-day` then `/plan-tomorrow` — there's no automatic chain between them in v1.

## When to skip this entirely

- Weekend afternoons where nothing work-shaped happened today
- Days you took off (vacation, sick) — skip the ritual; don't reflect on a non-work-day
- After running `/end-week`, since that subsumes the day-level reflection
