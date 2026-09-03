# Contributing to stock-screener-mcp

Thanks for helping make stock screening easier for AI agents. This guide covers setup, tests, style, and the two most common contributions: adding fields and adding client/market support.

## Development setup

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/) (recommended) or pip.

```bash
git clone https://github.com/xabbai/stock-screener-mcp.git
cd stock-screener-mcp
uv sync --extra test            # creates .venv with runtime + test deps
uv run stock-screener-mcp --help
```

pip alternative:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
```

Optional extras: `--extra cookies` / `.[cookies]` for authenticated data via Chrome cookies.

## Running tests

| What | Command | Notes |
|------|---------|-------|
| Unit + docs tests (fast, offline) | `uv run pytest -m "not network"` | Run before every commit |
| Live API tests | `uv run pytest -m network` | Hits TradingView's public scanner (~1–2 min) |
| Quick-start through a real MCP client | `uv run pytest tests/test_quickstart.py` | Launches `stock-screener-mcp --transport stdio` |
| Clean-environment install check | `bash scripts/clean_env_smoke.sh` | Builds the wheel, installs into a temp venv, runs the quick start |
| Field reference up to date | `uv run python scripts/gen_field_reference.py --check` | Regenerate without `--check` after registry changes |

CI runs the offline suite, the build, and the field-reference check; network tests are opt-in.

## Project layout

```
src/stock_screener_mcp/server.py          MCP server, screen_stocks tool, CLI
src/stock_screener_mcp/field_registry.py  FIELD_CATEGORIES, FIELD_METADATA — the single source of truth for fields
tests/                        unit, e2e (mocked), network, quickstart, docs-sync tests
docs/                         field reference (generated), client configs, troubleshooting, audit
scripts/                      gen_field_reference.py, clean_env_smoke.sh
```

## Adding a TradingView field

1. Confirm the exact field name in the [community field list](https://shner-elmo.github.io/TradingView-Screener/fields/stocks.html) or by running a live query:
   ```bash
   uv run python -c "from tradingview_screener import Query; print(Query().select('name','Perf.Y').limit(2).get_scanner_data())"
   ```
2. Add the name to the right category in `FIELD_CATEGORIES` and an entry in `FIELD_METADATA` (`type`, `range`, `units`, `description`).
3. Add it to the matching category line in the `screen_stocks` docstring in `stock_screener_mcp.py` (the docstring must stay under 300 lines; `tests/test_docs_sync.py` checks it equals the registry).
4. Regenerate docs: `uv run python scripts/gen_field_reference.py`.
5. Update the count in `tests/test_field_registry.py::test_registry_totals_match_public_claims` and, if the README states a total, the README.
6. Run `uv run pytest -m "not network"`. Add the field to a network test if it has special availability (ETF-only, IPO-only).

Never rename or remove an existing field: the backward-compatibility test guards the original set, and users depend on exact names.

## Adding market or client support

- **Markets** are passed straight to TradingView; nothing to add in code. If a market behaves differently (missing fields, different limits), document it in `docs/field-reference.md` intro or `docs/troubleshooting.md` and add a network test in `tests/test_field_registry.py` alongside the cross-market tests.
- **MCP clients**: add a validated config to `docs/client-configs.md`. State how it was validated (which command was run, whether the GUI was exercised).

## Code style

- PEP 8, 4-space indentation, type hints on public and helper functions, concise docstrings.
- Helpers stay private (leading underscore); the only public MCP tool is `screen_stocks`.
- No new runtime dependencies without an issue discussing it first; keep `mcp<2` until the server is migrated to the 2.x API.
- Keep behavior backward compatible: the `screen_stocks` signature and result shape are part of the public contract.

## Commits and pull requests

- Small, focused PRs. One field batch, one bug fix, one doc change.
- Commit messages: short imperative summary, optionally prefixed (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Fill in the PR template: what/why, commands you ran, compatibility notes, and whether docs were regenerated.
- Do not include browser cookies, tokens, `.env` files, logs with session data, or vendored third-party checkouts.

## Reporting bugs and security issues

Use the issue forms. For anything security-related (cookie handling, credential exposure, dependency vulnerabilities), follow [SECURITY.md](SECURITY.md) and do not open a public issue.

## License

By contributing you agree that your contributions are licensed under the MIT License.
