# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/). Until 1.0.0, minor versions may change the tool contract; such changes are called out explicitly.

## [Unreleased]

Nothing yet beyond 0.1.0 below.

## [0.1.0] - Unreleased

First public release. Replace "Unreleased" with the tag date when `v0.1.0` is created.

### Added
- `screen_stocks` MCP tool exposing 135 TradingView screener fields in 19 categories (trend, momentum, volatility, volume, ratings, price, valuation, profitability, growth, balance sheet, quality scores, performance, price extremes, gaps, dividends, ETF/fund, IPO, advanced technical, candlestick patterns).
- AND/OR filter trees with nesting, 24 filter operators including field-to-field comparisons and crossovers, sorting, pagination (`limit` 1–500, `offset` ≥ 0), market selection, language.
- Case-insensitive and fuzzy suggestions for unknown field names.
- `stock-screener-mcp` console script with `--transport {stdio,streamable-http}`, `--host`, `--port`, `--config`, `--version`; optional `config.json` and `STOCK_SCREENER_MCP_CONFIG`.
- Optional authenticated data via Chrome cookies (`cookies` extra) controlled by `STOCK_SCREENER_MCP_BROWSER_COOKIES=auto|on|off`.
- `DISCLAIMER.md`: the maintainer makes no claim that returned data is correct, complete, or up to date and accepts no liability for wrong, delayed, or missing data from the tool or TradingView; referenced from README and release notes.
- Documentation: README landing page, generated field reference (`docs/field-reference.md`), validated client configurations (Claude Desktop, Claude Code, Cursor, VS Code), troubleshooting guide, demo script and GIF.
- Community files: CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant 2.1), SECURITY, issue forms, PR template.
- CI (ruff, tests on Python 3.11–3.13, generated-docs check, build inspection, clean-environment smoke), CodeQL, Dependabot, and a tag-driven release workflow that drafts a GitHub release with SHA-256 checksums.

### Fixed
- Result rows keep exact TradingView field names; dotted fields such as `Value.Traded` or `BB.upper` were previously returned under positional keys (`_8`).
- Fresh installs no longer resolve `mcp` 2.x (which removed FastMCP); dependency pinned to `mcp>=1.26,<2` (and `tradingview-screener>=3.0,<4`).
- Five documented field names that never existed in TradingView (`Donchian.upper`, `Donchian.lower`, `Volume`, `RelativeVolume`, `Perf.1Y`) replaced by real, live-verified fields (`DonchCh20.Upper`, `DonchCh20.Lower`, `average_volume_60d_calc`, `Perf.Y`, `Perf.10Y`).

### Changed
- Source distribution now contains only source, tests, license and the files needed to run tests (previously 497 files including vendored repositories).
- License and project URLs declared in standard `pyproject.toml` tables.
- Project renamed from `tv-mcp` to `stock-screener-mcp` everywhere: distribution, repository, FastMCP server name, `--version` output, import package (`tv_mcp` → `stock_screener_mcp`, module `stock_screener_mcp.server`), console script (`tv-mcp-server` → `stock-screener-mcp`) and environment variables (`TV_MCP_BROWSER_COOKIES` → `STOCK_SCREENER_MCP_BROWSER_COOKIES`, `STOCK_TOOLS_CONFIG` → `STOCK_SCREENER_MCP_CONFIG`). No compatibility aliases. `tv-mcp` is taken on PyPI and a "tradingview-" name carries trademark risk.
- `field_registry` is imported as a package module.

<!-- Link references become valid once the v0.1.0 tag exists. -->
[Unreleased]: https://github.com/xabbai/stock-screener-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xabbai/stock-screener-mcp/releases/tag/v0.1.0
