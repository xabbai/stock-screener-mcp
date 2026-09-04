# stock-screener-mcp v0.1.0 — TradingView Stock Screener for AI Agents

**135 TradingView fields. One MCP tool.**

stock-screener-mcp is an open-source MCP server that lets Claude, Cursor, VS Code and other MCP clients screen global stocks using the TradingView screener: fundamentals, technicals, momentum, volume, valuation, dividends, ETFs, IPO data and candlestick patterns, with AND/OR filters, sorting and pagination.

## Highlights

- **One tool, 135 fields, 19 categories** — exact TradingView field names, documented in a generated [field reference](../field-reference.md).
- **Real filter logic** — nested AND/OR trees, 24 operators (`greater`, `in_range`, `crosses_above`, `above%`, …), field-to-field comparisons such as `close > EMA200`.
- **One-command install** — `uvx --from git+https://github.com/xabbai/stock-screener-mcp stock-screener-mcp --transport stdio`; validated configs for Claude Desktop, Claude Code, Cursor and VS Code.
- **Honest errors** — unknown fields get case-insensitive and fuzzy suggestions; validation errors come back inside the tool result.
- **stdio and Streamable HTTP** transports; no config file required.
- **Optional authenticated data** through your own TradingView browser session, controlled by `STOCK_SCREENER_MCP_BROWSER_COOKIES`.

## Installation

```bash
# no checkout needed (requires uv)
uvx --from git+https://github.com/xabbai/stock-screener-mcp stock-screener-mcp --transport stdio

# from source
git clone https://github.com/xabbai/stock-screener-mcp.git && cd stock-screener-mcp
uv sync --extra test && uv run stock-screener-mcp --transport stdio
```

Client configuration snippets: [docs/client-configs.md](../client-configs.md).

## Example

Ask your client:

> Find US stocks above their 200-day EMA, with RSI below 40, market cap above $2B, and relative volume above 1.5. Return the top 20 by traded value.

The client calls `screen_stocks` with four filters and gets `{"total_count": …, "rows": [{"ticker": "NYSE:HWM", "name": "HWM", "close": 254.89, "RSI": 37.3, …}], …}` sorted by `Value.Traded`.

## Limitations

- Uses the community `tradingview-screener` library and an undocumented TradingView endpoint; fields and behavior can change without notice. **Not affiliated with TradingView.**
- Public data may be delayed for some exchanges; authenticated data depends on your own TradingView plan.
- Screening only: no historical series, streaming, alerts or order execution.
- The maintainer does not claim returned data is correct, complete, or up to date and accepts no liability for wrong, delayed, or missing data from this tool or TradingView; nothing here is investment advice. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Compatibility

| Requirement | Supported |
|-------------|-----------|
| Python | 3.11, 3.12, 3.13 (CI matrix) |
| MCP SDK | `mcp>=1.26,<2` (2.x renamed FastMCP; migration planned) |
| tradingview-screener | `>=3.0,<4` |
| Transports | stdio, Streamable HTTP |
| Platforms | Linux, macOS, Windows (Python); Chrome cookie extraction where `rookiepy` supports it |

## Known issues

- GUI clients were validated through the MCP stdio client and documented configurations; end-to-end GUI walkthroughs with screenshots are tracked as a help-wanted issue.
- The project was renamed from `tv-mcp` to `stock-screener-mcp` before this release; the import package is `stock_screener_mcp`, the command is `stock-screener-mcp`, and the environment variables are `STOCK_SCREENER_MCP_BROWSER_COOKIES` / `STOCK_SCREENER_MCP_CONFIG`. There are no compatibility aliases for the old names.

## Upgrade notes

First release; nothing to upgrade from. The `screen_stocks` signature (nine required parameters) is the public contract for 0.x.

## Verifying artifacts

Each release attaches the wheel, the source distribution and a `SHA256SUMS` file. Verify with `sha256sum -c SHA256SUMS`.
