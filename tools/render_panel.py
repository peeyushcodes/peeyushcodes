"""
render_panel.py
---------------
Generates sysinfo.svg — upgraded terminal info panel with:
- System info rows (role, focus, stack, now, status)
- Skill bar rows with animated fill
- Social links row
Matrix green on dark background. Pure Python stdlib + SMIL.
"""

import os
from pathlib import Path

OUT     = Path(__file__).parent.parent / "sysinfo.svg"
PREVIEW = os.environ.get("PREVIEW", "0") == "1"

# ── Content ───────────────────────────────────────────────────────────────────
HOSTNAME = "peeyushcodes"
USER     = "peeyush"

INFO_ROWS = [
    ("name",   "Peeyush Kumar"),
    ("role",   "AI/ML Student"),
    ("focus",  "LLMs · ML · Intelligent Systems"),
    ("stack",  "Python · C++ · Go"),
    ("now",    "Building windows-developer-mcp"),
    ("status", "Open to Collaborate ✦"),
]

SKILLS = [
    ("Python",     92),
    ("C++",        70),
    ("Go",         55),
    ("ML / AI",    80),
]

SOCIAL = [
    ("github",   "github.com/peeyushcodes"),
    ("linkedin", "linkedin.com/in/peeyushkumar5317"),
    ("email",    "peeyushkumar5317@gmail.com"),
]

# ── Design ────────────────────────────────────────────────────────────────────
BG         = "#0d1117"
ACCENT     = "#39ff14"
DIM_GREEN  = "#2d6a0a"
MID_GREEN  = "#28a805"
LABEL_CLR  = "#8b949e"
WHITE      = "#e6edf3"
FONT       = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

SVG_W      = 460
PADDING    = 18
LINE_H     = 24
HEADER_H   = 34
SECTION_GAP = 8

# Calculate total height
n_rows     = len(INFO_ROWS)
n_skills   = len(SKILLS)
n_social   = len(SOCIAL)
SKILL_SECTION_H = 14 + n_skills * LINE_H + SECTION_GAP
SOCIAL_SECTION_H = 14 + n_social * (LINE_H - 4) + SECTION_GAP
SVG_H = HEADER_H + PADDING + n_rows * LINE_H + SKILL_SECTION_H + SOCIAL_SECTION_H + 20
# ──────────────────────────────────────────────────────────────────────────────

LABEL_W = 70    # width of label column


def fade_begin(i: int, base: float = 0.15) -> str:
    return "0s" if PREVIEW else f"{base + i * 0.16:.2f}s"


def animate_opacity(begin: str, dur: str = "0.35s") -> str:
    return f'<animate attributeName="opacity" values="0;1" dur="{dur}" begin="{begin}" fill="freeze"/>'


def animate_width(begin: str, to_val: int, dur: str = "0.5s") -> str:
    return f'<animate attributeName="width" values="0;{to_val}" dur="{dur}" begin="{begin}" fill="freeze"/>'


