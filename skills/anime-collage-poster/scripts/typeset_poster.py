"""Typeset titles onto a regenerated poster background and put the original character back on top.

Layers, bottom to top: BASE (new background) -> "behind" items -> ORIGINAL pixels where KEEP_MASK is white
-> cleanup patches -> "front" items. Items come from a JSON layout file (a list of objects), drawn in order.

Text item:
    {"text": "重音テト", "font": "YuGothB.ttc", "size": 250, "x": 50, "y": 70,
     "style": "outline" | "fill" | "solid", "color": [255, 255, 255], "stroke": 6,
     "stroke_color": [30, 10, 15], "axes": [900], "spacing": 0, "opacity": 1.0,
     "echo": {"dx": 6, "dy": 4, "color": [0, 190, 210], "opacity": 0.8},
     "box": [180, 20, 40], "pad": 10, "rotate": 0, "layer": "behind" | "front"}

"outline" draws hollow letters (a ring of width "stroke" around each glyph); "fill" draws solid letters;
"solid" draws letters filled with "color" and outlined in "stroke_color", readable over busy backgrounds.
"blur" softens the letters by that Gaussian radius in pixels.
"axes" sets variable-font axes (e.g. [900] for the heaviest NotoSerifSC-VF.ttf). "echo" adds an offset copy
in another color behind the letters, like misregistered print. Fonts given without a folder are looked up in
C:\\Windows\\Fonts. Items may hang off the canvas edges.

Scrap item: letters printed on a torn paper scrap with a soft shadow. Takes the text keys, with "scrap"
in place of "text" and "ink" for the letter color:
    {"scrap": "重", "font": "NotoSerifSC-VF.ttf", "axes": [900], "size": 210, "x": 30, "y": 40,
     "ink": [24, 18, 20], "paper": [240, 230, 208], "halftone": {"color": [200, 60, 70], "step": 12, "radius": 3},
     "pad": 26, "tear": 7, "seed": 1, "shadow": [6, 9, 0.35], "rotate": -7, "layer": "behind"}

Tape item: a strip of translucent tape with torn ends, pasted at (X, Y):
    {"tape": [X, Y, W, H], "rotate": 12, "color": [250, 248, 240], "opacity": 0.55, "seed": 3, "layer": "front"}

Patch item {"patch": [X0, Y0, X1, Y1], "from": [DX, DY]} cleans leftover gray glyph fragments in that box
after the character is composited: gray pixels (and a 2 px fringe) are replaced by the poster pixels
offset by (DX, DY). Saturated pixels such as hair and bright white paper are left alone. With "mode": "all"
the whole box is replaced instead, blended over a 3 px edge; use it only where the box holds no hair.
With "mode": "inpaint" (no "from" needed) every pixel that stands out from the box's dominant color is
filled in from its surroundings (OpenCV Telea) and given the surrounding paper grain; keep hair out of the box.

Usage:
    python typeset_poster.py BASE.png ORIGINAL.png KEEP_MASK.png LAYOUT.json OUT.png
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

FONT_DIRS = [
    Path(os.environ["FONT_DIR"]) if os.environ.get("FONT_DIR") else None,
    Path(r"C:\Windows\Fonts"),
    Path("/usr/share/fonts/truetype"),
    Path("/usr/share/fonts/opentype"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path("/System/Library/Fonts"),
    Path("/Library/Fonts"),
]


def resolve_font(font_path: Path) -> Path:
    if font_path.is_absolute():
        return font_path
    for d in FONT_DIRS:
        if d and (d / font_path).is_file():
            return d / font_path
    raise FileNotFoundError(
        f"font {font_path!s} not found in any font directory. Set FONT_DIR, use an absolute path, "
        "or install the font"
    )


def load_font(item: dict) -> ImageFont.FreeTypeFont:
    font_path = Path(item["font"])
    font = ImageFont.truetype(str(resolve_font(font_path)), item["size"])
    if "axes" in item:
        font.set_variation_by_axes(item["axes"])
    return font


def text_layer(item: dict) -> Image.Image:
    font = load_font(item)
    text, spacing, stroke = item["text"], item.get("spacing", 0), item.get("stroke", 0)
    advances = [font.getlength(ch) for ch in text]
    ascent, descent = font.getmetrics()
    width = int(sum(advances) + spacing * (len(text) - 1)) + 2 * stroke + 4
    height = ascent + descent + 2 * stroke + 4

    def glyphs(stroke_width: int) -> Image.Image:
        mask = Image.new("L", (width, height), 0)
        draw, x = ImageDraw.Draw(mask), stroke + 2
        for ch, advance in zip(text, advances):
            draw.text((x, stroke + 2), ch, font=font, fill=255, stroke_width=stroke_width, stroke_fill=255)
            x += advance + spacing
        return mask

    def colored(mask: Image.Image, color: list[int], opacity: float = item.get("opacity", 1.0)) -> Image.Image:
        layer = Image.new("RGBA", mask.size, tuple(color) + (0,))
        layer.putalpha(mask.point(lambda v: round(v * opacity)))
        return layer

    color = item.get("color", [255, 255, 255])
    style = item.get("style")
    if style == "outline":
        # Hollow letters: the stroked shape minus the filled glyph leaves only the outer ring
        layer = colored(ImageChops.subtract(glyphs(stroke), glyphs(0)), color)
    elif style == "solid":
        layer = colored(glyphs(stroke), item.get("stroke_color", [30, 10, 15]))
        layer.alpha_composite(colored(glyphs(0), color))
    else:
        layer = colored(glyphs(stroke), color)

    if item.get("blur"):
        # Soften crisp vector letters so they sit with the slightly soft generated artwork
        layer = layer.filter(ImageFilter.GaussianBlur(item["blur"]))
    if "echo" in item:
        # Misregistered print: an offset copy in another color sits behind the letters
        echo = item["echo"]
        dx, dy = echo.get("dx", 6), echo.get("dy", 4)
        canvas = Image.new("RGBA", (width + abs(dx), height + abs(dy)), (0, 0, 0, 0))
        canvas.alpha_composite(colored(layer.getchannel("A"), echo["color"], echo.get("opacity", 0.8)),
                               (max(dx, 0), max(dy, 0)))
        canvas.alpha_composite(layer, (max(-dx, 0), max(-dy, 0)))
        layer = canvas
    if "box" in item:
        pad = item.get("pad", 10)
        boxed = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), tuple(item["box"]) + (255,))
        boxed.alpha_composite(layer, (pad, pad))
        layer = boxed
    if item.get("rotate"):
        layer = layer.rotate(item["rotate"], expand=True, resample=Image.BICUBIC)
    return layer


def torn_outline(w: int, h: int, tear: float, rng: np.random.Generator, step: int = 8) -> list[tuple]:
    """Rectangle outline whose edges wobble inward by up to `tear` pixels, like torn paper."""
    top = [(x, rng.uniform(0, tear)) for x in range(0, w, step)]
    right = [(w - 1 - rng.uniform(0, tear), y) for y in range(0, h, step)]
    bottom = [(x, h - 1 - rng.uniform(0, tear)) for x in range(w - 1, -1, -step)]
    left = [(rng.uniform(0, tear), y) for y in range(h - 1, -1, -step)]
    return top + right + bottom + left


def scrap_layer(item: dict) -> Image.Image:
    rng = np.random.default_rng(item.get("seed", 0))
    inner = {k: v for k, v in item.items() if k not in ("rotate", "box")}
    letters = text_layer({**inner, "text": item["scrap"], "color": item.get("ink", [24, 18, 20])})
    pad, tear = item.get("pad", 24), item.get("tear", 7)
    w, h = letters.width + 2 * pad, letters.height + 2 * pad

    shape = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shape).polygon(torn_outline(w, h, tear, rng), fill=255)
    paper = np.empty((h, w, 3), np.float32)
    paper[:] = item.get("paper", [240, 232, 214])
    paper += rng.normal(0, 4, (h, w, 1))
    sheet = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert("RGBA")
    if "halftone" in item:
        dots = item["halftone"]
        step, r, dot_color = dots.get("step", 12), dots.get("radius", 3), tuple(dots["color"])
        draw = ImageDraw.Draw(sheet)
        for row, y in enumerate(range(0, h, step)):
            for x in range((row % 2) * step // 2, w, step):
                draw.ellipse([x - r, y - r, x + r, y + r], fill=dot_color)
    sheet.alpha_composite(letters, (pad, pad))
    sheet.putalpha(shape)

    dx, dy, strength = item.get("shadow", [6, 9, 0.35])
    blur = 6
    canvas = Image.new("RGBA", (w + dx + 2 * blur, h + dy + 2 * blur), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w, h), (20, 10, 12, 0))
    shadow.putalpha(shape.point(lambda v: round(v * strength)))
    canvas.alpha_composite(shadow, (blur + dx, blur + dy))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sheet, (blur, blur))
    if item.get("rotate"):
        canvas = canvas.rotate(item["rotate"], expand=True, resample=Image.BICUBIC)
    return canvas


def tape_layer(item: dict) -> Image.Image:
    rng = np.random.default_rng(item.get("seed", 0))
    _, _, w, h = item["tape"]
    jag, step = max(2, h // 8), max(3, h // 6)
    outline = [(rng.uniform(0, jag), 0), (w - 1 - rng.uniform(0, jag), 0)]
    outline += [(w - 1 - rng.uniform(0, 2 * jag), y) for y in range(step, h - 1, step)]
    outline += [(w - 1 - rng.uniform(0, jag), h - 1), (rng.uniform(0, jag), h - 1)]
    outline += [(rng.uniform(0, 2 * jag), y) for y in range(h - 1 - step, 0, -step)]
    shape = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shape).polygon(outline, fill=255)
    layer = Image.new("RGBA", (w, h), tuple(item.get("color", [250, 248, 240])) + (0,))
    layer.putalpha(shape.point(lambda v: round(v * item.get("opacity", 0.55))))
    if item.get("rotate"):
        layer = layer.rotate(item["rotate"], expand=True, resample=Image.BICUBIC)
    return layer


def render(item: dict) -> tuple[Image.Image, int, int]:
    if "scrap" in item:
        return scrap_layer(item), item["x"], item["y"]
    if "tape" in item:
        return tape_layer(item), item["tape"][0], item["tape"][1]
    return text_layer(item), item["x"], item["y"]


def clean_glyphs(poster: Image.Image, box: list[int], offset: list[int], whole_box: bool = False) -> None:
    """Replace glyph pixels inside box (or the whole box) with pixels from box shifted by offset."""
    x0, y0, x1, y1 = box
    dx, dy = offset
    pixels = np.asarray(poster, np.float32).copy()
    region = pixels[y0:y1, x0:x1, :3]
    source = pixels[y0 + dy:y1 + dy, x0 + dx:x1 + dx, :3]
    if whole_box:
        # Keep the source's paper grain but shift its color to the crimson just around the box
        frame = pixels[y0 - 4:y1 + 4, x0 - 4:x1 + 4, :3].copy()
        frame[4:-4, 4:-4] = np.nan
        ring = frame.reshape(-1, 3)
        ring = ring[(ring[:, 0] > 120) & (ring[:, 1] < 70) & (ring[:, 2] < 80)]
        if len(ring):
            source = source + (np.median(ring, axis=0) - np.median(source.reshape(-1, 3), axis=0))
        weight = np.clip(ndimage.distance_transform_edt(np.pad(np.ones(region.shape[:2]), 1))[1:-1, 1:-1] / 3, 0, 1)
    else:
        brightness = region.mean(axis=2)
        # Gray glyph strokes only: bright white paper and saturated hair stay untouched
        gray = (region.max(axis=2) - region.min(axis=2) < 60) & (brightness > 100) & (brightness < 225)
        weight = ndimage.binary_dilation(gray, iterations=2).astype(np.float32)
    region[:] = region * (1 - weight[..., None]) + source * weight[..., None]
    poster.paste(Image.fromarray(pixels.round().astype(np.uint8), poster.mode))


def inpaint_glyphs(poster: Image.Image, box: list[int]) -> None:
    """Fill pixels that stand out from the box's dominant color from their surroundings."""
    x0, y0, x1, y1 = box
    pixels = np.asarray(poster.convert("RGB"), np.uint8).copy()
    region = pixels[y0:y1, x0:x1].astype(np.float32)
    dominant = np.median(region.reshape(-1, 3), axis=0)
    odd = np.linalg.norm(region - dominant, axis=2) > 40
    odd = ndimage.binary_dilation(odd, iterations=2)
    mask = np.zeros(pixels.shape[:2], np.uint8)
    mask[y0:y1, x0:x1][odd] = 255
    filled = cv2.inpaint(pixels, mask, 5, cv2.INPAINT_TELEA).astype(np.float32)
    # Telea leaves flat color; add back grain with the spread of the untouched pixels in the box
    grain = region[~odd].std(axis=0) if (~odd).any() else np.zeros(3)
    noise = np.random.default_rng(0).normal(0, 1, filled.shape).astype(np.float32) * grain
    filled[mask > 0] += noise[mask > 0]
    rgb = Image.fromarray(np.clip(filled, 0, 255).round().astype(np.uint8))
    poster.paste(rgb.convert(poster.mode))


def paste(dst: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    """alpha_composite that tolerates layers hanging off the canvas."""
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + layer.width, dst.width), min(y + layer.height, dst.height)
    if x1 > x0 and y1 > y0:
        dst.alpha_composite(layer.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("original")
    parser.add_argument("keep_mask")
    parser.add_argument("layout")
    parser.add_argument("out")
    args = parser.parse_args()

    base = Image.open(args.base).convert("RGBA")
    original = Image.open(args.original).convert("RGBA")
    keep = Image.open(args.keep_mask).convert("L")
    items = json.loads(Path(args.layout).read_text(encoding="utf-8"))

    drawable = [item for item in items if "patch" not in item]
    for item in drawable:
        if item.get("layer", "behind") == "behind":
            paste(base, *render(item))
    poster = Image.composite(original, base, keep)
    for item in items:
        if "patch" in item:
            if item.get("mode") == "inpaint":
                inpaint_glyphs(poster, item["patch"])
            else:
                clean_glyphs(poster, item["patch"], item["from"], item.get("mode") == "all")
    for item in drawable:
        if item.get("layer") == "front":
            paste(poster, *render(item))

    poster.convert("RGB").save(args.out)
    print(f"saved {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
