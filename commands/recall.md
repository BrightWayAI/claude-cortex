---
description: Surface working memory into the current conversation. Runs automatically at conversation start to load the user profile and surface attention items. Also runs explicitly via /recall [project] to load full context for a specific project, or /recall alone for the full dashboard.
---

# /recall [project?]

You are surfacing working memory to set up the current session.

---

## Mode Detection

This command runs in one of three modes:

### Auto mode (conversation start — no user trigger)
- Silently load the user profile node first (apply preferences to behavior)
- Check for attention items (overdue P0s, stale threads, dormant nodes reviving)
- If the user's first message references a specific project → load that context
- If the user's first message is a greeting → show brief attention summary
- If the user's first message is a direct task → load relevant context silently, weave in
- Keep output SHORT — just what needs attention

### Explicit mode (user says /recall)
- Full dashboard or project recall as specified
- Complete output with all details

### Contextual mode (mid-conversation reference)
- User mentions a project, person, or topic with memory
- Don't dump a recall block — weave relevant knowledge into your response naturally
- Only surface what's relevant to the current discussion

---

## Step 0 — Load hot cache + User Profile (ALWAYS, before anything else)

**Hot cache (v4.7+):** Read `~/Documents/Claude/memory/hot.md` first if it exists. This is the rolling 7-day buffer of recent substrate — last week's reflections, active people, open threads, recent commitments. Apply immediately and silently for context awareness.

If `hot.md` is missing or `hot_cache.enabled: false` in user-context, skip it gracefully and continue with the User Profile load.

**User Profile:** Read `~/Documents/Claude/memory/user.md` if it exists.

Apply immediately and silently:
- Communication preferences → adjust your response style
- Working style → match their pace and patterns
- Corrections → avoid past mistakes
- Tool preferences → use their preferred tools/platforms
- Relationship context → know who's who
- Recent activity from hot.md → don't ask "what have you been working on" when the cache already says

**Do NOT announce this.** Just be the version of Claude they've trained you to be.

**Pending overnight draft check (v4.7+):** If `~/Documents/Claude/memory/staged/commit-drafts/` contains a file dated yesterday or today that hasn't been archived to `staged/commit-drafts/archive/`, a `/listen` run is pending review. At the end of the auto-recall flow (after Step 0 completes silently), surface ONE short line: "Heads up: overnight `/listen` proposals are pending. Run `/morning` when you're ready." Do not enumerate the proposals; just flag.

---

### Finding Memory

Memory is stored in `~/Documents/Claude/memory/`.

**Before reading**: Check if `~/Documents/Claude/memory/` is accessible.
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path="~/Documents/Claude")` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem.

If the directory cannot be accessed, explain that memory cannot be loaded without this folder and stop.

- `/recall` with no arguments: Read `memory/DASHBOARD.md` and present the dashboard view
- `/recall [node]`: Determine file path from node ID, read that file, present the full project view
  - If node has a prefix (e.g., `client:acme-corp`): `memory/{prefix}/{slug}.md`
  - If no prefix (e.g., `hiring`): `memory/{node-id}.md`
- `/recall person:<slug>` (v4.2+): Read `memory/person/<slug>.md`. If it exists, present the full person page (Identity → Relationship → Open threads → Recent interactions → Notes → Linked entities). If it doesn't, fall through to `/recall @<name>` behavior. **Increment the recall counter for this slug** at `memory/.person-recall-counter.json` (see "Person-page graduation counter" below). When the counter hits 3 for a person who has no page yet, prompt: "I've recalled <name> 3 times. Want to graduate them to a person page?" → if yes, run a one-shot synthesis pass over all node files mentioning them to seed the page.
- `/recall @person`: Read DASHBOARD.md to find which nodes exist, then search node files for PEOPLE entries matching the name. **Also increment the recall counter** as above so casual `@person` recalls still count toward graduation trigger #2.
- `/recall [topic]`: Read DASHBOARD.md to identify which nodes might be relevant, then search those node files for matching knowledge entries

If the memory directory doesn't exist or is empty, tell the user and offer to help set it up.

---

## If a project was specified (e.g. `/recall client:acme`, `/recall strategy:q2-growth`)

1. Read the node file from the memory directory
2. Pull: SUMMARY, recent LOGs, all knowledge entries (INSIGHT/LESSON/MODEL/GOTCHA/RECIPE/CORRECTION), PEOPLE, SIGNALs

3. Compute staleness:
   - **Active**: within 7 days
   - **Warm**: 8-14 days
   - **Cooling**: 15-30 days
   - **Dormant**: 30+ days

4. Present:

```
## [Project Node] — [today's date] [staleness badge]

