"""
render_portrait.py
------------------
Stage 2 of the portrait pipeline:
Converts assets/photo-ready.png into an animated ASCII SVG (portrait.svg).

- Maps pixel brightness to a glyph ramp (white BG → space, dark → dense)
- Single Matrix Green accent color
- Row-by-row clip-path reveal animation (40ms stagger per row)
- Plays once then holds with a blinking cursor

No loops — the portrait settles and stays.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "portrait.svg"
PHOTO = Path(__file__).parent.parent / "assets" / "photo-ready.png"

# ── Design tokens ─────────────────────────────────────────────────────────────
BG       = "#0d1117"
ACCENT   = "#39ff14"
DIM      = "#1a6b0a"
FONT     = "ui-monospace, 'Cascadia Code', 'Fira Code', monospace"

# ASCII output dimensions (chars)
COLS     = 52
ROWS     = 38

# SVG text settings
FONT_SIZE = 10
CHAR_W    = 6.1    # monospace char width at font-size 10
LINE_H    = 11     # line height px

STAGGER_MS = 40    # ms between each row reveal
SVG_W      = int(COLS * CHAR_W) + 24
SVG_H      = ROWS * LINE_H + 40

# Glyph ramp: index 0 = lightest (white BG → empty), index -1 = darkest
# Inverted: white pixel → space, dark pixel → dense char
GLYPHS = " .'`:,;~+*?oxXO0#@"


def photo_to_ascii(photo_path: Path) -> list[str]:
    """Convert cleaned photo to list of ASCII strings, one per row."""
    from PIL import Image
    import numpy as np

    img = Image.open(photo_path).convert("L")  # grayscale

    # Crop to roughly portrait aspect ratio (center crop)
    w, h = img.size
    target_h = int(w * (ROWS / COLS) * (CHAR_W / LINE_H))
    if target_h < h:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))

    # Resize to char grid
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)

    # Map brightness to glyphs
    # 255 (white/background) → space, 0 (black/dark) → dense char
    n = len(GLYPHS) - 1
    rows = []
    for row in pixels:
        line = ""
        for px in row:
            idx = int(px / 255 * n)
            line += GLYPHS[idx]
        rows.append(line)
    return rows


def make_clippath(idx: int) -> str:
    begin_s = idx * STAGGER_MS / 1000
    y = idx * LINE_H + 14
    return (
        f'<clipPath id="c{idx}">'
        f'<rect x="0" y="{y}" width="{SVG_W}" height="{LINE_H + 1}">'
        f'<animate attributeName="width" values="0;{SVG_W}" '
        f'dur="0.22s" begin="{begin_s:.3f}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(ascii_rows: list[str]) -> str:
    n = len(ascii_rows)
    hold_begin = (n * STAGGER_MS / 1000) + 0.35

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'style="background:{BG};border-radius:10px;font-family:{FONT};">'
    )

    # ── Defs ─────────────────────────────────────────────────────────────────
    parts.append('<defs>')
    parts.append(
        '<filter id="glow" x="-10%" y="-10%" width="120%" height="120%">'
        '<feGaussianBlur stdDeviation="1.5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    for i in range(n):
        parts.append(make_clippath(i))
    parts.append('</defs>')

    # ── Scanlines overlay ────────────────────────────────────────────────────
    for row in range(0, SVG_H, LINE_H):
        parts.append(
            f'<rect x="0" y="{row}" width="{SVG_W}" height="1" '
            f'fill="{DIM}" opacity="0.06"/>'
        )

    # ── ASCII rows ────────────────────────────────────────────────────────────
    for i, row_text in enumerate(ascii_rows):
        y = (i + 1) * LINE_H + 14
        # spaces only → skip (keep BG transparent)
        if row_text.strip() == "":
            continue
        # Vary color slightly: dense rows get brighter accent
        density = len(row_text.replace(" ", "")) / max(len(row_text), 1)
        color = ACCENT if density > 0.15 else DIM
        glow = ' filter="url(#glow)"' if density > 0.3 else ''
        parts.append(
            f'<text x="12" y="{y}" font-size="{FONT_SIZE}" fill="{color}" '
            f'clip-path="url(#c{i})"{glow} xml:space="preserve">'
            f'{escape_xml(row_text)}</text>'
        )

    # ── Bottom prompt + blinking cursor ──────────────────────────────────────
    cursor_y = n * LINE_H + 28
    parts.append(
        f'<text x="12" y="{cursor_y}" font-size="{FONT_SIZE}" '
        f'fill="{ACCENT}" opacity="0" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="0;1" '
        f'dur="0.3s" begin="{hold_begin:.2f}s" fill="freeze"/>'
        f'$ <animate attributeName="opacity" values="1;0;1" '
        f'dur="0.9s" begin="{hold_begin:.2f}s" repeatCount="indefinite"/>█'
        f'</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if not PHOTO.exists():
        print(f"ERROR: {PHOTO} not found.")
        print("Run: python tools/clean_photo.py assets/photo-source.jpg")
        raise SystemExit(1)

    print(f"Converting {PHOTO} to ASCII...")
    ascii_rows = photo_to_ascii(PHOTO)

    print(f"Rendering {len(ascii_rows)} rows -> {OUT}...")
    svg = render(ascii_rows)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
