"""
Quick-start smoke tests: launch the installed `tv-mcp-server` CLI exactly as an MCP client would
and run the README quick-start screen over stdio.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

QUICKSTART_ARGS = {
    "filters": [
        {"left": "close", "op": "greater", "right": "EMA200"},
        {"left": "RSI", "op": "less", "right": 40},
        {"left": "market_cap_basic", "op": "greater", "right": 2_000_000_000},
        {"left": "relative_volume_10d_calc", "op": "greater", "right": 1.5},
    ],
    "columns": ["name", "close", "RSI", "EMA200", "market_cap_basic", "relative_volume_10d_calc", "Value.Traded"],
    "markets": ["america"],
    "sort_by": "Value.Traded",
    "sort_order": "desc",
    "nulls_first": False,
    "limit": 20,
    "offset": 0,
    "language": "en",
}


def _server_command():
    exe = shutil.which("tv-mcp-server")
    if exe is None:
        pytest.skip("tv-mcp-server is not on PATH (install the package first)")
    return exe


def test_cli_help_exits_zero():
    exe = _server_command()
    result = subprocess.run([exe, "--help"], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0
    assert "--transport" in result.stdout


@pytest.mark.network
@pytest.mark.asyncio
async def test_quickstart_screen_over_stdio():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    exe = _server_command()
    env = dict(os.environ, TV_MCP_BROWSER_COOKIES="off")
    params = StdioServerParameters(command=exe, args=["--transport", "stdio"], env=env)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert "screen_stocks" in {t.name for t in tools.tools}

            result = await session.call_tool("screen_stocks", QUICKSTART_ARGS)
            assert not result.isError, result.content
            text = next(c.text for c in result.content if getattr(c, "text", None))
            payload = json.loads(text)

    assert "error" not in payload, payload
    assert isinstance(payload["rows"], list)
    assert payload["total_count"] >= 0
    assert payload["sort"]["by"] == "Value.Traded"
    assert set(payload["columns"]) == set(QUICKSTART_ARGS["columns"])
    assert len(payload["rows"]) >= 1, "Quick-start screen returned no rows; check filters or API"
