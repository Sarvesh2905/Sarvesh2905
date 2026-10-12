"""Create the animated terminal-style ASCII portrait used in the profile README."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "sarvesh.jpg"
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "sarvesh-ascii.svg"

COLS = int(os.environ.get("ASCII_COLS", "132"))
ROWS = round(COLS * 8 / 15)
RAMP = " .`:-=+*cs#%@"
CANVAS = 840
TITLE = 42
STATUS = 42
PAD = 22
ART_W = CANVAS - 2 * PAD
ART_H = CANVAS - TITLE - STATUS - 2 * PAD
CELL_W = ART_W / COLS
CELL_H = ART_H / ROWS


def prepare(image: Image.Image) -> Image.Image:
    """Crop the headshot around Sarvesh and boost its terminal contrast."""
    w, h = image.size
    # Proportional coordinates keep the crop stable if the source is resized.
    crop = image.crop((int(w * 0.18), int(h * 0.24), int(w * 0.82), h))
    # Terminal glyphs are taller than they are wide, so this intentionally
    # compresses the portrait vertically before the font restores its shape.
    crop = crop.resize((COLS, ROWS), Image.Resampling.LANCZOS).convert("L")
    crop = crop.filter(ImageFilter.GaussianBlur(0.35))
    crop = ImageEnhance.Contrast(crop).enhance(1.75)
    crop = ImageEnhance.Brightness(crop).enhance(1.12)
    return crop


def ascii_rows(image: Image.Image) -> list[str]:
    pixels = image.load()
    rows: list[str] = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            lum = pixels[x, y] / 255
            # Bright surfaces disappear; this visually separates the subject.
            if lum > 0.83:
                line.append(" ")
            else:
                index = round((1 - lum**1.18) * (len(RAMP) - 1))
                line.append(RAMP[max(0, min(index, len(RAMP) - 1))])
        rows.append("".join(line))
    return rows


def render(rows: list[str]) -> str:
    static = os.environ.get("STATIC") == "1"
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        '<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#070b12"/></linearGradient></defs>',
        f'<rect width="{CANVAS}" height="{CANVAS}" rx="18" fill="url(#bg)"/>',
        f'<rect x="1" y="1" width="{CANVAS-2}" height="{CANVAS-2}" rx="17" fill="none" stroke="#1f6feb" stroke-opacity=".55" stroke-width="2"/>',
        f'<line y1="{TITLE}" x2="{CANVAS}" y2="{TITLE}" stroke="#1f6feb" stroke-opacity=".35"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        pieces.append(f'<circle cx="{PAD + i*20}" cy="21" r="6" fill="{color}"/>')
    pieces.append(f'<text x="{CANVAS/2}" y="27" text-anchor="middle" fill="#7d8590" font-size="15">sarvesh@github: ~/portrait.sh</text>')

    top = TITLE + PAD
    font_size = CELL_H * 0.91
    row_duration = 5.4 / ROWS
    for index, line in enumerate(rows):
        y = top + index * CELL_H + CELL_H * 0.79
        safe = html.escape(line)
        text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.2f}" fill="#c9d1d9" '
                f'font-size="{font_size:.2f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')
        if static:
            pieces.append(text)
            continue
        delay = index * row_duration
        pieces.append(
            f'<clipPath id="row{index}"><rect x="{PAD}" y="{top + index*CELL_H:.2f}" '
            f'width="0" height="{CELL_H + .5:.2f}"><animate attributeName="width" from="0" '
            f'to="{ART_W}" begin="{delay:.3f}s" dur="{row_duration:.3f}s" fill="freeze"/></rect></clipPath>'
            f'<g clip-path="url(#row{index})">{text}</g>'
        )

    baseline = CANVAS - 18
    pieces.extend([
        f'<line y1="{CANVAS-STATUS}" x2="{CANVAS}" y2="{CANVAS-STATUS}" stroke="#1f6feb" stroke-opacity=".35"/>',
        f'<text x="{PAD}" y="{baseline}" fill="#7d8590" font-size="16">sarvesh@github:~$ whoami <tspan fill="#39d353">Sarvesh P</tspan></text>',
        f'<rect x="335" y="{baseline-14}" width="9" height="17" fill="#39d353"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect>',
        '<style>@media(prefers-reduced-motion:reduce){animate{display:none}}</style>',
        '</svg>',
    ])
    return "".join(pieces)


if __name__ == "__main__":
    portrait = prepare(Image.open(SOURCE).convert("RGB"))
    OUTPUT.write_text(render(ascii_rows(portrait)), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