def render() -> str:
    parts = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Glow filter ──────────────────────────────────────────────────────────
    parts.append(
        '<defs><filter id="glow">'
        '<feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter></defs>'
    )

    # ── Header bar ───────────────────────────────────────────────────────────
    parts.append(
        f'<rect x="0" y="0" width="{SVG_W}" height="{HEADER_H}" '
        f'rx="10" fill="{DIM_GREEN}" opacity="0.3"/>'
    )
    for i, dot_color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PADDING + i * 18}" cy="{HEADER_H // 2}" r="5" fill="{dot_color}"/>')
    parts.append(
        f'<text x="{SVG_W // 2}" y="{HEADER_H // 2 + 5}" '
        f'font-size="12" fill="{ACCENT}" text-anchor="middle" filter="url(#glow)">'
        f'{USER}@{HOSTNAME} — system info</text>'
    )

    # ── Info rows ─────────────────────────────────────────────────────────────
    y = HEADER_H + PADDING + 4
    for i, (key, val) in enumerate(INFO_ROWS):
        begin = fade_begin(i)
        # Arrow prompt
        parts.append(
            f'<text x="{PADDING}" y="{y}" font-size="12" fill="{DIM_GREEN}" opacity="0">'
            f'{animate_opacity(begin)}▸</text>'
        )
        # Key
        parts.append(
            f'<text x="{PADDING + 14}" y="{y}" font-size="11" fill="{LABEL_CLR}" opacity="0">'
            f'{animate_opacity(begin)}{key}</text>'
        )
        # Separator
        parts.append(
            f'<text x="{PADDING + LABEL_W}" y="{y}" font-size="12" fill="{DIM_GREEN}" opacity="0">'
            f'{animate_opacity(begin)}→</text>'
        )
        # Value
        highlight = key in ("focus", "now", "status", "name")
        v_color  = ACCENT if highlight else WHITE
        glow     = ' filter="url(#glow)"' if highlight else ''
        parts.append(
            f'<text x="{PADDING + LABEL_W + 16}" y="{y}" '
            f'font-size="12" fill="{v_color}" opacity="0"{glow}>'
            f'{animate_opacity(begin)}{val}</text>'
        )
        y += LINE_H

    # ── Divider ───────────────────────────────────────────────────────────────
    y += 4
    divider_begin = fade_begin(len(INFO_ROWS))
    parts.append(
        f'<line x1="{PADDING}" y1="{y}" x2="{SVG_W - PADDING}" y2="{y}" '
        f'stroke="{DIM_GREEN}" stroke-width="1" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.5" dur="0.4s" begin="{divider_begin}" fill="freeze"/>'
        f'</line>'
    )
    y += 12

    # ── Skills section label ───────────────────────────────────────────────────
    skill_label_begin = fade_begin(len(INFO_ROWS) + 1)
    parts.append(
        f'<text x="{PADDING}" y="{y}" font-size="10" fill="{LABEL_CLR}" opacity="0">'
        f'{animate_opacity(skill_label_begin)}── skills ──</text>'
    )
    y += LINE_H - 4

    # ── Skill bars ────────────────────────────────────────────────────────────
    bar_max_w = SVG_W - PADDING * 2 - 80  # width for the bar
    bar_x     = PADDING + 80
    bar_h     = 8

    for i, (skill, pct) in enumerate(SKILLS):
        begin    = fade_begin(len(INFO_ROWS) + 2 + i)
        fill_w   = int(bar_max_w * pct / 100)

        # Skill label
        parts.append(
            f'<text x="{PADDING}" y="{y + bar_h}" font-size="11" fill="{LABEL_CLR}" opacity="0">'
            f'{animate_opacity(begin)}{skill}</text>'
        )
        # Bar background
        parts.append(
            f'<rect x="{bar_x}" y="{y}" width="{bar_max_w}" height="{bar_h}" '
            f'rx="4" fill="{DIM_GREEN}" opacity="0.3"/>'
        )
        # Bar fill (animated)
        glow_filter = ' filter="url(#glow)"' if pct >= 80 else ''
        parts.append(
            f'<rect x="{bar_x}" y="{y}" width="0" height="{bar_h}" '
            f'rx="4" fill="{ACCENT}"{glow_filter} opacity="0">'
            f'{animate_opacity(begin)}'
            f'{animate_width(begin, fill_w, "0.6s")}'
            f'</rect>'
        )
        # Percentage label
        parts.append(
            f'<text x="{bar_x + bar_max_w + 6}" y="{y + bar_h}" '
            f'font-size="10" fill="{DIM_GREEN}" opacity="0">'
            f'{animate_opacity(begin)}{pct}%</text>'
        )
        y += LINE_H

    # ── Second divider ────────────────────────────────────────────────────────
    y += 4
    div2_begin = fade_begin(len(INFO_ROWS) + 2 + len(SKILLS) + 1)
    parts.append(
        f'<line x1="{PADDING}" y1="{y}" x2="{SVG_W - PADDING}" y2="{y}" '
        f'stroke="{DIM_GREEN}" stroke-width="1" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.5" dur="0.4s" begin="{div2_begin}" fill="freeze"/>'
        f'</line>'
    )
    y += 12

    # ── Social links label ────────────────────────────────────────────────────
    social_label_begin = fade_begin(len(INFO_ROWS) + 2 + len(SKILLS) + 2)
    parts.append(
        f'<text x="{PADDING}" y="{y}" font-size="10" fill="{LABEL_CLR}" opacity="0">'
        f'{animate_opacity(social_label_begin)}── connect ──</text>'
    )
    y += LINE_H - 6

    # ── Social rows ───────────────────────────────────────────────────────────
    social_icons = {"github": "⌥", "linkedin": "in", "email": "@"}
    for i, (platform, handle) in enumerate(SOCIAL):
        begin = fade_begin(len(INFO_ROWS) + 2 + len(SKILLS) + 3 + i)
        icon  = social_icons.get(platform, "•")
        parts.append(
            f'<text x="{PADDING}" y="{y}" font-size="11" fill="{MID_GREEN}" opacity="0">'
            f'{animate_opacity(begin)}[{icon}]</text>'
        )
        parts.append(
            f'<text x="{PADDING + 28}" y="{y}" font-size="11" fill="{LABEL_CLR}" opacity="0">'
            f'{animate_opacity(begin)}{handle}</text>'
        )
        y += LINE_H - 4

    # ── Blinking cursor ───────────────────────────────────────────────────────
    y += 4
    cursor_begin = fade_begin(len(INFO_ROWS) + 2 + len(SKILLS) + 3 + len(SOCIAL))
    parts.append(
        f'<text x="{PADDING}" y="{y}" font-size="12" fill="{ACCENT}" '
        f'opacity="0" filter="url(#glow)">'
        f'{animate_opacity(cursor_begin)}'
        f'▸ <animate attributeName="opacity" values="0;1;0" '
        f'dur="1s" begin="{cursor_begin}" repeatCount="indefinite"/>_</text>'
    )

    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
