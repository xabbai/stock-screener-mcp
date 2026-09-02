"""
Tests for the TradingView Field Registry.

This module validates the field registry structure, required field coverage,
and provides network-based tests for field discovery automation and schema validation.
"""

import pytest
from tradingview_screener import Query

from tv_mcp.field_registry import FIELD_CATEGORIES, FIELD_METADATA, get_all_fields


# ============================================================================
# Category Structure Validation
# ============================================================================


def test_all_categories_are_non_empty():
    """Verify that every category in FIELD_CATEGORIES has at least 1 field."""
    for category_name, fields in FIELD_CATEGORIES.items():
        assert len(fields) > 0, f"Category '{category_name}' must have at least one field"


def test_no_duplicate_fields_across_categories():
    """Verify that no field appears in more than one category."""
    seen_fields = {}
    for category_name, fields in FIELD_CATEGORIES.items():
        for field in fields:
            if field in seen_fields:
                pytest.fail(
                    f"Field '{field}' appears in both '{seen_fields[field]}' "
                    f"and '{category_name}' categories"
                )
            seen_fields[field] = category_name


def test_get_all_fields_matches_category_union():
    """Verify that get_all_fields() returns the union of all category sets."""
    expected_fields = set()
    for category_fields in FIELD_CATEGORIES.values():
        expected_fields.update(category_fields)

    actual_fields = get_all_fields()

    assert actual_fields == expected_fields, (
        f"get_all_fields() should return the exact union of all category fields. "
        f"Missing: {expected_fields - actual_fields}, "
        f"Extra: {actual_fields - expected_fields}"
    )


# ============================================================================
# Required Field Coverage Tests
# ============================================================================


def test_registry_totals_match_public_claims():
    """The README and tool docstring advertise 135 fields across 19 categories."""
    assert len(FIELD_CATEGORIES) == 19
    assert len(get_all_fields()) == 135
    assert len(FIELD_METADATA) == 135


def test_phantom_field_names_are_absent():
    """Names that were once documented but never existed in TradingView must not be in the registry."""
    phantom = {"Donchian.upper", "Donchian.lower", "Volume", "RelativeVolume", "Perf.1Y"}
    assert not (phantom & get_all_fields())


def test_launch_audit_added_fields_present():
    """Fields added in the launch audit (live-verified 2026-09-02) sit in the expected categories."""
    assert {"DonchCh20.Upper", "DonchCh20.Lower"} <= FIELD_CATEGORIES["volatility"]
    assert "average_volume_60d_calc" in FIELD_CATEGORIES["volume_flow"]
    assert {"Perf.Y", "Perf.10Y"} <= FIELD_CATEGORIES["performance"]


def test_valuation_fields_present():
    """Assert that all required valuation fields exist in the registry."""
    required_valuation_fields = {
        "price_earnings_ttm",
        "price_earnings_forward_fy",
        "price_book_ratio",
        "price_book_fq",
        "price_sales_ratio",
        "price_revenue_ttm",
        "price_free_cash_flow_ttm",
        "enterprise_value_ebitda_ttm",
    }

    valuation_category = FIELD_CATEGORIES.get("valuation", set())

    missing_fields = required_valuation_fields - valuation_category
    assert not missing_fields, (
        f"Missing required valuation fields: {missing_fields}"
    )


def test_profitability_fields_present():
    """Assert that all required profitability fields exist in the registry."""
    required_profitability_fields = {
        "earnings_per_share_basic_ttm",
        "earnings_per_share_diluted_ttm",
        "net_income_ttm",
        "ebitda_ttm",
        "gross_margin_ttm",
        "operating_margin_ttm",
        "after_tax_margin",
    }

    profitability_category = FIELD_CATEGORIES.get("profitability", set())

    missing_fields = required_profitability_fields - profitability_category
    assert not missing_fields, (
        f"Missing required profitability fields: {missing_fields}"
    )


def test_growth_fields_present():
    """Assert that all required growth fields exist in the registry."""
    required_growth_fields = {
        "total_revenue_yoy_growth_ttm",
        "earnings_per_share_diluted_yoy_growth_ttm",
        "free_cash_flow_yoy_growth_ttm",
        "total_revenue_qoq_growth_fq",
        "earnings_per_share_diluted_qoq_growth_fq",
    }

    growth_category = FIELD_CATEGORIES.get("growth", set())

    missing_fields = required_growth_fields - growth_category
    assert not missing_fields, (
        f"Missing required growth fields: {missing_fields}"
    )


