"""
render_banner.py
----------------
Generates banner.svg — cycles through phrases with fade-in/fade-out.
Uses SMIL opacity animation with clean keyTimes formatting.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "banner.svg"

BG     = "#0d1117"
ACCENT = "#39ff14"
DIM    = "#1a6b0a"
FONT   = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

SVG_W  = 820
SVG_H  = 72

PHRASES = [
    "Peeyush Kumar — AI/ML Student & Builder",
    "Building intelligent systems from scratch.",
    "windows-developer-mcp  ·  taipan  ·  resume-builder",
    "Open to research collaborations & internships.",
]

PHRASE_DUR = 3.2   # seconds each phrase is shown (including fade)
FADE       = 0.4   # fade duration in seconds
TOTAL      = len(PHRASES) * PHRASE_DUR  # 12.8s total cycle


def phrase_keyframes(idx: int) -> tuple[str, str]:
    """Returns strictly monotonic (keyTimes, values) for phrase[idx]."""
    start    = idx * PHRASE_DUR
    fade_in  = start + FADE
    fade_out = start + PHRASE_DUR - FADE
    end      = start + PHRASE_DUR

    times  = []
    values = []

    # 1. Start at 0
    if start > 0:
        times.append(0.0)
        values.append("0")
        times.append(start)
        values.append("0")
    else:
        times.append(0.0)
        values.append("0")

    # 2. Fade in & Hold
    times.append(fade_in)
    values.append("1")
    times.append(fade_out)
    values.append("1")

    # 3. Fade out & End at 1.0
    if end < TOTAL:
        times.append(end)
        values.append("0")
        times.append(TOTAL)
        values.append("0")
    else:
        times.append(TOTAL)
        values.append("0")

    # Format keyTimes as fractions normalized to [0, 1]
    kt_strs = [f"{t / TOTAL:.5f}".rstrip("0").rstrip(".") for t in times]
    # Ensure first is "0" and last is "1" exactly if floating point rounded
    if kt_strs[0] == "": kt_strs[0] = "0"
    if kt_strs[-1] in ("1", "1.0", "1.00000"): kt_strs[-1] = "1"

    return ";".join(kt_strs), ";".join(values)


def render() -> str:
    parts = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:8px;font-family:{FONT};">'
    )

    # ── Glow filter ──────────────────────────────────────────────────────────
    parts.append(
        '<defs><filter id="glow" x="-5%" y="-30%" width="110%" height="160%">'
        '<feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter></defs>'
    )

    text_y = SVG_H // 2 + 6

    # ── Static prompt prefix ──────────────────────────────────────────────────
    prefix = "~/peeyushcodes $ "
    parts.append(
        f'<text x="24" y="{text_y}" font-size="16" fill="{DIM}" '
        f'letter-spacing="0.5">{prefix}</text>'
    )

    text_x = 24 + len(prefix) * 10

    # ── Phrase texts (opacity-animated) ───────────────────────────────────────
    for i, phrase in enumerate(PHRASES):
        kt, kv = phrase_keyframes(i)
        parts.append(
            f'<text x="{text_x}" y="{text_y}" font-size="16" '
            f'fill="{ACCENT}" letter-spacing="0.3" opacity="0" filter="url(#glow)">'
            f'<animate attributeName="opacity" '
            f'keyTimes="{kt}" values="{kv}" '
            f'dur="{TOTAL:.2f}s" repeatCount="indefinite"/>'
            f'{phrase}</text>'
        )

    # ── Blinking cursor ───────────────────────────────────────────────────────
    parts.append(
        f'<text x="{text_x}" y="{text_y}" font-size="16" '
        f'fill="{ACCENT}" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="1;0;1" '
        f'dur="0.85s" repeatCount="indefinite"/>▌</text>'
    )

    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
