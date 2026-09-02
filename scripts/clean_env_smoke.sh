#!/usr/bin/env bash
# Clean-environment smoke test for tv-mcp.
#
# Builds the wheel, installs it into a brand-new virtual environment, launches
# `tv-mcp-server --transport stdio` through a real MCP stdio client, runs the README
# quick-start screen, and reports the elapsed wall-clock time.
#
# Usage: bash scripts/clean_env_smoke.sh [python-version]   (default 3.11)
set -euo pipefail

PY_VERSION="${1:-3.11}"
START=$(date +%s)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "[1/4] Building wheel"
uv build --out-dir "$TMP/dist" >/dev/null 2>&1
WHEEL=$(ls "$TMP"/dist/*.whl)

echo "[2/4] Creating clean venv (Python $PY_VERSION)"
uv venv "$TMP/venv" --python "$PY_VERSION" >/dev/null 2>&1

echo "[3/4] Installing $(basename "$WHEEL")"
uv pip install --python "$TMP/venv/bin/python" "$WHEEL" >/dev/null 2>&1

echo "[4/4] Running quick-start screen over stdio"
TV_MCP_BROWSER_COOKIES=off "$TMP/venv/bin/python" - "$TMP/venv/bin/tv-mcp-server" <<'PY'
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

exe = sys.argv[1]
args = {
    "filters": [
        {"left": "close", "op": "greater", "right": "EMA200"},
        {"left": "RSI", "op": "less", "right": 40},
        {"left": "market_cap_basic", "op": "greater", "right": 2_000_000_000},
        {"left": "relative_volume_10d_calc", "op": "greater", "right": 1.5},
    ],
    "columns": ["name", "close", "RSI", "EMA200", "market_cap_basic", "relative_volume_10d_calc", "Value.Traded"],
    "markets": ["america"], "sort_by": "Value.Traded", "sort_order": "desc",
    "nulls_first": False, "limit": 20, "offset": 0, "language": "en",
}

async def main():
    params = StdioServerParameters(command=exe, args=["--transport", "stdio"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = {t.name for t in (await s.list_tools()).tools}
            assert "screen_stocks" in names, names
            res = await s.call_tool("screen_stocks", args)
            payload = json.loads(next(c.text for c in res.content if getattr(c, "text", None)))
            assert "rows" in payload and "error" not in payload, payload
            print(f"rows={len(payload['rows'])} total_count={payload['total_count']}")

asyncio.run(main())
PY

ELAPSED=$(( $(date +%s) - START ))
echo "OK clean-environment quick start succeeded elapsed=${ELAPSED}s"
