# Codex custom-agent sources

These TOML files are the tracked source for `.codex/agents/`. They intentionally
omit a model so each role inherits the parent model, and they force read-only
sandboxes so proposal agents cannot bypass Cortex's deterministic write path.

`conversation-miner` is not mapped because Codex has no supported
`connector.session_history.read` implementation for other sessions.
