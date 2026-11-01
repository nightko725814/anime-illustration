"""Paste the masked area of an inpainted render back onto the picked image and report what changed.

ComfyUI's masked inpaint returns a whole frame that went through the VAE, so even pixels outside the
mask drift a little. Compositing with the same mask keeps the rest of the picked image pixel-identical.

Usage:
    python composite_mask.py BASE.png INPAINTED.png MASK.png OUT.png
"""

from __future__ import annotations

import argparse

import numpy as np
from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="The picked image to keep")
    parser.add_argument("inpainted", help="ComfyUI output of the masked inpaint")
    parser.add_argument("mask", help="Grayscale mask, white = take the inpainted pixels")
    parser.add_argument("out")
    args = parser.parse_args()

    base = Image.open(args.base).convert("RGB")
    out = Image.composite(Image.open(args.inpainted).convert("RGB"), base, Image.open(args.mask).convert("L"))
    out.save(args.out)

    changed = np.abs(np.asarray(out, np.int16) - np.asarray(base, np.int16)).max(axis=2) > 0
    if changed.any():
        ys, xs = np.nonzero(changed)
        print(f"saved {args.out}: {int(changed.sum())} pixels changed, x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
    else:
        print(f"saved {args.out}: no pixels changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
