"""
render_portrait.py
------------------
Converts assets/photo-ready.png into an animated ASCII SVG (portrait.svg).

Key design:
- White background pixels → space (invisible, shows SVG dark bg)
- Dark pixels (hair) → dense chars
- Mid-bright pixels (skin) → medium chars
- Row-by-row clip-path reveal (40ms stagger), plays once then holds.
"""

from pathlib import Path

OUT   = Path(__file__).parent.parent / "portrait.svg"
PHOTO = Path(__file__).parent.parent / "assets" / "photo-ready.png"

# ── Design tokens ─────────────────────────────────────────────────────────────
BG         = "#0d1117"
ACCENT     = "#39ff14"
DIM        = "#1a6b0a"
FONT       = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

# Output grid
# KEY: CHAR_W=6px, LINE_H=12px → chars are 2× taller than wide
# So for a square image: ROWS = COLS × (CHAR_W / LINE_H) = COLS / 2
# Using COLS=62, ROWS=31 → rendered 372×372px (square, correct proportions)
COLS       = 62
ROWS       = 31

# SVG text metrics at font-size 10px monospace
FONT_SIZE  = 10
CHAR_W     = 6.0    # px per character
LINE_H     = 12     # px per line

STAGGER_MS = 42     # ms between row reveals
PAD_LEFT   = 10
SVG_W      = int(COLS * CHAR_W) + PAD_LEFT + 4
SVG_H      = ROWS * LINE_H + 44

# Glyph ramp — index 0 = lightest (white→empty space), index -1 = darkest
# INVERTED mapping: bright pixel → sparse glyph, dark pixel → dense glyph
GLYPHS = " .'`^,:;Il!i><~+_-?][{}1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def photo_to_ascii(photo_path: Path) -> list[str]:
    """Convert cleaned photo (white bg) to ASCII rows.
    Bright pixel (white bg) → sparse/space glyph.
    Dark pixel (hair, shadows) → dense glyph.
    """
    from PIL import Image
    import numpy as np

    img = Image.open(photo_path).convert("L")  # grayscale
    w, h = img.size

    # ── Aspect ratio fix ────────────────────────────────────────────────────
    # The rendered grid is COLS*CHAR_W wide × ROWS*LINE_H tall.
    # To avoid stretch, the image crop must have the SAME ratio:
    #   target_h = image_w * (ROWS * LINE_H) / (COLS * CHAR_W)
    # For COLS=62, ROWS=31, CHAR_W=6, LINE_H=12:
    #   target_h = w * (31*12)/(62*6) = w * 372/372 = w  → no crop (square in, square out)
    rendered_w = COLS * CHAR_W
    rendered_h = ROWS * LINE_H
    target_h = int(w * rendered_h / rendered_w)
    target_h = min(target_h, h)

    # Crop — focus on face (top 85% of the image = head + shoulders)
    if target_h < h:
        top = max(0, int((h - target_h) * 0.1))
        img = img.crop((0, top, w, top + target_h))
    else:
        # Full square: crop to top 85% to cut excess chest area
        img = img.crop((0, 0, w, int(h * 0.85)))

    # Resize to char grid
    img = img.resize((COLS, ROWS), Image.LANCZOS)

    # Bilateral filter for smooth skin while preserving hair edges
    import cv2
    import numpy as _np
    cv_img = _np.array(img)
    cv_img = cv2.bilateralFilter(cv_img, 7, 50, 50)
    img = Image.fromarray(cv_img)

    # Boost contrast sharply so hair goes dark and skin goes bright
    from PIL import ImageEnhance
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(1.8)

    pixels = _np.array(img)
    n = len(GLYPHS) - 1

    rows = []
    for row in pixels:
        line = ""
        for px in row:
            # INVERTED: bright (255=white bg) → index 0 (space)
            #           dark   (0=hair/shadow) → index n (dense char)
            idx = n - int(px / 255 * n)
            line += GLYPHS[idx]
        rows.append(line)
    return rows


def make_clippath(idx: int) -> str:
    begin_s = idx * STAGGER_MS / 1000
    y = idx * LINE_H + PAD_LEFT
    return (
        f'<clipPath id="c{idx}">'
        f'<rect x="0" y="{y}" width="{SVG_W}" height="{LINE_H + 1}">'
        f'<animate attributeName="width" values="0;{SVG_W}" '
        f'dur="0.20s" begin="{begin_s:.3f}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def char_color(density: float) -> str:
    """Map character density to a color — denser = brighter green."""
    if density > 0.65:
        return ACCENT        # bright green for very dark areas (hair, shadows)
    elif density > 0.35:
        return "#28a805"     # mid green for face/skin mid-tones
    elif density > 0.08:
        return DIM           # dim for highlights and light skin
    else:
        return DIM           # nearly empty rows


def render(ascii_rows: list[str]) -> str:
    n = len(ascii_rows)
    hold_begin = (n * STAGGER_MS / 1000) + 0.3

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Defs: glow filter + clip paths ───────────────────────────────────────
    parts.append('<defs>')
    parts.append(
        '<filter id="glow" x="-10%" y="-10%" width="120%" height="120%">'
        '<feGaussianBlur stdDeviation="1.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    for i in range(n):
        parts.append(make_clippath(i))
    parts.append('</defs>')

    # ── Scanlines overlay (subtle) ────────────────────────────────────────────
    for row in range(0, SVG_H, LINE_H * 2):
        parts.append(
            f'<rect x="0" y="{row}" width="{SVG_W}" height="1" '
            f'fill="{DIM}" opacity="0.07"/>'
        )

    # ── ASCII text rows ───────────────────────────────────────────────────────
    for i, row_text in enumerate(ascii_rows):
        stripped = row_text.strip()
        if not stripped:
            continue  # fully blank row — skip, SVG bg shows through

        y = (i + 1) * LINE_H + PAD_LEFT
        density = len(stripped) / max(len(row_text), 1)
        color = char_color(density)
        # Only apply expensive glow filter to dense rows (hair/shoulders)
        glow = ' filter="url(#glow)"' if density > 0.5 else ''

        parts.append(
            f'<text x="{PAD_LEFT}" y="{y}" font-size="{FONT_SIZE}" '
            f'fill="{color}" clip-path="url(#c{i})"{glow} '
            f'xml:space="preserve">{escape_xml(row_text)}</text>'
        )

    # ── Blinking cursor at end ────────────────────────────────────────────────
    cursor_y = n * LINE_H + PAD_LEFT + 14
    parts.append(
        f'<text x="{PAD_LEFT}" y="{cursor_y}" font-size="{FONT_SIZE}" '
        f'fill="{ACCENT}" opacity="0" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="0;1" '
        f'dur="0.3s" begin="{hold_begin:.2f}s" fill="freeze"/>'
        f'$ <animate attributeName="opacity" values="1;0;1" '
        f'dur="0.9s" begin="{hold_begin:.2f}s" repeatCount="indefinite"/>_'
        f'</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if not PHOTO.exists():
        print(f"ERROR: {PHOTO} not found.")
        print("Run: python tools/clean_photo.py assets/photo-source.jpg")
        raise SystemExit(1)

    print(f"Converting {PHOTO} to ASCII ({COLS}x{ROWS} grid)...")
    ascii_rows = photo_to_ascii(PHOTO)

    print(f"Rendering {len(ascii_rows)} rows -> {OUT}...")
    svg = render(ascii_rows)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
