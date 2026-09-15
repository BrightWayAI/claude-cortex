"""Host-neutral operations exposed by the Cortex MCP adapter.

All reads are bounded and all writes shell out to ``scripts/cortex_cli.py``.
The bridge accepts its home directory and environment explicitly so tests can
never resolve or touch a real user's Cortex data by accident.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.config_root import ConfigRootResult, resolve_config_root  # noqa: E402
from scripts.lib.node_paths import (  # noqa: E402
    PathTraversalError,
    node_id_to_relative_path,
    resolve_node_path,
)
from scripts.configure_cortex import ConfigureError, configure_cortex  # noqa: E402


MAX_READ_CHARS = 40_000
MAX_SEARCH_FILES = 2_000
MAX_SEARCH_FILE_CHARS = 1_000_000
MAX_MUTATION_CHARS = 100_000
DEFAULT_RECALL_FILES = (
    "hot.md",
    "user.md",
    "DASHBOARD.md",
)


class CortexBridgeError(RuntimeError):
    """A safe, user-presentable bridge failure."""


@dataclass(frozen=True)
class CortexBridge:
    """Resolve and operate on exactly one Cortex root per invocation."""

    home: Path
    environ: Mapping[str, str]
    explicit_root: str | None = None
    repo_root: Path = REPO_ROOT

    def resolve(self) -> ConfigRootResult:
        return resolve_config_root(
            home=self.home,
            environ=self.environ,
            explicit=self.explicit_root,
        )

    @property
    def memory_root(self) -> Path:
        return self.resolve().path / "memory"

    def status(self) -> dict[str, object]:
        result = self.resolve()
        memory_root = result.path / "memory"
        count = 0
        if memory_root.is_dir():
            count = sum(1 for path in memory_root.rglob("*.md") if path.is_file())
        return {
            "config_root": str(result.path),
            "resolution_source": result.source,
            "memory_exists": memory_root.is_dir(),
            "markdown_file_count": count,
        }

    def configure(
        self,
        config_root: str,
        *,
        force_pointer: bool = False,
        user_confirmed: bool,
    ) -> dict[str, object]:
        """Set the shared pointer and initialize a minimal local Cortex root."""
        self._require_confirmation(user_confirmed)
        try:
            result = configure_cortex(
                home=self.home,
                config_root=config_root,
                environ=self.environ,
                force_pointer=force_pointer,
                initialize=True,
                repo_root=self.repo_root,
            )
        except ConfigureError as exc:
            raise CortexBridgeError(str(exc)) from exc
        return result.as_dict()

    def recall(self, node: str | None = None, *, max_chars: int = 24_000) -> dict[str, object]:
        limit = max(1, min(max_chars, MAX_READ_CHARS))
        if node:
            relative = self._node_relative(node)
            content = self._read_relative(relative, limit)
            return {
                "node": node,
                "path": relative,
                "content": content,
                "truncated": len(content) >= limit,
            }

        sections: list[str] = []
        paths: list[str] = []
        remaining = limit
        for relative in DEFAULT_RECALL_FILES:
            if remaining <= 0:
                break
            try:
                content = self._read_relative(relative, remaining)
            except CortexBridgeError:
                continue
            section = f"## {relative}\n{content}"
            sections.append(section[:remaining])
            paths.append(relative)
            remaining -= len(sections[-1]) + 2
        return {
            "node": None,
            "paths": paths,
            "content": "\n\n".join(sections),
            "truncated": remaining <= 0,
        }

    def search(self, query: str, *, limit: int = 20) -> dict[str, object]:
        query = query.strip()
        if not query:
            raise CortexBridgeError("query must not be empty")
        result_limit = max(1, min(limit, 50))
        needle = query.casefold()
        hits: list[dict[str, object]] = []
        files_seen = 0
        memory_root = self.memory_root
        if not memory_root.is_dir():
            raise CortexBridgeError(f"Cortex memory directory does not exist: {memory_root}")

        for path in sorted(memory_root.rglob("*.md")):
            if not path.is_file():
                continue
            files_seen += 1
            if files_seen > MAX_SEARCH_FILES:
                break
            relative = path.relative_to(memory_root).as_posix()
            try:
                # Follow and validate symlinks before opening content.
                safe_path = resolve_node_path(memory_root, relative)
                handle = safe_path.open(encoding="utf-8")
            except (OSError, UnicodeError, PathTraversalError):
                continue
            with handle:
                chars_seen = 0
                for line_number, line in enumerate(handle, start=1):
                    remaining_chars = MAX_SEARCH_FILE_CHARS - chars_seen
                    if remaining_chars <= 0:
                        break
                    visible = line[:remaining_chars]
                    chars_seen += len(visible)
                    if needle not in visible.casefold():
                        continue
                    hits.append(
                        {
                            "path": relative,
                            "line": line_number,
                            "snippet": visible.strip()[:500],
                            "citation": f"{relative}:{line_number}",
                        }
                    )
                    if len(hits) >= result_limit:
                        break
            if len(hits) >= result_limit:
                break

        return {
            "query": query,
            "hits": hits,
            "hit_count": len(hits),
            "files_scanned": min(files_seen, MAX_SEARCH_FILES),
            "scan_truncated": files_seen > MAX_SEARCH_FILES,
        }

    def add_note(self, node: str, content: str, *, user_confirmed: bool) -> dict[str, object]:
        self._require_confirmation(user_confirmed)
        clean = content.strip()
        if not clean:
            raise CortexBridgeError("note content must not be empty")
        relative = self._node_relative(node)
        entry = f"[{node.strip()}] LOG {date.today().isoformat()} — Note: {clean}"
        output = self._run_cli("prepend-section", relative, "## Changelog", payload=entry)
        return {"node": node, "path": relative, "entry": entry, "cli_output": output}

    def update_section(
        self,
        node: str,
        heading: str,
        content: str,
        *,
        mode: str,
        user_confirmed: bool,
    ) -> dict[str, object]:
        self._require_confirmation(user_confirmed)
        operation = {
            "append": "append-section",
            "prepend": "prepend-section",
            "replace": "replace-section",
        }.get(mode)
        if operation is None:
            raise CortexBridgeError("mode must be append, prepend, or replace")
        if not heading.startswith("## ") or "\n" in heading:
            raise CortexBridgeError("heading must be one Markdown H2 heading such as '## Summary'")
        relative = self._node_relative(node)
        output = self._run_cli(operation, relative, heading, payload=content)
        return {
            "node": node,
            "path": relative,
            "heading": heading,
            "mode": mode,
            "cli_output": output,
        }

    def reindex(self, *, user_confirmed: bool) -> dict[str, object]:
        self._require_confirmation(user_confirmed)
        return {"cli_output": self._run_cli("reindex")}

    def refresh_hot(self, *, trigger: str = "manual", user_confirmed: bool) -> dict[str, object]:
        self._require_confirmation(user_confirmed)
        clean_trigger = trigger.strip() or "manual"
        if len(clean_trigger) > 80 or any(ch in clean_trigger for ch in "\r\n"):
            raise CortexBridgeError("trigger must be a short single-line label")
        return {"cli_output": self._run_cli("refresh-hot", "--trigger", clean_trigger)}

    def _read_relative(self, relative: str, limit: int) -> str:
        target = resolve_node_path(self.memory_root, relative)
        if not target.is_file():
            raise CortexBridgeError(f"Cortex node does not exist: {relative}")
        try:
            with target.open(encoding="utf-8") as handle:
                text = handle.read(limit + 1)
        except (OSError, UnicodeError) as exc:
            raise CortexBridgeError(f"Could not read Cortex node {relative}: {exc}") from exc
        if len(text) <= limit:
            return text
        return text[:limit].rstrip() + "\n\n[truncated by Cortex MCP bridge]"

    @staticmethod
    def _node_relative(node: str) -> str:
        clean = node.strip()
        if not clean:
            raise CortexBridgeError("node must not be empty")
        if clean in DEFAULT_RECALL_FILES or clean.endswith(".md"):
            return clean
        return node_id_to_relative_path(clean)

    @staticmethod
    def _require_confirmation(user_confirmed: bool) -> None:
        if not user_confirmed:
            raise CortexBridgeError(
                "Write refused: show the exact proposed change to the user and obtain "
                "confirmation before retrying with user_confirmed=true."
            )

    def _run_cli(self, command: str, *arguments: str, payload: str | None = None) -> str:
        if payload is not None and len(payload) > MAX_MUTATION_CHARS:
            raise CortexBridgeError(
                f"mutation payload exceeds the {MAX_MUTATION_CHARS}-character safety limit"
            )
        cli = self.repo_root / "scripts" / "cortex_cli.py"
        argv = [
            sys.executable,
            str(cli),
            command,
            "--memory-root",
            str(self.memory_root),
            *arguments,
        ]
        stdin = None
        if payload is not None:
            argv.append("-")
            stdin = payload
        try:
            completed = subprocess.run(
                argv,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env=dict(os.environ),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CortexBridgeError(f"Cortex CLI failed to run: {exc}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
            raise CortexBridgeError(f"Cortex CLI rejected the mutation: {detail}")
        return completed.stdout.strip()
