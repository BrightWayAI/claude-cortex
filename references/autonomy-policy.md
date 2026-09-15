# Nucleus autonomy policy

`policy_version: 1.0.0`

This is the versioned default copied into a new memory instruction file. Users may
customize it; the normalized policy hash, not the version label alone, controls
re-acknowledgment.

## Always

- Read the minimum relevant Cortex context before Nucleus work.
- In unattended runs, stage cited proposals instead of editing durable memory.
- Cite file paths, thread IDs, or record IDs for proposed facts.
- Log metadata-only agent/scheduled-run outcomes.

## Ask first

- Send an email, DM, or Slack message.
- Create or change CRM deals, stages, or other external records.
- Delete or archive a memory node.
- Register, change, replace, or remove a scheduled task.
- Spend metered enrichment/research credits.
- Write outside the resolved config root unless the user's current request already
  names and authorizes that destination.

## Never

- Send on the user's behalf without explicit per-message approval.
- Write durable shared memory from an unattended run; staged proposals only.
- Store secrets, payment-card data, government IDs, or raw connector payloads in
  memory or run receipts.
- Silently overwrite a fact; supersede it with dated provenance.
- Treat a cached scheduler ID, connector configuration, or generated artifact as
  proof that an external action succeeded.
