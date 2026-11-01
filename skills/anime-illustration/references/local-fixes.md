# Local fixes on a picked image

The user picked an image and wants one spot changed. Re-prompting re-lays out the whole picture even with the same seed, so redraw only a masked region and paste it back. Everything outside the mask stays pixel-identical.

A complete worked example lives in [../examples/nira_china_bubble_fix](../examples/nira_china_bubble_fix/README.md).

## Steps

1. **Find the spot precisely.** Crop around it and draw a 50 px coordinate grid on the crop. Read the grid off the zoomed image before deciding the mask.

2. **Make the mask** in full-resolution coordinates. White means redraw. Keep it as small as the problem, feathered 4–8 px, and away from eyes and other features you must not touch. A mask that touches an eyelid can change the eye.

   ```python
   from PIL import Image, ImageDraw, ImageFilter
   m = Image.new("L", (1920, 1080), 0)
   ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)   # or .polygon([...])
   m.filter(ImageFilter.GaussianBlur(5)).save("fix_mask.png")
   ```

   Preview it by tinting the masked area green on a crop before rendering.

3. **Stage the inputs.** Either copy the picked image and the mask into `ComfyUI/input/`, or pass their local paths with `--upload`:

   ```
   python run_workflow.py assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json --prompt-file fix.txt \
       --image picked.png --mask fix_mask.png --denoise 0.9 --seed 44 --prefix fix_s44 --upload
   ```

4. **Write a short prompt about the region only.** Give the style line, what should be there, and the colors around it. Do not repeat the whole brief. Examples are in [../assets/prompts/](../assets/prompts/).

5. **Render 2–3 seeds.** Add `--front` if other jobs are queued.

6. **Paste back and check:**

   ```
   python composite_mask.py picked.png <comfy output> fix_mask.png fixed.png
   ```

   It prints the changed-pixel box. That box must sit inside the mask.

7. **Compare.** Show a side-by-side crop (original vs each seed) with `compare.py`. Pick the cleanest one; if none is clean, say so.

## What worked and what didn't

A field-tested table — reuse the shape of these fixes:

| Problem | Approach | Result |
|---|---|---|
| Weird thumb on a hand pushed into hair | Redraw the whole hand (big ellipse, denoise 0.75) | Failed. The hand was erased or left as a ghost |
| Same | Mask only the extra thumb blob and prompt it as the hair behind it, denoise 0.9 | Worked on 1 of 2 seeds. A tiny pale leftover was then filled with OpenCV Telea |
| Bubble gum missing in every full render | Circle mask in front of the lips (r ≈ 54 px at 1920×1080), "big round glossy pink bubble-gum bubble … partly covering her chin", denoise 0.98 | 1 of 3 seeds drew a convincing bubble; the others redrew the lips without it. See the worked example |
| Same, as a fallback | Paint a draft disc (pink gradient, darker rim, white highlight), then refine at 0.45 | The draft alone already read well. Refining is optional |
| Wrong word on a flat color panel | Real-font replacement in an image editor | Clean: only 3,246 px changed |
| Lighting change (face too dark) | Low-denoise img2img (0.35–0.5) of the whole image | Layout kept but the lighting barely changed. Lighting needs a text-to-image re-render or a painted-light pass |
| Malformed gloved hand gripping a plug | Whole-hand ellipse, 2 seeds: one at denoise 0.65, one at 0.8 | 0.65 redrew a proper gripping hand. 0.8 erased the hand into a block of color, like the thumb case above |
| Two bad hands in separate spots | One mask with two blobs, then paste each blob back from whichever seed did it best | Works because the blobs don't overlap. Only the hands changed (51k px) |
| Wide dark-navy hair streak, needed thin and pale instead | (1) Color-detect the streak inside a corridor polygon, recolor as a draft, inpaint at 0.5 and 0.65 with the eye and earring kept out of the mask. (2) Text-to-image on the same seed with only the streak sentences changed | (1) Clean and natural. (2) The layout stayed almost identical on the same seed and the streak blended best. For a change spread over a large area, try the same-seed re-render alongside the local fix |
| Earring too saturated ("更浅更透明一点") | Recolor only the crystal polygon (no AI): keep its facet light/dark, lift toward near-white, blend 45% with an OpenCV Telea estimate of the background. Keep the glints | Reads as clear glass at 1:1 (743 px changed). An AI refine was skipped because it tends to paint the color back |
| Garbled fake signature in a corner | Inside a box around it, select pixels brighter than the local median (15 px median blur, +18), dilate 2 px, then Telea | Clean on a dark floor (2,034 px), with no AI pass |
| "稍微萝莉一点、可爱一点" on a picked OC | Face-only polygon from the bangs' lower edge to the chin; "youthful doll-like baby face, full soft cheeks…" at denoise 0.55 | Clean paste: bigger round eyes and a blush — but too much. For "slightly" use milder words ("slightly youthful, a little softer than a mature face but still refined") and leave out blush and "baby face" |

## Tiny leftovers with OpenCV

Select only the odd pixels (for example pale skin pixels left in hair), dilate them by 2 px, and run Telea inpainting. It works for a few hundred pixels. Large areas turn into smears.

```python
import cv2, numpy as np
odd = (reg[..., 0] > 200) & (reg[..., 1] > 160) & (reg[..., 2] > 150)    # adjust to the leftover's color
mask[y0:y1, x0:x1][ndimage.binary_dilation(odd, iterations=2)] = 255
out = cv2.inpaint(img, mask, 4, cv2.INPAINT_TELEA)
```

## Saving the result

Composites have no single re-render command. Save the base preset path, the raw inpaint output, the mask, the inpaint workflow (exported from the output's metadata) and the prompt next to `best.png`. Then verify that recomposing from those files gives exactly `best.png` (`pixel_diff.py`). The bundled example folder follows exactly this layout.