**Current State**
[living summary]

**What We Know**
[Knowledge entries grouped by type. Show up to 5 most recent, note "N more" if needed.]

Models:
- [MODEL entry]

Gotchas:
- [GOTCHA entry]

Lessons:
- [LESSON entry]

Recipes:
- [RECIPE entry]

Corrections:
- [CORRECTION entry]

Insights:
- [INSIGHT entry]

**Blockers**
[active blockers, or "None"]

**Open Threads** ([count])
- [FRESH/ONGOING/STALE] [thread]

**Next Actions**
- [P0] [action] ← HIGHLIGHT
- [P1] [action]
- [P2] [action]
- [WAITING:who] [action]

**Unanswered Questions**
[from prior sessions, or "None"]

**Key People**
- [Name] ([role]) — [context]

**Recent Sessions**
- [date] [title]: [1-line summary]
- [date] [title]: [1-line summary]
- [date] [title]: [1-line summary]

**Signals from other projects**
[cross-project flags, or "None"]
```

5. Flag [STALE] threads with a warning.
6. End with: **"What are we working on today?"**

---

## If no project specified (just `/recall`)

Full working world dashboard. Sort by recency.

```
## Working World — [today's date]

### Active (within 7 days)

**[node-id]** [badge]
[summary — 1-2 sentences]
Knowledge: [count] entries
Open threads: [count]
Next up: [top action]

...

### Warm / Cooling / Dormant
[same format, less detail]

---

### Needs Attention
[STALE threads, overdue P0s, unresolved blockers]

### Recent Learning
[3-5 most recently committed INSIGHT/LESSON/GOTCHA entries across ALL nodes]

### Cross-Project Signals
[Recent SIGNALs]

### People Across Projects
[Anyone in 2+ nodes]
```

End with: **"Which project are we picking up today?"**

---

## If a person page was specified (`/recall person:sarah-chen`) — v4.2+

1. Read `memory/person/<slug>.md` if it exists.
2. If it exists, present:

```
## [Name] — person page

> Last updated: [date] · Temperature: [Cold|Warm|Active|Dormant]

**Identity** — [title], [company link]. [email]
**How we know each other** — [relationship line]

**Open threads**
- [WAITING:them] — [thread]
- [WAITING:you] — [thread]
- [P0] — [thread]

**Recent interactions (last 90 days)**
- [date] — [type] — [summary]
- ... (top 5)

**Linked projects** — [client/...], [bizdev/...]

**Notes**
[free-form]
```

3. If the page doesn't exist, fall through to the legacy `@person` cross-project profile below. Then surface the recall-counter check: "No person page for <slug> yet. After 3 recalls I'll offer to graduate them." (Show counter status if available.)

4. **Increment the recall counter** at `memory/.person-recall-counter.json`:

   ```json
   {
     "sarah-chen": { "count": 4, "last_recalled_at": "2026-05-12T14:23:00Z" },
     "tom-reyes": { "count": 2, "last_recalled_at": "2026-05-10T09:11:00Z" }
   }
   ```

   - Read the file (create if missing). Look up the slug. If absent, initialize `{count: 1, last_recalled_at: now}`. Otherwise increment count, update timestamp.
   - **If count crosses 3 AND no page exists yet** → after rendering the legacy profile, ask: "I've recalled <name> 3 times now. Want to graduate them to a person page? I'll synthesize a starting page from existing mentions across nodes." If yes, scan all project node files for PEOPLE entries matching the name, synthesize an initial page following the schema in cortex's CLAUDE.md, write to `memory/person/<slug>.md`, add an "Active people" entry to DASHBOARD.md, and reset the counter for this slug to `count: 0` (since the page now exists).
   - **If a page already exists** → still increment the counter (useful telemetry for `/cleanup` to identify cold pages later) but don't prompt.

---

## If a person was specified (`/recall @kim`) — legacy cross-project profile

```
## [Name] — Cross-Project Profile

**Projects:** [node-id]: [role]. [node-id]: [role].

**Recent mentions:** [date] in [node]: [context]

