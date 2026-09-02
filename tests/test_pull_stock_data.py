import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

import tv_mcp.tv_mcp as pull_stock_data


@pytest.fixture(autouse=True)
def stub_fastmcp(monkeypatch):
    """Prevent FastMCP decorator side effects during unit tests."""

    class MockFastMCP:
        def __init__(self, *_args, **_kwargs):
            pass

        def tool(self, func):
            return func

    monkeypatch.setattr(pull_stock_data, "FastMCP", MockFastMCP)
    # Ensure the existing module-level mcp uses the passthrough decorator
    if hasattr(pull_stock_data, "mcp"):
        pull_stock_data.mcp.tool = lambda func: func


@pytest.fixture
def mock_dataframe():
    row_template = SimpleNamespace
    rows = [
        row_template(
            ticker="AAPL",
            close=150,
            open=140,
            volume=2000000,
            average_volume_90d_calc=1500000,
            market_cap_basic=2000000000,
            price_earnings_growth_ttm=0.2,
            RSI=25,
            earnings_per_share_fy=3,
            expense_ratio=0.15,
        ),
        row_template(
            ticker="GOOG",
            close=2800,
            open=2750,
            volume=1000000,
            average_volume_90d_calc=900000,
            market_cap_basic=1500000000,
            price_earnings_growth_ttm=0.15,
            RSI=65,
            earnings_per_share_fy=4,
            expense_ratio=0.1,
        ),
    ]

    return pd.DataFrame([row.__dict__ for row in rows])


@pytest.fixture
def mock_query(monkeypatch, mock_dataframe):
    query_instance = MagicMock()
    query_instance.select.return_value = query_instance
    query_instance.order_by.return_value = query_instance
    query_instance.limit.return_value = query_instance
    query_instance.where.return_value = query_instance
    query_instance.where2.return_value = query_instance
    query_instance.offset.return_value = query_instance
    query_instance.set_markets.return_value = query_instance
    query_instance.set_tickers.return_value = query_instance
    query_instance.set_index.return_value = query_instance
    query_instance.query = {"columns": ["name", "close"], "markets": ["america"]}
    query_instance.url = "https://scanner.tradingview.com/america/scan"
    query_instance.get_scanner_data.return_value = (len(mock_dataframe), mock_dataframe)

    query_cls = MagicMock(return_value=query_instance)
    monkeypatch.setattr(pull_stock_data, "Query", query_cls)
    return query_instance


def test_deserialize_content_variants():
    json_content = [SimpleNamespace(text=json.dumps({"stock_data": []}))]
    plain_text_content = [SimpleNamespace(text="raw string")]

    assert pull_stock_data.deserialize_content(json_content) == {"stock_data": []}
    assert pull_stock_data.deserialize_content(plain_text_content) == "raw string"
    assert pull_stock_data.deserialize_content([]) is None


def test_format_query_result_keeps_dotted_field_names():
    """Regression: itertuples() renamed 'Value.Traded' to '_8'; to_dict must keep exact names."""
    df = pd.DataFrame([
        {"ticker": "NYSE:HWM", "name": "HWM", "Value.Traded": 1.4e9, "BB.upper": 260.1, "Perf.1M": 3.2},
    ])
    result = pull_stock_data._format_query_result((1, df), ["name", "Value.Traded", "BB.upper", "Perf.1M"])
    assert result["rows"] == [
        {"ticker": "NYSE:HWM", "name": "HWM", "Value.Traded": 1.4e9, "BB.upper": 260.1, "Perf.1M": 3.2}
    ]
    assert result["total_count"] == 1


def test_load_server_config_defaults_when_missing(tmp_path):
    config_path = tmp_path / "config.json"

    config = pull_stock_data._load_server_config(config_path)

    assert config["transport"] == "streamable-http"
    assert config["http"]["host"] == "127.0.0.1"
    assert config["http"]["port"] == 8000


def test_load_server_config_applies_overrides_and_validates(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {"transport": "streamable-http", "http": {"host": "0.0.0.0", "port": "9001"}}
        )
    )

    config = pull_stock_data._load_server_config(config_path)

    assert config["transport"] == "streamable-http"
    assert config["http"]["host"] == "0.0.0.0"
    assert config["http"]["port"] == 9001


def test_load_server_config_invalid_transport_raises(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"transport": "invalid"}))

    with pytest.raises(ValueError, match="Unsupported transport"):
        pull_stock_data._load_server_config(config_path)


def test_run_server_streamable_http(monkeypatch):
    mock_mcp = MagicMock()
    mock_mcp.name = "TestServer"
    monkeypatch.setattr(pull_stock_data, "mcp", mock_mcp)

    pull_stock_data._run_server(
        {"transport": "streamable-http", "http": {"host": "0.0.0.0", "port": 9000}, "stdio": {}}
    )

    # _run_server sets settings attributes, then calls run with transport only
    assert mock_mcp.settings.host == "0.0.0.0"
    assert mock_mcp.settings.port == 9000
    assert mock_mcp.settings.json_response is True
    mock_mcp.run.assert_called_once_with(transport="streamable-http")


def test_run_server_stdio(monkeypatch):
    mock_mcp = MagicMock()
    mock_mcp.name = "TestServer"
    monkeypatch.setattr(pull_stock_data, "mcp", mock_mcp)

    pull_stock_data._run_server({"transport": "stdio", "http": {}, "stdio": {}})

    mock_mcp.run.assert_called_once_with(transport="stdio")


