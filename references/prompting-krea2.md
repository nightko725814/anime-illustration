# Prompting Krea 2

Krea 2 (here: Krea 2 Turbo) does not behave like SD1.5/SDXL prompting. These rules come from repeated renders on the reference setup; each one changed real outcomes.

## Structure

Write natural-language paragraphs in this order:

1. identity block (who the character is, see below)
2. pose and action
3. expression and attitude
4. outfit
5. props or companions
6. background
7. lighting
8. style and medium
9. exclusions (inside the main text)

Each detail should serve the focal point, mood or depth. A pile of disconnected adjectives does not.

## Rules that change outcomes

- **No artist names.** Krea 2 ignores them, including "@artist" strings. Style comes from a LoRA (z3zz4 at 0.95 on Turbo is the painterly "Teto-poster" style) or from concrete descriptors: line weight, shading, palette, grain.
- **No negative prompt.** The workflows run at CFG 1 with a zeroed negative (`ConditioningZeroOut`). State exclusions inside the main text ("no text, no letters, no logos"). Negations are weak — describe what you want rather than what you don't.
- **Small props and gestures get dropped.** Bubble gum, a hand flipping hair and similar details vanish easily, especially in long prompts. An opened stomach panel with snapped wires shrank to a small gap at the belt in a short prompt and vanished entirely from a 2,500-word brief. Put them early, give a concrete size and position, and check every render. If they are still missing on an image you like, add them locally with a masked inpaint ([local-fixes.md](local-fixes.md)) instead of re-rolling everything.
- **Praying hands:** interlaced, clasped fingers came out with extra or merged fingers in all three seeds. Palms pressed flat together, fingers straight and aligned pointing up, seen in profile, came out right in 3 of 3 seeds.
- **Corner signatures:** in a church scene every seed added a garbled fake signature at the bottom left, even with "no signatures" in the prompt. Check the corners; remove one locally if needed.

## Identity block

Compact and specific:

- hair length, color, inner color and streaks;
- eyes, plus makeup and marks;
- accessories and outfit;
- companions or props;
- the typical expression.

Anchor it in an official design the user confirmed, not in your memory of the character. See SKILL.md step 1.

## Attitude and lighting that worked

- **"Cool and cocky"**: glancing back over the shoulder, sharp half-lidded eyes, one eyebrow raised, a lopsided smirk, chin up, fingers pushed into the hair.
- **"Youthful, not dark or mature"**: bright pastel palette plus a clear frontal key light.
- **Front light, when a face reads too dark:**
  - key light from the front and slightly above, so the face and upper torso are the brightest area;
  - a glossy ring of sheen on the hair and catchlights in the eyes;
  - small highlights on the nose bridge, cheeks and lips;
  - a thin pink rim light.

## Two proven styles

- **"Teto-poster" style:** Turbo + z3zz4 LoRA at 0.95 → painterly anime with crisp lines, readable text. Workflow: `assets/workflows/krea2_turbo_z3zz4_api.json`.
- **ZUTOMAYO-MV flat style:** plain Turbo + "flat 2D cartoon, thin dark outlines, flat cel colors, soft glow, film grain, faint CRT scanlines" and the MV's palette (deep teal-navy plus neon pink for 海馬成長痛). Workflow: `assets/workflows/krea2_turbo_plain_api.json`. Full example prompt: [../assets/prompts/example_ztmy_mv_flat_style.txt](../assets/prompts/example_ztmy_mv_flat_style.txt).

## Prompt-only requests

For SD-style tools that do use negatives, give a positive prompt, a separate deduplicated negative prompt, and aspect/resolution notes only when relevant. For Krea 2 itself, one positive paragraph.