def test_balance_sheet_fields_present():
    """Assert that all required balance sheet fields exist in the registry."""
    required_balance_sheet_fields = {
        "total_assets",
        "total_debt",
        "shrhldrs_equity_fq",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
    }

    balance_sheet_category = FIELD_CATEGORIES.get("balance_sheet", set())

    missing_fields = required_balance_sheet_fields - balance_sheet_category
    assert not missing_fields, (
        f"Missing required balance sheet fields: {missing_fields}"
    )


def test_quality_scores_present():
    """Assert that all required quality score fields exist in the registry."""
    required_quality_fields = {
        "piotroski_f_score_ttm",
        "altman_z_score_ttm",
    }

    quality_category = FIELD_CATEGORIES.get("quality_scores", set())

    missing_fields = required_quality_fields - quality_category
    assert not missing_fields, (
        f"Missing required quality score fields: {missing_fields}"
    )


def test_performance_fields_present():
    """Assert that all required performance fields exist in the registry."""
    required_performance_fields = {
        "Perf.W",
        "Perf.1M",
        "Perf.3M",
        "Perf.6M",
        "Perf.3Y",
        "Perf.5Y",
        "Perf.YTD",
        "Perf.5D",
        "Perf.Y",
        "Perf.10Y",
    }

    performance_category = FIELD_CATEGORIES.get("performance", set())

    missing_fields = required_performance_fields - performance_category
    assert not missing_fields, (
        f"Missing required performance fields: {missing_fields}"
    )


def test_price_extremes_fields_present():
    """Assert that all required price extreme fields exist in the registry."""
    required_price_extremes_fields = {
        "price_52_week_high",
        "price_52_week_low",
        "High.All",
        "Low.All",
        "High.1M",
        "Low.1M",
        "High.3M",
        "Low.3M",
        "High.6M",
        "Low.6M",
    }

    price_extremes_category = FIELD_CATEGORIES.get("price_extremes", set())

    missing_fields = required_price_extremes_fields - price_extremes_category
    assert not missing_fields, (
        f"Missing required price extreme fields: {missing_fields}"
    )


def test_gap_fields_present():
    """Assert that all required gap fields exist in the registry."""
    required_gap_fields = {
        "gap",
        "gap_up",
        "gap_down",
        "premarket_gap",
    }

    gap_category = FIELD_CATEGORIES.get("gap", set())

    missing_fields = required_gap_fields - gap_category
    assert not missing_fields, (
        f"Missing required gap fields: {missing_fields}"
    )


def test_dividend_fields_present():
    """Assert that all required dividend fields exist in the registry."""
    required_dividend_fields = {
        "dps_common_stock_prim_issue_fy",
        "dps_common_stock_prim_issue_fq",
        "dividend_yield_recent",
        "dividend_payout_ratio_fy",
        "dividend_payout_ratio_ttm",
        "dividends_paid",
        "ex_dividend_date_recent",
        "ex_dividend_date_upcoming",
    }

    dividend_category = FIELD_CATEGORIES.get("dividend", set())

    missing_fields = required_dividend_fields - dividend_category
    assert not missing_fields, (
        f"Missing required dividend fields: {missing_fields}"
    )


def test_etf_fund_fields_present():
    """Assert that all required ETF/fund fields exist in the registry."""
    required_etf_fund_fields = {
        "aum",
        "nav",
        "expense_ratio",
        "etf_holdings_count",
        "nav_discount_premium",
        "fund_flows.1M",
        "fund_flows.1Y",
        "fund_flows.3M",
        "fund_flows.3Y",
        "fund_flows.5Y",
        "fund_flows.YTD",
    }

    etf_fund_category = FIELD_CATEGORIES.get("etf_fund", set())

    missing_fields = required_etf_fund_fields - etf_fund_category
    assert not missing_fields, (
        f"Missing required ETF/fund fields: {missing_fields}"
    )


def test_ipo_fields_present():
    """Assert that all required IPO fields exist in the registry."""
    required_ipo_fields = {
        "ipo_offer_date",
        "ipo_offer_price_usd",
        "ipo_deal_amount_usd",
        "ipo_announcement_date",
        "ipo_price_range_usd_min",
        "ipo_price_range_usd_max",
    }

    ipo_category = FIELD_CATEGORIES.get("ipo", set())

    missing_fields = required_ipo_fields - ipo_category
    assert not missing_fields, (
        f"Missing required IPO fields: {missing_fields}"
    )


