# MCP client configuration

tv-mcp runs as a local MCP server. Most clients launch it as a subprocess over **stdio**; a few can also connect to a running **Streamable HTTP** endpoint.

All configurations below use the same command line. It was executed on 2026-09-02 by `tests/test_quickstart.py` and `scripts/clean_env_smoke.sh` through the official MCP Python stdio client (see the validation table at the end).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`). uv downloads Python 3.11+ automatically if needed.
- No TradingView account is required for public data.

## Choose how the server is launched

### Option A — one command, no checkout (uvx from Git)

```bash
uvx --from git+https://github.com/xabbai/tv-mcp tv-mcp-server --transport stdio
```

Use this as `command: uvx` with the remaining words as `args` in the client configs below.

### Option B — local checkout

```bash
git clone https://github.com/xabbai/tv-mcp.git
uv run --directory /ABSOLUTE/PATH/tv-mcp tv-mcp-server --transport stdio
```

### Option C — HTTP endpoint (advanced / shared)

```bash
uvx --from git+https://github.com/xabbai/tv-mcp tv-mcp-server --transport streamable-http --host 127.0.0.1 --port 8000
```

The MCP endpoint is then `http://127.0.0.1:8000/mcp`. Point clients that support remote/HTTP servers at that URL.

## Environment variables

| Variable | Values | Effect |
|----------|--------|--------|
| `TV_MCP_BROWSER_COOKIES` | `auto` (default), `off`, `on` | Whether to read your Chrome `tradingview.com` cookies for authenticated data. Requires the `cookies` extra (`uvx --from "git+https://github.com/xabbai/tv-mcp#egg=tv-mcp[cookies]"` or `pip install "tv-mcp[cookies]"`). Set `off` for public data only. |
| `STOCK_TOOLS_CONFIG` | file path | Alternative to `--config`; a JSON file with `transport` and `http.host`/`http.port`. |

## Claude Desktop

File: `claude_desktop_config.json` (Settings → Developer → Edit Config).

```json
{
  "mcpServers": {
    "tv-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/xabbai/tv-mcp", "tv-mcp-server", "--transport", "stdio"],
      "env": { "TV_MCP_BROWSER_COOKIES": "off" }
    }
  }
}
```

Local checkout variant:

```json
{
  "mcpServers": {
    "tv-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/ABSOLUTE/PATH/tv-mcp", "tv-mcp-server", "--transport", "stdio"]
    }
  }
}
```

Restart Claude Desktop after editing. The `screen_stocks` tool appears under the tools icon.

## Claude Code

```bash
claude mcp add tv-mcp -- uvx --from git+https://github.com/xabbai/tv-mcp tv-mcp-server --transport stdio
```

Or commit a project-scoped `.mcp.json`:

```json
{
  "mcpServers": {
    "tv-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/xabbai/tv-mcp", "tv-mcp-server", "--transport", "stdio"]
    }
  }
}
```

## Cursor

File: `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project).

```json
{
  "mcpServers": {
    "tv-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/xabbai/tv-mcp", "tv-mcp-server", "--transport", "stdio"],
      "env": { "TV_MCP_BROWSER_COOKIES": "off" }
    }
  }
}
```

## VS Code (GitHub Copilot agent mode)

File: `.vscode/mcp.json` in your workspace (or add via *MCP: Add Server*).

```json
{
  "servers": {
    "tv-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/xabbai/tv-mcp", "tv-mcp-server", "--transport", "stdio"],
      "env": { "TV_MCP_BROWSER_COOKIES": "off" }
    }
  }
}
```

HTTP variant for VS Code (server started separately with Option C):

```json
{
  "servers": {
    "tv-mcp-http": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## Try it

Ask your client:

> Find US stocks above their 200-day EMA with RSI below 40, market cap above $2B and relative volume above 1.5. Return the top 20 by traded value.

The client should call `screen_stocks` with filters on `close > EMA200`, `RSI < 40`, `market_cap_basic > 2000000000`, `relative_volume_10d_calc > 1.5`, sorted by `Value.Traded`.

## Validation status (2026-09-02)

| Item | How it was validated |
|------|----------------------|
| `tv-mcp-server --transport stdio` over MCP stdio, quick-start screen | Executed: `tests/test_quickstart.py` (dev env) and `scripts/clean_env_smoke.sh` (fresh venv, wheel install, 3 s end to end, 20 rows) |
| `uvx --from <local source> tv-mcp-server --help` | Executed |
| `uvx --from git+https://github.com/xabbai/tv-mcp ...` | **Not yet executable**: the repository has not been pushed publicly. Re-run after publication. |
| `uv run --directory … tv-mcp-server --transport stdio` | Same CLI as above; `uv run tv-mcp-server` executed in the checkout |
| Claude Desktop / Claude Code / Cursor / VS Code JSON | Schema follows each vendor's documented format; JSON validated by script. The GUI clients themselves were **not** exercised in this environment. |

## Troubleshooting

- **`No module named 'mcp.server.fastmcp'`** — an old install resolved mcp 2.x. Upgrade tv-mcp (the dependency is now pinned to `mcp<2`) or reinstall.
- **Client shows no tools** — check the command runs in a terminal first; the server must be started with `--transport stdio` for subprocess clients.
- **`uvx: command not found`** — install uv and restart the client so it picks up `PATH`.
- **Empty rows** — loosen the filters; screens run against the live TradingView scanner and results change intraday.
