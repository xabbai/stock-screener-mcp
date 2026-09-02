import argparse
import json
import logging
import os
import sys
from difflib import get_close_matches
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from tradingview_screener import Query
from tradingview_screener.query import And, Or

try:  # installed package / `python -m tv_mcp.tv_mcp`
    from .field_registry import get_all_fields
except ImportError:  # run directly as a script: `python src/tv_mcp/tv_mcp.py`
    _script_dir = Path(__file__).parent.resolve()
    if str(_script_dir) not in sys.path:
        sys.path.insert(0, str(_script_dir))
    from field_registry import get_all_fields  # type: ignore[no-redef]

DEFAULT_CONFIG: dict[str, Any] = {
    "transport": "streamable-http",
    "http": {"host": "127.0.0.1", "port": 8000},
    "stdio": {},
}

SUPPORTED_TRANSPORTS = {"streamable-http", "stdio"}
CONFIG_ENV_VAR = "STOCK_TOOLS_CONFIG"

try:
    __version__ = _pkg_version("tv-mcp")
except PackageNotFoundError:  # running from a plain source tree without installation
    __version__ = "0.0.0+unknown"

# Browser-cookie policy for authenticated/live TradingView data.
#   auto (default): use Chrome cookies if the optional `rookiepy` extra is installed
#   on:             require cookies; fail loudly if rookiepy is missing or extraction fails
#   off:            never touch browser cookies (public data only)
COOKIE_POLICY_ENV = "TV_MCP_BROWSER_COOKIES"
COOKIE_POLICIES = {"auto", "on", "off"}

ALLOWED_SCREEN_FIELDS: set[str] = get_all_fields()

ALLOWED_OPERATIONS = {
    "greater",
    "egreater",
    "less",
    "eless",
    "equal",
    "nequal",
    "in_range",
    "not_in_range",
    "above%",
    "below%",
    "in_range%",
    "not_in_range%",
    "crosses",
    "crosses_above",
    "crosses_below",
    "has",
    "has_none_of",
    "match",
    "nmatch",
    "empty",
    "nempty",
    "in_day_range",
    "in_week_range",
    "in_month_range",
}

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

_ASCII_BANNER = r"""
 _____  __     __          __  __    ____   ____
|_   _| \ \   / /  _____  |  \/  |  / ___| |  _ \
  | |    \ \ / /  |_____| | |\/| | | |     | |_) |
  | |     \ V /           | |  | | | |___  |  __/
  |_|      \_/            |_|  |_|  \____| |_|
"""

mcp = FastMCP("tv-mcp")


def deserialize_content(content):
    """
    Deserialize content blocks into Python objects.

    Args:
        content (list): List of ContentBlock objects.

    Returns:
        dict|list|str: Deserialized content.
    """
    if not content:
        return None

    # Assume the first content block is the main response
    first_content = content[0]

    # Check if it's a text content block with JSON data
    if hasattr(first_content, "text"):
        try:
            return json.loads(first_content.text)
        except json.JSONDecodeError:
            return first_content.text

    return None


def _validate_field(field: str) -> str:
    if not isinstance(field, str):
        raise ValueError("Field names must be strings.")
    if field not in ALLOWED_SCREEN_FIELDS:
        # Try case-insensitive matching first
        case_insensitive_match = None
        for allowed_field in ALLOWED_SCREEN_FIELDS:
            if field.lower() == allowed_field.lower():
                case_insensitive_match = allowed_field
                break

        if case_insensitive_match:
            suggestions = [case_insensitive_match]
        else:
            # Use fuzzy matching with a lower cutoff for better suggestions
            suggestions = get_close_matches(field, ALLOWED_SCREEN_FIELDS, n=5, cutoff=0.3)

        if suggestions:
            raise ValueError(
                f"Unsupported field '{field}'. Did you mean: {', '.join(suggestions)}? "
                f"Use exact TradingView field names."
            )
        raise ValueError(
            f"Unsupported field '{field}'. No similar fields found. "
            f"See tool description for supported field categories."
        )
    return field


def _validate_operation(op: str) -> str:
    if not isinstance(op, str):
        raise ValueError("Operation must be a string.")
    if op not in ALLOWED_OPERATIONS:
        raise ValueError(f"Unsupported operation '{op}'. Allowed: {sorted(ALLOWED_OPERATIONS)}")
    return op