def test_advanced_technical_fields_present():
    """Assert that all required advanced technical indicator fields exist in the registry."""
    required_advanced_technical_fields = {
        "W.R",
        "UO",
        "KltChnl.upper",
        "KltChnl.lower",
        "P.SAR",
        "HullMA9",
        "HullMA20",
        "HullMA200",
        "VWMA",
    }

    advanced_technical_category = FIELD_CATEGORIES.get("advanced_technical", set())

    missing_fields = required_advanced_technical_fields - advanced_technical_category
    assert not missing_fields, (
        f"Missing required advanced technical indicator fields: {missing_fields}"
    )


def test_candlestick_patterns_fields_present():
    """Assert that all required candlestick pattern fields exist in the registry."""
    required_candlestick_patterns_fields = {
        "Candle.Doji",
        "Candle.Doji.Dragonfly",
        "Candle.Doji.Gravestone",
        "Candle.Engulfing.Bullish",
        "Candle.Engulfing.Bearish",
        "Candle.Hammer",
        "Candle.InvertedHammer",
        "Candle.Harami.Bullish",
        "Candle.Harami.Bearish",
        "Candle.MorningStar",
        "Candle.EveningStar",
    }

    candlestick_patterns_category = FIELD_CATEGORIES.get("candlestick_patterns", set())

    missing_fields = required_candlestick_patterns_fields - candlestick_patterns_category
    assert not missing_fields, (
        f"Missing required candlestick pattern fields: {missing_fields}"
    )


# ============================================================================
# Field Metadata Coverage Test (PERF-04)
# ============================================================================


def test_all_fields_have_metadata():
    """Verify every registered field has metadata with required keys (PERF-04)."""
    all_fields = get_all_fields()
    required_keys = {"type", "range", "units", "description"}

    missing_metadata = all_fields - set(FIELD_METADATA.keys())
    assert not missing_metadata, f"Fields missing metadata: {missing_metadata}"

    for field, meta in FIELD_METADATA.items():
        missing_keys = required_keys - set(meta.keys())
        assert not missing_keys, f"Field '{field}' missing metadata keys: {missing_keys}"


# ============================================================================
# Field Discovery Automation Test (FOUND-01)
# ============================================================================


@pytest.mark.network
def test_field_discovery_flags_staleness():
    """
    Validate that all fields in our registry work with the TradingView API.

    This test catches when we have fields that TradingView no longer supports.
    Runs in batches of 10 fields, then identifies specific invalid fields if a batch fails.

    Marked with @pytest.mark.network - skipped by default, run explicitly with `pytest -m network`.
    """
    all_fields = list(get_all_fields())
    batch_size = 10
    invalid_fields = []

    # Test fields in batches to speed up discovery
    for i in range(0, len(all_fields), batch_size):
        batch = all_fields[i:i + batch_size]

        try:
            query = Query().select(*batch).limit(1)
            query.get_scanner_data()
        except Exception as batch_error:
            # Batch failed - test each field individually to identify the culprit
            for field in batch:
                try:
                    query = Query().select(field).limit(1)
                    query.get_scanner_data()
                except Exception:
                    invalid_fields.append(field)

    assert not invalid_fields, (
        f"The following fields in our registry cause TradingView API errors: {invalid_fields}. "
        f"These fields may have been deprecated or renamed by TradingView. "
        f"Update FIELD_CATEGORIES in field_registry.py to remove or rename them."
    )


# ============================================================================
# Schema/Type Validation Test (FOUND-02)
# ============================================================================


@pytest.mark.network
def test_field_types_are_numeric_or_string():
    """
    Validate that field values from TradingView API are expected types.

    Samples 2-3 representative fields from each category and verifies returned values
    are int, float, str, or None. This catches unexpected types that would break
    downstream processing.

    Marked with @pytest.mark.network - skipped by default, run explicitly with `pytest -m network`.
    """
    # Sample 2-3 fields from each category
    sample_fields = []
    for category_name, fields in FIELD_CATEGORIES.items():
        field_list = list(fields)
        sample_count = min(3, len(field_list))
        sample_fields.extend(field_list[:sample_count])

    # Query TradingView with sample fields, limit 5 rows
    query = Query().select(*sample_fields).limit(5)
    result = query.get_scanner_data()

    if not isinstance(result, tuple) or len(result) != 2:
        pytest.fail(f"Unexpected TradingView response format: {type(result)}")

    _, data_frame = result
    rows = list(data_frame.itertuples())

    # Validate types for each field in each row
    invalid_types = []
    for row in rows:
        row_dict = row._asdict()
        for field in sample_fields:
            if field in row_dict:
                value = row_dict[field]
                # Allow int, float, str, or None
                if value is not None and not isinstance(value, (int, float, str)):
                    invalid_types.append({
                        "field": field,
                        "value": value,
                        "type": type(value).__name__,
                        "ticker": getattr(row, "ticker", "unknown"),
                    })

    assert not invalid_types, (
        f"Found unexpected field types from TradingView API: {invalid_types}. "
        f"All field values should be int, float, str, or None."
    )


