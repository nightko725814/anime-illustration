"""Lay out images in a grid (default: one column), each scaled to the same width, with a label bar.

Usage:
    python compare.py OUT.jpg "label1=path1" "label2=path2" ... [--width 1280] [--cols 2]
"""

from __future__ import annotations

import argparse

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",       # Windows: Microsoft YaHei (CJK-safe)
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(size: int):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out")
    parser.add_argument("items", nargs="+", help="label=path")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--cols", type=int, default=1)
    args = parser.parse_args()

    font = load_font(28)

    cells = []
    for item in args.items:
        label, path = item.split("=", 1)
        src = Image.open(path).convert("RGB")
        img = src.resize((args.width, round(src.height * args.width / src.width)), Image.LANCZOS)
        cell = Image.new("RGB", (args.width, img.height + 44), (24, 24, 24))
        ImageDraw.Draw(cell).text((12, 6), f"{label}  ({src.width}x{src.height})", fill=(240, 240, 240), font=font)
        cell.paste(img, (0, 44))
        cells.append(cell)

    gap = 8
    rows = [cells[i:i + args.cols] for i in range(0, len(cells), args.cols)]
    row_heights = [max(c.height for c in row) for row in rows]
    sheet = Image.new("RGB", (args.cols * args.width + (args.cols - 1) * gap,
                              sum(row_heights) + (len(rows) - 1) * gap), (0, 0, 0))
    y = 0
    for row, height in zip(rows, row_heights):
        for col, cell in enumerate(row):
            sheet.paste(cell, (col * (args.width + gap), y))
        y += height + gap
    sheet.save(args.out, quality=90)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
