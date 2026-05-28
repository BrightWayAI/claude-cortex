---
name: sync-linked-entities
description: Natural-language entrypoint for cross-artifact drift detection. Fires when the user has just made a meaningful change to a node (status flip, reframe, engagement wound down) and says "check the linked nodes," "sync linked artifacts," "make sure the related stuff is consistent," or similar. Resolves the source node from recent edit or context, then routes to /sync-linked-entities.
---

# Skill — sync linked entities

This skill activates on phrases like:

- "check the linked nodes for drift"
- "make sure the related stuff is consistent"
- "sync linked artifacts"
- "propagate this change to linked entities"
- "any drift in the network after that change?"
- "check if other nodes need updates"

## Behavior

1. Resolve the source node:
   - If the user named a specific node in the same conversation turn → use that
   - If memory-as-git is enabled → check most recently committed or currently-uncommitted modified node
   - Otherwise → ask "Which node should I scan linked entities for?"
2. Invoke `/sync-linked-entities <source-node>`
3. Walk findings with the user per the command spec

Respect the autonomy slider — in `auto` mode, skip resolution prompts when unambiguous.

## When NOT to fire

- For broad memory cleanup (use `/cleanup` instead)
- For adding new wikilinks to bare-text mentions (use `/relink-memory`)
- For DASHBOARD-side drift (covered by `/cleanup` Section L in v4.12.0+)
- For migrating staged substrates (use `/migrate-staged-substrates`)

## Routing for nucleus-router

| Utterance | Routes to |
|---|---|
| "check linked nodes" | `/sync-linked-entities` |
| "sync linked artifacts" | `/sync-linked-entities` |
| "any drift in the network" | `/sync-linked-entities` |
| "propagate this change" | `/sync-linked-entities` |
