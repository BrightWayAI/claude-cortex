---
description: Capture your writing voice once (descriptors, banned phrases, sentence-length preference, hook patterns, sign-off style) in one canonical file at ~/Documents/Claude/voice.md. All drafting plugins (bizdev-outreach, weekly-outreach, lead-engine, news-curator) read from this file so your voice stays consistent and you only update it in one place. Re-run anytime to refine.
---

# /setup-voice

One-time voice bootstrap. Captures the writing-voice rules every drafting plugin needs and writes them to a canonical shared file at `~/Documents/Claude/voice.md`.

After this is done, every drafting plugin (bizdev-outreach for outreach, weekly-outreach for weekly BD, lead-engine for DMs, news-curator's post-assembler for LinkedIn posts) reads voice from this file. You update voice in one place, every drafter benefits.

---

## Step 1 — Check for existing voice config

Read `~/Documents/Claude/voice.md` if it exists.

- **Populated** → ask: "Voice already captured. Update specific sections, or start over?"
  - "Update [section]" → jump there.
  - "Start over" → continue full interview.
- **Missing** → start fresh.

---

## Step 2 — The interview

One section at a time. Confirm before moving on. This interview takes 5–7 minutes if you have your bearings.

### Section 1 — Voice descriptors

- **Three words** that describe how you want your writing to sound. Examples: "warm, direct, low-jargon" / "contrarian, sharp, plainspoken" / "calm, specific, generous." If you can only think of two, that's fine. Don't pick more than four — descriptors lose meaning past four.
- **One word you're consciously NOT** — what's the trap you're trying to avoid? (e.g., "salesy," "academic," "preachy.")

### Section 2 — Banned phrases

The marketplace ships with a default banned list (see below). Adopt it as your starting point, then add/remove.

**Default banned list:**
- "just checking in"
- "circling back"
- "touching base"
- "I hope this email finds you well"
- "per my last email"
- "at your earliest convenience"
- "synergy" / "leverage" (verb) / "align" / "delight" / "move the needle"
- "to whom it may concern"
- "would love to pick your brain"
- "let me know if you have any questions"

Ask:
- Any of these you actually like and want to keep? (Strike them from your list.)
- Any phrases beyond this list that you ban for yourself? (Add them.)

### Section 3 — Sentence length and rhythm

- **Length preference** — short and punchy / mixed / longer-form?
- **Paragraphs** — do you prefer single-line paragraphs (LinkedIn-style) or denser prose paragraphs?
- **Em-dashes, colons, parentheticals** — do you use them often, occasionally, or avoid them?

### Section 4 — Hook patterns

For posts and outbound openers, what hook style lands for you?

- **Contrarian** — challenge a common assumption with evidence
- **Observation** — name a pattern most people haven't connected
- **Prediction** — extrapolate where things point
- **Question** — pose a real question, then answer it
- **Story** — short anecdote that earns the point

Pick your top 1–2 patterns. Note any you actively want to AVOID (often "story" doesn't fit B2B operators; "contrarian" can feel exhausting if overused).

### Section 5 — Sign-off, signature, CTAs

- **How do you typically sign emails?** ("— [name]" / "Best, [name]" / no sign-off / etc.)
- **CTA style** — what do you reach for at the end of an outbound message? (e.g., "worth a 15-minute call?" / "want me to send the teardown?" / "open to a quick thread?")
- **Hashtags** — for LinkedIn posts: preferred set (or "no hashtags") and max count

### Section 6 — Voice exemplars (optional but powerful)

If you have 1–3 short writing samples you'd point to as "this is exactly the voice I want to hit," paste them or link them. The drafters read these to calibrate.

If you don't have exemplars handy, skip this section. You can add them later by editing `~/Documents/Claude/voice.md` directly.

---

## Step 3 — Write the voice file

Populate `~/Documents/Claude/voice.md` using this exact structure (every drafter parses it):

```markdown
# Writing Voice

_Last updated: [today]_
_Created by /setup-voice (cortex plugin)_

## Voice descriptors
- **Three words:** ...
- **NOT this:** ...

## Banned phrases
- [bullet list — copy from defaults, then add/remove per the interview]

## Sentence length and rhythm
- **Length:** [short / mixed / longer]
- **Paragraphs:** [single-line / dense]
- **Em-dashes / colons / parentheticals:** [often / occasionally / avoid]

## Hook patterns
- **Preferred:** [1–2 styles]
- **Avoid:** [any styles to skip]

## Sign-off and CTAs
- **Sign-off:** ...
- **CTA style:** ...
- **Hashtags:** [preferred set, or "no hashtags"]

## Exemplars
[paste or link 1–3 voice exemplars here, or "none yet"]
```

---

## Step 4 — Confirm and offer next step

Summarize what was saved (one short paragraph). Then offer:

> "Voice saved. All drafting plugins (bizdev-outreach, weekly-outreach, lead-engine, news-curator/post-assembler) will read this automatically — your voice stays consistent across every channel. Update anytime by re-running `/setup-voice` or editing `~/Documents/Claude/voice.md` directly."

---

## Behavior rules

- One section at a time. Don't bombard.
- The interview should feel like talking to an editor who's about to ghostwrite for you. Not a form.
- Idempotent. Re-running updates existing sections.
- The file lives at `~/Documents/Claude/voice.md` — a stable canonical location independent of any specific plugin.

## What this is NOT for

- Plugin-specific voice rules (e.g., "lead-engine DMs follow the 27-word opener pattern") — those stay in plugin-specific reference files. The shared voice.md is for global-to-you rules.
- Tonal customization per audience or per channel — that's drafting-time logic. The shared voice.md captures *your default voice*; specific situations adjust.
