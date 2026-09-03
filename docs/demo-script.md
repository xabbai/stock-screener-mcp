# Demo script

A 30-second demo that proves the core value: a natural-language request becomes one `screen_stocks` call and a ranked table.

## Storyboard (4 beats, ≤ 30 s)

| Beat | Seconds | What is on screen |
|------|---------|-------------------|
| 1. Ask | 0–6 | The MCP client with the prompt being typed |
| 2. Call | 6–12 | The client's tool-call panel: `screen_stocks` with the four filters visible |
| 3. Result | 12–24 | A compact table: name, close, RSI, EMA200, market cap, relative volume, traded value (5–10 rows) |
| 4. Tagline | 24–30 | "135 TradingView fields. One MCP tool." + repository URL |

## The prompt

> Find US stocks above their 200-day EMA, with RSI below 40, market cap above $2B, and relative volume above 1.5. Return the top 20 by traded value.

## Expected tool call

```json
{
  "filters": [
    {"left": "close", "op": "greater", "right": "EMA200"},
    {"left": "RSI", "op": "less", "right": 40},
    {"left": "market_cap_basic", "op": "greater", "right": 2000000000},
    {"left": "relative_volume_10d_calc", "op": "greater", "right": 1.5}
  ],
  "columns": ["name", "close", "RSI", "EMA200", "market_cap_basic", "relative_volume_10d_calc", "Value.Traded"],
  "markets": ["america"],
  "sort_by": "Value.Traded",
  "sort_order": "desc",
  "nulls_first": false,
  "limit": 20,
  "offset": 0,
  "language": "en"
}
```

Clients word the call slightly differently; the four filters, `markets: ["america"]`, and sorting by `Value.Traded` are what must be visible.

## Expected result shape

`total_count` in the tens (varies intraday), `rows` with the seven requested columns plus `ticker`, sorted by `Value.Traded` descending. See `docs/assets/demo-capture.json` for a real capture.

## Prerequisites for recording a GUI client

1. Client configured per [client-configs.md](client-configs.md) with `"env": {"TV_MCP_BROWSER_COOKIES": "off"}` — never record with a personal TradingView session.
2. A fresh chat with no prior messages; window sized to roughly 1280×800 so text stays legible at README width.
3. Screen-recording tool: macOS QuickTime/Cmd-Shift-5, Windows Xbox Game Bar or OBS, Linux OBS or `wf-recorder`/`ffmpeg -f x11grab`.

## Recording steps (Claude Desktop or Cursor)

1. Start recording. Type the prompt; do not paste (typing is beat 1).
2. When the tool-call panel appears, expand it so the filters are readable (beat 2). Hold 3–4 s.
3. Let the answer render; if the client summarizes in prose, ask "show as a table" before recording, or pick the run where it tables the result (beat 3). Hold on the table 5 s.
4. Stop recording. Add the tagline as a final title card in your editor, or reuse the last frame of `docs/assets/demo.gif`.

## Converting to GIF

```bash
ffmpeg -i demo.mov -vf "fps=8,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer" -loop 0 docs/assets/demo.gif
```

Keep it under 2 MB; trim dead time so the whole thing is ≤ 30 s.

## Redaction checklist (before committing any asset)

- [ ] No account name, email, avatar, or workspace name visible in the client chrome
- [ ] No browser window, cookie banner, or Chrome profile visible
- [ ] `TV_MCP_BROWSER_COOKIES=off` was set (public data), and no wording implies real-time data
- [ ] No other MCP servers or private tool names in the client's tool list
- [ ] No local filesystem paths with usernames in the tool-call panel
- [ ] The result table shows tickers and numbers only (public market data)

## The rendered fallback (current README asset)

`docs/assets/demo.gif` is generated, not screen-recorded: `scripts/make_demo_gif.py capture` runs the real screen (public data) and stores the top rows in `docs/assets/demo-capture.json`; `render` draws the four beats with Pillow. Regenerate after significant output changes:

```bash
uv run --with pillow python scripts/make_demo_gif.py capture
uv run --with pillow python scripts/make_demo_gif.py render
```

Alt text used in README: "Demo: an MCP client asks for oversold large-cap US stocks above their 200-day EMA, stock-screener-mcp calls screen_stocks and returns a ranked table". Replace the rendered GIF with a real GUI recording when one passes the checklist above.