**Open items involving them:** [WAITING:them] [description]
```

Apply the same recall-counter increment described in the person-page section above. If the counter crosses 3 for a person with no page yet, offer to graduate.

---

## Person-page graduation counter (v4.2+)

`memory/.person-recall-counter.json` is a small JSON map keyed by slug. Cortex maintains it as part of any recall that names a person (`person:slug` or `@name` form). The file is private to cortex; other plugins should treat it as opaque.

When the counter for a slug crosses 3 and `memory/person/<slug>.md` does not yet exist, the next `/recall` for that person surfaces the graduation prompt. Other graduation triggers (dossier from contact-researcher, project-setup primary contact, etc.) bypass the counter and create the page directly.

---

## If a topic/keyword was specified (`/recall pricing`, `/recall onboarding`)

Search all knowledge entries + LOGs for the topic.

```
## What we know about: [topic]

**Mental Models**
[MODEL entries]

**Lessons & Insights**
[LESSON/INSIGHT entries]

**Gotchas**
[GOTCHA entries]

**Recipes**
[RECIPE entries]

**Corrections**
[CORRECTION entries]

**Appears in:** [nodes where this comes up]
```

End with: **"Want to dive deeper or add to what we know?"**

### Duplicate-topic surfacing (v4.2+)

Before rendering the topic answer above, run a one-pass Haiku-tier semantic check to catch the user re-discovering ideas they already wrote about:

1. Read DASHBOARD.md's Active Nodes section (just the node-id + 1-line summary per row).
2. Send the query + the dashboard summaries to a Haiku-tier classifier with this prompt:

   > Given the query `<query>` and these node summaries: `<list>`, return the single closest semantic match if any node summary is plausibly about the same topic. Otherwise return `null`. Output exactly `{"match": "<node-id>"}` or `{"match": null}` — no other text.

3. If `match` is non-null AND the matched node is NOT one the recall just rendered:

   > Surface a heads-up BEFORE the main topic answer:
   >
   > "Note: `<matched-node>` may already cover this. Want to read that first?"
   >
   > Then continue rendering the regular topic answer below the note.

4. If `match` is null, render the topic answer normally. No note.

Cost: one Haiku call per topic recall (~$0.01). Trade-off: catches "I forgot I already wrote about this" cases ~80% of the time, in exchange for one cheap classification call per topic query.

---

## If auto-recall at conversation start (greeting or general opening)

Read `DASHBOARD.md` and scan for attention items. Present a BRIEF summary:

```
Welcome back. Here's what needs attention:

**Overdue**
- [P0 action] in [node] — was due [date]

**Stale**
- [thread] in [node] — no progress in [count] sessions

**Recent**
- Last worked on [node] ([date]): [1-line summary]

What are we working on?
```

Rules for auto-recall output:
- **Maximum 8 lines.** This is a glance, not a report.
- If nothing needs attention: "All clear — what are we working on?"
- Only show overdue P0s (not P1/P2), stale threads (3+ sessions), and the 1-2 most recent sessions
- If the user profile has relationship context relevant to today (e.g., a known meeting cadence), weave it in
- Never show the full dashboard in auto mode — that's what explicit `/recall` is for

---

## If contextual recall (mid-conversation mention)

When the user mentions a project, person, or topic with memory:

1. Read the relevant node file
2. Identify the 1-3 most relevant knowledge entries for the current context
3. Weave them into your response naturally — don't format as a recall block
4. Example: User says "I need to follow up with Acme" → you know from memory their
   procurement needs 3 quotes → say "Heads up — Acme's procurement requires 3 vendor
   quotes even for renewals, so factor in 2 weeks lead time."
5. Only surface what's RELEVANT. Having memory doesn't mean dumping memory.

---

## Behavior notes

- No entries → say so, ask if they want to start building context
- Sparse memory → surface what exists, note it'll improve with each session
- Don't editorialize — surface committed data accurately
- Human-readable dates ("March 4")
- Knowledge entries are high-signal — show them prominently, not buried
- Stale threads or overdue P0s → flag proactively
- User profile → apply silently, never announce
- Auto-recall → be brief, be useful, get out of the way

## `[recalled:...]` tag updates (v4.3+)

When `/recall` (any mode) renders a knowledge entry from a node file, update that entry's `[recalled:YYYY-MM-DD]` tag to today's local date before exiting. This is the substrate for v4.4's decay layer — entries that get recalled stay fresh; entries that don't get recalled drift toward demotion.

Rules:
- Only the `[recalled:...]` tag changes. The `[confirmed:...]` tag stays put — confirmation is a stronger signal that requires an explicit re-affirmation event.
- Auto-recall and Contextual recall update tags only on entries actually rendered to the user, not on every entry read internally for context. The threshold is "did the user see this?"
- If an entry pre-dates v4.3 and has no tags, add both `[confirmed:<original-date>] [recalled:<today>]` — backfill the substrate as you touch entries.
- Updates are append-style edits to the existing node file. No new file writes. Idempotent.

This work happens silently. Don't announce tag updates to the user.

## Decay-aware rendering (v4.4+)

`/recall` now classifies every knowledge entry it renders into one of four states based on the age of `[confirmed:...]` and the effective threshold for the entry's type and the node's `decay_profile`. See `references/decay-model.md` for the full model.

### Loading thresholds

Before rendering, read `<config-root>/memory/.decay-config.md` (create with documented defaults if missing). Extract:

- `threshold_fresh`, `threshold_dormant`, `threshold_cold` (in days)
- `type_modifiers` (per-entry-type multipliers — `CORRECTION: 0` means immune to decay)

For each node being rendered, check its front-matter for `decay_profile:` (values: `fast` = 0.5, `normal` = 1.0, `slow` = 2.0, or numeric). The effective threshold for an entry is:

```
effective_threshold = base_threshold × type_modifier × decay_profile_multiplier
```

If `type_modifier` is 0 (CORRECTION), the entry is never flagged regardless of age.

### State classification

For each entry, compute `age_days = today - confirmed_date`. State:

| age_days vs. thresholds | State |
|---|---|
| `< threshold_fresh` | Fresh |
| `threshold_fresh ≤ age < threshold_dormant` | Stale |
| `threshold_dormant ≤ age < threshold_cold` | Dormant |
| `age ≥ threshold_cold` | Cold |

Entries in the `## Demoted knowledge` section are skipped from active rendering (rendered separately and de-emphasized — see "Rendering demoted entries" below).

