#!/usr/bin/env python3
"""Build a Cortex ZIP from tracked and non-ignored files only."""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.check_release import audit_release, shareable_paths  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent


def build_archive(output: Path, root: Path = ROOT) -> int:
    root = root.resolve()
    output = output.expanduser().resolve()
    if output == root or root in output.parents:
        raise ValueError("release output must be outside the repository")
    findings = audit_release(root)
    if findings:
        details = "\n".join(str(finding) for finding in findings)
        raise ValueError(f"release audit failed:\n{details}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(shareable_paths(root)):
            relative = path.relative_to(root).as_posix()
            archive.write(path, f"cortex/{relative}")
    return len(shareable_paths(root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        count = build_archive(args.output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote {args.output.expanduser().resolve()} with {count} shareable files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
