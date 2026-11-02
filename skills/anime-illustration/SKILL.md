---
name: anime-illustration
description: Create or refine anime-style character illustrations, meaning single images without titles or collage layouts, from a written brief or reference images. Deliver either ready-to-paste prompts or images rendered locally with Krea 2 Turbo in ComfyUI, refined with a pick-and-fix loop (render candidates → pick one → freeze it → fix one spot at a time with masked local inpaint while everything else stays pixel-identical). Use this whenever the user wants to draw, 画, 生成 or redo an anime or fan-art character (Kasane Teto, ZUTOMAYO's Nira-chan, Miku, an OC). Also use it when they ask to match a character's canonical look from references, to change a pose, expression, outfit, attitude or lighting ("更帅更痞", "正面补光", "朝气一点"), or to fix one spot on a picked image (a weird hand or thumb, a missing prop like bubble gum, an extra blob) while everything else stays the same. For posters with titles, text or mixed-media collage, this skill is the wrong fit — use the sibling `anime-collage-poster` skill instead.
---

# Anime Illustration

Make an anime character illustration the user is happy with, usually by rendering a few candidates locally, letting the user pick, freezing the pick, and then fixing single spots without disturbing the rest. If the user only wants a prompt, write it (step 2) and stop.

Source repository: https://github.com/nightko725814/anime-illustration — this file is `skills/anime-illustration/SKILL.md` there. Deeper material lives in the repo: `references/setup.md` (environment), `references/prompting-krea2.md` (prompt rules), `references/local-fixes.md` (fix playbook), `references/characters.template.md`, and a worked example in `examples/nira_china_bubble_fix/`.

## 0. Setup (once per machine, check once per session)

Tested environment: RTX 3060 Laptop 6 GB VRAM, 16 GB RAM (32 GB comfortable — RAM, not VRAM, is the usual bottleneck), Windows 11, Python 3.11+, ComfyUI 0.42.0+.

1. **ComfyUI + the one required custom node** ([ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)):

   ```
   git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI
   python -m venv venv && venv/Scripts/pip install -r requirements.txt
   git clone https://github.com/city96/ComfyUI-GGUF custom_nodes/ComfyUI-GGUF
   venv/Scripts/pip install -r custom_nodes/ComfyUI-GGUF/requirements.txt
   ```

2. **Models** go in a models root wired into ComfyUI through `extra_model_paths.yaml` (copy the repo's `extra_model_paths.yaml.example` into the ComfyUI folder and set `base_path`). Required files, by name — the workflow JSONs load exactly these names:

   | Role | File |
   |---|---|
   | Base | `diffusion_models/krea2_turbo-Q4_K_M.gguf` |
   | Text encoder | `text_encoders/qwen3vl_4b_fp8_scaled.safetensors` |
   | VAE | `vae/qwen_image_vae.safetensors` |
   | Style LoRA (recommended) | `loras/z3zz4-k2-4_c1-st5000.safetensors` |

   Download and verify against the manifest (`models/models.toml` in the repo — exact filenames, sizes, sources, SHA-256):

   ```
   python scripts/download_models.py --root <models-root>              # download + verify SHA-256
   python scripts/download_models.py --root <models-root> --check-only # verify only
   ```

3. **Start the server** (the flags are the 6 GB-friendly profile; drop them on bigger GPUs) and wait until it answers before submitting anything:

   ```
   python main.py --listen 127.0.0.1 --port 8188 --lowvram --cpu-vae --disable-auto-launch
   ```

   Health checks: `GET http://127.0.0.1:8188/system_stats` (free RAM/VRAM), `GET /queue` (running/pending jobs). Outputs land in `ComfyUI/output/`; `scripts/run_workflow.py --upload` pushes inputs over HTTP so no manual copying into `ComfyUI/input/` is needed.

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
- Confirmed profiles live in `references/characters.md`. Start it from `references/characters.template.md` and add a new character once the user has confirmed it. (The file is gitignored so personal characters stay private.)

## 2. Write the prompt

Write natural-language paragraphs in this order: identity block → pose and action → expression and attitude → outfit → props or companions → background → lighting → style and medium → exclusions. Each detail should serve the focal point, mood or depth. A pile of disconnected adjectives does not.

The full guide for Krea 2 — which is what renders here — is `references/prompting-krea2.md`. The rules that change outcomes most:

- **No artist names.** Krea 2 ignores them, including "@artist" strings. Style comes from a LoRA (z3zz4) or from concrete descriptors such as line weight, shading, palette and grain.
- **No negative prompt.** The workflows run at CFG 1 with a zeroed negative (`ConditioningZeroOut`). State exclusions inside the main text ("no text, no letters, no logos"). Negations are weak, so describe what you want rather than what you don't.
- **Small props and gestures get dropped.** Bubble gum, a hand flipping hair and similar details vanish easily, especially in long prompts. Put them early, give a concrete size and position, and check every render for them. If they are still missing on an image the user likes, add them locally (step 5) instead of re-rolling everything.
- **Corner signatures:** scenes with walls or floors often grow a garbled fake signature in a bottom corner, even with "no signatures" in the prompt. Check the corners, and remove one locally (see `references/local-fixes.md`).

## 3. Render locally

Defaults baked into all workflows: 1920×1080 in a single pass, Krea 2 Turbo Q4 GGUF, 10 steps er_sde / simple, CFG 1. Workflows (API format, prompt goes in at `PROMPT_PLACEHOLDER`):

- `assets/workflows/krea2_turbo_z3zz4_api.json` — Turbo + z3zz4 style LoRA @ 0.95 (default)
- `assets/workflows/krea2_turbo_plain_api.json` — Turbo, no LoRA
- `assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json` — masked local inpaint (step 5)

- **Confirm the render config with a checklist.** After the user states the character setup, present the config once as a checkbox list, every default pre-ticked (workflow, base model, LoRA, style line, aspect ratio, resolution — the full list is in the repo's SKILL.md history / step 3 of the workflow guide). The user either confirms ("全默认" / "defaults") or ticks the items to change. Skip the list when the brief already pinned these, or when the user only asked for a written prompt.
- **Run it:**

  ```
  python scripts/run_workflow.py assets/workflows/krea2_turbo_z3zz4_api.json --prompt-file P.txt --seed N --prefix name
  ```

  Extras: `--lora name:strength` (repeatable), `--as-is` (re-run a frozen preset unchanged), `--image/--mask --upload` (inpaint inputs), `--denoise`, `--sampler`, `--front` (jump the queue), `--server`/`COMFY_URL`, `--output-dir`/`COMFY_OUTPUT`. Exit code 4 means ComfyUI reported an error.
- **Seeds:** render 2–3 of them, e.g. 3120095504871, 20261030 and 1234. Each 1920×1080 image takes about 4–5 minutes on the reference machine, so run batches in the background and report progress as images land.
- **Check before sending:** look at every image yourself first. Note the hits and misses against the request (identity, prop present, pose, garbled text, corner signatures). Then build a labeled grid and send it:

  ```
  python scripts/compare.py OUT.jpg "label=path" ... --cols 2 --width 960
  ```

## 4. Iterate with the user

- **One change per round.** Ask which image is closest, then change only what the user flagged. If the feedback could apply to several images on screen, confirm which image before queueing renders. Earlier rounds that "fixed" unflagged traits drifted away from what the user liked.
- **Freeze the pick.** When the user picks ("就这张", "this one"):
  1. Run `scripts/freeze_preset.py RENDER.png presets/NAME --note "why"` to create a folder with best.png, workflow_api.json, prompt.txt and a README.
  2. Verify bit-exact reproduction: first free ComfyUI's cache with `POST /free {"unload_models": true, "free_memory": true}` (otherwise the "re-render" can come back from cache in ~3 seconds and proves nothing — a real Turbo re-render takes minutes), then re-render with `scripts/run_workflow.py <preset>/workflow_api.json --as-is --prefix verify`.
  3. Run `scripts/pixel_diff.py A.png B.png` and write the result into the preset README.

  For composites, recompose from the saved pieces and diff that instead. (This works because every output PNG carries its API graph in the `prompt` text chunk.)
- **Stop stale work when the user changes direction mid-batch.** Stopping a background loop does not remove jobs it already submitted — delete pending jobs with `POST /queue {"delete": [prompt_id]}`. Full stall/paging recipes: `docs/troubleshooting.md` in the repo.

## 5. Fix one spot on a picked image

Changing the prompt re-lays out the whole picture even with the same seed. A masked local inpaint changes only the masked region. Full recipes and worked examples are in `references/local-fixes.md`. In short:

1. **Mask:** draw a mask (ellipse or polygon, feathered 4–8 px) over only the problem. For a subject-shaped mask, `scripts/sam_mask.py IMAGE OUT --box x0,y0,x1,y1 [--pos x,y ...] [--neg x,y ...]` uses SAM 2.1 (run it in the ComfyUI venv).
2. **Prompt:** write a short prompt that describes only that region. Examples are in `assets/prompts/fix_*.txt`.
3. **Render:** run `assets/workflows/krea2_turbo_z3zz4_local_inpaint_api.json` with `--image`, `--mask`, `--denoise 0.75–0.98` and 2–3 seeds (about 4 minutes each on the reference machine).
4. **Paste back:** use `scripts/composite_mask.py BASE INPAINTED MASK OUT`, then read the reported changed box. It should cover only the spot.

Common cases:

- **Remove a blob or an extra digit:** mask only the blob and prompt it as whatever is behind it (hair, background). Redrawing a whole hand tends to erase it or leave a ghost.
- **Add a missing prop:** put a circle mask where the prop belongs, at about 0.98 denoise. If no seed draws it, paint a simple draft shape and refine at about 0.45. A worked example is in `examples/nira_china_bubble_fix/`.
- **Tiny leftovers:** use OpenCV Telea on just the odd pixels.
- **A wrong word in the image:** that is typography — replace it in an image editor with the real font rather than fighting the model.

## Checks (before calling a result done)

- [ ] `/system_stats` answered before the batch was submitted; free RAM stayed healthy during renders.
- [ ] Every rendered image was looked at: identity matches the identity block, small props present, no garbled text, corners free of fake signatures.
- [ ] The comparison grid sent to the user is labeled, and the user's pick is the one being iterated on.
- [ ] A frozen preset re-renders bit-exact (`pixel_diff.py` clean) after a `/free` cache flush, and the result is written into the preset README.
- [ ] After a local fix, the `composite_mask.py` changed box covers only the intended spot.
- [ ] New models verify with `download_models.py --check-only` against `models/models.toml`.

## Conventions

- Keep one project folder per art project with `prompts/`, `images/`, `render/`, `compare/` and `presets/` subfolders. Descriptive file names in the user's language are fine.
- Models live in the models root wired through `extra_model_paths.yaml`. Filenames must match the workflows, or edit the loader nodes (`UnetLoaderGGUF`, `CLIPLoader`, `VAELoader`, `LoraLoaderModelOnly`) to yours.
- Between batches, unload with `POST /free {"unload_models": true, "free_memory": true}`; avoid queueing many different jobs at once (ComfyUI runs one job at a time).
- The user values the raw generated feel. Offer cleanups; don't impose them.

## Reference scene profile

`references/scene-profile-example.md` is a scene-specific recipe ("Teto as a puppet bride") showing how to write one. Use scene profiles only when recreating or adapting that exact scene; bring your own reference image.
