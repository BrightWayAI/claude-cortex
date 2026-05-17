---
description: Capture user identity (name, company, role, what you do, time zone, primary tools) once, in one canonical identity.md. Other plugins in the this marketplace read from this file during their own setup interviews so identity isn't asked across multiple setups. Honors `~/Documents/.claude-plugin-config-root` if set; otherwise writes to `~/Documents/Claude/identity.md` by default. Re-run anytime to update.
---

# /setup-identity

One-time identity bootstrap. Captures the basics that every plugin needs and writes them to a canonical shared file. Lives in whatever folder you've designated as your plugin config root (or `~/Documents/Claude/` by default for backward compatibility).

After this runs, every plugin's `/setup-*` command reads identity from this file instead of re-asking. You only ever update identity in one place.

---

## Step 0 — Resolve plugin config root

Per-plugin config in this marketplace lives under a user-chosen folder, recorded at `~/Documents/.claude-plugin-config-root` (a single-line text file in the user's home directory containing the absolute path of the chosen folder).

### A — Try the pointer

Ensure access to `~/Documents`. In Cowork, call `request_cowork_directory(~/Documents)` once if not already granted. In Claude Code (or any environment with direct filesystem access), no mount is needed. Then read `~/Documents/.claude-plugin-config-root`.

- **Pointer exists**: read line 1 → that's the config root path. Ensure access to `<config-root>`. If running in Cowork and the folder isn't already mounted in this session, call `request_cowork_directory(<config-root>)`. If running in Claude Code or another environment with direct filesystem access, no mount call is needed. Skip to Step 1.
- **Pointer missing**: continue to section B.

### B — First-time bootstrap

The pointer doesn't exist, so this is the user's first plugin setup of any kind. Prompt:

> "First-time plugin setup. Where should I store your plugin config — identity, voice, and per-plugin settings? Pick a folder you control (e.g., `~/Documents/Claude/`, `~/Documents/PluginConfig/`, or any path you prefer). The folder will hold `identity.md`, `voice.md`, and a `plugins/` subdirectory with one file per plugin."

Once the user provides the path:

1. Ensure access to `<path>`. If running in Cowork and the folder isn't already mounted in this session, call `request_cowork_directory(<path>)`. If running in Claude Code or another environment with direct filesystem access, no mount call is needed — proceed to read or write the file.
2. Create `<path>/plugins/` if it doesn't exist.
3. Write the absolute path to `~/Documents/.claude-plugin-config-root`.
4. Confirm: "Saved. All marketplace plugin configs will live under `<path>` from now on. You can change this later by editing `~/Documents/.claude-plugin-config-root` directly."

For the rest of this document, **`<identity-path>`** refers to `<config-root>/identity.md`.

---

## Step 1 — Check for existing identity

Read `<identity-path>` if it exists.

- **Populated** → ask: "Identity already captured. Update specific sections, or start over?"
  - "Update [section]" → jump there.
  - "Start over" → continue full interview.
- **Missing** → start fresh. Create the parent directory if needed.

---

## Step 2 — The interview

One section at a time. Confirm before moving on.

### Section 1 — Person

- Full name
- Title / role (founder, principal, VP marketing, etc.)
- Email address (primary work)
- Time zone (IANA format, e.g., `America/New_York`)
- Pronouns (optional)

### Section 2 — Company

- Company name
- One-sentence description of what your company does
- Industry (e.g., AI consulting, climate tech, SaaS, healthcare)
- Stage / type (founder, agency, in-house team, freelancer, nonprofit, etc.)
- Website URL
- Headcount range (1, 2–10, 11–50, 51–200, 200+)

### Section 3 — Primary tools

These help plugins know what's available without re-asking.

- Primary CRM (HubSpot / Salesforce / Pipedrive / Attio / Affinity / none)
- Primary calendar (Google Calendar / Outlook / Apple / other)
- Primary email (Gmail / Outlook / other)
- Communication tools you use daily (Slack, Teams, Discord — pick what applies)
- Storage / drive (Google Drive / Dropbox / OneDrive / Notion / other)

### Section 4 — Communication defaults

- Default response time you commit to (e.g., "within 1 business day")
- Default working hours (start, end)
- Out-of-office cadence (e.g., "rarely; back same day," "Fridays off," "vacation pre-announced")

---

## Step 3 — Write the identity file

Populate `<identity-path>` with the answers, using this exact structure (other plugins parse it):

```markdown
# User Identity

_Last updated: [today]_
_Created by /setup-identity (cortex plugin)_

## Person
- **Name:** ...
- **Title / role:** ...
- **Email:** ...
- **Time zone:** ...
- **Pronouns:** ... (optional)

## Company
- **Name:** ...
- **What we do:** ... (one sentence)
- **Industry:** ...
- **Stage:** ...
- **Website:** ...
- **Headcount:** ...

## Primary tools
- **CRM:** ...
- **Calendar:** ...
- **Email:** ...
- **Communication tools:** ...
- **Storage / drive:** ...

## Communication defaults
- **Response time:** ...
- **Working hours:** ...
- **Out-of-office:** ...
```

Create the parent directory if it doesn't exist.

---

## Step 3.5 — Write privacy defaults (.gitignore) (v4.7.2+)

After the identity file is written, ensure `<config-root>/.gitignore` exists with the privacy-sensitive paths excluded. Defensive — protects future `/listen` runs from accidentally committing raw email / Slack / transcript content to a git repo.

Logic:
1. If `<config-root>/.gitignore` exists, leave it alone (idempotent — `/listen` Step 0.5 will append missing patterns later if needed).
2. If it doesn't exist, write the full template from `references/gitignore-template.md`. Log one line to the user: "Wrote `.gitignore` with privacy defaults — protects raw archive content from accidental git commits. See `references/gitignore-template.md` for what's covered."
3. If `<config-root>/` lives inside a common cloud-sync path (iCloud, Dropbox, OneDrive, Google Drive), also surface a one-line note: "`.gitignore` doesn't prevent cloud sync. If you sync this folder via <provider>, see `references/gitignore-template.md` for the local-only archive pattern."

No user gate. Best-effort — if the write fails, log internally and continue.

---

## Step 4 — Confirm and offer next step

Summarize what was captured (one short paragraph). Then offer:

> "Identity saved to `<identity-path>`. Other plugins (lead-engine, weekly-outreach, plan-tomorrow, etc.) will read this automatically — you won't be asked these questions again. To configure a specific plugin's domain settings (CRM properties, ICP, voice, offerings catalog, etc.), run that plugin's setup command — those interviews skip identity questions and only ask plugin-specific things."

---

## Behavior rules

- One section at a time. Don't bombard.
- Skip what doesn't apply. "I don't have a CRM yet" is valid.
- Idempotent. Re-running updates existing sections.
- Never silently overwrite. If a value would change, confirm with the user.
- The file lives at `<identity-path>` — wherever the plugin config root points (or the legacy default). Stable across sessions. Plugins read it but don't own it.

## What this is NOT for

- Plugin-specific configuration (CRM custom properties, ICP, voice rules, offerings catalog) — those go in each plugin's per-plugin config at `<config-root>/plugins/<plugin>.user-context.md` via that plugin's setup.
- Capturing observations / preferences — that's what cortex's passive observation does, written to `~/Documents/Claude/memory/user.md` (cortex memory stays at its existing location regardless of config-root choice).
