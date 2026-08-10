"""
render_peeyush_banner.py
------------------------
Generates peeyush_banner.svg — an animated SVG banner displaying the
PEEYUSH ASCII block art with a left-to-right typing reveal animation,
glow filter, scanline effect, and blinking terminal cursor.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "peeyush_banner.svg"

# ── Design tokens ─────────────────────────────────────────────────────────────
BG     = "#0d1117"
ACCENT = "#39ff14"
DIM    = "#1a6b0a"
FONT   = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

# PEEYUSH ASCII Block Art
ASCII_ART = [
    "██████╗ ███████╗███████╗██╗   ██╗██╗   ██╗███████╗██╗  ██╗",
    "██╔══██╗██╔════╝██╔════╝╚██╗ ██╔╝██║   ██║██╔════╝██║  ██║",
    "██████╔╝█████╗  █████╗   ╚████╔╝ ██║   ██║███████╗███████║",
    "██╔═══╝ ██╔══╝  ██╔══╝    ╚██╔╝  ██║   ██║╚════██║██║  ██║",
    "██║     ███████╗███████╗   ██║   ╚██████╔╝███████║██║  ██║",
    "╚═╝     ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝",
]

FONT_SIZE = 13
LINE_H    = 17
PAD_TOP   = 24
PAD_LEFT  = 28

# Calculate SVG dimensions
SVG_W = 820
SVG_H = len(ASCII_ART) * LINE_H + PAD_TOP * 2 + 16

TYPE_DUR  = 1.4   # seconds for typing reveal
START_DEL = 0.25  # start delay in seconds


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render() -> str:
    parts = []

    # SVG header
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Defs: glow filter + typing clip path ─────────────────────────────────
    parts.append('<defs>')
    parts.append(
        '<filter id="glow" x="-10%" y="-20%" width="120%" height="140%">'
        '<feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    # Clip path that expands width from 0 to SVG_W left-to-right
    parts.append(
        f'<clipPath id="type-clip">'
        f'<rect x="0" y="0" width="0" height="{SVG_H}">'
        f'<animate attributeName="width" values="0;{SVG_W}" '
        f'dur="{TYPE_DUR}s" begin="{START_DEL}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )
    parts.append('</defs>')

    # ── Background & Subtle Scanlines ─────────────────────────────────────────
    parts.append(f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}" rx="10"/>')
    for y in range(0, SVG_H, 4):
        parts.append(
            f'<rect x="0" y="{y}" width="{SVG_W}" height="1" '
            f'fill="{DIM}" opacity="0.05"/>'
        )

    # ── ASCII Block Text (Clipped for typing animation) ────────────────────────
    for i, line in enumerate(ASCII_ART):
        text_y = PAD_TOP + (i + 1) * LINE_H
        parts.append(
            f'<text x="{PAD_LEFT}" y="{text_y}" font-size="{FONT_SIZE}" '
            f'fill="{ACCENT}" clip-path="url(#type-clip)" filter="url(#glow)" '
            f'xml:space="preserve">{escape_xml(line)}</text>'
        )

    # ── Animated Cursor moving left-to-right then blinking at end ─────────────
    cursor_x_start = PAD_LEFT
    cursor_x_end   = PAD_LEFT + len(ASCII_ART[0]) * 8.0  # char width ~8px
    finish_time    = START_DEL + TYPE_DUR

    parts.append(
        f'<text y="{PAD_TOP + LINE_H}" font-size="{FONT_SIZE}" fill="{ACCENT}" filter="url(#glow)">'
        f'<animate attributeName="x" values="{cursor_x_start};{cursor_x_end}" '
        f'dur="{TYPE_DUR}s" begin="{START_DEL}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" dur="0.8s" '
        f'begin="{finish_time:.2f}s" repeatCount="indefinite"/>█'
        f'</text>'
    )

    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
