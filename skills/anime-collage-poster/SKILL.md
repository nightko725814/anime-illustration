---
name: anime-collage-poster
description: Make anime character posters with titles, typography and mixed-media collage (torn paper, tape, halftone, sheet music, cassettes, polaroids, offset character echoes), using the local Krea2 + z3zz4 "Teto recipe" driven by a ~2000-word art-direction brief. Also fix the text or background of such posters afterwards. Use this whenever the user wants a 拼贴 / 海报 / collage / key visual / poster with 文字 or 标题, or wants to replicate a reference collage poster. Use it too for adapting the Teto or Nira-chan posters to another character, outfit or theme (中华娘, 紫黑中华风, ZTMY concert motifs, vintage British posters, paper flowers), or for correcting garbled, extra or wrong words on such an image ("把断夜中改成真夜中", "文字有多余的"). For a plain character illustration without text or collage, use anime-illustration.
---

# Anime Collage Poster

Build 1920×1080 collage posters like the bundled theme packs: Teto in crimson with front light, Nira-chan in a pastel hoodie, and Nira-chan in a purple-black Chinese style (renders in [../../../docs/gallery.md](../../docs/gallery.md)). The pipeline is: long brief → Krea2 Turbo + z3zz4 → pick → freeze → targeted fixes only.

## Why the recipe works

- **Model and sampler:** Krea2 Turbo Q4 GGUF + z3zz4 0.95, 1920×1080 single pass, 10 steps er_sde / simple, CFG 1, zeroed negative ([assets/workflows/krea2_turbo_z3zz4_api.json](assets/workflows/krea2_turbo_z3zz4_api.json)). Each image takes about 4–5 minutes on the reference RTX 3060 6 GB laptop. Environment details are in [references/setup.md](references/setup.md).
- **The long brief does the art direction.** A ~2000-word, 18-paragraph brief sets the layout axes, palette, surfaces, character echoes, cut-out masks, the prop cluster, blocks, typography, labels, tape, ink, halftone, lighting, hierarchy and mood. A 250-word prompt gives a plain illustration. That gap was the single biggest jump in quality during testing.
- **The base model decides the clutter.** RedCraft fine-tunes fill everything with debris, put paint flecks on faces and drop titles. Official Turbo gives structured posters with readable titles. Three LoRAs stacked on an INT4 model overload into noise.
- **Krea2 ignores artist names**, so the "@artist" strings in downloaded packs do nothing. Style comes from LoRAs.
- **Any prompt edit re-lays out everything,** even with the same seed. After an image has been picked, fix it locally rather than re-prompting.

[references/lessons.md](references/lessons.md) has the full decision log: what was tried, what the feedback said, and what stuck.

## Workflow

### 1. Write the brief by adapting a proven one

Start from the closest example in `assets/briefs/`:

| Example | Character and theme |
|---|---|
| `teto_crimson_front_light.txt` | Teto, crimson palette |
| `nira_hoodie_pastel_cool.txt` | Nira-chan, pastel hoodie, cool attitude |
| `nira_china_purple_black_kosinryu.txt` | Nira-chan, purple-black Chinese, 香辛龍 concert motifs |
| `reference_pack_original_miku.txt` | The original pack brief (cobalt Miku) |
| `teto_british_paper_flowers.txt` | Teto, vintage British posters + paper flowers |
| `adachi_rei_android_broken_wires.txt` | Adachi Rei, android with broken wiring |

Adapt it paragraph by paragraph using [references/brief-template.md](references/brief-template.md), which says what each paragraph controls and what to swap. Keep the sentence structure. Swap the subject identity, palette, surfaces, prop cluster, exact texts, labels, lighting and final atmosphere. Ready-made palettes, materials and texts per theme are in [references/theme-packs.md](references/theme-packs.md).

- **Character identity:** take it from the sibling skill's `../anime-illustration/references/characters.md` (start that file from its template) or from the user's references. Never guess a character's look.
- **Text:** keep the exact strings to three (title, romaji or brand, one small word) plus a few tiny labels. More text means more garbling, such as extra glyphs, duplicated syllables or wrong kanji (籠 came out as 龍 or 能).
- **Must-have props and actions** (bubble gum, a hand in the hair) go concretely into paragraph 1. They can still be ignored, so plan for a local fix. In the Adachi Rei test, an opened stomach panel with broken wires was named in paragraphs 1, 6, 15 and 16 and still vanished.
- **Companions and props:** mention them only where needed, or they get drawn twice.

