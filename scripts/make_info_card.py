#!/usr/bin/env python3
"""Generate the animated neofetch-style profile information card."""

from __future__ import annotations

import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"

ROWS = [
    ("user", "Alexander Lewis"),
    ("role", "DevOps Intern @ Nuvo Prime"),
    ("focus", "Full-stack development"),
    ("build", "Automation · CI/CD · deployments"),
    ("tools", "Docker · GitHub Actions · Linux · Git"),
    ("mode", "Learn fast. Ship clean. Improve."),
]


def main() -> None:
    static = os.getenv("STATIC") == "1"
    width, height = 490, 430
    line_css = (
        ".line { opacity: 1; transform: none; }"
        if static
        else ".line { opacity: 0; transform: translateX(-8px); animation: enter .45s ease forwards; }"
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Alexander Lewis profile information</title>',
        '<desc id="desc">A terminal-style summary of Alexander Lewis, DevOps Intern and full-stack developer.</desc>',
        """<style>
        text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        __LINE_CSS__
        @keyframes enter { to { opacity: 1; transform: translateX(0); } }
        @media (prefers-reduced-motion: reduce) { .line { opacity: 1; transform: none; animation: none; } }
        </style>""".replace("__LINE_CSS__", line_css),
        '<rect x="1" y="1" width="488" height="428" rx="12" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="22" cy="21" r="5" fill="#ff5f56"/><circle cx="39" cy="21" r="5" fill="#ffbd2e"/><circle cx="56" cy="21" r="5" fill="#27c93f"/>',
        '<text x="245" y="26" text-anchor="middle" fill="#8b949e" font-size="11">alex@github — zsh</text>',
        '<text class="line" x="28" y="76" fill="#3fb950" font-size="18" font-weight="700" style="animation-delay:.15s">alexlewiscode@github</text>',
        '<text class="line" x="28" y="101" fill="#30363d" font-size="14" style="animation-delay:.25s">────────────────────────────────────────</text>',
    ]
    colors = ["#58a6ff", "#d2a8ff", "#f0883e", "#3fb950", "#ff7b72", "#79c0ff"]
    for index, ((key, value), color) in enumerate(zip(ROWS, colors)):
        y = 143 + index * 42
        delay = 0.38 + index * 0.14
        parts.append(f'<g class="line" style="animation-delay:{delay:.2f}s"><text x="28" y="{y}" fill="{color}" font-size="13">{html.escape(key)}</text><text x="116" y="{y}" fill="#c9d1d9" font-size="13">{html.escape(value)}</text></g>')
    parts.extend(
        [
            '<text class="line" x="28" y="400" fill="#8b949e" font-size="11" style="animation-delay:1.35s">building dependable systems, end to end.</text>',
            '<rect x="446" y="390" width="7" height="12" fill="#3fb950"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>',
            '</svg>',
        ]
    )
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
