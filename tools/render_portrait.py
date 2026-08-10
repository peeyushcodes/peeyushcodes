"""
render_portrait.py
------------------
Generates portrait.svg — a stylized ASCII avatar that draws itself
top-to-bottom using SMIL clip-path animations.
No photo required: uses a built-in procedural ASCII art design.
Accent: Matrix Green (#39ff14) on dark background.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "portrait.svg"

# ── Design tokens ─────────────────────────────────────────────────────────────
BG     = "#0d1117"
ACCENT = "#39ff14"
DIM    = "#2d6a0a"
FONT   = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"
CHAR_W = 8.4   # approximate monospace char width at font-size 13
LINE_H = 16
STAGGER_MS = 38  # ms delay between row reveals
SVG_W  = 360
# ──────────────────────────────────────────────────────────────────────────────

# Procedural ASCII avatar — a stylized coder portrait
PORTRAIT_LINES = [
    "   ██████████████████   ",
    "  ██  ░░░░░░░░░░░░  ██  ",
    " ██  ░░ ┌──────┐ ░░  ██ ",
    " ██  ░░ │ ◉  ◉ │ ░░  ██ ",
    " ██  ░░ │      │ ░░  ██ ",
    " ██  ░░ │  ──  │ ░░  ██ ",
    " ██  ░░ └──────┘ ░░  ██ ",
    "  ██  ░░  ████  ░░  ██  ",
    "   ████████████████████  ",
    "   ██ ┌──────────┐ ██   ",
    "   ██ │  <CODE/> │ ██   ",
    "   ██ └──────────┘ ██   ",
    "    ██████████████████   ",
    "    ██            ██   ",
    "   ████          ████  ",
    "",
    "  ┌─────────────────────┐",
    "  │  peeyush@github  ~  │",
    "  │  $ git push origin  │",
    "  │  > All systems go ✦ │",
    "  └─────────────────────┘",
    "",
    "  ···················  ",
    "  · always building · ",
    "  ···················  ",
]


def make_clip(idx: int, total_rows: int, line_count: int) -> str:
    """Creates a clipPath that reveals row `idx` after a stagger delay."""
    cid = f"clip{idx}"
    begin_s = idx * STAGGER_MS / 1000
    dur_s   = 0.25
    y       = idx * LINE_H
    return (
        f'<clipPath id="{cid}">'
        f'<rect x="0" y="{y}" width="{SVG_W}" height="{LINE_H}">'
        f'<animate attributeName="width" values="0;{SVG_W}" '
        f'dur="{dur_s}s" begin="{begin_s:.3f}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )


def render() -> str:
    lines_out = []
    n = len(PORTRAIT_LINES)
    svg_h = n * LINE_H + 30
    hold_begin = n * STAGGER_MS / 1000 + 0.5

    lines_out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{svg_h}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Defs: glow filter + clip paths ───────────────────────────────────────
    lines_out.append('<defs>')
    lines_out.append(
        '<filter id="glow">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    for i in range(n):
        lines_out.append(make_clip(i, n, n))
    lines_out.append('</defs>')

    # ── Background scanlines (subtle) ────────────────────────────────────────
    for row in range(0, svg_h, LINE_H):
        lines_out.append(
            f'<rect x="0" y="{row}" width="{SVG_W}" height="1" '
            f'fill="{DIM}" opacity="0.08"/>'
        )

    # ── ASCII art rows ────────────────────────────────────────────────────────
    pad_left = 12
    for i, text in enumerate(PORTRAIT_LINES):
        y_text = (i + 1) * LINE_H + 8
        # alternate between bright and dim for depth
        color = ACCENT if (i % 3 != 1) else DIM
        glow_attr = ' filter="url(#glow)"' if color == ACCENT else ''
        lines_out.append(
            f'<text x="{pad_left}" y="{y_text}" '
            f'font-size="13" fill="{color}" '
            f'clip-path="url(#clip{i})"{glow_attr} '
            f'xml:space="preserve">{text}</text>'
        )

    # ── Blinking cursor after full reveal ────────────────────────────────────
    cursor_y = (n + 1) * LINE_H + 8
    lines_out.append(
        f'<text x="{pad_left}" y="{cursor_y}" font-size="13" fill="{ACCENT}" '
        f'opacity="0" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="0;1" dur="0.3s" '
        f'begin="{hold_begin:.2f}s" fill="freeze"/>'
        f'$ _<animate attributeName="opacity" values="1;0;1" '
        f'dur="1s" begin="{hold_begin:.2f}s" repeatCount="indefinite"/>'
        f'</text>'
    )

    lines_out.append('</svg>')
    return "\n".join(lines_out)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
