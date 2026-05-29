---
description: The foundational onboarding walker. Chains the essential setup commands needed for Nucleus to be productive — identity, voice, note sources, Obsidian vault, per-plugin setups, diagnostics, optional schedule registration. Idempotent. Re-running detects what's already configured and only runs what's missing. The "I just installed Nucleus, now what" command.
---

# /start-nucleus

You are running the foundational onboarding walker. The user just typed `/start-nucleus` (or the router routed "start nucleus" / "let's begin" / "onboard me" / "get started" / "set me up" to this command). Your job is to take them from zero to a working Nucleus install in ~15-30 minutes, gating each step so they can skip what doesn't apply.

This command never modifies memory or settings without the user's go-ahead. Every step is a chained invocation of an existing setup command — `/start-nucleus` itself doesn't write anything.

---

## Step 0 — Resolve config root + detect state

Standard config-root pattern. Read `~/Documents/.claude-plugin-config-root`. If missing, the first step (`/setup-identity`) will create it.

Detect current state by checking for marker files:

| Marker | Indicates |
|---|---|
| `<config-root>/identity.md` exists | `/setup-identity` has been run |
| `<config-root>/voice.md` exists | `/setup-voice` has been run |
| `<config-root>/plugins/cortex.user-context.md` exists with `note_sources` section | `/setup-sources` has been run |
| `<config-root>/.obsidian/` exists | `/setup-obsidian` has been run |
| `<config-root>/plugins/<plugin>.user-context.md` exists | that plugin's setup has been run |
| `<config-root>/memory/log.md` contains a `setup-identity` entry | first-run was done at some point |

Build a status report:

```
Nucleus onboarding — status:

  Foundational:
    [✓] Identity captured (Zach Wagner, BrightWay AI)
    [✗] Voice not yet captured  ← will run next
    [✗] Note sources not configured
    [✗] Obsidian vault not scaffolded

  Per-plugin:
    [✓] daily-brief configured
    [✗] lead-engine installed but not configured
    [✗] relationships installed but not configured
    [—] news-curator not installed
    ...

  Schedules:
    [✗] Not registered yet

Estimated remaining: ~12 minutes if you don't skip anything.

Want to keep going? (y / n / skip-to <step-name>)
```

If everything is already configured, surface a one-line "Nucleus is fully set up. Want me to run `/diagnose` to verify, or no?" and exit on user confirmation either way.

---

## Step 1 — Foundational: identity

If `identity.md` is missing:

> "First, who are you? I'll capture name, role, company, time zone, working hours, and tool stack. Other plugins read this so they don't ask the same questions again. ~5 minutes."
>
> "Want to proceed with `/setup-identity` now? (y / skip)"

On `y`: invoke `/setup-identity`. Let it run to completion. Return here on completion.
On `skip`: log "skipped identity" and warn that downstream steps may not work (`/setup-voice`, `/setup-obsidian`, plugins all assume identity exists).

If `identity.md` exists: skip to Step 2 silently.

---

## Step 2 — Foundational: voice

If `voice.md` is missing:

> "Next, your voice. I'll have you paste 2 sample emails or messages you've written — I'll extract your tone, vocabulary, sentence rhythm, and banned phrases. All drafting plugins (lead-engine, relationships, news-curator, client-status, referral-engine, writing-style) read from here. ~5 minutes."
>
> "Skip if you don't plan to draft anything in your voice. Run `/setup-voice` now? (y / skip)"

On `y`: invoke `/setup-voice`. On `skip`: log and continue. If skipped, the drafting plugins will fall back to a generic voice but with reduced fidelity.

---

## Step 3 — Foundational: note sources

If `<config-root>/plugins/cortex.user-context.md` lacks a `note_sources` section:

> "If you use Granola, Gemini, Fireflies, Otter, or a Drive folder for meeting notes, I can connect them. This enables the `/listen` overnight ingest pipeline — yesterday's transcripts get mined into memory while you sleep, and `/morning` walks the proposals. ~5 minutes."
>
> "Skip if you don't have any note adapters. Run `/setup-sources`? (y / skip)"

On `y`: invoke `/setup-sources`. On `skip`: `/listen` will still work but transcript-mining will be empty.

---

## Step 4 — Foundational: Obsidian vault (recommended)

If `<config-root>/.obsidian/` is missing:

> "Want a graph-view of your memory? `/setup-obsidian` scaffolds an Obsidian vault config over `<config-root>/` so you can open it in Obsidian (free, https://obsidian.md) and see your people, clients, topics connected by wikilinks. Works on mobile too. ~1 minute."
>
> "Recommended. Run `/setup-obsidian`? (y / skip)"

On `y`: invoke `/setup-obsidian`. On `skip`: silent.

---

## Step 5 — Per-plugin setups

Detect which Nucleus plugins are installed. The detection mechanism depends on runtime:
- **Cowork:** check the installed-plugins list via runtime API if available; otherwise infer from `<config-root>/plugins/*.user-context.md` and from which command files are visible in the session.
- **Claude Code:** check `~/.claude/plugins/` (or wherever the plugins are mounted).

For each installed plugin that has a setup command but no `<config-root>/plugins/<plugin>.user-context.md`:

