"""Compare two images pixel by pixel, e.g. a preset's best.png against a fresh --as-is re-render.

Usage:
    python pixel_diff.py A.png B.png
"""

from __future__ import annotations

import argparse
import hashlib

import numpy as np
from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("a")
    parser.add_argument("b")
    args = parser.parse_args()

    a = np.asarray(Image.open(args.a).convert("RGB"))
    b = np.asarray(Image.open(args.b).convert("RGB"))
    if a.shape != b.shape:
        print(f"different sizes: {a.shape[1]}x{a.shape[0]} vs {b.shape[1]}x{b.shape[0]}")
        return 1
    same = (a == b).all(axis=2).mean() * 100
    max_diff = int(np.abs(a.astype(np.int16) - b.astype(np.int16)).max())
    identical = hashlib.sha256(a.tobytes()).hexdigest() == hashlib.sha256(b.tobytes()).hexdigest()
    print(f"identical pixels {same:.4f}%  max diff {max_diff}  pixel data identical: {identical}")
    return 0 if identical else 2


if __name__ == "__main__":
    raise SystemExit(main())
