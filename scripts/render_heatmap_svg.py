#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
FG = "#c9d1d9"
MUTED = "#8b949e"
EDGE = "#30363d"
BG = "#0d1117"
FONT = "ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, monospace"


def build_svg(data: dict[str, object]) -> str:
    days = data["days"]
    cols = 53
    cell = 12
    gap = 3
    left = 18
    top = 52
    grid_w = cols * (cell + gap) - gap
    grid_h = 7 * (cell + gap) - gap
    legend_y = top + grid_h + 22
    footer_y = legend_y + 26
    width = 860
    height = footer_y + 42

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap">',
        f"<style><![CDATA[text{{font-family:{FONT}}}.title{{fill:{FG};font-size:15px;font-weight:700}}.meta{{fill:{MUTED};font-size:12px}}.day{{stroke:{EDGE};stroke-width:.7}}.panel{{fill:{BG};stroke:{EDGE};stroke-width:1.2}}]]></style>",
        f'<rect width="100%" height="100%" fill="transparent"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" class="panel"/>',
        f'<text x="{left}" y="28" class="title">contribution graph</text>',
        f'<text x="{width-18}" y="28" text-anchor="end" class="meta">{data["total"]} contributions in the last year</text>',
    ]

    for item in days:
        week = int(item["week"])
        day = int(item["day"])
        count = int(item["count"])
        level = int(item["level"])
        x = left + week * (cell + gap)
        y = top + day * (cell + gap)
        delay = week * 0.025 + day * 0.01
        color = PALETTE[level]
        out.extend(
            [
                f'<g transform="translate({x - 8},{y - 8})" opacity="0">',
                f'  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.3f}s" fill="freeze"/>',
                f'  <animateTransform attributeName="transform" type="translate" from="{x - 8},{y - 8}" to="{x},{y}" dur="0.4s" begin="{delay:.3f}s" fill="freeze"/>',
                f'  <rect width="{cell}" height="{cell}" rx="3" class="day" fill="{color}">',
                f'    <title>{item["date"]}: {count} contributions</title>',
                f'  </rect>',
                f'</g>',
            ]
        )

    legend_x = width - 210
    out.append(f'<text x="{legend_x - 42}" y="{legend_y + 10}" class="meta">Less</text>')
    for i, color in enumerate(PALETTE):
        out.append(
            f'<rect x="{legend_x + i * 18}" y="{legend_y}" width="12" height="12" rx="3" fill="{color}" stroke="{EDGE}" stroke-width=".6"/>'
        )
    out.append(f'<text x="{legend_x + 104}" y="{legend_y + 10}" class="meta">More</text>')

    best = data["best_day"]
    footer = (
        f'{data["current_streak"]} day streak  '
        f'longest {data["longest_streak"]}  '
        f'best {best["date"]} ({best["count"]})'
    )
    out.append(f'<text x="{left}" y="{footer_y}" class="meta">{footer}</text>')
    out.append(f'<text x="{left}" y="{footer_y + 20}" class="meta">{data["username"]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main() -> int:
    data = json.loads(Path("data/contributions.json").read_text(encoding="utf-8"))
    Path("contrib-heatmap.svg").write_text(build_svg(data), encoding="utf-8")
    print("contrib-heatmap.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
