"""Generate the animated terminal identity card shown beside the portrait."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "profile-card.svg"
W = H = 840
PAD = 38

ROWS = [
    ("name", "Sarvesh P", "#39d353"),
    ("role", "Full-Stack + AI Developer", "#58a6ff"),
    ("now", "Bright Pathways, Singapore", "#f2cc60"),
    ("education", "B.Tech IT '27 · CGPA 8.31", "#e6edf3"),
    ("stack", "React · Node · Python · MongoDB", "#a371f7"),
    ("ai", "LLMs · RAG · automation · agents", "#ff7b72"),
    ("location", "India · remote", "#e6edf3"),
    ("status", "building things that ship", "#39d353"),
]


def render() -> str:
    static = os.environ.get("STATIC") == "1"
    animation_css = ".line{opacity:1}" if static else ".line{opacity:0;animation:show .42s cubic-bezier(.2,.8,.2,1) forwards}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<style>{animation_css}@keyframes show{{from{{opacity:0;transform:translateX(-16px)}}to{{opacity:1;transform:none}}}}@media(prefers-reduced-motion:reduce){{.line{{opacity:1;animation:none}}}}</style>',
        '<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#070b12"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="#1f6feb" stroke-opacity=".55" stroke-width="2"/>',
        '<line y1="42" x2="840" y2="42" stroke="#1f6feb" stroke-opacity=".35"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{PAD + i*20}" cy="21" r="6" fill="{color}"/>')
    parts.extend([
        '<text x="420" y="27" text-anchor="middle" fill="#7d8590" font-size="15">sarvesh@github: ~/whoami</text>',
        '<text class="line" style="animation-delay:.10s" x="38" y="100" fill="#39d353" font-size="27" font-weight="700">$ neofetch sarvesh</text>',
        '<line class="line" style="animation-delay:.20s" x1="38" y1="126" x2="802" y2="126" stroke="#30363d"/>',
    ])
    y = 184
    for i, (key, value, color) in enumerate(ROWS):
        delay = .32 + i * .16
        parts.append(
            f'<g class="line" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD}" y="{y}" fill="#7d8590" font-size="24">{html.escape(key)}</text>'
            f'<text x="245" y="{y}" fill="{color}" font-size="22">{html.escape(value)}</text></g>'
        )
        y += 68
    parts.extend([
        '<g class="line" style="animation-delay:1.72s">',
        '<rect x="38" y="735" width="90" height="18" rx="4" fill="#39d353"/><rect x="138" y="735" width="90" height="18" rx="4" fill="#58a6ff"/><rect x="238" y="735" width="90" height="18" rx="4" fill="#a371f7"/><rect x="338" y="735" width="90" height="18" rx="4" fill="#f2cc60"/><rect x="438" y="735" width="90" height="18" rx="4" fill="#ff7b72"/><rect x="538" y="735" width="90" height="18" rx="4" fill="#c9d1d9"/>',
        '</g>',
        '<text class="line" style="animation-delay:1.9s" x="38" y="812" fill="#7d8590" font-size="20">$ open_to_collaboration <tspan fill="#39d353">true</tspan></text>',
        '<rect x="535" y="792" width="11" height="23" fill="#39d353"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect>',
        '</svg>',
    ])
    return "".join(parts)


if __name__ == "__main__":
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
