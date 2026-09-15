# Shared-memory write contract

This contract is dormant for a single writer and becomes mandatory before a second
person or autonomous host writes to the same shared memory remote.

## Goals

- Preserve the existing simple Markdown node model.
- Keep `memory/me/`, raw archives, and private staged drafts local to each actor.
- Make shared writes attributable, reviewable, idempotent, and conflict-safe.
- Retain one deterministic merge point instead of allowing concurrent model edits.

## Actor identity and provenance

`<config-root>/memory/me/identity.md` contains a stable `Actor ID`. Use a short,
kebab-case value that does not change with a job title or device. Every new durable
knowledge entry adds `[by:<actor-id>]` after its timestamps. Changelog entries use
`by:<actor-id>` in their provenance suffix. Existing entries without authorship remain
valid as `legacy-unknown`.

## Proposal intake

Each actor converts private/raw evidence into a sanitized proposal and writes it
append-only at:

`memory/proposals/<actor-id>/<YYYY-MM-DD>/<proposal-id>.md`

```markdown
---
schema_version: 1.0.0
proposal_id: <uuid>
actor_id: <stable actor id>
created_at: <ISO-8601>
base_revision: <git commit SHA or null>
target_node: client/acme
operation: append-knowledge | append-changelog | replace-summary | update-thread
status: proposed
---

## Sources
- <path/thread/record ID plus bounded locator>

## Proposed change
<distilled content only; no raw connector payload>

## Rationale
<why this belongs and what it may conflict with>
```

Proposal files are immutable. Review state is appended to a sibling
`<proposal-id>.decision.jsonl`, never written back into the proposal frontmatter.
Each decision event includes timestamp, reviewer actor ID, action
(`accepted|rejected|conflict|superseded`), resulting revision when accepted, and a
short reason.

## Merge authority

Exactly one merge workflow writes shared nodes at a time:

1. Verify proposal schema, actor ID, sources, and target path.
2. Compare `base_revision` with the current memory revision.
3. Re-read the target and detect semantic or line-level conflicts.
4. Present accept/reject/edit when a human review is required.
5. Acquire the shared Cortex lock.
6. Apply the accepted operation through `cortex_cli.py`/shared libraries atomically.
7. Add `[by:<actor-id>]`, append the decision event, commit, then release the lock.

If the base revision moved but the target section is unchanged, the merge may rebase
automatically and records that fact. If the same fact, decision, summary, or thread
changed, mark `conflict`; never use last-writer-wins. Superseded knowledge follows the
normal dated supersession convention.

## Privacy boundary

Shared proposals may contain distilled business facts and citations. They must not
contain transcript bodies, email/Slack message bodies, secrets, government IDs,
private reflections, voice samples, or content copied from `memory/me/`. Keep raw
material in the actor's private archive/staged scope and cite it by opaque locator.

The shared memory remote must remain private. `.gitignore` excludes `me/`, `staged/`,
raw archive material, caches, and local registration state.

## Transition before teammate two

Before enabling a second writer:

1. Give each person a unique Actor ID and private config root/private `me/` scope.
2. Put only the shareable memory repository on a private shared remote.
3. Enable proposal intake; disable direct model writes to shared nodes for all actors.
4. Designate one merge workflow and test simultaneous proposals against fixtures.
5. Verify conflicts, rejection, replay/idempotency, and remote recovery before using
   real client memory.

Do not create `memory/org/` merely for collaboration. The write boundary and private
scope provide the isolation; preserving existing node paths avoids a marketplace-wide
breaking migration.
