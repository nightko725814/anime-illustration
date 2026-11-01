"""Cut the anime character out of an image with SkyTNT's anime-seg (isnetis.onnx) and save a soft mask.

White = character, black = background. Runs on CPU; needs onnxruntime, numpy, pillow and scipy
(in a venv of your own). Download isnetis.onnx with scripts/download_models.py (role: anime_seg)
or point --model / ISNETIS_ONNX at it.

Busy collage backgrounds confuse the model, so it helps to run it on a crop around the character
(--crop), cut away far-off paper scraps with a hand-drawn polygon (--keep), sharpen the soft edge
(--low/--high) and drop stray islands (--largest).

Usage:
    python cutout_mask.py IMAGE OUT_MASK.png [--crop X0,Y0,X1,Y1] [--keep X,Y X,Y ...]
                          [--low 0.35 --high 0.65] [--largest] [--model ...] [--size 1024]
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage


def predict(session: ort.InferenceSession, img: Image.Image, s: int) -> np.ndarray:
    """Soft character mask in [0, 1] at the size of img."""
    w0, h0 = img.size
    h, w = (s, round(s * w0 / h0)) if h0 > w0 else (round(s * h0 / w0), s)
    top, left = (s - h) // 2, (s - w) // 2
    # Letterbox into an s x s canvas, as the model was trained
    canvas = np.zeros((s, s, 3), np.float32)
    canvas[top:top + h, left:left + w] = np.asarray(img.resize((w, h), Image.BILINEAR), np.float32) / 255
    pred = session.run(None, {session.get_inputs()[0].name: canvas.transpose(2, 0, 1)[None]})[0][0, 0]
    pred = np.clip(pred[top:top + h, left:left + w], 0, 1)
    resized = Image.fromarray((pred * 255).astype(np.uint8)).resize((w0, h0), Image.BILINEAR)
    return np.asarray(resized, np.float32) / 255


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("out")
    parser.add_argument("--model", default=os.environ.get("ISNETIS_ONNX"),
                        help="Path to isnetis.onnx (default: env ISNETIS_ONNX)")
    parser.add_argument("--size", type=int, default=1024, help="Square input size the model expects")
    parser.add_argument("--crop", default=None, help="X0,Y0,X1,Y1: run the model on this region only")
    parser.add_argument("--keep", nargs="+", default=None, help="Polygon X,Y points; mask is zeroed outside it")
    parser.add_argument("--feather", type=float, default=6, help="Blur radius for the --keep polygon edge")
    parser.add_argument("--low", type=float, default=0.0, help="Mask values at or below this become 0")
    parser.add_argument("--high", type=float, default=1.0, help="Mask values at or above this become 1")
    parser.add_argument("--largest", action="store_true", help="Keep only the largest connected region")
    args = parser.parse_args()
    if not args.model:
        parser.error(
            "no isnetis.onnx given. Pass --model /path/to/isnetis.onnx, set ISNETIS_ONNX, or run "
            "scripts/download_models.py --role anime_seg first"
        )

    src = Image.open(args.image).convert("RGB")
    session = ort.InferenceSession(args.model, providers=["CPUExecutionProvider"])

    if args.crop:
        x0, y0, x1, y1 = (int(v) for v in args.crop.split(","))
        mask = np.zeros((src.height, src.width), np.float32)
        mask[y0:y1, x0:x1] = predict(session, src.crop((x0, y0, x1, y1)), args.size)
    else:
        mask = predict(session, src, args.size)

    if args.keep:
        poly = Image.new("L", src.size, 0)
        ImageDraw.Draw(poly).polygon([tuple(int(v) for v in p.split(",")) for p in args.keep], fill=255)
        poly = poly.filter(ImageFilter.GaussianBlur(args.feather))
        mask *= np.asarray(poly, np.float32) / 255

    mask = np.clip((mask - args.low) / max(args.high - args.low, 1e-6), 0, 1)

    if args.largest:
        labels, count = ndimage.label(mask > 0.5)
        if count > 1:
            sizes = ndimage.sum(np.ones_like(labels), labels, range(1, count + 1))
            main_region = ndimage.binary_dilation(labels == 1 + int(np.argmax(sizes)), iterations=3)
            mask *= main_region

    Image.fromarray((mask * 255).astype(np.uint8)).save(args.out)
    print(f"saved {args.out}  coverage={mask.mean():.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
