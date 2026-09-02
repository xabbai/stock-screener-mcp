"""
TradingView Field Registry

This module contains canonical TradingView field names organized by category.
All field names match the official TradingView Screener API specification.

Reference: https://shner-elmo.github.io/TradingView-Screener/fields/stocks.html
"""

from typing import Any

# Field categories mapping to canonical TradingView field names
FIELD_CATEGORIES: dict[str, set[str]] = {
    "trend": {
        "EMA5",
        "EMA10",
        "EMA20",
        "EMA50",
        "EMA100",
        "EMA200",
        "ADX",
        "Ichimoku.BLine",
        "Ichimoku.CLine",
    },
    "momentum": {
        "RSI",
        "CCI20",
        "AO",
        "Stoch.K",
        "Stoch.D",
    },
    "volatility": {
        "ATR",
        "BB.upper",
        "BB.lower",
        "BBPower",
        "DonchCh20.Upper",
        "DonchCh20.Lower",
    },
    "volume_flow": {
        "ChaikinMoneyFlow",
        "average_volume_10d_calc",
        "average_volume_30d_calc",
        "average_volume_60d_calc",
        "relative_volume_10d_calc",
    },
    "composite_signals": {
        "Recommend.All",
        "Recommend.MA",
        "Recommend.Other",
    },
    "price_structure": {
        "close",
        "open",
        "high",
        "low",
        "change",
        "change_abs",
        "name",
        "volume",
        "market_cap_basic",
        "Value.Traded",
    },
    "valuation": {
        "price_earnings_ttm",
        "price_earnings_forward_fy",
        "price_book_ratio",
        "price_book_fq",
        "price_sales_ratio",
        "price_revenue_ttm",
        "price_free_cash_flow_ttm",
        "enterprise_value_ebitda_ttm",
    },
    "profitability": {
        "earnings_per_share_basic_ttm",
        "earnings_per_share_diluted_ttm",
        "net_income_ttm",
        "ebitda_ttm",
        "gross_margin_ttm",
        "operating_margin_ttm",
        "after_tax_margin",
    },
    "growth": {
        "total_revenue_yoy_growth_ttm",
        "earnings_per_share_diluted_yoy_growth_ttm",
        "free_cash_flow_yoy_growth_ttm",
        "total_revenue_qoq_growth_fq",
        "earnings_per_share_diluted_qoq_growth_fq",
    },
    "balance_sheet": {
        "total_assets",
        "total_debt",
        "shrhldrs_equity_fq",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
    },
    "quality_scores": {
        "piotroski_f_score_ttm",
        "altman_z_score_ttm",
    },
    "performance": {
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
    },
    "price_extremes": {
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
    },
    "gap": {
        "gap",
        "gap_up",
        "gap_down",
        "premarket_gap",
    },
    "dividend": {
        "dps_common_stock_prim_issue_fy",
        "dps_common_stock_prim_issue_fq",
        "dividend_yield_recent",
        "dividend_payout_ratio_fy",
        "dividend_payout_ratio_ttm",
        "dividends_paid",
        "ex_dividend_date_recent",
        "ex_dividend_date_upcoming",
    },
    "etf_fund": {
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
    },
    "ipo": {
        "ipo_offer_date",
        "ipo_offer_price_usd",
        "ipo_deal_amount_usd",
        "ipo_announcement_date",
        "ipo_price_range_usd_min",
        "ipo_price_range_usd_max",
    },
    "advanced_technical": {
        "W.R",
        "UO",
        "KltChnl.upper",
        "KltChnl.lower",
        "P.SAR",
        "HullMA9",
        "HullMA20",
        "HullMA200",
        "VWMA",
    },
    "candlestick_patterns": {
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
    },
}


def get_all_fields() -> set[str]:
    """
    Get the union of all field sets across all categories.

    Returns:
        Set[str]: Complete set of all supported TradingView field names.
    """
    all_fields: set[str] = set()
    for category_fields in FIELD_CATEGORIES.values():
        all_fields.update(category_fields)
    return all_fields


