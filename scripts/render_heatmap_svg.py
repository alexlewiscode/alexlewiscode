#!/usr/bin/env python3
"""Render contribution JSON as a self-contained animated SVG."""

from __future__ import annotations

import calendar
import html
import json
import os
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def main() -> None:
    static = os.getenv("STATIC") == "1"
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    days = data["days"]
    parsed = [(date.fromisoformat(item["date"]), item) for item in days]
    first_sunday = min(day for day, _ in parsed)

    by_week: dict[int, list[tuple[date, dict[str, object]]]] = defaultdict(list)
    for day, item in parsed:
        week = (day - first_sunday).days // 7
        by_week[week].append((day, item))

    width, height = 860, 238
    grid_x, grid_y, step, cell = 62, 70, 14, 11
    animation_css = (
        ".day { opacity: 1; transform: none; }"
        if static
        else ".day { opacity: 0; transform: translateY(-9px); animation: reveal .38s cubic-bezier(.2,.8,.2,1) forwards; }"
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub contribution activity</title>',
        f'<desc id="desc">{data["total"]:,} contributions in the last year.</desc>',
        """<style>
        text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        __ANIMATION_CSS__
        @keyframes reveal { to { opacity: 1; transform: translateY(0); } }
        @media (prefers-reduced-motion: reduce) { .day { opacity: 1; transform: none; animation: none; } }
        </style>""".replace("__ANIMATION_CSS__", animation_css),
        '<rect x="1" y="1" width="858" height="236" rx="12" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="22" cy="21" r="5" fill="#ff5f56"/><circle cx="39" cy="21" r="5" fill="#ffbd2e"/><circle cx="56" cy="21" r="5" fill="#27c93f"/>',
        '<text x="430" y="26" text-anchor="middle" fill="#8b949e" font-size="12">github activity — last 53 weeks</text>',
    ]

    seen_months: set[tuple[int, int]] = set()
    for week in sorted(by_week):
        for day, _ in by_week[week]:
            key = (day.year, day.month)
            if day.day <= 7 and key not in seen_months:
                seen_months.add(key)
                parts.append(
                    f'<text x="{grid_x + week * step}" y="55" fill="#8b949e" font-size="10">{calendar.month_abbr[day.month]}</text>'
                )
                break

    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        parts.append(f'<text x="20" y="{grid_y + row * step + 9}" fill="#8b949e" font-size="10">{label}</text>')

    for day, item in parsed:
        week = (day - first_sunday).days // 7
        row = (day.weekday() + 1) % 7
        x, y = grid_x + week * step, grid_y + row * step
        level = min(5, max(0, int(item["level"])))
        delay = 0.10 + week * 0.022 + row * 0.025
        label = f'{item["count"]} contributions on {day.isoformat()}'
        parts.append(
            f'<rect class="day" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{html.escape(label)}</title></rect>'
        )

    stats = (
        f'{data["total"]:,} contributions  ·  current streak {data["current_streak"]} days  ·  '
        f'longest streak {data["longest_streak"]} days'
    )
    parts.extend(
        [
            f'<text x="62" y="208" fill="#c9d1d9" font-size="12">{html.escape(stats)}</text>',
            '<text x="674" y="208" fill="#8b949e" font-size="10">Less</text>',
            *[
                f'<rect x="{706 + index * 15}" y="198" width="11" height="11" rx="2" fill="{color}"/>'
                for index, color in enumerate(PALETTE[:5])
            ],
            '<text x="786" y="208" fill="#8b949e" font-size="10">More</text>',
            '</svg>',
        ]
    )
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
