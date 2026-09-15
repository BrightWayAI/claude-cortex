#!/usr/bin/env python3
"""Configure a user's vendor-neutral Cortex root and initialize it safely.

This writes ``~/.cortex/config-root`` and, unless ``--pointer-only`` is
selected, creates a minimal Cortex memory nucleus. Tests inject ``--home`` and
always use temporary directories; normal users should omit ``--home``.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.atomic_write import atomic_write  # noqa: E402
from scripts.lib.config_root import ConfigRootError, resolve_config_root  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent


class ConfigureError(RuntimeError):
    """A configuration refusal safe to show to the user."""


@dataclass(frozen=True)
class ConfigureResult:
    config_root: Path
    pointer_path: Path
    pointer_changed: bool
    initialized_files: tuple[str, ...]
    resolution_warning: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "config_root": str(self.config_root),
            "pointer_path": str(self.pointer_path),
            "pointer_changed": self.pointer_changed,
            "initialized_files": list(self.initialized_files),
            "resolution_warning": self.resolution_warning,
        }


def configure_cortex(
    *,
    home: Path,
    config_root: str,
    environ: Mapping[str, str] | None = None,
    force_pointer: bool = False,
    initialize: bool = True,
    repo_root: Path = REPO_ROOT,
) -> ConfigureResult:
    """Write the shared pointer and optionally seed a minimal memory root."""
    try:
        target = resolve_config_root(home=home, explicit=config_root).path
    except ConfigRootError as exc:
        raise ConfigureError(str(exc)) from exc

    pointer_path = home / ".cortex" / "config-root"
    pointer_changed = True
    if pointer_path.exists():
        try:
            current_raw = pointer_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ConfigureError(f"could not read existing pointer {pointer_path}: {exc}") from exc
        try:
            current = resolve_config_root(home=home, explicit=current_raw).path
        except ConfigRootError as exc:
            if not force_pointer:
                raise ConfigureError(
                    f"existing pointer {pointer_path} is invalid; inspect it or retry with "
                    "--force-pointer after confirming the replacement"
                ) from exc
            current = None
        if current == target:
            pointer_changed = False
        elif not force_pointer:
            raise ConfigureError(
                f"existing pointer {pointer_path} resolves to {current}; refusing to replace it "
                f"with {target} without --force-pointer"
            )

    initialized: list[str] = []
    if initialize:
        memory_root = target / "memory"
        memory_root.mkdir(parents=True, exist_ok=True)
        seeds = {
            "DASHBOARD.md": (
                "# Working Memory Dashboard\n\n"
                "_Cortex is initialized. Add your first project with `remember`, `note`, "
                "or `start-workstream`._\n\n"
                "## Needs Attention\n\nNone yet.\n"
            ),
            "user.md": (
                f"# user\n\n> Last updated: {date.today().isoformat()}\n\n"
                "## Summary\n\nAdd identity and working preferences with `setup-identity`.\n"
            ),
            "log.md": "# Cortex Log\n\n",
        }
        for relative, content in seeds.items():
            if (memory_root / relative).exists():
                continue
            _run_cortex_cli(repo_root, memory_root, "write-file", relative, payload=content)
            initialized.append(relative)
        derived_missing = {
            name for name in ("index.md", "hot.md") if not (memory_root / name).exists()
        }
        _run_cortex_cli(repo_root, memory_root, "reindex")
        _run_cortex_cli(repo_root, memory_root, "refresh-hot", "--trigger", "setup")
        initialized.extend(name for name in ("index.md", "hot.md") if name in derived_missing)

    # Publish the new pointer only after initialization succeeds so a failed
    # setup cannot leave the host resolving to a partial memory root.
    if pointer_changed:
        atomic_write(pointer_path, f"{target}\n")

    env_root = (environ or {}).get("CORTEX_CONFIG_ROOT")
    warning = None
    if env_root is not None:
        try:
            active_env = resolve_config_root(home=home, explicit=env_root).path
        except ConfigRootError:
            warning = (
                "CORTEX_CONFIG_ROOT is set but invalid and takes precedence over the new pointer; "
                "unset or correct it before using Cortex."
            )
        else:
            if active_env != target:
                warning = (
                    f"CORTEX_CONFIG_ROOT currently resolves to {active_env} and takes precedence "
                    f"over the new pointer {target}."
                )

    return ConfigureResult(
        config_root=target,
        pointer_path=pointer_path,
        pointer_changed=pointer_changed,
        initialized_files=tuple(initialized),
        resolution_warning=warning,
    )


def _run_cortex_cli(
    repo_root: Path,
    memory_root: Path,
    command: str,
    *arguments: str,
    payload: str | None = None,
) -> None:
    argv = [
        sys.executable,
        str(repo_root / "scripts" / "cortex_cli.py"),
        command,
        "--memory-root",
        str(memory_root),
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
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigureError(f"Cortex initialization failed: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        raise ConfigureError(f"Cortex initialization was rejected: {detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-root",
        required=True,
        help="Absolute path (or ~/...) that will own memory/, archive/, and plugin config",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--force-pointer",
        action="store_true",
        help="Replace a pointer that currently targets a different root",
    )
    parser.add_argument(
        "--pointer-only",
        action="store_true",
        help="Write the pointer without creating the minimal memory files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = configure_cortex(
            home=args.home,
            config_root=args.config_root,
            environ=os.environ,
            force_pointer=args.force_pointer,
            initialize=not args.pointer_only,
        )
    except ConfigureError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Cortex config root: {result.config_root}")
    print(f"Shared pointer: {result.pointer_path}")
    if result.initialized_files:
        print("Initialized: " + ", ".join(result.initialized_files))
    else:
        print("Initialized: no new files (existing content preserved)")
    if result.resolution_warning:
        print(f"WARNING: {result.resolution_warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
