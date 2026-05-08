---
description: Capture user identity (name, company, role, what you do, time zone, primary tools) once, in one canonical file at ~/Documents/Claude/identity.md. Other plugins in the BrightWayAI marketplace read from this file during their own setup interviews so identity isn't asked 9 times. Re-run anytime to update.
---

# /setup-identity

One-time identity bootstrap. Captures the basics that every plugin needs and writes them to a canonical shared file at `~/Documents/Claude/identity.md`.

After this is done, every plugin's `/setup-*` command reads identity from this file instead of re-asking. You only ever update identity in one place.

---

## Step 1 — Check for existing identity

Read `~/Documents/Claude/identity.md` if it exists.

- **Populated** → ask: "Identity already captured. Update specific sections, or start over?"
  - "Update [section]" → jump there.
  - "Start over" → continue full interview.
- **Missing** → start fresh. Create the directory if needed.

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

Populate `~/Documents/Claude/identity.md` with the answers, using this exact structure (other plugins parse it):

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

Create `~/Documents/Claude/` if it doesn't exist.

---

## Step 4 — Confirm and offer next step

Summarize what was captured (one short paragraph). Then offer:

> "Identity saved. Other plugins (lead-engine, weekly-outreach, plan-tomorrow, etc.) will read this automatically — you won't be asked these questions again. To configure a specific plugin's domain settings (CRM properties, ICP, voice, etc.), run that plugin's setup command (`/lead-setup`, `/setup-outreach`, etc.) — those interviews will skip identity questions and only ask plugin-specific things."

---

## Behavior rules

- One section at a time. Don't bombard.
- Skip what doesn't apply. "I don't have a CRM yet" is valid.
- Idempotent. Re-running updates existing sections.
- Never silently overwrite. If a value would change, confirm with the user.
- The file lives at `~/Documents/Claude/identity.md` — a stable canonical location independent of any specific plugin. Plugins read it but don't own it.

## What this is NOT for

- Plugin-specific configuration (CRM custom properties, ICP, voice rules, offerings catalog) — those go in each plugin's own `references/user-context.md` via that plugin's setup.
- Capturing observations / preferences — that's what cortex's passive observation does, written to `~/Documents/Claude/memory/user.md`.
