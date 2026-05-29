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

## Step 3.6 — Initialize memory-as-git (v4.12.0+)

After the identity file + parent .gitignore are written, offer to initialize `<config-root>/memory/` as a git repository. Versioned memory becomes the substrate for daily diff review (`/morning` Step 0.5) and rollback safety (`git revert HEAD` undoes a day).

Logic:
1. Check whether `<config-root>/memory/` exists. If not, skip (cortex memory hasn't been bootstrapped yet — first `/end-day` will create it; init can happen then).
2. Check whether `<config-root>/memory/.git/` exists. If yes → "Memory-as-git already initialized; skipping init."
3. If memory exists but no git → prompt:
   > "Initialize memory-as-git? This makes `<config-root>/memory/` a local git repo so:
   >   - Each `/end-day` commits the day's memory changes as one reviewable unit
   >   - `/morning` surfaces what changed overnight as a git diff
   >   - You can `git revert HEAD` to roll back a day if something landed wrong
   >   - Optional: push to a private GitHub or self-hosted git for off-machine backup
   >
   > Default: yes, local-only (your memory stays on this machine). Recommended unless you have a reason to skip. (y / n / skip-for-now)"

4. On `y` or default-yes (autonomy: auto):
   ```
   cd <config-root>/memory

   # If .git/ already exists, skip git init but still validate .gitignore (4a below).

   git init -b main
   git config user.name "<identity.name from identity.md>"
   git config user.email "<identity.email from identity.md or fallback to local@brightwayai>"
   ```
   Then proceed to Step 4a.

4a. **Write or validate `memory/.gitignore` (v4.12.1+ bug-aware logic):**

   The v4.12.0 template emitted inline comments which `.gitignore` parses as literal filenames. This bug-fix logic detects and repairs.

   ```
   target_path = <config-root>/memory/.gitignore
   reference_template = read content from `cortex/references/memory-gitignore-template.md` Template section

   If target_path does NOT exist:
     Write reference_template to target_path. (Fresh install — no bug to fix.)

   If target_path exists:
     Read its content.
     Detect inline-comment bug: scan each non-empty line; if any line matches the pattern `^[^#]\S+\s+#` (a non-# starting character followed by whitespace and #), the bug is present.
     If bug present:
       Rewrite target_path from reference_template.
       Run: git rm --cached hot.md index.md log.md .state.json .person-mention-counts.json .person-recall-counter.json 2>/dev/null
       (silently ignore errors for files not currently tracked)
       Surface to user: "Detected v4.12.0 .gitignore bug (inline comments). Rewrote memory/.gitignore from corrected template and un-tracked cache files. Subsequent commits will exclude them properly."
     Else:
       Leave target_path alone (idempotent — user may have customized).
   ```

5. **Initial commit (only if `.git/` was freshly created in step 4):**
   ```
   git add .
   git commit -m "Initial memory snapshot (cortex v4.12.1 /setup-identity init)"
   ```
   Surface: "Memory-as-git initialized. Local repo at `<config-root>/memory/.git/`. Daily commits via `/end-day` Step 5.8; diff review via `/morning` Step 0.5."

5a. On `n` or `skip-for-now`:
   Surface: "Skipped. Re-run `/setup-identity` later, or set `memory_as_git.enabled: true` in `<config-root>/plugins/cortex.user-context.md` and run `/end-day` to init."

6. **Optional remote configuration** (only if user said `y` AND autonomy is not `auto`):
   > "Configure a remote for off-machine backup? (private GitHub recommended for moderate privacy; self-hosted gitea/forgejo/gitlab for higher control; press Enter to skip and stay local-only)"

   If user provides a URL:
   - Write `memory_as_git.remote: <url>` to `<config-root>/plugins/cortex.user-context.md`
   - Write `memory_as_git.push_on_close: true` to same
   - Surface: "Remote configured. `/end-day` Step 5.8 will push after each commit."
   - DO NOT run an initial push here — let the user manually `git remote add origin <url> && git push -u origin main` after verifying the remote URL.

**Idempotent:** safe to re-run. Existing `.git/` is preserved.

---

## Step 3.7 — Wire identity into user.md graph (v4.12.0+)

After identity.md is written, ensure `<config-root>/memory/user.md` has a wikilink to `[[identity]]` in its Canonical Files section. Without this link, identity.md is an orphan in the Obsidian graph view.

Logic:
1. Check whether `<config-root>/memory/user.md` exists. If not, skip — cortex's first `/remember` will create it with proper canonical-file references.
2. Read `<config-root>/memory/user.md`.
3. Check whether `[[identity]]` is already present anywhere in the file. If yes, skip (idempotent).
4. Look for a `## Canonical Files` section header in user.md.
   - **If found**: append `- [[identity]] — user profile (name, company, tools, working hours)` as a bullet under it.
   - **If not found**: insert a new section right before the first existing `##` heading:
     ```
     ## Canonical Files
     - [[identity]] — user profile (name, company, tools, working hours)
     ```
5. Write user.md back.

Symmetric note: `/setup-voice` Step 3.7 does the same for `[[voice]]`. Both are idempotent. The end state: `user.md` Canonical Files section links to every root-level canonical file so Obsidian's graph view shows the connections.

**Why this matters:** voice.md and identity.md are the most-referenced canonical files in the vault but they live at `<config-root>/` root, NOT inside `memory/`. `/relink-memory` scans only `memory/` so it can never auto-fix this. The setup commands are the only place where the link can be reliably written.

No user gate. Best-effort — if user.md doesn't exist or the write fails, log and continue.

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
