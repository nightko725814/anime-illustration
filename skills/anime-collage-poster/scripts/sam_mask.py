"""Segment one object with SAM 2.1 from a box and click points, and save a soft mask (white = object).

Runs in the ComfyUI venv (torch + transformers >= 5). Useful where the anime cutout model fails, e.g.
crimson hair on a crimson background: give a box around the part plus a few points on it (--pos) and on
the background next to it (--neg).

Download the model with scripts/download_models.py (role: sam2) or set --model / SAM2_MODEL_DIR
to the sam2.1-hiera-large directory.

Usage:
    python sam_mask.py IMAGE OUT_MASK.png --box X0,Y0,X1,Y1 [--pos X,Y ...] [--neg X,Y ...]
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import torch
from PIL import Image
from transformers import Sam2Model, Sam2Processor


def points(values: list[str]) -> list[list[int]]:
    return [[int(v) for v in p.split(",")] for p in values]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("out")
    parser.add_argument("--box", required=True, help="X0,Y0,X1,Y1 around the object")
    parser.add_argument("--pos", nargs="*", default=[], help="X,Y points on the object")
    parser.add_argument("--neg", nargs="*", default=[], help="X,Y points on the background")
    parser.add_argument("--model", default=os.environ.get("SAM2_MODEL_DIR"),
                        help="Directory of sam2.1-hiera-large (default: env SAM2_MODEL_DIR)")
    args = parser.parse_args()
    if not args.model:
        parser.error(
            "no SAM 2.1 model directory given. Pass --model /path/to/sam2.1-hiera-large, set "
            "SAM2_MODEL_DIR, or run scripts/download_models.py --role sam2 first"
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = Sam2Processor.from_pretrained(args.model)
    model = Sam2Model.from_pretrained(args.model).to(device).eval()

    image = Image.open(args.image).convert("RGB")
    clicks = points(args.pos) + points(args.neg)
    kwargs = {"input_boxes": [[[int(v) for v in args.box.split(",")]]]}
    if clicks:
        kwargs["input_points"] = [[clicks]]
        kwargs["input_labels"] = [[[1] * len(args.pos) + [0] * len(args.neg)]]
    inputs = processor(images=image, return_tensors="pt", **kwargs).to(device)

    with torch.no_grad():
        outputs = model(**inputs, multimask_output=True)
    scores = outputs.iou_scores[0, 0].float().cpu().numpy()
    best = int(np.argmax(scores))
    logits = processor.post_process_masks(outputs.pred_masks.float().cpu(), inputs["original_sizes"],
                                          binarize=False)[0][0, best]
    mask = torch.sigmoid(logits).numpy()

    Image.fromarray((mask * 255).astype(np.uint8)).save(args.out)
    print(f"saved {args.out}  scores={np.round(scores, 3).tolist()} picked={best} coverage={mask.mean():.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
