---
name: setup-identity
description: Capture or update user identity in one canonical file (~/Documents/Claude/identity.md) so other plugins don't re-ask name/company/role 9 times. Auto-fires on "/setup-identity", "set up my identity", "set up shared identity", "configure my profile across plugins", "update my identity", or when another plugin's setup reports the shared identity file is missing.
---

See `commands/setup-identity.md` for the full interview.

## When this skill fires

- User runs `/setup-identity` directly
- User says: "set up my identity", "configure my profile across plugins", "update my identity"
- User installs the marketplace and asks "where do I start?" — recommend running `/setup-identity` first as the foundation, then plugin-specific setups
- Another plugin's setup detects `~/Documents/Claude/identity.md` is missing and routes here

## Why this skill exists

Without it, every plugin asks for name/company/role/CRM/calendar separately. That's 9× setup friction and creates drift when something changes (your title, your company name).

With it: identity lives in one canonical file. Plugins read it. You update it in one place.

## What's NOT in identity.md

- Plugin-specific configuration (CRM custom property names, ICP, voice rules, offerings catalog) — those stay in each plugin's `references/user-context.md`.
- Observations / preferences (communication style, corrections, working patterns) — those live in cortex's `~/Documents/Claude/memory/user.md` and are managed by passive observation.

Identity is the *facts that don't change often*. Plugin context is the *plugin-specific configuration*. User profile is the *learned preferences*. Three different things, three different files.