def _convert_filter_spec(filter_spec: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a single filter spec to TradingView filter dict."""
    if not isinstance(filter_spec, dict):
        raise ValueError("Each filter must be an object with 'left', 'op', and optional 'right'.")

    left = _validate_field(filter_spec.get("left"))
    op = _validate_operation(filter_spec.get("op"))
    right = filter_spec.get("right")

    if op in {"empty", "nempty"}:
        return {"left": left, "operation": op, "right": None}

    if right is None:
        raise ValueError(f"Filter for field '{left}' requires a 'right' value for operation '{op}'.")

    return {"left": left, "operation": op, "right": right}


def _build_logic_tree(node: dict[str, Any]) -> dict[str, Any]:
    """Recursively build an And/Or operation tree for where2."""
    logic = node.get("logic", "and")
    if logic not in {"and", "or"}:
        raise ValueError("Logic must be 'and' or 'or'.")

    conditions = node.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise ValueError("conditions must be a non-empty list.")

    operands: list[dict[str, Any]] = []
    for cond in conditions:
        if isinstance(cond, dict) and "logic" in cond:
            operands.append(_build_logic_tree(cond))
        else:
            operands.append(_convert_filter_spec(cond))

    return And(*operands) if logic == "and" else Or(*operands)


def _apply_filters(query: Query, filters: Any) -> Query:
    """Apply filters to the Query supporting AND/OR logic."""
    if not filters:
        return query

    if isinstance(filters, list):
        converted = [_convert_filter_spec(f) for f in filters]
        return query.where(*converted)

    if isinstance(filters, dict):
        if "logic" in filters:
            op_tree = _build_logic_tree(filters)
            return query.where2(op_tree)
        # single filter dict
        return query.where(_convert_filter_spec(filters))

    raise ValueError("filters must be a list or dict.")


def _format_query_result(query_result: Any, columns: list[str]) -> dict[str, Any]:
    """Convert TradingView response to a simple dict."""
    if not isinstance(query_result, tuple) or len(query_result) != 2:
        raise ValueError("Unexpected response format from TradingView Screener.")

    total_count, data_frame = query_result
    # to_dict keeps exact column names; itertuples() would rename dotted fields
    # such as "Value.Traded" or "BB.upper" to positional names like "_8".
    rows: list[dict[str, Any]] = data_frame.to_dict(orient="records")

    return {"total_count": total_count, "columns": columns, "rows": rows}


def _screen_stocks(
    filters: Any,
    columns: list[str],
    markets: list[str],
    sort_by: str,
    sort_order: str,
    nulls_first: bool,
    limit: int,
    offset: int,
    language: str,
) -> dict[str, Any]:
    """
    Core implementation for the screen_stocks tool.
    """
    query = Query()

    # language override
    query.query.setdefault("options", {})["lang"] = language

    # market selection
    if markets:
        query.set_markets(*markets)

    validated_columns = [_validate_field(c) for c in columns] if columns else None
    if validated_columns:
        query.select(*validated_columns)

    query = _apply_filters(query, filters)

    # sorting
    sort_field = sort_by or "Value.Traded"
    if sort_field != "Value.Traded":
        sort_field = _validate_field(sort_field)
    ascending = False if sort_order.lower() == "desc" else True
    query.order_by(sort_field, ascending=ascending, nulls_first=bool(nulls_first))

    # pagination
    try:
        limit_val = int(limit)
        offset_val = int(offset)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit and offset must be integers.") from exc

    if limit_val < 1:
        raise ValueError("limit must be at least 1.")
    if limit_val > 500:
        raise ValueError("limit must not exceed 500.")
    if offset_val < 0:
        raise ValueError("offset must be zero or positive.")

    query.limit(limit_val).offset(offset_val)

    cookies = _load_browser_cookies()

    result = query.get_scanner_data(cookies=cookies) if cookies else query.get_scanner_data()
    response = _format_query_result(result, validated_columns or query.query.get("columns", []))
    response["market_context"] = {"markets": query.query.get("markets"), "url": query.url}
    response["applied_filters"] = filters or []
    response["sort"] = {"by": sort_field, "order": "asc" if ascending else "desc", "nulls_first": nulls_first}
    response["range"] = {"offset": offset_val, "limit": limit_val}
    return response


@mcp.tool()
def screen_stocks(
    filters: Any,
    columns: list[str],
    markets: list[str],
    sort_by: str,
    sort_order: str,
    nulls_first: bool,
    limit: int,
    offset: int,
    language: str,
):
    """
    Screen stocks via TradingView screener with flexible filters, columns, markets, and pagination.

    Args:
        filters: (required) list or dict describing filter conditions, or empty list/dict for no filters.
            Each condition: {left, op, right}.
            Supported ops: greater, egreater, less, eless, equal, nequal, in_range, not_in_range,
            above%, below%, in_range%, not_in_range%, crosses, crosses_above, crosses_below,
            has, has_none_of, match, nmatch, empty, nempty, in_day_range, in_week_range, in_month_range.
            For OR/AND logic use: {"logic":"or|and","conditions":[...]} with nested groups allowed.
        columns: (required) list of fields to return, or empty list for default columns.
            Field categories (use exact field names):
            Trend: EMA5, EMA10, EMA20, EMA50, EMA100, EMA200, ADX, Ichimoku.BLine, Ichimoku.CLine
            Momentum: RSI, CCI20, AO, Stoch.K, Stoch.D
            Volatility: ATR, BB.upper, BB.lower, BBPower, DonchCh20.Upper, DonchCh20.Lower
            Volume/Flow: ChaikinMoneyFlow, average_volume_10d_calc, average_volume_30d_calc, average_volume_60d_calc, relative_volume_10d_calc
            Composite: Recommend.All, Recommend.MA, Recommend.Other
            Price/Structure: close, open, high, low, change, change_abs, name, volume, market_cap_basic, Value.Traded
            Valuation: price_earnings_ttm, price_earnings_forward_fy, price_book_ratio, price_book_fq, price_sales_ratio, price_revenue_ttm, price_free_cash_flow_ttm, enterprise_value_ebitda_ttm
            Profitability: earnings_per_share_basic_ttm, earnings_per_share_diluted_ttm, net_income_ttm, ebitda_ttm, gross_margin_ttm, operating_margin_ttm, after_tax_margin
            Growth: total_revenue_yoy_growth_ttm, earnings_per_share_diluted_yoy_growth_ttm, free_cash_flow_yoy_growth_ttm, total_revenue_qoq_growth_fq, earnings_per_share_diluted_qoq_growth_fq
            Balance Sheet: total_assets, total_debt, shrhldrs_equity_fq, current_ratio, quick_ratio, debt_to_equity
            Quality: piotroski_f_score_ttm, altman_z_score_ttm
            Performance: Perf.5D, Perf.W, Perf.1M, Perf.3M, Perf.6M, Perf.YTD, Perf.Y, Perf.3Y, Perf.5Y, Perf.10Y
            Price Extremes: price_52_week_high, price_52_week_low, High.All, Low.All, High.1M, Low.1M, High.3M, Low.3M, High.6M, Low.6M
            Gap: gap, gap_up, gap_down, premarket_gap
            Dividend: dps_common_stock_prim_issue_fy, dps_common_stock_prim_issue_fq, dividend_yield_recent, dividend_payout_ratio_fy, dividend_payout_ratio_ttm, dividends_paid, ex_dividend_date_recent, ex_dividend_date_upcoming
            ETF/Fund: aum, nav, expense_ratio, etf_holdings_count, nav_discount_premium, fund_flows.1M, fund_flows.1Y, fund_flows.3M, fund_flows.3Y, fund_flows.5Y, fund_flows.YTD
            IPO: ipo_offer_date, ipo_offer_price_usd, ipo_deal_amount_usd, ipo_announcement_date, ipo_price_range_usd_min, ipo_price_range_usd_max
            Advanced Technical: W.R, UO, KltChnl.upper, KltChnl.lower, P.SAR, HullMA9, HullMA20, HullMA200, VWMA
            Candlestick Patterns: Candle.Doji, Candle.Doji.Dragonfly, Candle.Doji.Gravestone, Candle.Engulfing.Bullish, Candle.Engulfing.Bearish, Candle.Hammer, Candle.InvertedHammer, Candle.Harami.Bullish, Candle.Harami.Bearish, Candle.MorningStar, Candle.EveningStar
        markets: (required) list of markets (e.g., ["america", "italy"]), or empty list for default ["america"] market.
            Uses TradingView global scan when multiple markets provided.
        sort_by: (required) field to sort on, or empty string for default "Value.Traded".
        sort_order: (required) "asc" or "desc".
        nulls_first: (required) whether to place nulls first in sort.
        limit: (required) max rows (1-500).
        offset: (required) starting offset (>=0).
        language: (required) language code (e.g., "en", "de", "fr").

    Returns:
        dict with total_count, rows, columns, market_context, applied_filters, sort, range.

    Note on Live Data:
        This tool automatically attempts to use rookiepy to load cookies from your Chrome browser
        for authenticated/live data access. If rookiepy is not installed or fails, it falls back
        to public data. To enable live data:
        1. Install rookiepy: pip install -e .[cookies]
        2. Be logged in to TradingView in your Chrome browser
        3. The tool will automatically detect and use your session

    Examples:
        # Minimal usage: Get default results with no filters or custom parameters
        # Use empty values ([], "") for parameters you don't need
        screen_stocks(
            filters=[],              # No filters - returns all stocks
            columns=[],              # Empty list uses default columns: name, close, volume, market_cap_basic
            markets=[],              # Empty list uses default market: ["america"]
            sort_by="",              # Empty string uses default sort: "Value.Traded"
            sort_order="desc",       # Standard sort order
            nulls_first=False,       # Standard null handling
            limit=50,                # Number of results
            offset=0,                # Start from beginning
            language="en"            # Language for results
        )

        # Basic filter: Find stocks with RSI < 30 (oversold)
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

        # Multiple filters with AND logic: Oversold stocks with high volume
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

        # OR logic: Stocks that are either oversold OR overbought
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

        # Complex nested logic: (RSI < 30 AND volume > 1M) OR (close > EMA200 AND ADX > 25)
        screen_stocks(
            filters={
                "logic": "or",
                "conditions": [
                    {
                        "logic": "and",
                        "conditions": [
                            {"left": "RSI", "op": "less", "right": 30},
                            {"left": "volume", "op": "greater", "right": 1000000}
                        ]
                    },
                    {
                        "logic": "and",
                        "conditions": [
                            {"left": "close", "op": "greater", "right": "EMA200"},
                            {"left": "ADX", "op": "greater", "right": 25}
                        ]
                    }
                ]
            },
            columns=["name", "close", "RSI", "volume", "EMA200", "ADX"],
            markets=[],
            sort_by="",
            sort_order="desc",
            nulls_first=False,
            limit=25,
            offset=0,
            language="en"
        )

        # Screen multiple markets: US and Italian stocks
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

        # Price breakout: Stocks trading above upper Bollinger Band
        screen_stocks(
            filters=[{"left": "close", "op": "greater", "right": "BB.upper"}],
            columns=["name", "close", "BB.upper", "BB.lower", "volume"],
            markets=[],
            sort_by="volume",
            sort_order="desc",
            nulls_first=False,
            limit=20,
            offset=0,
            language="en"
        )

        # Pagination example: Get results 50-100
        screen_stocks(
            filters=[{"left": "market_cap_basic", "op": "greater", "right": 1000000000}],
            columns=["name", "close", "market_cap_basic"],
            markets=[],
            sort_by="",
            sort_order="desc",
            nulls_first=False,
            limit=50,
            offset=50,
            language="en"
        )
    """
    try:
        return _screen_stocks(
            filters=filters,
            columns=columns,
            markets=markets,
            sort_by=sort_by,
            sort_order=sort_order,
            nulls_first=nulls_first,
            limit=limit,
            offset=offset,
            language=language,
        )
    except Exception as exc:  # surface validation errors cleanly
        logger.exception("screen_stocks failed: %s", exc)
        return {"error": str(exc)}


def _cookie_policy() -> str:
    """Read and validate the browser-cookie policy from the environment."""
    policy = os.getenv(COOKIE_POLICY_ENV, "auto").strip().lower() or "auto"
    if policy not in COOKIE_POLICIES:
        raise ValueError(f"Invalid {COOKIE_POLICY_ENV}='{policy}'. Use one of {sorted(COOKIE_POLICIES)}.")
    return policy


def _load_browser_cookies():
    """
    Return a cookie jar for tradingview.com according to TV_MCP_BROWSER_COOKIES, or None.

    Cookies are read from the local Chrome profile via the optional `rookiepy` extra and are
    only held in memory for the current request. They are never written to disk or logged.
    """
    policy = _cookie_policy()
    if policy == "off":
        return None

    try:
        import rookiepy  # optional extra: pip install "tv-mcp[cookies]"
    except ImportError:
        if policy == "on":
            raise ValueError(
                f"{COOKIE_POLICY_ENV}=on but the optional 'rookiepy' package is not installed. "
                "Install it with: pip install 'tv-mcp[cookies]'"
            ) from None
        logger.debug("rookiepy not installed; using public TradingView data.")
        return None

    try:
        cookies = rookiepy.to_cookiejar(rookiepy.chrome([".tradingview.com"]))
        logger.info("Using Chrome cookies for authenticated TradingView data.")
        return cookies
    except Exception as exc:
        if policy == "on":
            raise ValueError(f"Could not read Chrome cookies for tradingview.com: {exc}") from exc
        logger.debug("Cookie extraction failed (%s); using public TradingView data.", exc)
        return None


def _default_server_config() -> dict[str, Any]:
    """Return a fresh default config dict."""
    return {
        "transport": DEFAULT_CONFIG["transport"],
        "http": DEFAULT_CONFIG["http"].copy(),
        "stdio": DEFAULT_CONFIG["stdio"].copy(),
    }


def _resolve_config_path(cli_config: str | None) -> Path:
    """Resolve config path from CLI flag, env var, or repo root default."""
    if cli_config:
        return Path(cli_config)

    env_config = os.getenv(CONFIG_ENV_VAR)
    if env_config:
        return Path(env_config)

    return Path(__file__).resolve().parents[2] / "config.json"


def _validate_server_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize server configuration."""
    transport = config.get("transport", DEFAULT_CONFIG["transport"])
    if transport not in SUPPORTED_TRANSPORTS:
        raise ValueError(f"Unsupported transport '{transport}'. Use one of {sorted(SUPPORTED_TRANSPORTS)}.")

    http_config = config.get("http", {})
    host = http_config.get("host", DEFAULT_CONFIG["http"]["host"])
    port = http_config.get("port", DEFAULT_CONFIG["http"]["port"])
    try:
        port = int(port)
    except (TypeError, ValueError) as exc:
        raise ValueError("HTTP port must be an integer") from exc

    if not (0 < port < 65536):
        raise ValueError("HTTP port must be between 1 and 65535")

    if transport == "streamable-http" and not host:
        raise ValueError("HTTP host must be provided for streamable-http transport")

    config["transport"] = transport
    config["http"] = {"host": host, "port": port}
    config.setdefault("stdio", {})
    return config


def _load_server_config(config_path: Path) -> dict[str, Any]:
    """Load server configuration from a JSON file, applying defaults."""
    config = _default_server_config()

    if not config_path.exists():
        logging.info(f"Config file not found at {config_path}; using defaults")
        return config

    try:
        raw_config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config file {config_path}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ValueError("Config file must contain a JSON object at the top level")

    config["transport"] = raw_config.get("transport", config["transport"])
    if isinstance(raw_config.get("http"), dict):
        config["http"].update(raw_config["http"])
    if isinstance(raw_config.get("stdio"), dict):
        config["stdio"].update(raw_config["stdio"])

    return _validate_server_config(config)


def _run_server(config: dict[str, Any]) -> None:
    """Start the MCP server with the provided configuration."""
    transport = config["transport"]

    if transport == "streamable-http":
        host = config["http"]["host"]
        port = config["http"]["port"]
        print(_ASCII_BANNER, file=sys.stderr)
        print(f"Starting TV-MCP server on http://{host}:{port}/mcp", file=sys.stderr)
        logging.info(f"Starting MCP server '{mcp.name}' on http://{host}:{port}/")
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.settings.json_response = True  # keep HTTP responses as JSON text blocks
        mcp.run(transport="streamable-http")
    elif transport == "stdio":
        logging.info(f"Starting MCP server '{mcp.name}' with stdio transport")
        mcp.run(transport="stdio")
    else:
        raise ValueError(f"Unsupported transport '{transport}'")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tv-mcp-server",
        description="Run the tv-mcp TradingView screener MCP server.",
    )
    parser.add_argument("--version", action="version", version=f"tv-mcp {__version__}")
    parser.add_argument(
        "--config",
        help=(
            "Path to config.json controlling transport and server settings. "
            f"Defaults to the {CONFIG_ENV_VAR} env var or the repository root config.json."
        ),
    )
    parser.add_argument(
        "--transport",
        choices=sorted(SUPPORTED_TRANSPORTS),
        help="Transport to use. Overrides the config file. 'stdio' for MCP clients that launch "
        "the server as a subprocess; 'streamable-http' to serve http://HOST:PORT/mcp.",
    )
    parser.add_argument("--host", help="HTTP bind host (streamable-http only). Overrides the config file.")
    parser.add_argument("--port", type=int, help="HTTP port (streamable-http only). Overrides the config file.")
    return parser


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return _build_arg_parser().parse_args(argv)


def _apply_cli_overrides(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Apply --transport/--host/--port on top of the loaded config and re-validate."""
    if getattr(args, "transport", None):
        config["transport"] = args.transport
    if getattr(args, "host", None):
        config.setdefault("http", {})["host"] = args.host
    if getattr(args, "port", None) is not None:
        config.setdefault("http", {})["port"] = args.port
    return _validate_server_config(config)


def _main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    config_path = _resolve_config_path(args.config)
    config = _apply_cli_overrides(_load_server_config(config_path), args)
    logging.info(f"Using config from {config_path} with transport={config['transport']}")
    _run_server(config)


if __name__ == "__main__":
    _main()
