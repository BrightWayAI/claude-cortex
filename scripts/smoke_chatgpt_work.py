#!/usr/bin/env python3
"""Exercise the bundled MCP server end-to-end against temporary memory only."""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_TOOLS = {
    "cortex_status",
    "cortex_configure",
    "cortex_recall",
    "cortex_search",
    "cortex_add_note",
    "cortex_update_section",
    "cortex_reindex",
    "cortex_refresh_hot",
}


async def smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="cortex-mcp-smoke-") as temp:
        base = Path(temp)
        fixture_home = base / "home"
        fixture_root = base / "config-root"
        child_env = dict(os.environ)
        child_env["HOME"] = str(fixture_home)
        child_env.pop("CORTEX_CONFIG_ROOT", None)

        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(ROOT / "adapters" / "chatgpt_work" / "server.py"), "--transport", "stdio"],
            cwd=str(ROOT),
            env=child_env,
        )
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                listed = await session.list_tools()
                names = {tool.name for tool in listed.tools}
                if names != EXPECTED_TOOLS:
                    raise RuntimeError(
                        f"unexpected MCP tools: missing={sorted(EXPECTED_TOOLS - names)}, "
                        f"extra={sorted(names - EXPECTED_TOOLS)}"
                    )

                configured = await session.call_tool(
                    "cortex_configure",
                    {
                        "config_root": str(fixture_root),
                        "user_confirmed": True,
                    },
                )
                if configured.is_error:
                    raise RuntimeError(f"cortex_configure failed: {configured.content}")

                status = await session.call_tool("cortex_status", {})
                if status.is_error:
                    raise RuntimeError(f"cortex_status failed: {status.content}")
                recall = await session.call_tool("cortex_recall", {})
                if recall.is_error:
                    raise RuntimeError(f"cortex_recall failed: {recall.content}")

        pointer = fixture_home / ".cortex" / "config-root"
        if pointer.read_text(encoding="utf-8").strip() != str(fixture_root):
            raise RuntimeError("MCP configuration wrote an unexpected pointer")
        if not (fixture_root / "memory" / "DASHBOARD.md").is_file():
            raise RuntimeError("MCP configuration did not initialize fixture memory")


def main() -> int:
    asyncio.run(smoke())
    print("OK: ChatGPT Work MCP listed 8 tools and configured/recalled temporary memory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