def test_screen_stocks_basic_flow(mock_query):
    filters = [{"left": "RSI", "op": "less", "right": 30}]
    result = pull_stock_data._screen_stocks(
        filters=filters,
        columns=["RSI", "close"],
        markets=[],
        sort_by="",
        sort_order="desc",
        nulls_first=False,
        limit=10,
        offset=5,
        language="en"
    )

    assert result["total_count"] == 2
    assert len(result["rows"]) == 2
    assert result["columns"] == ["RSI", "close"]
    mock_query.where.assert_called_once()
    mock_query.order_by.assert_called_once()
    mock_query.limit.assert_called_once_with(10)
    mock_query.offset.assert_called_once_with(5)


def test_screen_stocks_or_logic_uses_where2(mock_query):
    filters = {"logic": "or", "conditions": [{"left": "RSI", "op": "less", "right": 30}, {"left": "close", "op": "greater", "right": 100}]}

    pull_stock_data._screen_stocks(
        filters=filters,
        columns=["RSI", "close"],
        markets=[],
        sort_by="",
        sort_order="desc",
        nulls_first=False,
        limit=50,
        offset=0,
        language="en"
    )

    mock_query.where2.assert_called_once()


def test_screen_stocks_validation_error_returns_error():
    with pytest.raises(ValueError, match="Unsupported field"):
        pull_stock_data._screen_stocks(
            filters=[{"left": "not_a_field", "op": "equal", "right": 1}],
            columns=[],
            markets=[],
            sort_by="",
            sort_order="desc",
            nulls_first=False,
            limit=50,
            offset=0,
            language="en"
        )


# ============================================================================
# Backward Compatibility Tests (FOUND-05)
# ============================================================================

# Original 39 fields that existed before field registry expansion
ORIGINAL_ALLOWED_FIELDS = frozenset({
    # Trend
    "EMA5", "EMA10", "EMA20", "EMA50", "EMA100", "EMA200", "ADX",
    "Ichimoku.BLine", "Ichimoku.CLine",
    # Momentum
    "RSI", "CCI20", "AO", "Stoch.K", "Stoch.D",
    # Volatility
    "ATR", "BB.upper", "BB.lower", "BBPower",
    # Volume & Flow
    "ChaikinMoneyFlow", "average_volume_10d_calc", "average_volume_30d_calc",
    "relative_volume_10d_calc",
    # Composite signals
    "Recommend.All", "Recommend.MA", "Recommend.Other",
    # Price & structure
    "close", "open", "high", "low", "change", "change_abs",
    # Common base fields
    "name", "volume", "market_cap_basic", "Value.Traded",
})


def test_screen_stocks_backward_compat_original_fields():
    """
    Verify all 39 original fields are still present in ALLOWED_SCREEN_FIELDS.

    This is FOUND-05: ensures field expansion never removes existing fields.
    Field registry expansion should only add fields, never remove them.
    """
    current_fields = pull_stock_data.ALLOWED_SCREEN_FIELDS

    missing_fields = ORIGINAL_ALLOWED_FIELDS - current_fields

    assert not missing_fields, (
        f"Field expansion must not remove existing fields. "
        f"Missing original fields: {sorted(missing_fields)}"
    )


def test_screen_stocks_all_params_still_required():
    """
    Verify that _screen_stocks function signature has not changed.

    All parameters must remain required (no optional params added) to ensure
    backward compatibility with existing callers.
    """
    # Try calling with each parameter omitted one at a time
    base_args = {
        "filters": [],
        "columns": [],
        "markets": [],
        "sort_by": "",
        "sort_order": "desc",
        "nulls_first": False,
        "limit": 10,
        "offset": 0,
        "language": "en",
    }

    for param_to_omit in base_args.keys():
        args = {k: v for k, v in base_args.items() if k != param_to_omit}

        with pytest.raises(TypeError, match=param_to_omit):
            pull_stock_data._screen_stocks(**args)


def test_validate_field_accepts_new_fundamental_fields():
    """
    Verify that _validate_field accepts the new fundamental fields.

    Tests a sample of new fields from different fundamental categories to ensure
    they are properly registered and validated.
    """
    new_fundamental_fields = [
        "price_earnings_ttm",  # valuation
        "ebitda_ttm",  # profitability
        "current_ratio",  # balance_sheet
        "piotroski_f_score_ttm",  # quality_scores
    ]

    for field in new_fundamental_fields:
        # Should not raise ValueError
        result = pull_stock_data._validate_field(field)
        assert result == field


def test_validate_field_still_rejects_unknown_fields():
    """
    Verify that _validate_field still rejects fields not in the registry.

    Ensures validation logic is still working correctly after field expansion.
    """
    with pytest.raises(ValueError, match="Unsupported field"):
        pull_stock_data._validate_field("definitely_not_a_field")


# ============================================================================
# Fuzzy Matching Validation Tests (PERF-05)
# ============================================================================

def test_validate_field_suggests_similar_fields():
    """Verify fuzzy matching suggests close field names for typos."""
    with pytest.raises(ValueError, match="Did you mean") as exc_info:
        pull_stock_data._validate_field("rsi")  # lowercase typo
    assert "RSI" in str(exc_info.value)


def test_validate_field_suggests_for_partial_names():
    """Verify fuzzy matching works for partial field names."""
    with pytest.raises(ValueError, match="Did you mean") as exc_info:
        pull_stock_data._validate_field("Perf.1")  # partial
    # Should suggest Perf.1M, Perf.1Y
    error_msg = str(exc_info.value)
    assert "Perf." in error_msg


def test_validate_field_no_suggestions_for_gibberish():
    """Verify no suggestions shown when input is completely unrelated."""
    with pytest.raises(ValueError, match="No similar fields found"):
        pull_stock_data._validate_field("xyzzy_completely_wrong_12345")
