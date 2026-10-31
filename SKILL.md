---
name: anime-illustration
description: Create or refine anime-style character illustrations, meaning single images without titles or collage layouts, from a written brief or reference images. Deliver either ready-to-paste prompts or images rendered locally with Krea 2 in ComfyUI. Use this whenever the user wants to draw, 画, 生成 or redo an anime or fan-art character (Kasane Teto, ZUTOMAYO's Nira-chan, Miku, an OC). Also use it when they ask to match a character's canonical look from references, to change a pose, expression, outfit, attitude or lighting ("更帅更痞", "正面补光", "朝气一点"), or to fix one spot on a picked image (a weird hand or thumb, a missing prop like bubble gum, an extra blob) while everything else stays the same. For posters with titles, text or mixed-media collage, this skill is the wrong fit.
---

# Anime Illustration

Make an anime character illustration the user is happy with, usually by rendering a few candidates locally, letting the user pick, freezing the pick, and then fixing single spots without disturbing the rest. If the user only wants a prompt, write it (step 2) and stop.

## 1. Pin down the character from references, not memory

Guessing a character's look wastes whole render rounds. In testing, a guessed short bob had to become long hair, a guessed "ginger" cat turned out to be a pale-pink cat from one specific MV, and the "same" mascot had several canonical looks across music videos. So:

- For a character not yet in the profiles below, search briefly.
  - **One clear official design:** use it and tell the user which look you used. Adachi Rei's UTAU design, taken from Moegirl, came out close on the first render.
  - **Several looks, or sources that disagree:** ask the user for a reference image of the exact look they want, unless they already gave one.
  - **Where to look:** Moegirl (`zh.moegirl.org.cn`) has the most detailed 外观特征 sections for Japanese vocal-synth and anime characters, and its `File:` pages show the official art. Open it in a browser, because plain fetchers often get an empty page. Fandom wikis sit behind a Cloudflare check; don't try to get past it.
  - **Saving references:** put the ones the user gives you into the project's `images/` folder with descriptive names.
- Turn the confirmed look into a compact identity block:
  - hair length, color, inner color and streaks;
  - eyes, plus makeup and marks;
  - accessories and outfit;
  - companions or props;
  - the typical expression.

  When the user's latest correction disagrees with an older reference, the correction wins.
- Confirmed profiles live in `references/characters.md`. Start it from [references/characters.template.md](references/characters.template.md) and add a new character once the user has confirmed it. (The file is gitignored so personal characters stay private.)

## 2. Write the prompt

Write natural-language paragraphs in this order: identity block → pose and action → expression and attitude → outfit → props or companions → background → lighting → style and medium → exclusions. Each detail should serve the focal point, mood or depth. A pile of disconnected adjectives does not.

The full guide for Krea 2 — which is what renders here — is [references/prompting-krea2.md](references/prompting-krea2.md). The rules that change outcomes most:

- **No artist names.** Krea 2 ignores them, including "@artist" strings. Style comes from a LoRA (z3zz4) or from concrete descriptors such as line weight, shading, palette and grain.
- **No negative prompt.** The workflows run at CFG 1 with a zeroed negative. State exclusions inside the main text ("no text, no letters, no logos"). Negations are weak, so describe what you want rather than what you don't.
- **Small props and gestures get dropped.** Bubble gum, a hand flipping hair and similar details vanish easily, especially in long prompts. Put them early, give a concrete size and position, and check every render for them. If they are still missing on an image the user likes, add them locally (step 5) instead of re-rolling everything.
- **Corner signatures:** scenes with walls or floors often grow a garbled fake signature in a bottom corner, even with "no signatures" in the prompt. Check the corners, and remove one locally ([references/local-fixes.md](references/local-fixes.md)).

## 3. Render locally

The environment is described in [references/setup.md](references/setup.md): ComfyUI launch, models, workflows and script options. Read it before the first render of a session.

- **Confirm the render config with a checklist.** After the user states the character setup, present the config once as a checkbox list, every default pre-ticked. The user either confirms ("全默认" / "defaults") or ticks the items to change. Skip the list when the brief already pinned these, or when the user only asked for a written prompt:

  ```
  渲染配置（默认已勾选，改哪项勾哪项 / defaults pre-ticked, tick what to change）:
  - [x] 工作流 workflow:      krea2_turbo_z3zz4_api.json（风格 LoRA 版）
        [ ] krea2_turbo_plain_api.json（无 LoRA）
        [ ] krea2_turbo_z3zz4_local_inpaint_api.json（局部修复）
  - [x] 绘图模型 base model:  krea2_turbo-Q4_K_M.gguf
        [ ] redcraft23INT8INT4FP8_30Krea2.safetensors（约 3× 快，画面更杂）
        [ ] 其他 diffusion_models 里的文件（Anima / Illustrious / NoobAI / Qwen-Image 等未经本套工作流测试）
  - [x] LoRA:                 z3zz4-k2-4_c1-st5000.safetensors @ 0.95
        [ ] BArtstyle-KREA2-V1-1 @ 0.75
        [ ] Yoneyama_Mai_Krea2 @ 0.45
        [ ] 不用 LoRA    [ ] 自定义 name.safetensors:strength
  - [x] 画师串 / 风格:        交给 LoRA（Krea 2 忽略画师名，画师串请写成具体的线条/上色/颗粒描述）
        [ ] ZUTOMAYO-MV flat style 描述串（见 prompting-krea2.md）
        [ ] 自定义风格串 ________
  - [x] 比例:                 16:9    [ ] 9:16    [ ] 1:1    [ ] 其他 ________
  - [x] 分辨率:               1920×1080（单次直出）
        [ ] 1280×720    [ ] 2560×1440    [ ] 与所选比例匹配的其他分辨率
  ```

- **Defaults:** 1920×1080 in a single pass, Krea 2 Turbo Q4 GGUF, 10 steps er_sde / simple, CFG 1. Use [assets/workflows/krea2_turbo_z3zz4_api.json](assets/workflows/krea2_turbo_z3zz4_api.json) for the painterly style or [krea2_turbo_plain_api.json](assets/workflows/krea2_turbo_plain_api.json) without the LoRA.
- **Seeds:** render 2–3 of them, e.g. 3120095504871, 20261030 and 1234. Each image takes about 4–5 minutes on the reference RTX 3060 6 GB laptop, so run batches in the background and report progress as images land.
- **Check before sending:** look at every image yourself first. Note the hits and misses against the request, such as identity, prop present, pose or garbled text. Then build a labeled grid with `scripts/compare.py` and send it.

## 4. Iterate with the user

- **One change per round.** Ask which image is closest, then change only what the user flagged. If the feedback could apply to several images on screen, confirm which image before queueing renders. Earlier rounds that "fixed" unflagged traits drifted away from what the user liked.
- **Freeze the pick.** When the user picks ("就这张", "this one"):
  1. Run `scripts/freeze_preset.py` to create a folder with best.png, workflow_api.json, prompt.txt and a README.
  2. Re-render it with `scripts/run_workflow.py <preset>/workflow_api.json --as-is --prefix verify`. If that graph was the last one ComfyUI ran, the "re-render" comes back from ComfyUI's cache in about 3 seconds and proves nothing. Send `POST /free {"unload_models": true, "free_memory": true}` first. A real Turbo re-render takes minutes.
  3. Run `scripts/pixel_diff.py` and write the result into the preset README.

  For composites, recompose from the saved pieces and diff that instead.
- **Stop stale work when the user changes direction mid-batch.** See [docs/troubleshooting.md](docs/troubleshooting.md) for stopping queued or running jobs safely.

## 5. Fix one spot on a picked image

Changing the prompt re-lays out the whole picture even with the same seed. A masked local inpaint changes only the masked region. Full recipes and worked examples are in [references/local-fixes.md](references/local-fixes.md). In short:

1. **Mask:** draw a mask (ellipse or polygon, feathered 4–8 px) over only the problem.
2. **Prompt:** write a short prompt that describes only that region. Examples are in `assets/prompts/fix_*.txt`.
3. **Render:** run [assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json](assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json) with `--image`, `--mask`, `--denoise 0.75–0.98` and 2–3 seeds.
4. **Paste back:** use `scripts/composite_mask.py`, then read the reported changed box. It should cover only the spot.

Common cases:

- **Remove a blob or an extra digit:** mask only the blob and prompt it as whatever is behind it (hair, background). Redrawing a whole hand tends to erase it or leave a ghost.
- **Add a missing prop:** put a circle mask where the prop belongs, at about 0.98 denoise. If no seed draws it, paint a simple draft shape and refine at about 0.45. A worked example is in [examples/nira_china_bubble_fix](examples/nira_china_bubble_fix/README.md).
- **Tiny leftovers:** use OpenCV Telea on just the odd pixels.
- **A wrong word in the image:** that is typography — replace it in an image editor with the real font rather than fighting the model.

## Conventions

- Keep one project folder per art project with `prompts/`, `images/`, `render/`, `compare/` and `presets/` subfolders. Descriptive file names in the user's language are fine.
- Models live in a models root wired through `extra_model_paths.yaml` (see [references/setup.md](references/setup.md)). Download new ones there and verify the SHA-256 with `scripts/download_models.py --check-only` against `models/models.toml`.
- The user values the raw generated feel. Offer cleanups; don't impose them.

## Reference scene profile

[references/scene-profile-example.md](references/scene-profile-example.md) is a scene-specific recipe ("Teto as a puppet bride") showing how to write one. Use scene profiles only when recreating or adapting that exact scene; bring your own reference image.