### Render flag inline

Append a state flag at the end of each entry's rendered line (only for Stale / Dormant / Cold — Fresh entries render unflagged):

- Stale → ` [stale-confidence]`
- Dormant → ` [dormant — last confirmed <N> days ago]`
- Cold → ` [cold — last confirmed <N> days ago; consider rehearse or archive]`

The flag is rendering-only — it does NOT get written into the entry text. The entry's underlying line stays unchanged; the flag is decorative on the recall output.

### Recall-time triage offer

After rendering all entries, if any are flagged Stale / Dormant / Cold AND the user invoked `/recall` explicitly (not auto-recall, not contextual), offer:

> "[N] entries flagged as aging:
>  [N_stale] stale · [N_dormant] dormant · [N_cold] cold
>
>  Triage now?
>  (r)e-confirm — mark them all as confirmed today
>  (s)elect — walk one by one, choose per entry
>  (d)emote all dormant + cold — move to Demoted knowledge sections
>  (k)skip — leave as-is; they'll resurface on next recall or rehearsal"

Do NOT offer this in auto-recall mode (the user is greeting you; don't interrupt with a triage prompt). Do NOT offer for contextual recall either (mid-conversation references shouldn't break flow).

### Per-action behavior

- **Re-confirm all** → for each flagged entry, update `[confirmed:<today>]`. Print a one-line confirmation.
- **Select** → walk one entry at a time, prompt per entry:
  > "<entry text>
  >  (c)onfirm / (d)emote / (a)rchive entry / (s)kip / (e)dit then confirm"
  - `confirm` — update `[confirmed:<today>]`
  - `demote` — move entry to the node's `## Demoted knowledge` section (create if missing). Append demotion metadata: `↳ demoted <today> by user-recall-action`. Original tags travel with the entry.
  - `archive entry` — there's no entry-level archive; this is the same as `demote` plus a note that the user asked to remove it. (For node-level archive, point user to `/forget`.)
  - `edit then confirm` — drop into inline edit; on save, update `[confirmed:<today>]`
  - `skip` — leave as-is
- **Demote all dormant + cold** → bulk move every Dormant and Cold entry to `## Demoted knowledge` in its respective node. Stale entries stay active.
- **Skip** → no changes.

### Rendering demoted entries

In project-view and topic-view recall, render the `## Demoted knowledge` section AFTER the active sections, with a header note: "Below: entries previously demoted. Kept for reference; not surfaced as active knowledge." Don't include demoted entries in knowledge-entry summary counts or in "What We Know" highlights.

### Auto-create `.decay-config.md` if missing

On first `/recall` after v4.4 lands, if `<config-root>/memory/.decay-config.md` doesn't exist, create it with the documented defaults from `references/decay-model.md`. Don't prompt the user — defaults are sensible; user can tune later.
