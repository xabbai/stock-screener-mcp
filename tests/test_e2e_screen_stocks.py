"""
End-to-end integration tests for screen_stocks tool with fundamental fields.

These tests validate that screen_stocks works end-to-end through the MCP tool
interface with the new fundamental metric fields (valuation, profitability, growth,
balance sheet, quality scores).
"""

import json

import pytest


@pytest.mark.asyncio
async def test_screen_stocks_with_valuation_filters(mcp_client):
    """
    Test screen_stocks with valuation field filters.

    Validates that valuation fields like price_earnings_ttm can be used in filters
    and that results are returned correctly.
    """
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "price_earnings_ttm", "op": "less", "right": 20}],
            "columns": ["name", "close", "price_earnings_ttm"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert "total_count" in result

    # Verify we have rows returned
    assert len(result["rows"]) > 0

    # Verify columns are correct
    assert result["columns"] == ["name", "close", "price_earnings_ttm"]


@pytest.mark.asyncio
async def test_screen_stocks_with_balance_sheet_columns(mcp_client):
    """
    Test screen_stocks with balance sheet field columns.

    Validates that balance sheet fields like current_ratio and debt_to_equity
    can be retrieved as columns.
    """
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [],
            "columns": ["name", "current_ratio", "debt_to_equity"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result

    # Verify we have rows returned
    assert len(result["rows"]) > 0

    # Verify columns are correct
    assert result["columns"] == ["name", "current_ratio", "debt_to_equity"]


@pytest.mark.asyncio
async def test_screen_stocks_with_quality_score_filter(mcp_client):
    """
    Test screen_stocks with quality score field filter.

    Validates that quality score fields like piotroski_f_score_ttm can be used
    in filter conditions.
    """
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "piotroski_f_score_ttm", "op": "greater", "right": 5}],
            "columns": ["name", "close", "piotroski_f_score_ttm"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result

    # Verify we have rows returned
    assert len(result["rows"]) > 0


@pytest.mark.asyncio
async def test_screen_stocks_backward_compat_existing_filters(mcp_client):
    """
    Test backward compatibility with existing usage patterns.

    Uses the EXACT same parameters as the existing test_screen_stocks_basic_flow
    unit test (RSI < 30 filter, RSI/close columns) to ensure existing usage
    patterns still work after field expansion.
    """
    # This matches the call pattern from test_screen_stocks_basic_flow in test_pull_stock_data.py
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "RSI", "op": "less", "right": 30}],
            "columns": ["RSI", "close"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 5,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify same response shape as before
    assert "total_count" in result
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["RSI", "close"]

    # Verify pagination was applied
    assert "range" in result
    assert result["range"]["offset"] == 5
    assert result["range"]["limit"] == 10


@pytest.mark.asyncio
async def test_performance_return_filter(mcp_client):
    """Test filtering by monthly performance returns."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "Perf.1M", "op": "greater", "right": 0}],
            "columns": ["name", "close", "Perf.1M", "Perf.YTD"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "Perf.1M", "Perf.YTD"]

    # Verify we have at least one row (AAPL with Perf.1M=5.2)
    assert len(result["rows"]) >= 1


@pytest.mark.asyncio
async def test_gap_metric_filter(mcp_client):
    """Test filtering by gap events."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "gap", "op": "greater", "right": 0}],
            "columns": ["name", "close", "gap"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "gap"]

    # Verify we have at least one row (AAPL with gap=0.5)
    assert len(result["rows"]) >= 1


@pytest.mark.asyncio
async def test_price_extremes_columns(mcp_client):
    """Test selecting price extreme columns."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [],
            "columns": ["name", "close", "price_52_week_high", "price_52_week_low"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "price_52_week_high", "price_52_week_low"]

    # Verify we have rows returned
    assert len(result["rows"]) > 0


@pytest.mark.asyncio
async def test_dividend_yield_filter(mcp_client):
    """Test filtering by dividend yield."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [{"left": "dividend_yield_recent", "op": "greater", "right": 0}],
            "columns": ["name", "close", "dividend_yield_recent"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "dividend_yield_recent"]

    # Verify we have at least one row (AAPL with dividend_yield_recent=0.55)
    assert len(result["rows"]) >= 1


@pytest.mark.asyncio
async def test_ipo_price_columns(mcp_client):
    """Test selecting IPO price columns."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [],
            "columns": ["name", "close", "ipo_offer_price_usd"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "ipo_offer_price_usd"]

    # Verify we have rows returned
    assert len(result["rows"]) > 0


@pytest.mark.asyncio
async def test_advanced_technical_columns(mcp_client):
    """Test selecting advanced technical indicator columns."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [],
            "columns": ["name", "close", "W.R", "UO", "P.SAR"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "W.R", "UO", "P.SAR"]

    # Verify we have rows returned
    assert len(result["rows"]) > 0


@pytest.mark.asyncio
async def test_candlestick_pattern_filter(mcp_client):
    """Test selecting candlestick pattern columns."""
    response = await mcp_client.call_tool(
        "screen_stocks",
        args={
            "filters": [],
            "columns": ["name", "close", "Candle.Doji", "Candle.Hammer"],
            "markets": [],
            "sort_by": "",
            "sort_order": "desc",
            "nulls_first": False,
            "limit": 10,
            "offset": 0,
            "language": "en",
        },
    )

    result = json.loads(response[0].text)

    # Verify response structure
    assert "rows" in result
    assert "columns" in result
    assert result["columns"] == ["name", "close", "Candle.Doji", "Candle.Hammer"]

    # Verify we have rows returned
    assert len(result["rows"]) > 0
