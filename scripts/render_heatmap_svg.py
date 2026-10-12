"""Render an animated GitHub-style contribution heatmap from cached JSON."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "contrib-heatmap.svg"
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, STEP = 12, 3, 15
PAD, LABEL = 24, 34


def grid(days: list[dict]) -> list[list[dict | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    column: list[dict | None] = [None] * ((first.weekday() + 1) % 7)
    columns = []
    for day in days:
        column.append(day)
        if len(column) == 7:
            columns.append(column)
            column = []
    if column:
        columns.append(column + [None] * (7 - len(column)))
    return columns


def render(data: dict) -> str:
    columns = grid(data["days"])
    width = PAD * 2 + LABEL + len(columns) * STEP
    height = 238
    left, top = PAD + LABEL, 62
    animation_css = ".d{opacity:1}" if os.environ.get("STATIC") == "1" else ".d{opacity:0;animation:pop .38s cubic-bezier(.2,.8,.2,1) forwards}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<style>@keyframes pop{{from{{opacity:0;transform:translateY(-7px)}}to{{opacity:1;transform:none}}}}{animation_css}@media(prefers-reduced-motion:reduce){{.d{{opacity:1;animation:none}}}}</style>',
        f'<rect width="{width}" height="{height}" rx="14" fill="#0a0e14"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="13" fill="none" stroke="#1f6feb" stroke-opacity=".55"/>',
        f'<line y1="34" x2="{width}" y2="34" stroke="#1f6feb" stroke-opacity=".35"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{PAD+i*17}" cy="17" r="5" fill="{color}"/>')
    parts.append(f'<text x="{width/2}" y="22" text-anchor="middle" fill="#7d8590" font-size="12">sarvesh@github: ~/contributions --graph</text>')

    seen = set()
    for ci, col in enumerate(columns):
        for day in col:
            if day:
                date = dt.date.fromisoformat(day["date"])
                key = (date.year, date.month)
                if key not in seen and date.day <= 7:
                    seen.add(key)
                    parts.append(f'<text x="{left+ci*STEP}" y="53" fill="#7d8590" font-size="10">{date:%b}</text>')
                break
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{PAD}" y="{top+row*STEP+10}" fill="#7d8590" font-size="9">{label}</text>')

    for ci, col in enumerate(columns):
        for ri, day in enumerate(col):
            if day is None:
                continue
            delay = ci * .018 + ri * .035
            count = day["count"]
            level = max(0, min(int(day.get("level", 0)), 4))
            title = html.escape(f'{day["date"]}: {count} contribution' + ("s" if count != 1 else ""))
            parts.append(f'<rect class="d" style="animation-delay:{delay:.3f}s" x="{left+ci*STEP}" y="{top+ri*STEP}" width="{CELL}" height="{CELL}" rx="2.5" fill="{COLORS[level]}"><title>{title}</title></rect>')

    total = data["total_contributions"]
    current = data["current_streak"]["length"]
    longest = data["longest_streak"]["length"]
    best = data["best_day"]
    parts.extend([
        f'<line y1="178" x2="{width}" y2="178" stroke="#1f6feb" stroke-opacity=".25"/>',
        f'<text x="{PAD}" y="204" fill="#7d8590" font-size="13"><tspan fill="#39d353" font-weight="700">{total:,}</tspan> contributions · current streak <tspan fill="#58a6ff" font-weight="700">{current} days</tspan> · longest <tspan fill="#58a6ff" font-weight="700">{longest} days</tspan></text>',
        f'<text x="{width-PAD}" y="224" text-anchor="end" fill="#7d8590" font-size="11">best day <tspan fill="#f2cc60">{best["count"]}</tspan> · updated daily</text>',
        '</svg>',
    ])
    return "".join(parts)


if __name__ == "__main__":
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUTPUT.write_text(render(payload), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
