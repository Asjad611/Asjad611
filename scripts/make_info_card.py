#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


W = 490
H = 320
BG = "#0b0f14"
PANEL = "#111827"
EDGE = "#1f2937"
TEXT = "#d1d5db"
MUTED = "#94a3b8"
ACCENT = "#69f0a0"
GREEN = "#22c55e"
BLUE = "#60a5fa"
YELLOW = "#fbbf24"
PINK = "#fb7185"
FONT = "ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, monospace"


def line(y: int, label: str, value: str, color: str, delay: float, static: bool) -> str:
    if static:
        return (
            f'<text x="168" y="{y}" class="label">{label}</text>'
            f'<text x="246" y="{y}" class="value" fill="{color}">{value}</text>'
        )
    return (
        f'<g opacity="0" transform="translate(0,8)">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0,8" to="0,0" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="168" y="{y}" class="label">{label}</text>'
        f'<text x="246" y="{y}" class="value" fill="{color}">{value}</text>'
        f'</g>'
    )


def main() -> int:
    static = os.getenv("STATIC") == "1"
    name = os.getenv("PROFILE_NAME", "Asjad Mughal")
    role = os.getenv("PROFILE_ROLE", "Builder of small, useful systems")
    stack = os.getenv("PROFILE_STACK", "Python  GitHub Actions  SVG  JS")
    highlights = os.getenv(
        "PROFILE_HIGHLIGHTS",
        "Terminal art  Daily automation  Public profile polish",
    )
    now = os.getenv("PROFILE_NOW", "shipping profile visuals")
    prev = os.getenv("PROFILE_PREV", "daily activity generator")

    pieces = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Profile info card">',
        f"<style><![CDATA[.bg{{fill:{BG}}}.panel{{fill:{PANEL};stroke:{EDGE};stroke-width:1.2}}.title{{fill:{TEXT};font-family:{FONT};font-size:15px;font-weight:700}}.label{{fill:{MUTED};font-size:12px}}.value{{font-size:12px;font-weight:700}}.mono{{fill:{TEXT};font-family:{FONT};font-size:13px}}]]></style>",
        f'<rect width="100%" height="100%" fill="transparent"/>',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" class="panel"/>',
        f'<rect x="18" y="18" width="{W-36}" height="28" rx="10" fill="#0f172a" stroke="{EDGE}"/>',
        f'<circle cx="34" cy="32" r="4" fill="#f87171"/><circle cx="48" cy="32" r="4" fill="#fbbf24"/><circle cx="62" cy="32" r="4" fill="#34d399"/>',
        f'<text x="84" y="33" class="title">{name}</text>',
        f'<text x="30" y="82" class="mono">neofetch</text>',
        f'<text x="30" y="112" class="mono" fill="{ACCENT}">#</text>',
        f'<text x="30" y="140" class="mono" fill="{GREEN}">#</text>',
        f'<text x="30" y="168" class="mono" fill="{BLUE}">#</text>',
        f'<text x="30" y="196" class="mono" fill="{YELLOW}">#</text>',
        f'<text x="30" y="224" class="mono" fill="{PINK}">#</text>',
    ]
    pieces.extend(
        [
            line(112, "Now", now, ACCENT, 0.10, static),
            line(140, "Prev", prev, GREEN, 0.24, static),
            line(168, "Stack", stack, BLUE, 0.38, static),
            line(196, "Highlights", highlights, YELLOW, 0.52, static),
            f'<text x="30" y="252" class="mono" fill="{MUTED}">terminal mode: on</text>',
            f'<text x="30" y="274" class="mono" fill="{MUTED}">location: github.com/{os.getenv("GITHUB_USERNAME", "Asjad611")}</text>',
            "</svg>",
        ]
    )

    Path("info-card.svg").write_text("".join(pieces), encoding="utf-8")
    print("info-card.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
