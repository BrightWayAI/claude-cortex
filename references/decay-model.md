# Decay model (v4.4+)

How cortex's forgetting layer decides when knowledge entries and person pages have aged into staleness, dormancy, or coldness — and what happens next.

The model is read-time and event-time:

- **Read-time decay** — `/recall` checks the `[confirmed:...]` tag on every entry it surfaces; entries past the staleness threshold render with a `[stale-confidence]` flag and offer recall-time actions (re-confirm / demote / archive).
- **Event-time decay** — `/cleanup` and `/rehearse` run audits that surface aging entries proactively, without waiting for a recall.

Decay never modifies entry content. It changes the entry's **status** (active / stale / demoted / archived) — content stays legible.

## Lifecycle states

Every knowledge entry has one of four states:

| State | Definition | Where it lives |
|---|---|---|
| **Fresh** | confirmed within `<threshold_fresh>` days | normal section (e.g., `## Knowledge → ### Insights`) |
| **Stale** | confirmed `<threshold_fresh>` to `<threshold_dormant>` days ago | same section, rendered with `[stale-confidence]` flag in `/recall` |
| **Dormant** | confirmed `<threshold_dormant>` to `<threshold_cold>` days ago | same section, flagged as a `/rehearse` candidate |
| **Demoted** | user-demoted via `/recall` or `/rehearse` action, OR superseded by a contradicting commit | `## Demoted knowledge` section at the bottom of the node file |
| **Archived** | user-archived or auto-archive threshold crossed | `<config-root>/memory/archive/` (existing convention) |

Person pages have parallel states:

| State | Definition |
|---|---|
| **Active** | Last meaningful contact within 90 days, or recall counter incremented within 30 days |
| **Cooling** | 90-180 days since last contact, < 2 recalls in last 90 days |
| **Dormant** | 180-365 days, or no recalls in 180+ days |
| **Archived** | > 365 days since last contact AND no recalls in 180+ days → `/cleanup` proposes archive |

## Default thresholds

Stored at `<config-root>/memory/.decay-config.md` (created on first `/end-day` after v4.4 lands; user editable any time):

```yaml
# Knowledge entries — days since [confirmed:...]
threshold_fresh: 60
threshold_dormant: 180
threshold_cold: 365

# Per-entry-type modifiers (multiplier on the thresholds above)
# CORRECTION never decays automatically (it's an event, not a fact)
type_modifiers:
  INSIGHT: 1.0
  LESSON: 1.0
  MODEL: 1.0
  GOTCHA: 1.5      # Gotchas stay relevant longer
  RECIPE: 1.5      # Reusable techniques don't go stale fast
  DECISION: 1.5    # Decisions stay relevant longer (v4.9+); supersede via concept-drift / explicit revisit-trigger, not age
  CORRECTION: 0    # Never decays (0 means immune)

# Person pages — days since last meaningful contact
person_threshold_cooling: 90
person_threshold_dormant: 180
person_threshold_archive: 365

# Rehearsal cadence
rehearse_batch_size: 5         # How many entries /rehearse surfaces per run
rehearse_min_age_days: 90      # Don't rehearse entries newer than this
```

## Per-node overrides (front-matter)

A node can override its decay profile via YAML front-matter at the top of the file. Useful when a node's content has a faster or slower natural turnover than the global default.

```markdown
---
name: bizdev
type: domain
decay_profile: fast
---

# bizdev
...
```

`decay_profile` values:
- `fast` — multiply all thresholds by `0.5` (e.g., a 60-day threshold becomes 30)
- `normal` — global default (no override)
- `slow` — multiply all thresholds by `2.0`
- numeric (e.g., `1.5`) — exact multiplier

Per-node override stacks with per-type modifier multiplicatively. Example:
- `INSIGHT` on a `decay_profile: fast` node: `threshold_fresh = 60 × 1.0 (INSIGHT) × 0.5 (fast) = 30 days`
- `GOTCHA` on a `decay_profile: slow` node: `threshold_fresh = 60 × 1.5 (GOTCHA) × 2.0 (slow) = 180 days`

## How `/recall` uses this model

When `/recall` renders any knowledge entry (project view, person view, topic view, or auto-recall):

1. Read the entry's `[confirmed:YYYY-MM-DD]` tag (default to original commit date if absent)
2. Compute age in days
3. Look up the effective threshold for this entry's type + this node's `decay_profile`
4. Set state:
   - age < `threshold_fresh` → Fresh
   - `threshold_fresh` ≤ age < `threshold_dormant` → Stale
   - `threshold_dormant` ≤ age < `threshold_cold` → Dormant
   - age ≥ `threshold_cold` → Cold (still shown but with strong flag)
