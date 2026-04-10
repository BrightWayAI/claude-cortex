# Per-Project Configuration

Session Memory supports per-project configuration via a `.session-memory.json` file placed in the project root. This lets you control capture behavior, auto-recall, and knowledge priorities on a per-project basis.

---

## File Location

Place `.session-memory.json` in your project root (same level as `package.json`, `.git`, etc.):

```
my-project/
├── .session-memory.json    ← here
├── .git/
├── src/
└── ...
```

For Cowork: this file is read when the project directory is mounted.
For Claude Code: this file is read automatically from the working directory.

---

## Schema

```json
{
  "node": "client:acme-corp",
  "capture": "aggressive",
  "auto_recall": true,
  "auto_commit": true,
  "observe": true,
  "knowledge_types": ["model", "gotcha", "lesson", "recipe"],
  "memory_path": "~/Documents/Claude/memory",
  "ignore_patterns": ["*.test.*", "node_modules/**"]
}
```

## Fields

### `node` (string, optional)
Default project node ID for this directory. If not set, session-memory will auto-detect based on conversation context or directory name.

Examples: `"client:acme-corp"`, `"infra:data-pipeline"`, `"strategy:q2-growth"`

### `capture` (string, optional)
Controls how aggressively session-memory captures knowledge. Default: `"normal"`.

| Value | Behavior |
|-------|----------|
| `"aggressive"` | Capture everything — every decision, every observation, every domain fact mentioned in passing. Use for high-value client work, critical projects, or early-stage exploration where context is expensive to rebuild. |
| `"normal"` | Standard capture — decisions, significant knowledge, corrections, and observations. The default for most projects. |
| `"minimal"` | Only capture when explicitly triggered via commands (`/remember`, `/learn`, `/note`). Auto-commit and passive observation are disabled. Use for low-stakes scratch work or sensitive projects. |

### `auto_recall` (boolean, optional)
Whether to automatically load this project's context at conversation start. Default: `true`.

Set to `false` if you don't want the overhead of auto-recall for quick, unrelated conversations in this directory.

### `auto_commit` (boolean, optional)
Whether to automatically commit memory when the conversation ends. Default: `true`.

Set to `false` to require explicit `/remember` for every commit. Useful for sensitive projects where you want manual control over what's persisted.

### `observe` (boolean, optional)
Whether passive observation (learning about the user) runs in this project context. Default: `true`.

Set to `false` if this is a shared project or pairing context where observations about "the user" would be inaccurate (multiple people using the same project).

### `knowledge_types` (string[], optional)
Which knowledge types to prioritize for this project. Default: all types.

Options: `"insight"`, `"lesson"`, `"model"`, `"gotcha"`, `"recipe"`, `"correction"`

Example: A compliance project might prioritize `["gotcha", "model", "recipe"]` because traps, process knowledge, and playbooks matter most.

### `memory_path` (string, optional)
Override the memory storage location. Default: `"~/Documents/Claude/memory"`.

Use this if you want project-specific memory isolated from your global memory. The full path will be used as-is (no node subdirectories added).

### `ignore_patterns` (string[], optional)
Glob patterns for files/topics to exclude from observation and knowledge capture. Useful for avoiding noise from test files, generated code, etc.

---

## Examples

### High-value client engagement
```json
{
  "node": "client:acme-corp",
  "capture": "aggressive",
  "auto_recall": true,
  "auto_commit": true,
  "observe": true,
  "knowledge_types": ["model", "gotcha", "lesson", "recipe", "correction"]
}
```

### Personal scratch/learning project
```json
{
  "node": "learning:rust-experiments",
  "capture": "minimal",
  "auto_recall": false,
  "auto_commit": false
}
```

### Shared team project
```json
{
  "node": "infra:api-gateway",
  "capture": "normal",
  "auto_recall": true,
  "auto_commit": true,
  "observe": false
}
```

### Sensitive/confidential project
```json
{
  "node": "client:classified-project",
  "capture": "minimal",
  "auto_recall": true,
  "auto_commit": false,
  "memory_path": "~/Documents/Claude/memory-private"
}
```

---

## Platform Support

| Field | Cowork | Claude Code |
|-------|--------|-------------|
| `node` | Supported | Supported |
| `capture` | Supported | Supported |
| `auto_recall` | Supported (via skill auto-fire) | Supported (via INSTRUCTIONS.md) |
| `auto_commit` | Supported (via skill auto-fire) | Supported (via INSTRUCTIONS.md) |
| `observe` | Supported | Supported |
| `knowledge_types` | Supported | Supported |
| `memory_path` | Supported | Supported |
| `ignore_patterns` | Limited (no file watching) | Supported |