### 2. Render, pick, freeze

1. Render three seeds (3120095504871, 20261030, 1234).
2. Look at each image yourself for identity, props, hair rules and text, then send a labeled grid (`scripts/compare.py`).
3. Ask which is closest. Change one thing per round, and only what was flagged.
4. When one is picked, freeze it with `scripts/freeze_preset.py`, re-render with `--as-is`, and check with `scripts/pixel_diff.py`.

### 3. After the pick: targeted fixes only

Recipes are in [references/text-and-background.md](references/text-and-background.md).

- **Fix a wrong word:** erase its glyphs, then set the right word in a real font matched for color, size, weight and a slight blur, using `scripts/typeset_poster.py` patch and text items. Then confirm the changed-pixel box covers only the word. The 断夜中 → 真夜中 fix changed 3,246 px.
- **Fix text behind hair or props:** first get occluder masks with SAM, so the new text sits behind them.
- **Fix a missing prop or a bad hand:** use local inpaint as described in the sibling skill's `../anime-illustration/references/local-fixes.md` (example region prompts: `../anime-illustration/assets/prompts/fix_*.txt`), with [assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json](assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json).

### 4. Bigger changes only when asked

Re-typesetting all titles or regenerating the background are bigger changes. Read the next section before doing either.

## What reviewers liked and rejected

- **Liked:**
  - The raw generated energy: a fragmented, dense but readable collage. Garbled glyphs are tolerated.
  - The cool, cocky Teto attitude.
  - Either a bright youthful pastel palette or a dramatic purple-black Chinese style.
  - Exact character design from references.
- **Rejected:**
  - RedCraft debris backgrounds ("很乱，尤其是背景").
  - A calm, washed-out background ("方向不对").
  - A cleaned, flat regenerated background ("太空", "颜色单一", "没有碎片感").
  - Rigid real-font titles ("文字太过板正").
  - A character cut off inside the frame ("补齐下半身").

  After cleanup attempts, the raw image won ("就这种感觉算了吧"). Offer cleanup as an option, never by default.
- **Fixes and freezing:** when asked to fix one thing, fix exactly that, check nothing else changed, and ask before going broader. If the feedback could apply to several images on screen ("手有点不行" after a side-by-side), confirm which image before queueing renders. When someone says "先保存在这张", freeze it at once, even with known flaws, and write the flaws into the preset README.

## Typography toolkit

`scripts/typeset_poster.py BASE ORIGINAL KEEP_MASK LAYOUT.json OUT` draws in this layer order: base → "behind" items → the original pixels where KEEP_MASK is white → cleanup patches → "front" items. Pass the same image as BASE and ORIGINAL with an all-black mask to edit text on a finished image. Layout items:

| Item | Options |
|---|---|
| `text` | Styles `outline` / `fill` / `solid` (fill plus outline color). Also `echo` (misregistered copy), `blur`, `axes` (variable-font weight), `spacing`, `box`, `rotate` |
| `scrap` | A torn-paper letter card |
| `tape` | A translucent tape strip |
| `patch` | Glyph cleanup: `gray` / `all` / `inpaint` modes |

Fonts are resolved by name through `FONT_DIR` (env var) or the platform font directories:

- Japanese and Chinese: Yu Gothic (`YuGothB/M/R/L.ttc`); Noto Serif SC VF (weight axis 200–900, includes kana); Noto Sans SC VF.
- Latin: Arial Narrow (`ARIALN/ARIALNB.TTF`), `bahnschrift.ttf`, `PLAYBILL.TTF` (vintage poster), `OLDENGL.TTF`, `STENCIL.TTF`, Courier, Consolas, Georgia, Times, Impact.

Other tools:

- `scripts/glitch_slice.py` adds VHS strip shifts with an RGB split.
- `scripts/sam_mask.py` and `scripts/cutout_mask.py` make cutout masks (models via [../../../models/models.toml](../../models/models.toml)).
- `scripts/composite_mask.py` pastes an inpainted region back.

## Conventions

- The environment (ComfyUI, models, extra_model_paths.yaml) is shared with the sibling skill — see [references/setup.md](references/setup.md).
- Queue hygiene matters: stopping a shell loop does not remove its submitted ComfyUI job. See [../../../docs/troubleshooting.md](../../docs/troubleshooting.md).
- Keep one project folder per art project with `prompts/`, `render/`, `compare/`, `presets/` subfolders; freeze picks as soon as they are chosen.