# Field metadata with type, range, units, and description for all fields.
# One field per line is intentional (greppable table); formatting is disabled for this block.
# fmt: off
FIELD_METADATA: dict[str, dict[str, Any]] = {
    # Trend fields
    "EMA5": {"type": "float", "range": None, "units": "currency", "description": "5-period Exponential Moving Average"},
    "EMA10": {"type": "float", "range": None, "units": "currency", "description": "10-period Exponential Moving Average"},
    "EMA20": {"type": "float", "range": None, "units": "currency", "description": "20-period Exponential Moving Average"},
    "EMA50": {"type": "float", "range": None, "units": "currency", "description": "50-period Exponential Moving Average"},
    "EMA100": {"type": "float", "range": None, "units": "currency", "description": "100-period Exponential Moving Average"},
    "EMA200": {"type": "float", "range": None, "units": "currency", "description": "200-period Exponential Moving Average"},
    "ADX": {"type": "float", "range": [0, 100], "units": "index", "description": "Average Directional Index - trend strength indicator"},
    "Ichimoku.BLine": {"type": "float", "range": None, "units": "currency", "description": "Ichimoku Kijun-sen (Base Line)"},
    "Ichimoku.CLine": {"type": "float", "range": None, "units": "currency", "description": "Ichimoku Tenkan-sen (Conversion Line)"},

    # Momentum fields
    "RSI": {"type": "float", "range": [0, 100], "units": "index", "description": "14-period Relative Strength Index"},
    "CCI20": {"type": "float", "range": None, "units": "index", "description": "20-period Commodity Channel Index"},
    "AO": {"type": "float", "range": None, "units": "index", "description": "Awesome Oscillator"},
    "Stoch.K": {"type": "float", "range": [0, 100], "units": "percent", "description": "Stochastic %K"},
    "Stoch.D": {"type": "float", "range": [0, 100], "units": "percent", "description": "Stochastic %D"},

    # Volatility fields
    "ATR": {"type": "float", "range": [0, None], "units": "currency", "description": "14-period Average True Range"},
    "BB.upper": {"type": "float", "range": None, "units": "currency", "description": "Upper Bollinger Band"},
    "BB.lower": {"type": "float", "range": None, "units": "currency", "description": "Lower Bollinger Band"},
    "BBPower": {"type": "float", "range": None, "units": "index", "description": "Bull/Bear Power indicator"},
    "DonchCh20.Upper": {"type": "float", "range": None, "units": "currency", "description": "Upper Donchian Channel (20-period highest high)"},
    "DonchCh20.Lower": {"type": "float", "range": None, "units": "currency", "description": "Lower Donchian Channel (20-period lowest low)"},

    # Volume & Flow fields
    "ChaikinMoneyFlow": {"type": "float", "range": [-1, 1], "units": "ratio", "description": "Chaikin Money Flow indicator"},
    "average_volume_10d_calc": {"type": "float", "range": [0, None], "units": "count", "description": "10-day average volume"},
    "average_volume_30d_calc": {"type": "float", "range": [0, None], "units": "count", "description": "30-day average volume"},
    "average_volume_60d_calc": {"type": "float", "range": [0, None], "units": "count", "description": "60-day average volume"},
    "relative_volume_10d_calc": {"type": "float", "range": [0, None], "units": "ratio", "description": "Relative volume vs 10-day average"},

    # Composite signals
    "Recommend.All": {"type": "float", "range": [-1, 1], "units": "index", "description": "Overall recommendation score"},
    "Recommend.MA": {"type": "float", "range": [-1, 1], "units": "index", "description": "Moving average recommendation score"},
    "Recommend.Other": {"type": "float", "range": [-1, 1], "units": "index", "description": "Other indicators recommendation score"},

    # Price & structure fields
    "close": {"type": "float", "range": [0, None], "units": "currency", "description": "Latest closing price"},
    "open": {"type": "float", "range": [0, None], "units": "currency", "description": "Opening price"},
    "high": {"type": "float", "range": [0, None], "units": "currency", "description": "Highest price"},
    "low": {"type": "float", "range": [0, None], "units": "currency", "description": "Lowest price"},
    "change": {"type": "float", "range": None, "units": "percent", "description": "Price change percentage"},
    "change_abs": {"type": "float", "range": None, "units": "currency", "description": "Absolute price change"},
    "name": {"type": "string", "range": None, "units": "string", "description": "Security name or ticker"},
    "volume": {"type": "int", "range": [0, None], "units": "count", "description": "Trading volume"},
    "market_cap_basic": {"type": "float", "range": [0, None], "units": "currency", "description": "Market capitalization"},
    "Value.Traded": {"type": "float", "range": [0, None], "units": "currency", "description": "Total value traded"},

    # Valuation fields
    "price_earnings_ttm": {"type": "float", "range": None, "units": "ratio", "description": "Trailing twelve months Price/Earnings ratio"},
    "price_earnings_forward_fy": {"type": "float", "range": None, "units": "ratio", "description": "Forward fiscal year Price/Earnings ratio"},
    "price_book_ratio": {"type": "float", "range": None, "units": "ratio", "description": "Price to Book ratio"},
    "price_book_fq": {"type": "float", "range": None, "units": "ratio", "description": "Most recent quarter Price to Book ratio"},
    "price_sales_ratio": {"type": "float", "range": None, "units": "ratio", "description": "Price to Sales ratio"},
    "price_revenue_ttm": {"type": "float", "range": None, "units": "ratio", "description": "Trailing twelve months Price to Revenue ratio"},
    "price_free_cash_flow_ttm": {"type": "float", "range": None, "units": "ratio", "description": "Trailing twelve months Price to Free Cash Flow ratio"},
    "enterprise_value_ebitda_ttm": {"type": "float", "range": None, "units": "ratio", "description": "Trailing twelve months Enterprise Value to EBITDA ratio"},

    # Profitability fields
    "earnings_per_share_basic_ttm": {"type": "float", "range": None, "units": "currency", "description": "Trailing twelve months basic earnings per share"},
    "earnings_per_share_diluted_ttm": {"type": "float", "range": None, "units": "currency", "description": "Trailing twelve months diluted earnings per share"},
    "net_income_ttm": {"type": "float", "range": None, "units": "currency", "description": "Trailing twelve months net income"},
    "ebitda_ttm": {"type": "float", "range": None, "units": "currency", "description": "Trailing twelve months EBITDA"},
    "gross_margin_ttm": {"type": "float", "range": None, "units": "percent", "description": "Trailing twelve months gross margin"},
    "operating_margin_ttm": {"type": "float", "range": None, "units": "percent", "description": "Trailing twelve months operating margin"},
    "after_tax_margin": {"type": "float", "range": None, "units": "percent", "description": "After-tax profit margin"},

    # Growth fields
    "total_revenue_yoy_growth_ttm": {"type": "float", "range": None, "units": "percent", "description": "Year-over-year revenue growth (TTM)"},
    "earnings_per_share_diluted_yoy_growth_ttm": {"type": "float", "range": None, "units": "percent", "description": "Year-over-year diluted EPS growth (TTM)"},
    "free_cash_flow_yoy_growth_ttm": {"type": "float", "range": None, "units": "percent", "description": "Year-over-year free cash flow growth (TTM)"},
    "total_revenue_qoq_growth_fq": {"type": "float", "range": None, "units": "percent", "description": "Quarter-over-quarter revenue growth (most recent quarter)"},
    "earnings_per_share_diluted_qoq_growth_fq": {"type": "float", "range": None, "units": "percent", "description": "Quarter-over-quarter diluted EPS growth (most recent quarter)"},

    # Balance sheet fields
    "total_assets": {"type": "float", "range": [0, None], "units": "currency", "description": "Total assets"},
    "total_debt": {"type": "float", "range": [0, None], "units": "currency", "description": "Total debt"},
    "shrhldrs_equity_fq": {"type": "float", "range": None, "units": "currency", "description": "Shareholders equity (most recent quarter)"},
    "current_ratio": {"type": "float", "range": [0, None], "units": "ratio", "description": "Current assets to current liabilities ratio"},
    "quick_ratio": {"type": "float", "range": [0, None], "units": "ratio", "description": "Quick assets to current liabilities ratio"},
    "debt_to_equity": {"type": "float", "range": [0, None], "units": "ratio", "description": "Total debt to equity ratio"},

    # Quality scores
    "piotroski_f_score_ttm": {"type": "int", "range": [0, 9], "units": "index", "description": "Piotroski F-Score financial strength indicator (0-9)"},
    "altman_z_score_ttm": {"type": "float", "range": None, "units": "index", "description": "Altman Z-Score bankruptcy risk indicator"},

    # Performance fields
    "Perf.W": {"type": "float", "range": None, "units": "percent", "description": "Weekly performance return"},
    "Perf.1M": {"type": "float", "range": None, "units": "percent", "description": "1-month performance return"},
    "Perf.3M": {"type": "float", "range": None, "units": "percent", "description": "3-month performance return"},
    "Perf.6M": {"type": "float", "range": None, "units": "percent", "description": "6-month performance return"},
    "Perf.3Y": {"type": "float", "range": None, "units": "percent", "description": "3-year performance return"},
    "Perf.5Y": {"type": "float", "range": None, "units": "percent", "description": "5-year performance return"},
    "Perf.YTD": {"type": "float", "range": None, "units": "percent", "description": "Year-to-date performance return"},
    "Perf.5D": {"type": "float", "range": None, "units": "percent", "description": "5-day performance return"},
    "Perf.Y": {"type": "float", "range": None, "units": "percent", "description": "1-year performance return"},
    "Perf.10Y": {"type": "float", "range": None, "units": "percent", "description": "10-year performance return"},

    # Price extremes fields
    "price_52_week_high": {"type": "float", "range": [0, None], "units": "currency", "description": "52-week high price"},
    "price_52_week_low": {"type": "float", "range": [0, None], "units": "currency", "description": "52-week low price"},
    "High.All": {"type": "float", "range": [0, None], "units": "currency", "description": "All-time high price"},
    "Low.All": {"type": "float", "range": [0, None], "units": "currency", "description": "All-time low price"},
    "High.1M": {"type": "float", "range": [0, None], "units": "currency", "description": "1-month high price"},
    "Low.1M": {"type": "float", "range": [0, None], "units": "currency", "description": "1-month low price"},
    "High.3M": {"type": "float", "range": [0, None], "units": "currency", "description": "3-month high price"},
    "Low.3M": {"type": "float", "range": [0, None], "units": "currency", "description": "3-month low price"},
    "High.6M": {"type": "float", "range": [0, None], "units": "currency", "description": "6-month high price"},
    "Low.6M": {"type": "float", "range": [0, None], "units": "currency", "description": "6-month low price"},

    # Gap fields
    "gap": {"type": "float", "range": None, "units": "percent", "description": "Gap percentage from previous close"},
    "gap_up": {"type": "boolean", "range": None, "units": "boolean", "description": "Whether stock gapped up"},
    "gap_down": {"type": "boolean", "range": None, "units": "boolean", "description": "Whether stock gapped down"},
    "premarket_gap": {"type": "float", "range": None, "units": "percent", "description": "Premarket gap percentage"},

    # Dividend fields
    "dps_common_stock_prim_issue_fy": {"type": "float", "range": [0, None], "units": "currency", "description": "Dividends per share - fiscal year"},
    "dps_common_stock_prim_issue_fq": {"type": "float", "range": [0, None], "units": "currency", "description": "Dividends per share - most recent quarter"},
    "dividend_yield_recent": {"type": "float", "range": [0, None], "units": "percent", "description": "Forward dividend yield"},
    "dividend_payout_ratio_fy": {"type": "float", "range": [0, None], "units": "percent", "description": "Dividend payout ratio - fiscal year"},
    "dividend_payout_ratio_ttm": {"type": "float", "range": [0, None], "units": "percent", "description": "Dividend payout ratio - TTM"},
    "dividends_paid": {"type": "float", "range": None, "units": "currency", "description": "Total dividends paid - fiscal year"},
    "ex_dividend_date_recent": {"type": "date", "range": None, "units": "date", "description": "Most recent ex-dividend date"},
    "ex_dividend_date_upcoming": {"type": "date", "range": None, "units": "date", "description": "Upcoming ex-dividend date"},

    # ETF/Fund fields
    "aum": {"type": "float", "range": [0, None], "units": "currency", "description": "Assets under management"},
    "nav": {"type": "float", "range": [0, None], "units": "currency", "description": "Net asset value per share"},
    "expense_ratio": {"type": "float", "range": [0, None], "units": "percent", "description": "Annual fund operating expenses"},
    "etf_holdings_count": {"type": "int", "range": [0, None], "units": "count", "description": "Number of holdings in ETF"},
    "nav_discount_premium": {"type": "float", "range": None, "units": "percent", "description": "NAV discount/premium"},
    "fund_flows.1M": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for 1 month period"},
    "fund_flows.1Y": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for 1 year period"},
    "fund_flows.3M": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for 3 month period"},
    "fund_flows.3Y": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for 3 year period"},
    "fund_flows.5Y": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for 5 year period"},
    "fund_flows.YTD": {"type": "float", "range": None, "units": "currency", "description": "Fund flow for year-to-date period"},

    # IPO fields
    "ipo_offer_date": {"type": "date", "range": None, "units": "date", "description": "IPO offer date"},
    "ipo_offer_price_usd": {"type": "float", "range": [0, None], "units": "currency", "description": "IPO offer price in USD"},
    "ipo_deal_amount_usd": {"type": "float", "range": [0, None], "units": "currency", "description": "Total IPO deal amount"},
    "ipo_announcement_date": {"type": "date", "range": None, "units": "date", "description": "IPO announcement date"},
    "ipo_price_range_usd_min": {"type": "float", "range": [0, None], "units": "currency", "description": "Minimum IPO price range"},
    "ipo_price_range_usd_max": {"type": "float", "range": [0, None], "units": "currency", "description": "Maximum IPO price range"},

    # Advanced technical indicator fields
    "W.R": {"type": "float", "range": [-100, 0], "units": "index", "description": "Williams %R 14-period oscillator (-100 to 0)"},
    "UO": {"type": "float", "range": [0, 100], "units": "index", "description": "Ultimate Oscillator (7, 14, 28 periods)"},
    "KltChnl.upper": {"type": "float", "range": None, "units": "currency", "description": "Upper Keltner Channel"},
    "KltChnl.lower": {"type": "float", "range": None, "units": "currency", "description": "Lower Keltner Channel"},
    "P.SAR": {"type": "float", "range": [0, None], "units": "currency", "description": "Parabolic Stop and Reverse level"},
    "HullMA9": {"type": "float", "range": None, "units": "currency", "description": "9-period Hull Moving Average"},
    "HullMA20": {"type": "float", "range": None, "units": "currency", "description": "20-period Hull Moving Average"},
    "HullMA200": {"type": "float", "range": None, "units": "currency", "description": "200-period Hull Moving Average"},
    "VWMA": {"type": "float", "range": None, "units": "currency", "description": "20-period Volume Weighted Moving Average"},

    # Candlestick pattern fields
    "Candle.Doji": {"type": "float", "range": None, "units": "signal", "description": "Doji candlestick pattern signal"},
    "Candle.Doji.Dragonfly": {"type": "float", "range": None, "units": "signal", "description": "Dragonfly Doji pattern signal"},
    "Candle.Doji.Gravestone": {"type": "float", "range": None, "units": "signal", "description": "Gravestone Doji pattern signal"},
    "Candle.Engulfing.Bullish": {"type": "float", "range": None, "units": "signal", "description": "Bullish Engulfing pattern signal"},
    "Candle.Engulfing.Bearish": {"type": "float", "range": None, "units": "signal", "description": "Bearish Engulfing pattern signal"},
    "Candle.Hammer": {"type": "float", "range": None, "units": "signal", "description": "Hammer candlestick pattern signal"},
    "Candle.InvertedHammer": {"type": "float", "range": None, "units": "signal", "description": "Inverted Hammer pattern signal"},
    "Candle.Harami.Bullish": {"type": "float", "range": None, "units": "signal", "description": "Bullish Harami pattern signal"},
    "Candle.Harami.Bearish": {"type": "float", "range": None, "units": "signal", "description": "Bearish Harami pattern signal"},
    "Candle.MorningStar": {"type": "float", "range": None, "units": "signal", "description": "Morning Star pattern signal"},
    "Candle.EveningStar": {"type": "float", "range": None, "units": "signal", "description": "Evening Star pattern signal"},
}
# fmt: on


def get_field_metadata(field_name: str) -> dict[str, Any] | None:
    """
    Get metadata for a field, or None if field not found.

    Args:
        field_name: The TradingView field name to look up.

    Returns:
        Dictionary with type, range, units, and description keys, or None if not found.
    """
    return FIELD_METADATA.get(field_name)
