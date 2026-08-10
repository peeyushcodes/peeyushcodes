"""
render_banner.py
----------------
Generates banner.svg — a typing animation that cycles through phrases,
simulating a terminal prompt typing itself out.
Matrix green on dark background. Pure SMIL, no JS.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "banner.svg"

BG     = "#0d1117"
ACCENT = "#39ff14"
DIM    = "#1a6b0a"
FONT   = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

SVG_W  = 820
SVG_H  = 80

# Phrases to type out (cycles)
LINES = [
    "Peeyush Kumar — AI/ML Student & Builder",
    "Building intelligent systems from scratch.",
    "windows-developer-mcp · taipan · resume-builder",
    "Open to research collaborations & internships.",
]

# Timing per phrase (seconds)
CHAR_SPEED  = 0.055   # seconds per character typed
HOLD        = 1.4     # seconds to hold after fully typed
ERASE_SPEED = 0.025   # seconds per character erased

def phrase_duration(phrase: str) -> float:
    return len(phrase) * CHAR_SPEED + HOLD + len(phrase) * ERASE_SPEED + 0.3


def build_keyframes(phrase: str, global_start: float) -> tuple[str, str, float]:
    """Returns (type_animate, erase_animate, end_time)."""
    n = len(phrase)
    type_dur   = n * CHAR_SPEED
    erase_dur  = n * ERASE_SPEED
    hold_start = global_start + type_dur
    erase_start = hold_start + HOLD
    end        = erase_start + erase_dur

    # Build visible length keyframes for typing and erasing
    # We animate text length via a tspan with textLength
    return hold_start, erase_start, end


def render() -> str:
    total_dur = sum(phrase_duration(p) for p in LINES)

    lines_out = []
    lines_out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:8px;font-family:{FONT};">'
    )

    # Glow filter
    lines_out.append(
        '<defs><filter id="glow">'
        '<feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter></defs>'
    )

    # Prompt prefix (static)
    prefix = "~/peeyushcodes $ "
    prefix_x = 20
    text_y = SVG_H // 2 + 6

    lines_out.append(
        f'<text x="{prefix_x}" y="{text_y}" font-size="16" '
        f'fill="{DIM}" font-family="{FONT}">{prefix}</text>'
    )

    # Approximate width of prefix
    prefix_w = len(prefix) * 9.6
    text_x = int(prefix_x + prefix_w)

    # For each phrase, create a text element that appears/disappears
    t = 0.0
    for i, phrase in enumerate(LINES):
        n      = len(phrase)
        t_type = t
        t_hold = t + n * CHAR_SPEED
        t_erase = t_hold + HOLD
        t_end  = t_erase + n * ERASE_SPEED
        t_next = t_end + 0.25

        # Build values/keyTimes for textLength animation (type then erase)
        # We use clip-rect trick: animate a rect width from 0 to full then back
        cid = f"clip{i}"

        max_w  = n * 9.6   # approximate char width at font-size 16

        # ClipPath for this phrase
        lines_out.append(
            f'<defs><clipPath id="{cid}">'
            f'<rect x="{text_x}" y="0" height="{SVG_H}" width="0">'
            # Type: 0 → max_w
            f'<animate attributeName="width" '
            f'values="0;{max_w:.0f}" dur="{n * CHAR_SPEED:.2f}s" '
            f'begin="{t_type:.3f}s" fill="freeze" id="t{i}a"/>'
            # Hold then erase: max_w → 0
            f'<animate attributeName="width" '
            f'values="{max_w:.0f};0" dur="{n * ERASE_SPEED:.2f}s" '
            f'begin="{t_erase:.3f}s" fill="freeze" id="t{i}b"/>'
            f'</rect></clipPath></defs>'
        )

        # The text clipped by the above
        lines_out.append(
            f'<text x="{text_x}" y="{text_y}" font-size="16" '
            f'fill="{ACCENT}" font-family="{FONT}" '
            f'clip-path="url(#{cid})" filter="url(#glow)">'
            f'{phrase}</text>'
        )

        t = t_next

    # Blinking cursor
    lines_out.append(
        f'<text x="{text_x}" y="{text_y}" font-size="16" '
        f'fill="{ACCENT}" font-family="{FONT}" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="1;0;1" dur="0.8s" '
        f'repeatCount="indefinite"/>▌</text>'
    )

    lines_out.append('</svg>')
    return '\n'.join(lines_out)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
