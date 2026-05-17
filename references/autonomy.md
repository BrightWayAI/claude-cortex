# Per-command autonomy slider (v4.7.1+)

Karpathy's Software 3.0 framing: "LLM apps should be augmentations (Iron Man suits) with autonomy sliders, not full agents." Different capabilities deserve different levels of confirmation friction. Nucleus's default was "suggest+confirm everywhere," which is safe but uniform — users develop trust unevenly across capabilities and want to tune.

This reference defines the autonomy model and how it's configured.

## Three modes

| Mode | Behavior |
|---|---|
| **auto** | Command executes immediately on invocation. No confirmation. No "ok to run?" prompt. Use for capabilities you trust completely. |
| **suggest** (default) | The nucleus-router pattern: when an utterance matches the command, suggest it and ask "run it?" Wait for yes. Don't auto-dispatch. |
| **confirm** | Stronger than suggest. Even when invoked explicitly (e.g., user typed `/lead-draft`), the command pauses at decision points and re-confirms each material action before executing. Use for high-stakes operations where you want to review every move. |

A fourth implicit mode, `manual`, means the command exists but the router never auto-suggests it — the user must type the slash command literally. Useful for capabilities the user wants to keep "out of band."

## Default settings

If no autonomy config exists, these defaults apply. They reflect the operational risk profile of each command — observation and indexing are cheap to redo; outbound drafts and memory writes have blast radius.

```yaml
autonomy:
  # Memory observation and lookup — auto
  /recall: auto
  /search: auto
  /timeline: auto
  /reindex: auto

  # Memory writes — suggest (default user intent verification)
  /note: auto                # one-liner; trust it
  /learn: suggest
  /remember: suggest
  /forget: confirm            # destructive; always confirm
  /rehearse: suggest
  /cleanup: suggest

  # Overnight + autonomous — already designed to run unattended
  /listen: auto               # unchanged; cron-friendly
  /research-gaps: suggest
  /merge-research-draft: confirm  # per-proposal gating

  # End-of-day / end-of-week — interactive by nature
  /end-day: suggest
  /end-week: suggest
  /morning: confirm           # per-proposal gating

  # Setup — confirm (one-time, but each writes to disk)
  /setup-identity: confirm
  /setup-voice: confirm
  /setup-sources: confirm
  /setup-obsidian: confirm

  # Drafting (high blast radius — drafts could go to clients) — confirm
  /lead-draft: confirm
  /lead-connect: confirm
  /lead-warm: confirm
  /weekly-outreach: confirm
  /referral-ask: confirm
  /client-status: confirm
  /ai-roundup: confirm
  /style: suggest             # drafts are local; less risky

  # Daily flow — suggest
  /brief: suggest
  /process-brief: confirm     # writes Gmail drafts and CRM updates
  /plan-tomorrow: suggest

  # Ops — suggest
  /diagnose: auto
  /review-deliverable: suggest
  /log-agent-run: auto
  /agent-metrics: auto
  /register-schedules: confirm
  /nucleus-status: auto
  /nucleus-dashboard: suggest

  # Time tracking — confirm (creates billing-relevant data)
  /track-time: confirm
  /generate-invoices: confirm

  # Project ops — suggest
  /project-setup: suggest
  /referrals: suggest

  # Default fallback for anything not listed
  default: suggest
```

## User override

The user can override defaults in `<config-root>/plugins/cortex.user-context.md` under an `autonomy:` section. Any command not listed in the user override falls back to the defaults above.

Example user override:

```yaml
autonomy:
  /lead-draft: suggest        # user trusts the drafting more after a few weeks
  /track-time: auto            # user has a tight workflow; no need to confirm
  /forget: confirm             # keep the safety on this one
```

## How commands consult the setting

Each command consults its effective autonomy mode (user override → default) at the **gate point** — the moment it would otherwise pause for confirmation. Pseudocode:

```python
mode = resolve_autonomy(command_name)   # user_override or default or 'suggest'

if mode == 'auto':
    # run immediately, no confirmation
    execute()
elif mode == 'suggest':
    # standard suggest+confirm flow
    print(f"Sounds like you want to run {command_name}. Proceed?")
    if user_confirms():
        execute()
elif mode == 'confirm':
    # stricter: confirm each material action
    for action in plan_actions(command_name):
        print(f"About to {describe(action)}. Proceed?")
        if user_confirms():
            execute_action(action)
```

For commands without internal decision points (e.g., `/note`, `/recall`), `confirm` collapses to `suggest`. For commands with internal decision points (e.g., `/morning` walks N proposals one-by-one), `confirm` exposes those internal gates more aggressively.

## Router integration

The `nucleus-router` skill consults `autonomy` for the routed command. When the user's utterance matches, the router's "Sounds like you want to run X?" message is **suppressed for `auto` mode** — the command just runs. For `suggest` mode, the router behaves as today. For `confirm` mode, the router adds emphasis: "Want me to run X? It will prompt for confirmation on each step."

## What this does NOT change

- **No new permissions model.** Autonomy is about confirmation friction, not security. A user who trusts `/lead-draft` enough to set it to `auto` should still have full read-receipts via `memory/log.md`.
- **No bypass of plugin security policies.** Each plugin's `SECURITY.md` still governs what data flows where. Autonomy mode can't make a plugin send email it wasn't supposed to send.
- **No global "auto everything" mode.** There's no `autonomy.global: auto` shortcut. Users opt commands in individually as trust develops.

## Migration

- Users who don't edit their `cortex.user-context.md` get the defaults above. Most behavior is unchanged from v4.7 (suggest+confirm).
- Users on v4.7 who want autonomy: add the `autonomy:` section to their user-context file. No reload or restart needed — commands consult the file on each invocation.
- Setup commands (`setup-identity`, etc.) could prompt about autonomy preference on first run. Not required for v4.7.1 — defaults are fine; users discover the slider via docs.

## Where autonomy is currently wired (v4.7.2)

The autonomy slider is consulted at three levels:

1. **Router level (nucleus-router v0.1.3+).** Before suggesting confirmation for any routed command, the router reads the autonomy mode. `auto` skips the suggest+confirm prompt entirely; `confirm` adds emphasis. This affects ALL commands routed through the router.
2. **Command-level confirmation gates (cortex v4.7.2+).** Three cortex commands have their internal "Proceed?" gates updated to consult autonomy mode and conditionally skip:
   - `/forget` Step 3 (default mode: `confirm`)
   - `/cleanup` Step 3 (default mode: `suggest`)
   - `/setup-obsidian` Step 2 (default mode: `confirm`)
3. **Future wirings.** Other commands' internal gates haven't been updated:
   - `/remember` Step 5 is a summary, not a gate — autonomy doesn't apply naturally. Could add verbose-vs-terse output preference in future.
   - `/morning` and `/merge-research-draft` walk proposals one-by-one with per-item gates; auto-mode there would be dangerous and is intentionally not implemented.
   - `/rehearse` per-entry gates — same reasoning.
   - `/setup-identity`, `/setup-voice`, `/setup-sources` are interactive interview-style; autonomy=auto would mean "skip the interview and use defaults" which is structurally different from confirmation skipping. Not wired.

If a user sets a command to `auto` but the command's gates aren't wired (e.g., `/morning: auto`), the router still skips its prompt — but the command will still walk its internal gates. This is intentional: protect destructive proposal-merging from runaway autonomy.
