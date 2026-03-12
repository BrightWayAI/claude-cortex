---
name: forget
description: >
  Archive or remove a project node from working memory. Auto-fires when a user
  says "archive [project]", "we're done with [project]", "close out [project]",
  "remove [project] from memory", "merge [project] into [other project]", or
  "this project is finished". Also triggers on "clean up old projects" or
  "I don't need [project] anymore".
---

See commands/forget.md for the full workflow.

When this skill fires automatically:

- Identify which node the user wants to archive/remove

- Default to archive (safe) unless the user explicitly says "delete" or
  "remove completely"

- Always show what will be affected before executing

- Always get explicit confirmation — this is a destructive operation

- After archiving/deleting, clean up cross-references in other nodes

- If the node has open P0/P1 actions, warn before proceeding

- Support merging: if user says "merge X into Y", combine the nodes
