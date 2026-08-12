#!/usr/bin/env python3
from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: prep_photo.py <image>", file=sys.stderr)
        return 1

    src = Path(sys.argv[1])
    dst = Path("source-prepped.png")

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    except Exception as exc:
        print(f"pillow is required to prep photos: {exc}", file=sys.stderr)
        return 1

    image = Image.open(src).convert("RGBA")

    try:
        import numpy as np
        import cv2
        from rembg import remove

        cutout = remove(image)
        if isinstance(cutout, bytes):
            cutout = Image.open(BytesIO(cutout))
        elif not isinstance(cutout, Image.Image):
            cutout = Image.fromarray(np.array(cutout))
        image = cutout.convert("RGBA")

        rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2RGB)
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8))
        l = clahe.apply(l)
        merged = cv2.merge((l, a, b))
        image = Image.fromarray(cv2.cvtColor(merged, cv2.COLOR_LAB2RGBA))
    except Exception:
        image = image.convert("RGB").convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    alpha = image.getchannel("A")
    white.paste(image, mask=alpha)

    gray = ImageOps.grayscale(white.convert("RGB"))
    gray = gray.filter(ImageFilter.SHARPEN)
    gray = ImageEnhance.Contrast(gray).enhance(1.3)

    gray.save(dst)
    print(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
