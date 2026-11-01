# Fixing text and backgrounds on a picked poster

Use these recipes only for what was asked to change. Always finish with a changed-pixel check, and send a before/after crop.

## Read what the model actually wrote

Garbled titles are hard to read under hair and props. Isolate the strokes first. Hollow titles are a pale fill (`min(R,G,B) > 205`) with a saturated outline. Paint everything else dark and look at the result:

```python
pale = r.min(axis=2) > 205
outline = (r[..., 2] > 150) & (r[..., 0] > 90) & (r[..., 0] < 190) & (r[..., 1] < 120)   # purple outline; adjust
vis = np.full(r.shape, 30, np.uint8); vis[pale] = 255; vis[outline] = (200, 120, 255)
```

Typical defects:
- extra or duplicated syllables (にらちら…, "ZUTOM.:70MAYO");
- wrong kanji (籠 → 龍 / 能);
- doubled letters (うにぐぐり).

## Replace a word on a flat panel (proven: 断夜中 → 真夜中)

1. **Measure the old word.** Grid-crop it, take the median color of its glyph pixels (e.g. `[231, 255, 93]`), and get its ink box (x 40–139, y 570–606).
2. **Fit the new word.** Measure candidate sizes with `text_layer` and pick the size and spacing whose ink box matches. Mind the offset: `text_layer` pads by stroke+2 and its ink starts a few pixels in.
3. **Erase and redraw.** Erase with a `patch` box in `inpaint` mode inside the panel. The box's dominant color must be the panel color, so keep it off the panel's edges. Then draw the word with `blur` around 0.5 so it matches the soft generated art.
4. **Apply** to the finished image, with BASE = ORIGINAL = the picked image and an all-black keep mask:

```json
[
  {"patch": [36, 568, 146, 612], "mode": "inpaint"},
  {"text": "真夜中", "font": "YuGothB.ttc", "size": 37, "spacing": -1, "x": 36, "y": 567,
   "style": "fill", "color": [231, 255, 93], "blur": 0.5, "layer": "front"}
]
```

```
python typeset_poster.py picked.png picked.png keep_none.png layout.json fixed.png
```

Then diff it against the original. The changed box should be the word only (3,246 px in that fix).

## Replace text that sits behind hair, props or a dragon

1. **Get occluder masks with SAM.** Run `sam_mask.py` with a box around each occluder plus 4–12 positive and 2–5 negative points. For the character, put positives on the face, hair, buns, body and props in hand. Clean each mask with blur → threshold → open/close → largest component. Union the occluders.
2. **Erase the old strokes.** Use stroke pixels outside the occluders, dilated by 2 px. Fill with OpenCV Telea on flat paper, or with a background-only masked inpaint on textured panels.
3. **Draw the new text** as "behind" items, then composite the original occluder pixels back on top (the KEEP_MASK layer of `typeset_poster.py`).

This route was set up but then stopped by the user ("训练效果先保存在这张"). It has not been finished on a real poster yet.

## Full re-typesetting (only if asked)

`typeset_poster.py` can do more:
- solid white titles with a dark outline (readable over busy panels);
- hollow titles;
- ransom-note `scrap` letters on torn paper, with mixed fonts, rotations and a halftone paper, plus `tape` strips and cyan `echo` misregistration.

Clean real-font titles read as "太过板正"; the raw generated text won in testing. If asked for "more artistic" type, the scrap-letter look is the stronger option, but show it as an option next to the raw image.

## Regenerating the background around a kept character (only if asked)

1. **Cut out the character with SAM 2.1.** Use one box around the whole character and points on the face, both sides of the hair, the body, the held props and the waist or glove near the bottom edge. Add negatives on nearby paper scraps and old text.
   - anime-seg (`cutout_mask.py`) failed here. It scored crimson hair on a crimson background at 0.04, and it took collage scraps for foreground.
2. **Build the masks.** Keep = the soft character mask. The repaint mask = `1 - erode(keep > 0.5, 6 px)`, blurred by 3.
3. **Repaint.** Run `assets/workflows/krea2_turbo_z3zz4_bg_inpaint_api.json` (SetLatentNoiseMask, denoise 1.0) with a background-only prompt (`assets/briefs/bg_only_*.txt`). Two seeds.
4. **Composite** the original character pixels back on top with the keep mask. Check that the fully opaque character pixels are identical to the picked image.
5. **Keep the body running off the canvas edge.** A band that cut the character at the waist inside the frame was flagged immediately ("补齐下半身").

Results so far:
- A clean background was "太空 / 颜色单一 / 没有碎片感".
- A rich collage background was better.
- The user still preferred the raw original.

So treat regeneration as an experiment to show next to the raw image, not as a replacement.

## Verification habits

- After any edit, compute the changed-pixel count and box and report them.
- Freeze the user's pick before editing it, so there is always a clean original to return to.
- For composites, save every input (base preset, raw inpaint output, mask, workflow, prompt) and check that recomposing gives exactly `best.png`.