5. Render the entry with state flag inline. After listing surfaced entries, offer recall-time actions if any were Stale / Dormant / Cold:

   > "[N] entries flagged as aging. Want to triage now?
   >  (r)e-confirm — mark them current
   >  (d)emote — move to Demoted knowledge section
   >  (a)rchive — move to archive/
   >  (s)kip — leave as-is, will resurface next recall or rehearsal"

6. Per chosen action, edit the affected entries in place. Re-confirm updates `[confirmed:<today>]`. Demote moves the entry to the node's `## Demoted knowledge` section. Archive moves the entry's whole node to `archive/` (entry-level archive is `## Demoted knowledge`; node-level archive is the `/forget` flow).

## How `/remember` uses this model — concept-drift detection

When `/remember` writes a new INSIGHT, MODEL, GOTCHA, LESSON, or DECISION to a node:

1. After classification (Step 0 cheap-tier triage) decides the affected node, but BEFORE writing the new entry, scan the node's existing entries of the same type.
2. Send (new entry, existing entries of same type, last 60 days) to a Haiku-tier classifier:
   > "Does this new entry contradict, supersede, or meaningfully refine any of the existing entries? Output exactly: `{supersedes: [<entry-id>], reason: '...'}` or `{supersedes: null}`."
3. If `supersedes` is non-null → propose to the user:
   > "New entry: '...'.
   >  This appears to supersede: '<existing entry>'.
   >  (a)ccept supersede — move old to Demoted knowledge, write new in its place
   >  (k)eep both — write new entry alongside; old stays active
   >  (e)dit relationship — let user describe the relationship inline
   >  (s)kip new entry"
4. CORRECTION-type entries already do this manually via the existing `[old belief] → [corrected understanding]` shape. Concept-drift detection generalizes the pattern to INSIGHT/MODEL/GOTCHA/LESSON without requiring the user to flag the relationship manually.

Skip the drift check on the first commit to a brand-new node (no existing entries to contradict).

## How `/cleanup` uses this model

`/cleanup` adds two sections (Phase 6 already added orphan detection and person-page maintenance; v4.4 deepens them):

- **Dormant knowledge entries** — list all entries past `threshold_dormant` for their type+node profile, grouped by node. Per-entry suggestion: rehearse / demote / archive.
- **Dormant person pages** — list person pages where age past `person_threshold_dormant` AND no recalls in 180+ days. Suggest archive. On accept, move file from `memory/person/<slug>.md` to `memory/person/archive/<slug>.md`. `/recall person:<slug>` continues to find archived pages but flags them; bringing back to active is a one-line confirmation.

## How `/rehearse` uses this model

New command in v4.4. Surfaces a small batch of aging entries (default 5) and asks per entry:

> "Still true? Still useful?"

User actions per entry:
- **Yes** → updates `[confirmed:<today>]`, entry returns to Fresh
- **Update** → user edits inline, then re-confirms
- **Demote** → moves to `## Demoted knowledge` section of the node
- **Archive** → moves to `archive/`
- **Skip** → leaves as-is; entry will re-surface in a later rehearsal

Rehearsal is the active retention loop — the hippocampus-style consolidation pass that converts dormancy into either re-confirmation or removal.

Default cadence: weekly via `/end-week` (which now invokes `/rehearse` as part of its chain). Can also be run on demand via `/rehearse`.

Selection algorithm:
1. Pull all entries past `threshold_fresh` for their type+node profile
2. Filter to entries older than `rehearse_min_age_days` (default 90 — don't rehearse what's barely past Fresh)
3. Weight by age × type-importance (CORRECTIONs never appear; GOTCHAs and RECIPEs weighted slightly higher because their decay matters more to operational quality)
4. Pick `rehearse_batch_size` (default 5) — diverse across nodes when possible (don't make all 5 from one node)

## Why this design

- **Read-time + event-time symmetry.** Forgetting happens both passively (when entries get recalled and flagged) and actively (via cleanup + rehearse). Mirrors how memory works biologically — encountering an idea reinforces it; periodic review consolidates the network.
- **State, not deletion.** Content is never automatically deleted. Demoted entries stay readable; archived ones move to a separate folder but stay searchable. The user can always recover.
- **Per-type modifiers reflect real value-decay rates.** A GOTCHA from 2 years ago can still be true. An INSIGHT from 2 years ago is more likely to be stale. The 1.5x modifier on GOTCHA/RECIPE captures that intuition.
- **Per-node overrides.** Different domains decay at different rates. Marketing intelligence ages fast; engineering recipes age slow. The `decay_profile` knob lets the user tune per area.
- **User-in-the-loop on demotion / supersede.** Concept-drift detection proposes, never overrides. The cost is one extra prompt during /remember; the benefit is the system never silently flips a held belief.
