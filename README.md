# tv-mcp

A Model Context Protocol (MCP) server that exposes a `screen_stocks` tool for filtering stocks using 135 fields from the TradingView screener API.

## Installation

**Requirements:** Python 3.11+

### 1. Clone the repository

```bash
git clone https://github.com/xabbai/tv-mcp.git
cd tv-mcp
```

### 2. Install runtime dependencies

```bash
pip install -r requirements.txt -c constraints.txt
```

### 3. (Optional) Install the package with test dependencies

```bash
pip install -e ".[test]"
```

### 4. (Optional) Install with live-data cookie support

```bash
pip install -e ".[cookies]"
```

This enables authenticated TradingView data via Chrome cookies. Requires `rookiepy`. See [Live Data](#live-data-optional) for details.

---

## Configuration

The server reads configuration from `config.json`. It is located at the repository root by default. You can override the path using:

- The `STOCK_TOOLS_CONFIG` environment variable, or
- The `--config` CLI flag (e.g., `tv-mcp-server --config /path/to/config.json`)

### config.json schema

```json
{
  "transport": "streamable-http",
  "http": {
    "host": "127.0.0.1",
    "port": 8000
  }
}
```

### Command-line flags

Flags override values from `config.json`:

| Flag | Description |
|------|-------------|
| `--transport {stdio,streamable-http}` | Transport to use. Use `stdio` for MCP clients that launch the server as a subprocess. |
| `--host HOST` | HTTP bind host (`streamable-http` only) |
| `--port PORT` | HTTP port (`streamable-http` only) |
| `--config PATH` | Path to a `config.json` |

### Environment variables

| Variable | Description |
|----------|-------------|
| `STOCK_TOOLS_CONFIG` | Path to `config.json` (overridden by `--config`) |
| `TV_MCP_BROWSER_COOKIES` | `auto` (default): use Chrome cookies for authenticated TradingView data if the optional `rookiepy` extra is installed; `off`: public data only; `on`: require cookies and fail if unavailable. See [Live Data](#live-data-optional). |

### Supported transports

| Transport | Description |
|-----------|-------------|
| `streamable-http` (default) | Starts an HTTP server. MCP endpoint available at `http://HOST:PORT/mcp`. |
| `stdio` | Uses stdin/stdout for direct process communication. Useful for MCP clients that launch the server as a subprocess. |

---

## Usage

### Starting the server

Via installed entry point (after `pip install -e .`):

```bash
tv-mcp-server
```

With a custom config file:

```bash
tv-mcp-server --config /path/to/config.json
```

Via Python directly:

```bash
python src/tv_mcp/tv_mcp.py
```

Via uv:

```bash
uv run tv-mcp-server
```

### Connecting an MCP client

For `streamable-http` transport (default config), the MCP endpoint is:

```
http://127.0.0.1:8000/mcp
```

Point your MCP client at this URL. For `stdio` transport, point your MCP client at the `tv-mcp-server` executable directly.

### The screen_stocks tool

The `screen_stocks` tool screens stocks via the TradingView screener with flexible filters, columns, markets, and pagination support.

| Parameter | Description |
|-----------|-------------|
| `filters` | Filter conditions — a list of `{left, op, right}` dicts, or an AND/OR logic dict |
| `columns` | Fields to return (135 available across 19 categories; empty list returns defaults) |
| `markets` | Market(s) to query, e.g. `["america", "italy"]` (empty list defaults to `["america"]`) |
| `sort_by` | Field to sort on (empty string defaults to `"Value.Traded"`) |
| `sort_order` | `"asc"` or `"desc"` |
| `nulls_first` | Whether to place null values first in the sort |
| `limit` | Maximum rows to return (1-500) |
| `offset` | Pagination start offset (>= 0) |
| `language` | Language code for results (e.g. `"en"`, `"de"`, `"fr"`) |

Supported filter operations: `greater`, `egreater`, `less`, `eless`, `equal`, `nequal`, `in_range`, `not_in_range`, `above%`, `below%`, `in_range%`, `not_in_range%`, `crosses`, `crosses_above`, `crosses_below`, `has`, `has_none_of`, `match`, `nmatch`, `empty`, `nempty`, `in_day_range`, `in_week_range`, `in_month_range`.

---

## Examples

### 1. Minimal usage (no filters, default columns)

```python
screen_stocks(
    filters=[],              # No filters — returns all stocks
    columns=[],              # Empty list uses default columns: name, close, volume, market_cap_basic
    markets=[],              # Empty list uses default market: ["america"]
    sort_by="",              # Empty string uses default sort: "Value.Traded"
    sort_order="desc",
    nulls_first=False,
    limit=50,
    offset=0,
    language="en"
)
```

### 2. Basic filter: RSI < 30 (oversold stocks)

```python
screen_stocks(
    filters=[{"left": "RSI", "op": "less", "right": 30}],
    columns=["name", "close", "RSI", "volume"],
    markets=[],
    sort_by="",
    sort_order="desc",
    nulls_first=False,
    limit=10,
    offset=0,
    language="en"
)
```

### 3. Multiple AND filters: RSI < 30 AND volume > 1M

```python
screen_stocks(
    filters=[
        {"left": "RSI", "op": "less", "right": 30},
        {"left": "volume", "op": "greater", "right": 1000000}
    ],
    columns=["name", "close", "RSI", "volume"],
    markets=[],
    sort_by="volume",
    sort_order="desc",
    nulls_first=False,
    limit=20,
    offset=0,
    language="en"
)
```

### 4. OR logic: RSI < 30 OR RSI > 70

```python
screen_stocks(
    filters={
        "logic": "or",
        "conditions": [
            {"left": "RSI", "op": "less", "right": 30},
            {"left": "RSI", "op": "greater", "right": 70}
        ]
    },
    columns=["name", "close", "RSI"],
    markets=[],
    sort_by="",
    sort_order="desc",
    nulls_first=False,
    limit=15,
    offset=0,
    language="en"
)
```

### 5. Multi-market screening: US and Italian stocks

```python
screen_stocks(
    filters=[{"left": "RSI", "op": "less", "right": 35}],
    columns=["name", "close", "RSI"],
    markets=["america", "italy"],
    sort_by="",
    sort_order="desc",
    nulls_first=False,
    limit=30,
    offset=0,
    language="en"
)
```

---

## Field Reference

Use exact TradingView field names when specifying `columns` or `filters`. 135 fields are available across 19 categories:

| Category | Representative Fields |
|----------|-----------------------|
| **Trend** | `EMA5`, `EMA10`, `EMA20`, `EMA50`, `EMA100`, `EMA200`, `ADX`, `Ichimoku.BLine`, `Ichimoku.CLine` |
| **Momentum** | `RSI`, `CCI20`, `AO`, `Stoch.K`, `Stoch.D` |
| **Volatility** | `ATR`, `BB.upper`, `BB.lower`, `BBPower`, `DonchCh20.Upper`, `DonchCh20.Lower` |
| **Volume/Flow** | `ChaikinMoneyFlow`, `average_volume_10d_calc`, `average_volume_30d_calc`, `average_volume_60d_calc`, `relative_volume_10d_calc` |
| **Composite** | `Recommend.All`, `Recommend.MA`, `Recommend.Other` |
| **Price/Structure** | `close`, `open`, `high`, `low`, `change`, `change_abs`, `name`, `volume`, `market_cap_basic`, `Value.Traded` |
| **Valuation** | `price_earnings_ttm`, `price_earnings_forward_fy`, `price_book_ratio`, `price_book_fq`, `price_sales_ratio`, `price_revenue_ttm`, `price_free_cash_flow_ttm`, `enterprise_value_ebitda_ttm` |
| **Profitability** | `earnings_per_share_basic_ttm`, `earnings_per_share_diluted_ttm`, `net_income_ttm`, `ebitda_ttm`, `gross_margin_ttm`, `operating_margin_ttm`, `after_tax_margin` |
| **Growth** | `total_revenue_yoy_growth_ttm`, `earnings_per_share_diluted_yoy_growth_ttm`, `free_cash_flow_yoy_growth_ttm`, `total_revenue_qoq_growth_fq`, `earnings_per_share_diluted_qoq_growth_fq` |
| **Balance Sheet** | `total_assets`, `total_debt`, `shrhldrs_equity_fq`, `current_ratio`, `quick_ratio`, `debt_to_equity` |
| **Quality** | `piotroski_f_score_ttm`, `altman_z_score_ttm` |
| **Performance** | `Perf.5D`, `Perf.W`, `Perf.1M`, `Perf.3M`, `Perf.6M`, `Perf.YTD`, `Perf.Y`, `Perf.3Y`, `Perf.5Y`, `Perf.10Y` |
| **Price Extremes** | `price_52_week_high`, `price_52_week_low`, `High.All`, `Low.All`, `High.1M`, `Low.1M`, `High.3M`, `Low.3M`, `High.6M`, `Low.6M` |
| **Gap** | `gap`, `gap_up`, `gap_down`, `premarket_gap` |
| **Dividend** | `dps_common_stock_prim_issue_fy`, `dps_common_stock_prim_issue_fq`, `dividend_yield_recent`, `dividend_payout_ratio_fy`, `dividend_payout_ratio_ttm`, `dividends_paid`, `ex_dividend_date_recent`, `ex_dividend_date_upcoming` |
| **ETF/Fund** | `aum`, `nav`, `expense_ratio`, `etf_holdings_count`, `nav_discount_premium`, `fund_flows.1M`, `fund_flows.1Y`, `fund_flows.3M`, `fund_flows.3Y`, `fund_flows.5Y`, `fund_flows.YTD` |
| **IPO** | `ipo_offer_date`, `ipo_offer_price_usd`, `ipo_deal_amount_usd`, `ipo_announcement_date`, `ipo_price_range_usd_min`, `ipo_price_range_usd_max` |
| **Advanced Technical** | `W.R`, `UO`, `KltChnl.upper`, `KltChnl.lower`, `P.SAR`, `HullMA9`, `HullMA20`, `HullMA200`, `VWMA` |
| **Candlestick Patterns** | `Candle.Doji`, `Candle.Doji.Dragonfly`, `Candle.Doji.Gravestone`, `Candle.Engulfing.Bullish`, `Candle.Engulfing.Bearish`, `Candle.Hammer`, `Candle.InvertedHammer`, `Candle.Harami.Bullish`, `Candle.Harami.Bearish`, `Candle.MorningStar`, `Candle.EveningStar` |

For the full list of field names, see the `screen_stocks` docstring in `src/tv_mcp/tv_mcp.py`.

---

## Live Data (Optional)

By default, `screen_stocks` uses the public TradingView screener API. To access live or authenticated data, install the optional `rookiepy` dependency:

```bash
pip install -e ".[cookies]"
```

Once installed:

1. Log in to TradingView in your Chrome browser.
2. Start the server — it will automatically detect and use your Chrome session cookies.
3. If `rookiepy` is not installed or cookie extraction fails, the tool falls back to public data seamlessly.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
