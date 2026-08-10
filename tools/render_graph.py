"""
render_graph.py
---------------
Reads assets/contributions.json and renders an animated contribution
grid SVG using SMIL animations — no JS, no external services.
Accent color: Matrix Green (#39ff14) on dark background.
"""

import json
import math
from pathlib import Path

DATA = Path(__file__).parent.parent / "assets" / "contributions.json"
OUT = Path(__file__).parent.parent / "graph.svg"

# ── Design tokens ──────────────────────────────────────────────────────────────
BG          = "#0d1117"
ACCENT      = "#39ff14"
LEVELS      = ["#161b22", "#1a3a0a", "#2d6a0a", "#4caf17", "#39ff14"]
CELL        = 13          # square size px
GAP         = 2           # gap between cells
RADIUS      = 3           # corner radius
COLS        = 53          # weeks
ROWS        = 7           # days
FONT        = "ui-monospace, 'Cascadia Code', monospace"
LABEL_COLOR = "#8b949e"
WIDTH       = COLS * (CELL + GAP) + 60   # left margin for day labels
HEIGHT      = ROWS * (CELL + GAP) + 80   # header + footer
# ──────────────────────────────────────────────────────────────────────────────

DAY_LABELS  = ["Mon", "", "Wed", "", "Fri", "", "Sun"]


def load_data() -> tuple[list[dict], dict]:
    if DATA.exists():
        payload = json.loads(DATA.read_text())
        return payload["days"], payload["stats"]
    # fallback: empty grid
    return [], {"total": 0, "current_streak": 0, "longest_streak": 0, "busiest_day_of_week": "—"}


def bucket_into_grid(days: list[dict]) -> list[list[int]]:
    """Returns grid[col][row] = level (0-4). Most recent week = last col."""
    grid: list[list[int]] = []
    week: list[int] = []

    if not days:
        return [[0] * 7 for _ in range(COLS)]

    # Pad so that the first day aligns to its weekday
    from datetime import datetime
    first_dt = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    pad = first_dt.weekday()  # Mon=0
    padded = [{"date": "", "count": 0, "level": 0}] * pad + days

    for d in padded:
        week.append(d["level"])
        if len(week) == 7:
            grid.append(week)
            week = []
    if week:
        week += [0] * (7 - len(week))
        grid.append(week)

    # Trim or pad to exactly COLS columns
    while len(grid) < COLS:
        grid.insert(0, [0] * 7)
    grid = grid[-COLS:]
    return grid


def anim_begin(col: int) -> str:
    """Stagger start: each column appears 30ms after the previous."""
    delay_s = col * 0.03
    return f"{delay_s:.2f}s"


def render(grid: list[list[int]], stats: dict) -> str:
    left_margin = 36
    top_margin  = 16
    cell_step   = CELL + GAP

    lines = []

    # ── SVG header ──────────────────────────────────────────────────────────
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Embedded style for glow effect ──────────────────────────────────────
    lines.append(f"""<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>""")

    # ── Day-of-week labels (left side) ───────────────────────────────────────
    for row, label in enumerate(DAY_LABELS):
        y = top_margin + row * cell_step + CELL // 2 + 4
        lines.append(
            f'<text x="{left_margin - 6}" y="{y}" '
            f'font-size="9" fill="{LABEL_COLOR}" text-anchor="end">{label}</text>'
        )

    # ── Cell grid ────────────────────────────────────────────────────────────
    total_anim_time = COLS * 0.03 + 0.4  # last col + fade duration

    for col, week in enumerate(grid):
        x = left_margin + col * cell_step
        begin = anim_begin(col)
        for row, level in enumerate(week):
            y = top_margin + row * cell_step
            color = LEVELS[min(level, 4)]
            glow_filter = ' filter="url(#glow)"' if level >= 4 else ''
            # Each cell fades + scales in
            lines.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="{RADIUS}" fill="{color}"{glow_filter}>'
                f'<animate attributeName="opacity" '
                f'values="0;1" dur="0.35s" begin="{begin}" fill="freeze"/>'
                f'<animate attributeName="width" '
                f'values="0;{CELL}" dur="0.2s" begin="{begin}" fill="freeze"/>'
                f'</rect>'
            )

    # ── Stats footer ─────────────────────────────────────────────────────────
    footer_y = top_margin + ROWS * cell_step + 18
    stats_text = (
        f"✦ {stats['total']} contributions  "
        f"│  streak {stats['current_streak']}d  "
        f"│  best {stats['longest_streak']}d  "
        f"│  busiest: {stats['busiest_day_of_week']}"
    )
    lines.append(
        f'<text x="{left_margin}" y="{footer_y}" '
        f'font-size="10" fill="{LABEL_COLOR}">'
        f'<animate attributeName="opacity" values="0;1" '
        f'dur="0.5s" begin="{total_anim_time:.2f}s" fill="freeze"/>'
        f'{stats_text}</text>'
    )

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_y = footer_y + 14
    legend_x = left_margin
    lines.append(
        f'<text x="{legend_x}" y="{legend_y}" font-size="9" fill="{LABEL_COLOR}">'
        f'Less</text>'
    )
    for i, color in enumerate(LEVELS):
        lx = legend_x + 30 + i * (CELL + 2)
        lines.append(
            f'<rect x="{lx}" y="{legend_y - 9}" width="{CELL}" height="{CELL}" '
            f'rx="{RADIUS}" fill="{color}"/>'
        )
    lines.append(
        f'<text x="{legend_x + 30 + len(LEVELS) * (CELL + 2) + 4}" '
        f'y="{legend_y}" font-size="9" fill="{LABEL_COLOR}">More</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    days, stats = load_data()
    grid = bucket_into_grid(days)
    svg = render(grid, stats)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
