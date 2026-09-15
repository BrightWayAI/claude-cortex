---
description: Complete the ≤15-minute Nucleus foundation: resolve one shared config root, capture identity and voice, acknowledge the versioned autonomy policy, configure optional note sources, and verify Cortex plus Ops. Specialist-plugin setup is a separate, resumable follow-up rather than part of the 15-minute promise.
---

# /start-nucleus

This is the foundational onboarding walker. Its success condition is a useful Cortex
plus Ops installation in 15 minutes or less. It does not include every specialist
plugin interview in that time budget.

Each mutating step previews its change and uses the owning setup workflow. If the host
cannot programmatically invoke another skill, follow that workflow inline under the
same capability and mutation boundaries; never claim a chained invocation happened.

## Step 0 — Resolve root, host, and state

Resolve `<config-root>` through explicit override → `CORTEX_CONFIG_ROOT` →
`~/.cortex/config-root` → legacy pointer → default, using the shared resolver. A
malformed higher-priority pointer is an error. Request access only to the resolved
directory.

Detect installed plugins through the host's manifest/plugin API when available:

- Cowork / Claude Code — installed plugin catalog or visible plugin manifests.
- Codex — loaded Agent Plugin/skill catalog.
- ChatGPT desktop — enabled plugin/app catalog.
- Any host without discovery — report detection unavailable and ask only about the
  specific dependency needed for the next step.

Check these foundation markers:

| State | Canonical path |
|---|---|
| Identity | `<config-root>/memory/me/identity.md` |
| Voice | `<config-root>/memory/me/voice.md` |
| Autonomy acknowledgment | `<config-root>/memory/me/autonomy-acknowledgment.json` |
| Cortex settings | `<config-root>/plugins/cortex.user-context.md` |
| Obsidian settings | `<config-root>/.obsidian/` |
| Ops settings | `<config-root>/plugins/ops.user-context.md` |

Show only missing or stale foundation items, the active host, and an honest time
estimate. If the foundation is current, offer `/diagnose` and specialist setup.

## Step 1 — Identity (~4 minutes)

If identity is missing, preview and invoke `/setup-identity`. It captures a stable
actor ID, name, role, company, time zone, and tool stack. If skipped, explain which
later steps will be thinner; do not fabricate identity values.

## Step 2 — Voice (~4 minutes)

If voice is missing, offer `/setup-voice` using two representative writing samples.
Explain that Cortex owns the canonical voice file while the Comms plugin applies and
learns medium-specific patterns. If skipped, drafting remains available but generic.

## Step 3 — Versioned autonomy acknowledgment (~2 minutes)

Read the Autonomy policy section from `<config-root>/memory/CLAUDE.md` (or the
forwarded memory instructions). If none exists, offer to install the versioned
default from `references/autonomy-policy.md`; do not write it without confirmation.
Normalize the section to LF line endings, strip
trailing whitespace per line, preserve line order, and compute SHA-256.

The acknowledgment is valid only when all of these match:

- `schema_version` is supported;
- `policy_version` equals the current declared policy version. A pre-versioning
  custom policy is labeled `legacy-unversioned`; its hash still controls validity;
- `policy_sha256` equals the current normalized section hash;
- `actor_id` matches the active identity.

Record this personal, host-visible state at
`<config-root>/memory/me/autonomy-acknowledgment.json`:

```json
{
  "schema_version": "1.0.0",
  "policy_version": "1.0.0",
  "policy_sha256": "sha256:...",
  "acknowledged_at": "<ISO-8601>",
  "actor_id": "<identity Actor ID>",
  "host": "<cowork|claude-code|codex|chatgpt-work|other>"
}
```

An old empty `.autonomy-acknowledged` file is legacy evidence that the policy was
once shown, not a valid current acknowledgment. Preserve it, explain the one-time
upgrade, and write the versioned record only after the user accepts or customizes the
current policy. A changed policy hash always requires acknowledgment again.

## Step 4 — Optional note sources and Obsidian (~3 minutes)

If note sources are unconfigured, offer `/setup-sources`. Missing connectors are
optional and must be disclosed. If the user wants an Obsidian view, offer
`/setup-obsidian`; otherwise skip it without treating the foundation as unhealthy.

## Step 5 — Ops starter verification (~2 minutes)

The minimum supported bundle is Cortex plus Ops. If Ops is installed but
unconfigured, offer the quick `/setup-core` path for CRM name/stages and omit brand
customization for later. Then run `/diagnose` read-only.

Foundation success means:

- one resolved config root;
- identity present;
- current policy hash acknowledged;
- Cortex workflows discoverable;
- Ops discoverable when installed;
- missing optional connectors clearly listed.

Do not require specialist setup or schedule registration to call the foundation
complete.

## Step 6 — Optional automation

If the user wants nightly ingest and the host exposes a scheduler:

1. Require one successful manual `/listen` run so connector permissions are known.
2. Offer `/register-schedules`, which reads user-owned definitions from
   `<config-root>/plugins/ops/schedules.md` and confirms before registration.
3. Report registration separately from execution. A registered task is not proof of
   a successful run; run receipts or host history provide that evidence.

If the host has no scheduler, return the validated definition for manual setup.

## Step 7 — Specialist setup (outside the 15-minute foundation)

After foundation completion, show only installed specialists that still need setup:

| Plugin | Setup | Typical time |
|---|---|---:|
| briefing | `/setup-brief` | 5 min |
| growth | `/setup-relationships` | 5–10 min |
| clients | `/setup-projects`, `/setup-status` | 10–20 min |
| admin | `/setup-time` | 10 min |
| comms | `/setup-style` | 5 min |
| research | `/setup-news` | 5 min |
| alignment | `/setup` | 5 min |

Default to "do later." Let the user select one, several, or pause. Re-running
`/start-nucleus` resumes from canonical config files; specialist duration is never
included in the foundation estimate.

## Closing summary

Report foundation status, policy version/hash prefix, optional capabilities skipped,
schedule registration state, and specialists deferred. Suggest three outcomes rather
than command memorization: start the day, recall a client, and ask Ops to route a
Nucleus task.

Log one metadata-only `start-nucleus` run through Ops when available: host,
foundation items completed, specialists configured/deferred, elapsed time, and skipped
capabilities. Do not log identity values or connector payloads.

## Idempotency and reset

Re-runs compare canonical files and the policy hash; they do not rely on an umbrella
"onboarded" flag. New specialists appear as optional follow-ups.

`/start-nucleus --reset` is a diagnostic mode, not a bulk delete. It lists each
foundation record that would be reset and requires explicit confirmation per file.
Never delete identity, voice, memory nodes, plugin settings, or scheduler tasks as part
of onboarding reset. Normally only the versioned autonomy acknowledgment is eligible.

## Behavior rules

- Keep the foundation within 15 minutes; specialist setup is separate.
- Every step can pause or skip, with honest consequences.
- Installed plugin directories are read-only at runtime.
- All host-specific behavior goes through the capability matrix.
- External writes, sends, spending, and schedule registration retain their immediate
  confirmation gates.
- Do not claim a connector, chained workflow, schedule, or write succeeded without
  evidence from that capability.
