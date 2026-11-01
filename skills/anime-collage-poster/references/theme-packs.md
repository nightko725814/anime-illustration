# Theme packs

These packs were tried with this pipeline. Each lists the parts that change between themes, plus the verdict from test renders. The full briefs are in `assets/briefs/`.

## Teto · crimson collage, front light (picked)

- **Brief:** `teto_crimson_front_light.txt`
- **Palette:** scarlet and deep crimson dominant; blush pink, white, warm off-white paper and matte black; lime, acid-yellow, electric-cyan and mint accents; a little lavender and orange.
- **Surfaces:** red-painted cardboard, tracing paper, graph paper, photocopy, film frames.
- **Prop cluster:** a baguette in a kraft-paper bag, sheet music, a cassette with a loose tape loop, film negatives, ticket stubs, polaroids of Teto, red stamps, safety pins.
- **Texts:** 重音テト / Kasane Teto / テト. Labels: COLLAGE STUDY, FRAGMENTED MEMORY, RED NOISE, 断片, 無秩序, 感情, コラージュ.
- **Verdict:** the front-light text-to-image version was picked over the low-denoise img2img versions ("文生图补光版更好"). It is the reference point for "像 Teto 那样".

## Nira-chan · pastel hoodie, cool and cocky (picked)

- **Brief:** `nira_hoodie_pastel_cool.txt`
- **Palette:** pastel pink, soft lavender and periwinkle dominant; mint, lemon yellow and electric cyan accents; magenta and violet; little black. "Light and airy, never dark."
- **Surfaces:** lavender cardboard and a glitchy pastel pixel-block mosaic.
- **Prop cluster:** Uniguri-kun the hedgehog, a VHS tape, a CRT screen showing static, clock faces with detached second hands (秒針を噛む), fresh chive leaves (にら), star and heart stickers, sheet music, cassettes, polaroids.
- **Texts:** にらちゃん / ZUTOMAYO / うにぐり. Labels: MIDNIGHT NOISE, 真夜中.
- **Attitude:** glancing back over the shoulder, half-lidded eyes, fingers pushed into the hair ("更帅更痞，像 Teto 那样").
- **Verdict:** the user picked seed 20261030, then asked for two fixes: 断夜中 → 真夜中, and removing the extra blob in the thumb web.

## Nira-chan · purple-black Chinese, 香辛龍 concert (picked)

- **Brief:** `nira_china_purple_black_kosinryu.txt`
- **Source:** ZTMY's 2024 K-Arena show "本格中華喫茶・愛のペガサス ～羅武の香辛龍～", with a Chinese-café concept. The show opened on erhu, then a dragon "rampaging". The story centered on a phantom five-spice powder. Fried rice was cooked on stage and the audience held rice paddles. A winged moped stood for the "pegasus", ACAね emerged from a giant steamer, and there were a fountain, a big cherry, lasers and a mirror ball.
- **Palette:** deep royal purple and inky lacquer black dominant; magenta and neon purple; Chinese-red, antique-gold and jade-green accents; small whites.
- **Surfaces:** black lacquer panels, purple silk brocade with cloud and dragon patterns, purple and red paper-cut window lattices, gold-foil clouds, a dark violet night sky, mirror-ball sparkles, purple laser beams.
- **Prop cluster:** a bamboo steamer of xiaolongbao, a five-spice tin with star anise and cinnamon, a wok of fried rice with a rice paddle, an erhu, a porcelain teapot and cups, a big red cherry, a fountain splash, a winged retro moped, chopsticks, paper-cut flowers.
- **Hero element:** a black-and-gold dragon cut-out with purple scales, winding from the lower-left to the upper-right.
- **Texts:** にらちゃん / ZUTOMAYO / 小籠包 (籠 often comes out wrong). Labels: 香辛龍, 五香粉, 中華喫茶, 真夜中.
- **Verdict:** "紫黑中华风" was requested after a pastel version; seed 1234 was picked. Bubble gum was added by local inpaint. Then "训练效果先保存在这张".

## Nira-chan · pastel Chinese, 香辛龍 (superseded)

Same props as above with the Nira pastel palette. One seed rendered well and was the only full render that drew the bubble gum. The theme was switched to purple-black.

## ZUTOMAYO MV flat style (for illustrations, not posters)