# ============================================================================
# Performance Benchmark Test (TEST-04)
# ============================================================================


@pytest.mark.network
def test_expanded_field_set_performance():
    """Verify no performance degradation with 90 fields vs original set (TEST-04)."""
    import time

    # Time a query with a small field set (5 fields)
    small_fields = ["close", "open", "volume", "RSI", "ATR"]
    start = time.time()
    Query().select(*small_fields).limit(5).get_scanner_data()
    small_time = time.time() - start

    # Time a query with a larger field set (20 fields from multiple categories)
    large_fields = list(get_all_fields())[:20]
    start = time.time()
    Query().select(*large_fields).limit(5).get_scanner_data()
    large_time = time.time() - start

    # Large set should not take more than 3x the small set time
    # (generous margin for network variability)
    assert large_time < small_time * 3, (
        f"Performance degradation detected: {large_time:.2f}s vs {small_time:.2f}s "
        f"(ratio: {large_time/small_time:.1f}x, max allowed: 3x)"
    )


# ============================================================================
# Market-Specific Field Validation (SPEC-06)
# ============================================================================


@pytest.mark.network
def test_field_compatibility_across_markets():
    """
    Test field compatibility across different TradingView markets.

    Tests representative fields from each category against america, crypto, forex,
    and bonds markets. Documents which field categories work in which markets rather
    than treating incompatibilities as failures (since dividend, ETF, and IPO fields
    only apply to stock markets).

    Marked with @pytest.mark.network - skipped by default, run explicitly with `pytest -m network`.
    """
    markets = ["america", "crypto", "forex", "bonds"]
    compatibility_report = {}

    # Sample 2-3 representative fields from each category
    for category_name, fields in FIELD_CATEGORIES.items():
        field_list = list(fields)
        sample_count = min(3, len(field_list))
        sample_fields = field_list[:sample_count]

        compatibility_report[category_name] = {}

        for market in markets:
            market_results = []
            for field in sample_fields:
                try:
                    query = Query().set_markets(market).select(field).limit(1)
                    query.get_scanner_data()
                    market_results.append((field, True))
                except Exception:
                    market_results.append((field, False))

            # Calculate compatibility percentage for this category in this market
            compatible_count = sum(1 for _, success in market_results if success)
            total_count = len(market_results)
            compatibility_report[category_name][market] = {
                "compatible": compatible_count,
                "total": total_count,
                "fields": market_results,
            }

    # Print compatibility matrix for documentation
    print("\n=== Field Category Compatibility Across Markets ===\n")
    for category_name, market_data in compatibility_report.items():
        print(f"\n{category_name.upper()}:")
        for market, data in market_data.items():
            compatible = data["compatible"]
            total = data["total"]
            percentage = (compatible / total * 100) if total > 0 else 0
            status = "✓" if percentage == 100 else "✗" if percentage == 0 else "~"
            print(f"  {status} {market:10s}: {compatible}/{total} ({percentage:.0f}%)")
            # Show which specific fields failed if any
            if compatible < total:
                failed_fields = [f for f, success in data["fields"] if not success]
                print(f"      Failed: {', '.join(failed_fields)}")

    # Test always passes - it's for documentation purposes
    assert compatibility_report, "Compatibility report should have been generated"


@pytest.mark.network
def test_all_categories_have_api_compatible_fields():
    """
    Strict test: ALL registered fields MUST work with the america market.

    Tests all fields (not just samples) in batches of 10 against the america market.
    This is the primary market for the tool, so zero failures are acceptable.

    Marked with @pytest.mark.network - skipped by default, run explicitly with `pytest -m network`.
    """
    all_fields = list(get_all_fields())
    batch_size = 10
    invalid_fields = []

    # Test all fields in batches against america market
    for i in range(0, len(all_fields), batch_size):
        batch = all_fields[i:i + batch_size]

        try:
            query = Query().set_markets("america").select(*batch).limit(1)
            query.get_scanner_data()
        except Exception as batch_error:
            # Batch failed - test each field individually to identify the culprit
            for field in batch:
                try:
                    query = Query().set_markets("america").select(field).limit(1)
                    query.get_scanner_data()
                except Exception:
                    invalid_fields.append(field)

    assert not invalid_fields, (
        f"The following fields failed for the 'america' market: {invalid_fields}. "
        f"All registered fields MUST work with the primary america market. "
        f"Update FIELD_CATEGORIES in field_registry.py to fix or remove these fields."
    )
