"""
clean_photo.py
--------------
Stage 1 of the portrait pipeline:
  1. Remove background with rembg
  2. Fill transparent BG with white (so dark → dense chars, light BG → empty)
  3. Apply CLAHE (contrast enhancement) to bring out face detail
  4. Save as assets/photo-ready.png

Usage:
  python tools/clean_photo.py assets/photo-source.jpg
"""

import sys
from pathlib import Path

def main():
    import cv2
    import numpy as np
    from PIL import Image
    from rembg import remove

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/photo-source.jpg")
    out = Path("assets/photo-ready.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {src}...")
    img_bytes = src.read_bytes()

    # Step 1 — Remove background
    print("Removing background (rembg)...")
    removed_bytes = remove(img_bytes)
    rgba = Image.open(__import__("io").BytesIO(removed_bytes)).convert("RGBA")

    # Step 2 — Paste onto white canvas
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    white_bg.paste(rgba, mask=rgba.split()[3])
    rgb = white_bg.convert("RGB")

    # Step 3 — CLAHE contrast enhancement via OpenCV
    print("Enhancing contrast (CLAHE)...")
    cv_img = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(cv_img)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)
    enhanced = cv2.merge([l_eq, a, b])
    enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

    result = Image.fromarray(enhanced_rgb)
    result.save(out)
    print(f"Saved {out} ({result.size[0]}x{result.size[1]}px)")


if __name__ == "__main__":
    main()