Lives in the sibling anime-illustration skill (`anime-illustration/assets/prompts/example_ztmy_mv_flat_style.txt`): plain Turbo, flat cel colors, thin outlines, grain, scanlines, deep teal-navy with neon pink. The Teto collage style won for Nira-chan posters.

## Teto · vintage British posters + paper flowers (test render, verdict pending)

- **Brief:** `teto_british_paper_flowers.txt`. This is a full poster, adapted from the Teto brief on 2026-10-30 as the first test of this skill.
- **Older background-only prompt:** `bg_only_vintage_british_paper_flowers.txt` repaints only the left side. Its render was stopped when the user returned to the raw image.
- **Palette:** pillar-box red and crimson dominant; warm cream, deep navy, mustard and a little racing green; cyan and acid-yellow accents. The brief says "bold and saturated, never washed out", so the vintage colors don't turn dusty.
- **Surfaces:** aged cream paper, red cardboard, and torn lithograph poster fragments as pictures only: a double-decker bus, a phone box, Big Ben at dusk, Union Jack sections, a crest, stamps and postmarks, letterpress borders.
- **Prop cluster:** the baguette, a bouquet of crepe-paper roses and origami flowers, a teacup on a saucer, stamps and ticket stubs, a map fragment, a cassette, sheet music, polaroids.
- **Texts:** 重音テト / Kasane Teto / テト. Labels: FIRST CLASS, TEA TIME, FRAGMENTED MEMORY, 断片, コラージュ.
- **Result (seed 3120095504871, 328 s):**
  - Hits: every British motif, the baguette, the teacup and the stamps came out, and the palette stayed vivid.
  - Misses: the "paper" flowers came out as painted roses, and the hollow title sat at the top center instead of down the left edge.
  - Garbling: the bus advert and a few labels still got garbled lettering despite "pictures only".

## Adachi Rei · android with broken wiring (test render, verdict pending)

- **Brief:** `adachi_rei_android_broken_wires.txt`.
- **Identity:** her UTAU design, from Moegirl's 外观特征 section:
  - orange hair with a side ponytail, a chip hair clip, and orange camera-lens eyes;
  - black headphones with a mic, a searchlight and an antenna;
  - an oversized white hooded jacket with "00" and orange reflective stripes;
  - a black turtleneck, an orange belt and a gray circuit-print skort;
  - white gloves, and cables hanging from the hem.
- **Palette:** safety orange and white dominant; black, light gray and copper; oscilloscope-green, electric-cyan and acid-yellow accents; a little signal red.
- **Surfaces:** engineering graph paper, schematic sheets drawn as pictures, green circuit-board fragments, oscilloscope screen captures, perforated metal, anti-static bag scraps, and yellow-and-black hazard stripes.
- **Prop cluster:** snapped cables spilling from the stomach panel, AUX and USB plugs, a soldering iron, resistors and capacitors, an IC chip, screws and nuts, electrical-tape rolls, a multimeter, a cassette, sheet music, and polaroids of her.
- **Texts:** 足立レイ / ADACHI REI / レイ. Labels: SINE WAVE, HCI3-P0, ERROR, 断線, ノイズ.
- **Result (seed 3120095504871, 1,046 s under low RAM):**
  - Hits: the identity was right, the collage was dense but readable, and "ADACHI REI" and "レイ" came out clean.
  - Misses: the opened stomach with broken wires was dropped entirely; the skort came out navy and the headphones light gray.

## Reference pack (the original Miku poster)

`reference_pack_original_miku.txt` is the pack author's brief, about 1900 words:
- cobalt, ice blue, white, fluorescent lemon and coral;
- a blue-white bouquet;
- texts 初音未来 / Hatsune Miku / 初音ミク.

The original render used RedCraft 2.0 + z3zz4 0.55 + BArtstyle V1 0.75 ([assets/workflows/krea2_redcraft30_reference_recipe_api.json](../assets/workflows/krea2_redcraft30_reference_recipe_api.json) is the RedCraft 3.0 equivalent).

## Background-only prompts (for regenerating around a kept character)

| File | Verdict |
|---|---|
| `bg_only_clean_rejected_example.txt` | Few large blocks; too empty and rejected |
| `bg_only_rich_collage.txt` | Complete, consistent components; better, but the raw image still won |
| `bg_only_vintage_british_paper_flowers.txt` | Above |
