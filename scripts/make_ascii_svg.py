#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path


RAMP = " .`:-=+*cs#%@"
FG = "#d1d5db"
BG = "transparent"
FONT = "ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, monospace"


def fallback_grid(width: int = 96, height: int = 54) -> list[str]:
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            nx = (x - width * 0.5) / width
            ny = (y - height * 0.5) / height
            face = 0.0
            face += max(0.0, 1.0 - ((nx / 0.24) ** 2 + ((ny + 0.05) / 0.32) ** 2))
            hair = max(0.0, 1.0 - ((nx / 0.34) ** 2 + ((ny + 0.32) / 0.23) ** 2))
            shoulders = max(0.0, 1.0 - ((nx / 0.52) ** 2 + ((ny - 0.34) / 0.22) ** 2))
            eyes = 0.0
            eyes += 1.0 if abs(nx + 0.08) < 0.02 and abs(ny + 0.02) < 0.015 else 0.0
            eyes += 1.0 if abs(nx - 0.08) < 0.02 and abs(ny + 0.02) < 0.015 else 0.0
            nose = 1.0 if abs(nx) < 0.02 and -0.05 < ny < 0.08 else 0.0
            mouth = max(0.0, 1.0 - ((nx / 0.10) ** 2 + ((ny - 0.12) / 0.03) ** 2))
            value = max(face * 0.85, hair * 1.15, shoulders * 0.45, eyes * 1.2, nose * 0.7, mouth * 0.6)
            idx = min(len(RAMP) - 1, int((1.0 - min(value, 1.0)) * (len(RAMP) - 1)))
            row.append(RAMP[idx])
        grid.append("".join(row))
    return grid


def image_grid(path: Path) -> list[str]:
    try:
        from PIL import Image
    except Exception:
        return fallback_grid()

    image = Image.open(path).convert("L")
    width = 100
    aspect = image.height / max(image.width, 1)
    height = max(30, round(width * aspect * 0.42))
    image = image.resize((width, height))

    pixels = list(image.getdata())
    rows = []
    for y in range(height):
        chars = []
        for x in range(width):
            px = pixels[y * width + x]
            idx = int((255 - px) / 256 * len(RAMP))
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    char_w = 8.0
    char_h = 12.0
    width = int(math.ceil(len(rows[0]) * char_w + 48))
    height = int(math.ceil(len(rows) * char_h + 32))

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait">',
        f"<style><![CDATA[.glyph{{font-family:{FONT};font-size:11px;fill:{FG};letter-spacing:0;}} .cursor{{fill:{FG};opacity:.95;}}]]></style>",
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]

    left = 20
    top = 18
    for i, row in enumerate(rows):
        y = top + i * char_h
        clip_id = f"clip-row-{i}"
        begin = f"{i * 0.045}s"
        duration = "0.8s"
        row_width = len(row) * char_w
        out.extend(
            [
                f'<clipPath id="{clip_id}">',
                f'  <rect x="{left}" y="{y - 9}" width="0" height="{char_h + 4}">',
                f'    <animate attributeName="width" from="0" to="{row_width}" dur="{duration}" begin="{begin}" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>',
                f'  </rect>',
                f'</clipPath>',
                f'<g clip-path="url(#{clip_id})">',
                f'  <text class="glyph" x="{left}" y="{y}">{escape(row)}</text>',
                f'  <rect class="cursor" x="{left}" y="{y - 8}" width="7" height="11">',
                f'    <animate attributeName="x" from="{left}" to="{left + row_width - 7}" dur="{duration}" begin="{begin}" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>',
                f'  </rect>',
                f'</g>',
            ]
        )

    out.append("</svg>")
    return "\n".join(out)


def main() -> int:
    src = Path("source-prepped.png")
    rows = image_grid(src) if src.exists() else fallback_grid()
    Path("avi-ascii.svg").write_text(build_svg(rows), encoding="utf-8")
    print("avi-ascii.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
