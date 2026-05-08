---
name: setup-voice
description: Capture or update writing voice in one canonical file (~/Documents/Claude/voice.md) so every drafting plugin reads the same rules. Auto-fires on "/setup-voice", "set up my voice", "configure my voice across plugins", "update my writing voice", "my voice is changing", or when a drafting plugin reports the shared voice file is missing.
---

See `commands/setup-voice.md` for the full interview.

## When this skill fires

- User runs `/setup-voice` directly
- User says: "set up my voice", "configure my voice", "update my writing voice", "my voice is changing"
- User installs a drafting plugin and asks "where do I configure voice?"
- A drafting plugin's setup detects `~/Documents/Claude/voice.md` is missing and routes here

## Why this skill exists

Without it, every drafting plugin (bizdev-outreach, weekly-outreach, lead-engine, news-curator's post-assembler) captures voice rules separately. They drift. Adding a banned phrase means editing 4 files.

With it: voice lives in one canonical file. Drafters read it. You update it in one place.

## What's NOT in voice.md

- Plugin-specific voice rules (e.g., "lead-engine DMs follow the 27-word opener pattern") — those stay in each plugin's `references/user-context.md` or rules files.
- Audience-specific tonal adjustments — that's drafting-time logic.

The shared voice.md is the **default voice for everything you ship**. Specific contexts adjust on top.
