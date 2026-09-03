# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| Latest release on the `main` branch (0.x) | Yes |
| Older tags | No — please upgrade |

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

1. Preferred: use GitHub's private reporting at <https://github.com/xabbai/stock-screener-mcp/security/advisories/new> ("Report a vulnerability").
2. Fallback: email the maintainer at the address listed in `pyproject.toml` with the subject `stock-screener-mcp security`.

Include: affected version or commit, environment (OS, Python, client), reproduction steps, and impact. Do not include real cookies, session tokens, or account data; describe them instead.

You will receive an acknowledgement within 5 business days. Confirmed issues are fixed in a new release and disclosed in the release notes after a fix is available; reporters are credited if they wish.

## Scope and design notes

- stock-screener-mcp runs locally and holds no server-side secrets or accounts.
- Optional authenticated data reads your Chrome `tradingview.com` cookies **in memory only**, via the `rookiepy` extra, and only when `TV_MCP_BROWSER_COOKIES` is `auto` (extra installed) or `on`. Cookies are never written to disk or logs. Set `off` to disable.
- The Streamable HTTP transport binds to `127.0.0.1` by default and has no authentication; do not expose it to untrusted networks.
- Dependencies are pinned with upper bounds in `pyproject.toml` and locked in `uv.lock`; Dependabot keeps them current once enabled.
