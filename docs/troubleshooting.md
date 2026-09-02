# Troubleshooting

Symptoms are grouped by where they appear. Every fix below was checked against the current CLI (`tv-mcp-server --help`). If nothing here helps, open a bug report with the issue form; it asks for the details needed to reproduce.

## The client shows no `screen_stocks` tool

**Cause:** the server did not start, or it started in HTTP mode while the client expected stdio.

1. Run the exact `command` + `args` from your client config in a terminal. You should see no output and the process should wait for input (stdio) — press Ctrl-C to stop. Any traceback is the real error.
2. Make sure the args end with `--transport stdio`. Without it the server listens on `http://127.0.0.1:8000/mcp` and a subprocess client sees "Connection closed".
3. Restart the client after editing its config file.

## `uvx: command not found` or `spawn uvx ENOENT`

**Cause:** GUI apps on macOS and Windows often do not inherit your shell `PATH`.

- Use the absolute path to `uvx` in `command` (`which uvx` / `where uvx`), for example `/Users/you/.local/bin/uvx`.
- Or install uv system-wide and restart the client (log out/in on macOS).

## First run is slow or times out

**Cause:** `uvx --from git+…` clones the repository and resolves dependencies on first use; a slow network can exceed the client's startup timeout.

- Run the uvx command once in a terminal to warm the cache, then restart the client.
- Alternatively clone the repo and use the local-checkout config (`uv run --directory …`).

## `No module named 'mcp.server.fastmcp'`

**Cause:** an environment resolved `mcp` 2.x, which renamed FastMCP. tv-mcp pins `mcp<2`.

- Reinstall / upgrade tv-mcp, or in a source checkout run `uv sync`.

## `Unsupported field 'X'. Did you mean: …`

**Cause:** field names are exact and case-sensitive TradingView names (`RSI`, `BB.upper`, `market_cap_basic`).

- Use the suggestion from the error, or look the name up in [field-reference.md](field-reference.md).
- Fields missing from the reference can be requested with the feature-request form.

## `Unsupported operation 'X'`

Allowed operators are listed in [field-reference.md](field-reference.md#filter-operations). Common mistakes: `>` instead of `greater`, `gt`, `between` instead of `in_range`.

## Empty `rows` or unexpectedly small `total_count`

- Screens run against the live scanner; results change during the trading session and can be empty outside market hours for intraday-only conditions (gaps, crosses).
- Filters are ANDed by default. Loosen thresholds one at a time.
- Some fields are null for most instruments (ETF-only, IPO-only, dividend fields for non-payers); a filter on them excludes everything else.
- Field-to-field comparisons need both names to be valid fields, e.g. `{"left": "close", "op": "greater", "right": "EMA200"}`.

## Network errors, HTTP 4xx/5xx, or "Unexpected response format"

**Cause:** the TradingView scanner endpoint is undocumented and may rate-limit, change, or be unreachable through corporate proxies.

- Retry after a short pause; reduce `limit` and the number of columns.
- Check that `https://scanner.tradingview.com` is reachable from your machine.
- If the failure persists across days, upstream may have changed; open a bug report with the redacted error.

## Authenticated data (`TV_MCP_BROWSER_COOKIES`)

| Message | Fix |
|---------|-----|
| `TV_MCP_BROWSER_COOKIES=on but the optional 'rookiepy' package is not installed` | Install the extra: `uv sync --extra cookies` or `pip install "tv-mcp[cookies]"`. With `uvx`, use `--from "git+https://github.com/xabbai/tv-mcp#egg=tv-mcp[cookies]"`. |
| `Could not read Chrome cookies for tradingview.com` | Log in to TradingView in Chrome, close and reopen the browser, and ensure Chrome's cookie database is readable (on Linux the profile must not be locked by a different user). |
| Data still looks delayed | Cookie extraction succeeded but your TradingView plan may not include real-time data for that exchange. |

Set `TV_MCP_BROWSER_COOKIES=off` to guarantee public-data-only behavior.

## HTTP transport

- `address already in use`: another process uses the port; pass `--port 8010`.
- The endpoint is `http://HOST:PORT/mcp` (note the `/mcp` path). It has no authentication; keep `--host 127.0.0.1` unless you add a reverse proxy with auth.

## Windows notes

- Use forward slashes or escaped backslashes in JSON paths (`"C:/tools/tv-mcp"`).
- If `uvx` is installed for the current user only, GUI clients started as a different user will not find it.

## Getting more detail

Run the server in a terminal with the same flags as your client and watch stderr. Validation errors are returned to the client inside the tool result as `{"error": "..."}` rather than as transport errors.
