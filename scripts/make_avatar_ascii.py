#!/usr/bin/env python3
"""Download the GitHub avatar and render it as a self-typing ASCII SVG."""

from __future__ import annotations

import html
import os
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageOps

USERNAME = "alexlewiscode"
AVATAR_URL = "https://avatars.githubusercontent.com/u/321149164?v=4"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "avatar-ascii.svg"
RAMP = " .,:;irsXA253hMHGS#9B&@"


def main() -> None:
    static = os.getenv("STATIC") == "1"
    response = requests.get(AVATAR_URL, timeout=30, headers={"User-Agent": f"{USERNAME}-profile-readme/1.0"})
    response.raise_for_status()
    image = Image.open(BytesIO(response.content)).convert("L")
    subject_box = image.point(lambda value: 255 if value > 16 else 0).getbbox()
    if subject_box:
        left, top, right, bottom = subject_box
        subject_width, subject_height = right - left, bottom - top
        side = int(max(subject_width, subject_height) * 1.35)
        center_x, center_y = (left + right) // 2, (top + bottom) // 2
        crop_left = max(0, center_x - side // 2)
        crop_top = max(0, center_y - side // 2)
        crop_right = min(image.width, crop_left + side)
        crop_bottom = min(image.height, crop_top + side)
        image = image.crop((crop_left, crop_top, crop_right, crop_bottom))
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.35)
    image = image.resize((76, 42), Image.Resampling.LANCZOS)

    rows: list[str] = []
    for y in range(image.height):
        chars: list[str] = []
        for x in range(image.width):
            value = image.getpixel((x, y))
            # The source avatar has a black background, so low luminance becomes empty space.
            normalized = 0 if value < 18 else min(255, int((value - 18) * 1.08))
            chars.append(RAMP[round(normalized / 255 * (len(RAMP) - 1))])
        rows.append("".join(chars).rstrip())

    width, height = 370, 430
    font_size, line_height, left, top = 5.0, 8.0, 12, 64
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait of Alexander Lewis</title>',
        '<desc id="desc">A monochrome portrait generated from the alexlewiscode GitHub avatar.</desc>',
        '<rect x="1" y="1" width="368" height="428" rx="12" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="22" cy="21" r="5" fill="#ff5f56"/><circle cx="39" cy="21" r="5" fill="#ffbd2e"/><circle cx="56" cy="21" r="5" fill="#27c93f"/>',
        '<text x="185" y="26" text-anchor="middle" fill="#8b949e" font-family="ui-monospace,monospace" font-size="11">avatar-ascii.svg</text>',
        '<defs>',
    ]
    for index in range(len(rows)):
        if static:
            reveal = f'<rect x="{left}" y="{top + index * line_height - 7}" width="346" height="{line_height + 1}"/>'
        else:
            reveal = f'<rect x="{left}" y="{top + index * line_height - 7}" width="0" height="{line_height + 1}"><animate attributeName="width" from="0" to="346" dur="0.65s" begin="{index * 0.045:.3f}s" fill="freeze"/></rect>'
        parts.append(f'<clipPath id="row-{index}">{reveal}</clipPath>')
    parts.append('</defs>')
    for index, row in enumerate(rows):
        y = top + index * line_height
        parts.append(
            f'<text x="{left}" y="{y}" clip-path="url(#row-{index})" fill="#c9d1d9" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="{font_size}" xml:space="preserve">{html.escape(row)}</text>'
        )
    parts.extend(
        [
            '<text x="16" y="412" fill="#3fb950" font-family="ui-monospace,monospace" font-size="10">alex@github:~$</text>',
            '<rect x="104" y="403" width="7" height="11" fill="#3fb950"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>',
            '</svg>',
        ]
    )
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
