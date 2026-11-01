"""Add a VHS-style glitch: shift horizontal strips sideways with a red/cyan channel split.

Each --band is "y,height,shift" in pixels. The band is cut into a few sub-strips whose
shifts jitter around the given value, so the edge looks torn rather than ruler-straight.

Usage:
    python glitch_slice.py IN.png OUT.png --band 585,48,36 --band 700,10,-22 [--x0 560 --x1 1520]
"""

from __future__ import annotations

import argparse

import numpy as np
from PIL import Image


def shift_cols(block: np.ndarray, dx: int) -> np.ndarray:
    """Shift a (rows, cols, ...) block sideways; pixels the shift uncovers keep their original values."""
    out = block.copy()
    if dx > 0:
        out[:, dx:] = block[:, :-dx]
    elif dx < 0:
        out[:, :dx] = block[:, -dx:]
    return out


def glitch_strip(region: np.ndarray, dx: int, split: int, scanline: float) -> np.ndarray:
    out = np.empty_like(region)
    out[..., 0] = shift_cols(region[..., 0], dx + split)  # red pushed one way
    out[..., 1] = shift_cols(region[..., 1], dx)
    out[..., 2] = shift_cols(region[..., 2], dx - split)  # blue pushed the other way: red/cyan fringe
    if scanline > 0:
        out[::2] = (out[::2] * (1.0 - scanline)).astype(out.dtype)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--band", action="append", required=True, help="y,height,shift (repeatable)")
    parser.add_argument("--x0", type=int, default=0, help="Left edge of the glitched area")
    parser.add_argument("--x1", type=int, default=None, help="Right edge of the glitched area")
    parser.add_argument("--split", type=int, default=6, help="Red/cyan channel offset in pixels")
    parser.add_argument("--scanline", type=float, default=0.12, help="Darkening of every other row inside a band")
    parser.add_argument("--pieces", type=int, default=3, help="Sub-strips per band")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    img = Image.open(args.src).convert("RGB")
    arr = np.asarray(img).copy()
    x1 = args.x1 if args.x1 is not None else arr.shape[1]
    rng = np.random.default_rng(args.seed)

    for spec in args.band:
        y, height, dx = (int(v) for v in spec.split(","))
        cuts = np.sort(rng.choice(np.arange(1, height), size=min(args.pieces, height) - 1, replace=False))
        edges = [y, *(y + c for c in cuts), y + height]
        for top, bottom in zip(edges[:-1], edges[1:]):
            piece_dx = int(round(dx * rng.uniform(0.6, 1.3)))
            arr[top:bottom, args.x0:x1] = glitch_strip(arr[top:bottom, args.x0:x1], piece_dx, args.split, args.scanline)

    Image.fromarray(arr).save(args.dst)
    print(args.dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
