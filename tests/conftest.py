import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest
import pytest_asyncio
from mcp.server.fastmcp import FastMCP

import stock_screener_mcp.server as pull_stock_data


class _EmbeddedClient:
    """Minimal in-process client that directly calls registered tools on the FastMCP instance."""

    def __init__(self, mcp_server: FastMCP):
        self._mcp = mcp_server

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def call_tool(self, name, args=None, **_kwargs):
        tool = self._mcp._tool_manager.get_tool(name)  # type: ignore[attr-defined]
        if not tool:
            raise ValueError(f"Unknown tool {name}")
        # Call the underlying function directly to avoid transport/anyio overhead in tests
        result = tool.fn(**(args or {}))  # type: ignore[misc]
        return [SimpleNamespace(text=json.dumps(result, default=str))]

    async def list_tools(self):
        return self._mcp._tool_manager.list_tools()  # type: ignore[attr-defined]


@pytest.fixture
def mock_e2e_query(monkeypatch):
    """Provide a mock Query that returns deterministic data for e2e tests."""
    rows = [
        SimpleNamespace(
            ticker="AAPL",
            name="Apple",
            close=150,
            open=140,
            volume=2_000_000,
            market="america",
            average_volume_90d_calc=1_500_000,
            market_cap_basic=2_000_000_000,
            price_earnings_growth_ttm=0.2,
            SMA12=149,
            EMA12=148,
            RSI=45,
            earnings_per_share_fy=3.1,
            expense_ratio=0.12,
            # Fundamental fields for e2e tests
            price_earnings_ttm=15.2,
            ebitda_ttm=5_000_000,
            current_ratio=1.8,
            debt_to_equity=0.5,
            piotroski_f_score_ttm=7,
            # Performance fields for e2e tests
            **{"Perf.1M": 5.2, "Perf.YTD": 12.3, "gap": 0.5, "price_52_week_high": 180.0, "price_52_week_low": 120.0},
            # Specialized metrics for e2e tests
            dividend_yield_recent=0.55,
            aum=None,  # Not an ETF
            ipo_offer_price_usd=22.0,
            # Advanced technical and candlestick pattern fields for e2e tests
            **{"W.R": -25.5, "UO": 55.3, "P.SAR": 148.5, "VWMA": 149.2, "Candle.Doji": 0, "Candle.Hammer": 1},
        ),
        SimpleNamespace(
            ticker="GOOG",
            name="Alphabet",
            close=120,
            open=118,
            volume=1_000_000,
            market="america",
            average_volume_90d_calc=900_000,
            market_cap_basic=1_800_000_000,
            price_earnings_growth_ttm=0.15,
            SMA12=119,
            EMA12=118,
            RSI=55,
            earnings_per_share_fy=5.2,
            expense_ratio=0.10,
            # Fundamental fields for e2e tests
            price_earnings_ttm=18.5,
            ebitda_ttm=6_500_000,
            current_ratio=2.1,
            debt_to_equity=0.3,
            piotroski_f_score_ttm=8,
            # Performance fields for e2e tests
            **{"Perf.1M": -2.1, "Perf.YTD": 8.7, "gap": -0.3, "price_52_week_high": 150.0, "price_52_week_low": 100.0},
            # Specialized metrics for e2e tests
            dividend_yield_recent=None,  # No dividend
            aum=None,
            ipo_offer_price_usd=85.0,
            # Advanced technical and candlestick pattern fields for e2e tests
            **{"W.R": -65.2, "UO": 42.1, "P.SAR": 121.0, "VWMA": 119.8, "Candle.Doji": 1, "Candle.Hammer": 0},
        ),
    ]

    mock_df = pd.DataFrame([row.__dict__ for row in rows])

    mock_query = MagicMock()
    mock_query.query = {"columns": ["name", "close"], "markets": ["america"]}
    mock_query.url = "https://scanner.tradingview.com/america/scan"

    def select(*cols):
        mock_query.query["columns"] = [c for c in cols]
        return mock_query

    mock_query.select.side_effect = select
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.where2.return_value = mock_query
    mock_query.set_markets.return_value = mock_query
    mock_query.set_tickers.return_value = mock_query
    mock_query.set_index.return_value = mock_query

    def get_scanner_data(**_kwargs):
        return (len(rows), mock_df)

    mock_query.get_scanner_data.side_effect = get_scanner_data

    monkeypatch.setattr(pull_stock_data, "Query", MagicMock(return_value=mock_query))
    monkeypatch.setattr(pull_stock_data, "logging", pull_stock_data.logging)
    return mock_query


@pytest_asyncio.fixture
async def mcp_client(mock_e2e_query):
    """In-process client for e2e tests without network."""
    # Use embedded direct-call client to keep behavior consistent with prior FastMCP Client stub
    async with _EmbeddedClient(pull_stock_data.mcp) as client:
        yield client
