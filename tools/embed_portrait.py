"""
embed_portrait.py
-----------------
Embeds the generated ASCII art image into portrait.svg as a base64 data URI
with a row-by-row SMIL clip-path reveal animation.
No external image references — fully self-contained SVG.
"""

import base64
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

# ── Paths ─────────────────────────────────────────────────────────────────────
GENERATED = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:\Users\Peeyush\.gemini\antigravity-ide\brain"
    r"\283b70c8-6fc4-4997-96f9-0b45f3746e75"
    r"\ascii_portrait_generated_1786370367081.png"
)
OUT = Path(__file__).parent.parent / "portrait.svg"

# ── Design ────────────────────────────────────────────────────────────────────
BG         = "#0d1117"
ACCENT     = "#39ff14"
DIM        = "#1a6b0a"
FONT       = "ui-monospace, 'Cascadia Code', monospace"

IMG_W      = 340      # embedded image display width
IMG_H      = 340      # embedded image display height
PAD        = 10       # padding around image
SVG_W      = IMG_W + PAD * 2
SVG_H      = IMG_H + PAD * 2 + 36   # extra space for cursor at bottom

N_ROWS     = 34       # number of animation strip rows
STAGGER    = 0.042    # seconds between each row reveal
# ──────────────────────────────────────────────────────────────────────────────


def image_to_b64(path: Path, w: int, h: int) -> str:
    img = Image.open(path).convert("RGBA")
    img = img.resize((w, h), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, "PNG", optimize=True, compress_level=9)
    return base64.b64encode(buf.getvalue()).decode()


def build_svg(b64: str) -> str:
    row_h = IMG_H / N_ROWS
    hold_begin = N_ROWS * STAGGER + 0.3

    p = []

    # ── Header ────────────────────────────────────────────────────────────────
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Defs ──────────────────────────────────────────────────────────────────
    p.append('<defs>')

    # Glow filter
    p.append(
        '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="2.5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )

    # Row-by-row clip path — each rect animates from width=0 to full SVG width
    p.append('<clipPath id="reveal">')
    for i in range(N_ROWS):
        y = PAD + i * row_h
        begin = i * STAGGER
        p.append(
            f'<rect x="0" y="{y:.2f}" width="0" height="{row_h + 1:.2f}">'
            f'<animate attributeName="width" values="0;{SVG_W}" '
            f'dur="0.22s" begin="{begin:.3f}s" fill="freeze"/>'
            f'</rect>'
        )
    p.append('</clipPath>')
    p.append('</defs>')

    # ── Background ────────────────────────────────────────────────────────────
    p.append(f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}" rx="10"/>')

    # ── Subtle scanlines ──────────────────────────────────────────────────────
    for y in range(0, SVG_H, 4):
        p.append(
            f'<rect x="0" y="{y}" width="{SVG_W}" height="1" '
            f'fill="{DIM}" opacity="0.04"/>'
        )

    # ── Embedded image with clip-path reveal ──────────────────────────────────
    p.append(
        f'<image href="data:image/png;base64,{b64}" '
        f'x="{PAD}" y="{PAD}" width="{IMG_W}" height="{IMG_H}" '
        f'clip-path="url(#reveal)" '
        f'preserveAspectRatio="xMidYMid meet"/>'
    )

    # ── Green frame border that fades in after full reveal ────────────────────
    p.append(
        f'<rect x="{PAD}" y="{PAD}" width="{IMG_W}" height="{IMG_H}" '
        f'rx="4" fill="none" stroke="{DIM}" stroke-width="1" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.6" '
        f'dur="0.4s" begin="{hold_begin:.2f}s" fill="freeze"/>'
        f'</rect>'
    )

    # ── Blinking cursor below image ───────────────────────────────────────────
    cursor_y = PAD + IMG_H + 22
    p.append(
        f'<text x="{PAD}" y="{cursor_y}" font-size="12" '
        f'fill="{ACCENT}" opacity="0" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="0;1" '
        f'dur="0.3s" begin="{hold_begin:.2f}s" fill="freeze"/>'
        f'$ <animate attributeName="opacity" values="1;0;1" '
        f'dur="0.85s" begin="{hold_begin:.2f}s" repeatCount="indefinite"/>_'
        f'</text>'
    )

    p.append('</svg>')
    return '\n'.join(p)


def main():
    if not GENERATED.exists():
        print(f"ERROR: {GENERATED} not found")
        raise SystemExit(1)

    print(f"Loading {GENERATED.name} ({GENERATED.stat().st_size // 1024}KB)...")
    b64 = image_to_b64(GENERATED, IMG_W, IMG_H)
    print(f"Base64 encoded: {len(b64) // 1024}KB")

    svg = build_svg(b64)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg) // 1024}KB)")


if __name__ == "__main__":
    main()
