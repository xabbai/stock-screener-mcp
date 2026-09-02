#!/usr/bin/env python3
"""Render docs/assets/social-preview.png (1280x640) for the GitHub social preview.

uv run --with pillow python scripts/make_social_preview.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "docs" / "assets" / "social-preview.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    W, H = 1280, 640
    im = Image.new("RGB", (W, H), (24, 26, 32))
    d = ImageDraw.Draw(im)
    # left accent bar
    d.rectangle([0, 0, 14, H], fill=(99, 179, 237))
    d.text((70, 70), "tv-mcp", fill=(140, 146, 158), font=font(MONO, 34))
    d.text(
        (70, 130), "TradingView Stock Screener", fill=(235, 237, 240), font=font(FONT.replace(".ttf", "-Bold.ttf"), 64)
    )
    d.text((70, 205), "for AI Agents", fill=(235, 237, 240), font=font(FONT.replace(".ttf", "-Bold.ttf"), 64))
    d.text((70, 320), "135 TradingView fields. One MCP tool.", fill=(126, 211, 33), font=font(MONO, 40))
    d.text(
        (70, 400),
        "Screen global stocks from Claude, Cursor, VS Code and any MCP client:",
        fill=(200, 204, 210),
        font=font(FONT, 28),
    )
    d.text(
        (70, 440),
        "fundamentals · technicals · momentum · volume · valuation · dividends · ETFs",
        fill=(200, 204, 210),
        font=font(FONT, 28),
    )
    d.text(
        (70, 560),
        "github.com/xabbai/tv-mcp   ·   MIT   ·   not affiliated with TradingView",
        fill=(140, 146, 158),
        font=font(MONO, 24),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, optimize=True)
    print(f"wrote {OUT} {im.size} {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
