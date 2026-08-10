"""
render_panel.py
---------------
Generates sysinfo.svg — a terminal-style info panel that types itself in.
Accent: Matrix Green (#39ff14) on dark background.
No external dependencies — pure Python stdlib.
"""

import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "sysinfo.svg"
PREVIEW = os.environ.get("PREVIEW", "0") == "1"

# ── Content ───────────────────────────────────────────────────────────────────
HOSTNAME = "peeyushcodes"
USER     = "peeyush"
ROWS = [
    ("os",      "GitHub Profile v2.0"),
    ("role",    "CS Student"),
    ("focus",   "Systems & AI"),
    ("stack",   "Python · C++ · Go"),
    ("now",     "Learning & Building"),
    ("status",  "Open to Collaborate ✦"),
]
UPTIME = "∞ (always online)"

# ── Design ────────────────────────────────────────────────────────────────────
BG          = "#0d1117"
ACCENT      = "#39ff14"
DIM_GREEN   = "#2d6a0a"
LABEL_COLOR = "#8b949e"
FONT        = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

SVG_W = 460
SVG_H = 260
PADDING = 20
LINE_H  = 26
HEADER_H = 36
# ──────────────────────────────────────────────────────────────────────────────


def fade_begin(i: int) -> str:
    if PREVIEW:
        return "0s"
    return f"{0.2 + i * 0.18:.2f}s"


def animate(attr: str, begin: str, dur: str = "0.4s") -> str:
    return (
        f'<animate attributeName="{attr}" values="0;1" '
        f'dur="{dur}" begin="{begin}" fill="freeze"/>'
    )


def render() -> str:
    lines = []

    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Glow filter ──────────────────────────────────────────────────────────
    lines.append("""<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>""")

    # ── Header bar ───────────────────────────────────────────────────────────
    lines.append(
        f'<rect x="0" y="0" width="{SVG_W}" height="{HEADER_H}" '
        f'rx="10" fill="{DIM_GREEN}" opacity="0.35"/>'
    )
    # Window dots
    for i, dot_color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        cx = PADDING + i * 18
        lines.append(f'<circle cx="{cx}" cy="{HEADER_H//2}" r="5" fill="{dot_color}"/>')

    # Title
    title = f"{USER}@{HOSTNAME}: ~"
    lines.append(
        f'<text x="{SVG_W//2}" y="{HEADER_H//2 + 5}" '
        f'font-size="12" fill="{ACCENT}" text-anchor="middle" '
        f'filter="url(#glow)">{title}</text>'
    )

    # ── Rows ─────────────────────────────────────────────────────────────────
    y_start = HEADER_H + PADDING + 4
    label_w = 72

    for i, (key, val) in enumerate(ROWS):
        y = y_start + i * LINE_H
        begin = fade_begin(i)

        # prompt symbol
        lines.append(
            f'<text x="{PADDING}" y="{y}" font-size="13" fill="{DIM_GREEN}" opacity="0">'
            f'{animate("opacity", begin)}'
            f'▸</text>'
        )
        # key label
        lines.append(
            f'<text x="{PADDING + 14}" y="{y}" font-size="12" fill="{LABEL_COLOR}" opacity="0">'
            f'{animate("opacity", begin)}'
            f'{key}</text>'
        )
        # separator
        lines.append(
            f'<text x="{PADDING + label_w}" y="{y}" font-size="12" fill="{DIM_GREEN}" opacity="0">'
            f'{animate("opacity", begin)}'
            f'→</text>'
        )
        # value
        glow = ' filter="url(#glow)"' if key in ("focus", "now", "status") else ''
        v_color = ACCENT if key in ("focus", "now", "status") else "#e6edf3"
        lines.append(
            f'<text x="{PADDING + label_w + 16}" y="{y}" '
            f'font-size="12" fill="{v_color}" opacity="0"{glow}>'
            f'{animate("opacity", begin)}'
            f'{val}</text>'
        )

    # ── Blinking cursor at bottom ─────────────────────────────────────────────
    cursor_y = y_start + len(ROWS) * LINE_H + 4
    cursor_begin = fade_begin(len(ROWS))
    lines.append(
        f'<text x="{PADDING}" y="{cursor_y}" font-size="13" fill="{ACCENT}" opacity="0" '
        f'filter="url(#glow)">'
        f'{animate("opacity", cursor_begin)}'
        f'▸ <animate attributeName="opacity" values="0;1;0" '
        f'dur="1s" begin="{cursor_begin}" repeatCount="indefinite"/>_</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
