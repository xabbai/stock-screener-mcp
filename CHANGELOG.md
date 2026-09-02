# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/). Until 1.0.0, minor versions may change the tool contract; such changes are called out explicitly.

## [Unreleased]

### Added
- `DISCLAIMER.md`: the maintainer makes no claim that returned data is correct or up to date and accepts no liability for wrong data from the tool or TradingView; referenced from README and release notes.

## [0.1.0] - 2026-09-02

First public release (draft until the `v0.1.0` tag exists).

### Added
- `screen_stocks` MCP tool exposing 135 TradingView screener fields in 19 categories (trend, momentum, volatility, volume, ratings, price, valuation, profitability, growth, balance sheet, quality scores, performance, price extremes, gaps, dividends, ETF/fund, IPO, advanced technical, candlestick patterns).
- AND/OR filter trees with nesting, 24 filter operators including field-to-field comparisons and crossovers, sorting, pagination (`limit` ≤ 500, `offset`), market selection, language.
- Case-insensitive and fuzzy suggestions for unknown field names.
- `tv-mcp-server` console script with `--transport {stdio,streamable-http}`, `--host`, `--port`, `--config`, `--version`; optional `config.json` and `STOCK_TOOLS_CONFIG`.
- Optional authenticated data via Chrome cookies (`cookies` extra) controlled by `TV_MCP_BROWSER_COOKIES=auto|on|off`.
- Generated field reference (`docs/field-reference.md`), validated client configurations (Claude Desktop, Claude Code, Cursor, VS Code), troubleshooting guide, demo script and GIF.
- CI (lint, tests on Python 3.11–3.13, docs check, build inspection, clean-environment smoke), CodeQL, Dependabot, community files (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue and PR templates).

### Fixed
- Result rows kept exact TradingView field names; dotted fields such as `Value.Traded` or `BB.upper` were previously returned under positional keys (`_8`).
- Fresh installs no longer resolve `mcp` 2.x (which removed FastMCP); dependency pinned to `mcp>=1.26,<2`.
- Five documented field names that never existed in TradingView (`Donchian.upper`, `Donchian.lower`, `Volume`, `RelativeVolume`, `Perf.1Y`) replaced by real, live-verified fields (`DonchCh20.Upper`, `DonchCh20.Lower`, `average_volume_60d_calc`, `Perf.Y`, `Perf.10Y`).

### Changed
- Source distribution now contains only source, tests, license and docs needed to run tests (was 497 files including vendored repositories).
- FastMCP server name is `tv-mcp`; `field_registry` is imported as a package module.

[Unreleased]: https://github.com/xabbai/tv-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xabbai/tv-mcp/releases/tag/v0.1.0
