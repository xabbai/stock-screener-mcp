#!/usr/bin/env python3
"""
Build docs/assets/demo.gif from a real screen_stocks result.

    uv run --with pillow python scripts/make_demo_gif.py capture   # runs the quick-start screen (network)
    uv run --with pillow python scripts/make_demo_gif.py render    # renders the GIF from the capture (offline)

The GIF is a rendered storyboard (prompt -> tool call -> result -> tagline) using genuinely captured
output; it is not a screen recording of a GUI client. See docs/demo-script.md for recording a real client.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ASSETS = ROOT / "docs" / "assets"
CAPTURE = ASSETS / "demo-capture.json"
GIF = ASSETS / "demo.gif"

PROMPT = (
    "Find US stocks above their 200-day EMA, with RSI below 40, market cap above $2B, "
    "and relative volume above 1.5. Return the top 20 by traded value."
)
ARGS = {
    "filters": [
        {"left": "close", "op": "greater", "right": "EMA200"},
        {"left": "RSI", "op": "less", "right": 40},
        {"left": "market_cap_basic", "op": "greater", "right": 2_000_000_000},
        {"left": "relative_volume_10d_calc", "op": "greater", "right": 1.5},
    ],
    "columns": ["name", "close", "RSI", "EMA200", "market_cap_basic", "relative_volume_10d_calc", "Value.Traded"],
    "markets": ["america"],
    "sort_by": "Value.Traded",
    "sort_order": "desc",
    "nulls_first": False,
    "limit": 20,
    "offset": 0,
    "language": "en",
}


def capture() -> None:
    os.environ["STOCK_SCREENER_MCP_BROWSER_COOKIES"] = "off"  # never record with a personal session
    from stock_screener_mcp.server import _screen_stocks

    result = _screen_stocks(**ARGS)
    rows = [
        {
            "name": r["name"],
            "close": round(r["close"], 2),
            "RSI": round(r["RSI"], 1),
            "EMA200": round(r["EMA200"], 2),
            "market_cap_basic": r["market_cap_basic"],
            "relative_volume_10d_calc": round(r["relative_volume_10d_calc"], 2),
            "Value.Traded": r["Value.Traded"],
        }
        for r in result["rows"][:5]
    ]
    CAPTURE.write_text(
        json.dumps({"captured": date.today().isoformat(), "total_count": result["total_count"], "rows": rows}, indent=2)
    )
    print(f"captured {len(rows)} rows of {result['total_count']} -> {CAPTURE}")


def _human(n: float) -> str:
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= div:
            return f"{n / div:.1f}{unit}"
    return f"{n:.0f}"


def render() -> None:
    from PIL import Image, ImageDraw, ImageFont

    data = json.loads(CAPTURE.read_text())
    W, H = 960, 560
    BG, FG, DIM, ACC, OK = (24, 26, 32), (230, 232, 236), (140, 146, 158), (99, 179, 237), (126, 211, 33)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    try:
        font = ImageFont.truetype(font_path, 18)
        bold = ImageFont.truetype(font_path.replace(".ttf", "-Bold.ttf"), 18)
        big = ImageFont.truetype(font_path.replace(".ttf", "-Bold.ttf"), 30)
    except OSError:
        font = bold = big = ImageFont.load_default()
    LH = 26

    def wrap(text: str, width: int = 88) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > width:
                lines.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        return lines + [cur]

    def frame(lines: list[tuple[str, tuple, object]]) -> Image.Image:
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 40], fill=(36, 39, 48))
        d.ellipse([14, 13, 28, 27], fill=(255, 95, 86))
        d.ellipse([36, 13, 50, 27], fill=(255, 189, 46))
        d.ellipse([58, 13, 72, 27], fill=(39, 201, 63))
        d.text((90, 10), "MCP client  ·  stock-screener-mcp  ·  screen_stocks", fill=DIM, font=font)
        y = 58
        for text, color, f in lines:
            d.text((24, y), text, fill=color, font=f)
            y += LH if f is not big else 44
        return im

    frames: list[tuple[Image.Image, int]] = []
    prompt_lines = wrap(PROMPT)

    # Beat 1: the user types the prompt (6 frames)
    full = " ".join(prompt_lines)
    for i in range(1, 7):
        cut = full[: int(len(full) * i / 6)]
        lines = [("You", ACC, bold)] + [(ln, FG, font) for ln in wrap(cut)]
        frames.append((frame(lines), 650))

    # Beat 2: tool call (4 frames)
    base = [("You", ACC, bold)] + [(ln, FG, font) for ln in prompt_lines] + [("", FG, font)]
    call = [("→ screen_stocks(", OK, bold)]
    filt = [
        '    filters=[{"left": "close", "op": "greater", "right": "EMA200"},',
        '             {"left": "RSI", "op": "less", "right": 40},',
        '             {"left": "market_cap_basic", "op": "greater", "right": 2000000000},',
        '             {"left": "relative_volume_10d_calc", "op": "greater", "right": 1.5}],',
        '    markets=["america"], sort_by="Value.Traded", sort_order="desc", limit=20)',
    ]
    for i in range(1, 5):
        shown = filt[: i + 1] if i < 4 else filt
        frames.append((frame(base + call + [(ln, FG, font) for ln in shown]), 1100))

    # Beat 3: result rows appear one by one (5 frames + hold)
    header = f"{'name':<8}{'close':>10}{'RSI':>8}{'EMA200':>10}{'mkt cap':>10}{'rel vol':>9}{'traded':>10}"
    rows = [
        f"{r['name']:<8}{r['close']:>10.2f}{r['RSI']:>8.1f}{r['EMA200']:>10.2f}"
        f"{_human(r['market_cap_basic']):>10}{r['relative_volume_10d_calc']:>9.2f}{_human(r['Value.Traded']):>10}"
        for r in data["rows"]
    ]
    res_head = base + call + [(ln, FG, font) for ln in filt] + [("", FG, font)]
    res_head += [(f"← {data['total_count']} matches · top {len(rows)} by traded value · {data['captured']}", OK, bold)]
    res_head += [(header, DIM, bold)]
    for i in range(1, len(rows) + 1):
        frames.append((frame(res_head + [(ln, FG, font) for ln in rows[:i]]), 800))
    frames.append((frame(res_head + [(ln, FG, font) for ln in rows]), 3200))

    # Beat 4: tagline
    tag = [("", FG, font)] * 5 + [
        ("135 TradingView fields. One MCP tool.", FG, big),
        ("", FG, font),
        ("github.com/xabbai/stock-screener-mcp  ·  MIT  ·  not affiliated with TradingView", DIM, font),
        ("Screening data only — not investment advice.", DIM, font),
    ]
    frames.append((frame(tag), 5000))

    images = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for f, _ in frames]
    durations = [d for _, d in frames]
    images[0].save(GIF, save_all=True, append_images=images[1:], duration=durations, loop=0, optimize=True)
    total = sum(durations) / 1000
    size = GIF.stat().st_size
    print(f"wrote {GIF}: {len(images)} frames, {total:.1f}s, {size / 1024:.0f} KB")
    assert total <= 30, "demo must be 30 seconds or less"
    assert size < 2_000_000, "demo must stay under 2 MB"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"capture": capture, "render": render}.get(cmd, lambda: sys.exit(__doc__))()