| Plugin | Setup command | Captures |
|---|---|---|
| daily-brief | `/setup-brief` + `/setup-plan` | Section toggles, sort defaults, working hours, calendar conventions |
| lead-engine | `/lead-setup` | Company, ICP, signal preferences, value-adds |
| relationships | `/setup-relationships` | ICP, tier definitions, voices, time-budget, integrations (auto-imports from peer plugins) |
| referral-engine | `/setup-referrals` | Connector taxonomy, quiet threshold, ask cadence |
| news-curator | `/setup-news` | Topic, audience, sources, post format |
| client-status | `/setup-status` | Cadence, status template, per-client overrides |
| project-setup | `/setup-projects` | Offerings catalog, drive layout, communication defaults |
| time-tracking | `/setup-time` | Clients, billing models, calendar tagging |
| writing-style | `/setup-style` | Style file location, learning thresholds |
| core-ops | `/setup-core` | CRM, brand, deliverable conventions |
| weekly-alignment | `/setup` (in that plugin's skills) | Slack channels, teams, risk patterns |

Surface them as a single grouped menu:

```
Plugin setups needed:

  [1] /setup-brief + /setup-plan    (daily-brief — ~5 min)
  [2] /lead-setup                    (lead-engine — ~10 min)
  [3] /setup-relationships           (relationships — ~3 min for full Nucleus stack; auto-imports from peers)
  [4] /setup-referrals               (referral-engine — ~5 min)
  ...

Pick: all / numbered list (e.g., "1,3,4") / skip-all / one-at-a-time

Estimated: ~37 minutes for all.
```

Walk each chosen setup in order. Between each, offer: "Continue with the next setup or pause here?" Pausing means re-running `/start-nucleus` later will resume from where they left off (since the marker files persist).

---

## Step 6 — Verify with /diagnose

If core-ops is installed:

> "Let's verify everything is wired up. Running `/diagnose` — this checks for missing setups, connector gaps, subagent availability."

Invoke `/diagnose`. Surface its output.

If issues are surfaced, offer to fix them inline: "Want to go back to `<step>` to address this?"

If core-ops isn't installed, skip this step with a one-line note: "(Skipping /diagnose — core-ops not installed.)"

---

## Step 7 — Optional: register standing schedules

If core-ops is installed AND its schedule library has not yet been registered:

> "Last thing — Nucleus has a standing-schedules library for daily/weekly/monthly automation (nightly /listen, daily /end-day at 5pm, daily /relationships morning brief, Friday /end-week, monthly /generate-invoices, etc.). Want to register them with Cowork's scheduled-tasks system? You can always opt out of individual ones in `core-ops/references/schedules.md`."
>
> "Run `/register-schedules`? (y / skip)"

On `y`: invoke `/register-schedules`. On `skip`: silent.

---

## Step 8 — Closing summary + next steps

```
Nucleus onboarding complete.

Foundation:
  ✓ Identity captured
  ✓ Voice captured
  ✓ Note sources connected (Granola, Gemini)
  ✓ Obsidian vault scaffolded — open ~/Documents/Claude/ in Obsidian

Per-plugin (configured today):
  ✓ daily-brief
  ✓ lead-engine
  ✓ relationships

Schedules:
  ✓ Registered with Cowork (nightly /listen, daily /end-day, ...)

Try these:
  • Say "what's on my plate today" → router suggests /brief
  • Say "I just met Sarah at the AI Summit" → /remember + person page
  • Tonight: /listen runs on cron; tomorrow morning say "good morning" → /morning
  • Anytime: /route prints the full cheat sheet of capabilities

You're set up. Run /diagnose any time to check stack health.
```

Append one line to `<config-root>/memory/log.md` via the `log-writer` skill:
- **op_name:** `start-nucleus`
- **summary:** `onboarding completed — <N> foundational + <M> per-plugin setups run, <S> skipped, schedules <registered|skipped>.`

---

## Idempotent re-runs

`/start-nucleus` is safe to re-run any time. Steps with completed markers are silently skipped. New plugins installed since last run are detected and offered. If a setup was previously skipped, it's offered again (the user might want to come back to it).

`/start-nucleus --reset` (advanced) deletes all marker files and walks from scratch. Requires explicit confirmation per file before deletion. Rare; mostly for development or testing.

---

## Behavior rules

- **Every step has a skip.** Nothing is mandatory beyond `/setup-identity` (and even that can be skipped with a warning).
- **Honor pauses.** Users will get partway and stop. Re-running picks up exactly where they left off.
- **No silent setup writes.** Each setup-X has its own confirmation gate; `/start-nucleus` doesn't bypass them.
- **Honor autonomy.** If the user has set `autonomy: /start-nucleus: auto`, the menu collapses to "Going through all setups now — interrupt any time." Still walks each setup-X interactively (those have their own gates).
- **Telemetry (optional).** Log via core-ops `/log-agent-run` if installed: `skill: start-nucleus, setups_run: [...], skipped: [...], runtime_ms`.

## What this command does NOT do

- Does not modify identity / voice / source / Obsidian / plugin configs directly. Each setup-X owns its own file writes.
- Does not install plugins. The user uses Cowork's marketplace install for that.
- Does not run any non-setup workflows (`/brief`, `/listen`, `/end-day` etc.). Onboarding only.
- Does not bypass the per-setup confirmation gates. Each setup-X command is autonomous within its scope.
- Does not fail the run if a single setup errors. Reports the error, moves to the next, surfaces all errors in the closing summary.
