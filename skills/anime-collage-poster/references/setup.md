# Setup: local ComfyUI + Krea 2

Hardware the pipeline was tested on: **RTX 3060 Laptop 6 GB VRAM, 16 GB RAM, Windows 11**. It works on that machine, so anything bigger works. Two rules of thumb learned the hard way:

- **RAM is as important as VRAM.** ComfyUI offloads weights to RAM; once free RAM falls to ~2 GB, renders slow down dramatically or stall (see [../../../docs/troubleshooting.md](../../../docs/troubleshooting.md)). 16 GB is workable, 32 GB is comfortable.
- Low VRAM is fine. The launch flags below (`--lowvram --cpu-vae`) trade some speed for a 6 GB-friendly footprint.

This environment is shared with the sibling `anime-illustration` skill — one ComfyUI install, one models root, both skills.

## 1. ComfyUI

- Install ComfyUI (tested on 0.42.0) with its own Python venv, e.g.:

  ```
  git clone https://github.com/comfyanonymous/ComfyUI
  cd ComfyUI
  python -m venv venv && venv\Scripts\pip install -r requirements.txt
  ```

- Install the one required custom node: **[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)** — clone it into `custom_nodes/` and `pip install -r requirements.txt` into the same venv. No other custom nodes are needed.
- **Start the server:**

  ```
  python main.py --listen 127.0.0.1 --port 8188 --lowvram --cpu-vae --disable-auto-launch
  ```

- **Health checks:** `GET http://127.0.0.1:8188/system_stats` shows free RAM/VRAM; `GET /queue` shows running and pending jobs. After starting the server, wait until `/system_stats` answers before submitting anything.
- **Outputs** land in `ComfyUI/output/`. LoadImage/LoadImageMask read from `ComfyUI/input/` — or skip the manual copying and pass `--upload` to `scripts/run_workflow.py`.

## 2. Models

Pick a models root anywhere on disk (it does not need to be inside ComfyUI), e.g. `D:\models` or `~/models`.

| Role | File under the root | Size | Source |
|---|---|---|---|
| Base (required) | `diffusion_models/krea2_turbo-Q4_K_M.gguf` | 7.0 GB | [vantagewithai/Krea-2-Turbo-GGUF](https://huggingface.co/vantagewithai/Krea-2-Turbo-GGUF) |
| Text encoder (required) | `text_encoders/qwen3vl_4b_fp8_scaled.safetensors` | 4.9 GB | [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| VAE (required) | `vae/qwen_image_vae.safetensors` | 242 MB | [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| Style LoRA (required here) | `loras/z3zz4-k2-4_c1-st5000.safetensors` | 448 MB | [Civitai](https://civitai.com/models/2750764) (manual download) |
| Style LoRA (optional) | `loras/BArtstyle-KREA2-V1-1.safetensors` | 448 MB | [Civitai](https://civitai.com/models/29215) (manual) |
| Style-reference LoRA (optional) | `loras/krea2_style_reference.safetensors` | 436 MB | [ostris](https://huggingface.co/ostris/krea2_turbo_style_reference) |
| Faster base (optional) | `diffusion_models/redcraft23INT8INT4FP8_30Krea2.safetensors` | 6.0 GB | [Civitai](https://civitai.com/models/958009) (manual) |
| Cutout (optional) | `segmentation/isnetis.onnx` | 168 MB | [skytnt/anime-seg](https://huggingface.co/skytnt/anime-seg) |
| SAM 2.1 (for sam_mask.py) | `segmentation/sam2.1-hiera-large/` (4 files) | 856 MB | [facebook/sam2.1-hiera-large](https://huggingface.co/facebook/sam2.1-hiera-large) |

Then:

```
python scripts/download_models.py --root D:/models          # downloads HF files, verifies every SHA-256
python scripts/download_models.py --root D:/models --check-only   # verify only (run after manual Civitai downloads)
```

Exact filenames, sizes, URLs and SHA-256 hashes live in [../../../models/models.toml](../../../models/models.toml).

- **Wire the models root into ComfyUI:** copy [../../../extra_model_paths.yaml.example](../../../extra_model_paths.yaml.example) to your ComfyUI folder as `extra_model_paths.yaml` and set `base_path`. Restart ComfyUI.
- **Filenames must match the workflows.** The workflow JSONs load `krea2_turbo-Q4_K_M.gguf`, `qwen3vl_4b_fp8_scaled.safetensors`, `qwen_image_vae.safetensors` and `z3zz4-k2-4_c1-st5000.safetensors` by name. Keep those filenames, or edit the loader nodes (`UnetLoaderGGUF`, `CLIPLoader`, `VAELoader`, `LoraLoaderModelOnly`) to yours.
- The RedCraft entry loads through plain `UNETLoader` instead of `UnetLoaderGGUF` and prints a harmless "unet unexpected … comfy_quant" warning.

## 3. Workflows (`assets/workflows/`, API format)

The prompt goes in at the `PROMPT_PLACEHOLDER` text.

- `krea2_turbo_z3zz4_api.json`: **the poster recipe** — Turbo + z3zz4 at 0.95.
- `krea2_turbo_plain_api.json`: Turbo, no LoRA.
- `krea2_turbo_z3zz4_local_inpaint_api.json`: masked local inpaint (denoise 0.75 default, `--denoise` overrides).
- `krea2_turbo_z3zz4_bg_inpaint_api.json`: background-only repaint around a kept character (SetLatentNoiseMask, denoise 1.0).
- `krea2_redcraft30_reference_recipe_api.json`: the reference-pack recipe rebuilt on RedCraft 3.0.

Sampler defaults baked in: 1920×1080 single pass, 10 steps, er_sde / simple, CFG 1, negative = `ConditioningZeroOut` — **no negative prompt**. Krea 2 prompting specifics: [../anime-illustration/references/prompting-krea2.md](../../anime-illustration/references/prompting-krea2.md).

## 4. Scripts

| Script | Use | Python |
|---|---|---|
| `run_workflow.py WORKFLOW.json --prompt-file P.txt --seed N --prefix name` | Submit and wait; prints JSON with `seconds` and output paths | any 3.11+ |
| `compare.py OUT.jpg "label=path" ... --cols 2 --width 960` | Labeled comparison grid | any with PIL |
| `freeze_preset.py RENDER.png presets/NAME --note "why"` | Freeze a pick into a re-renderable preset | any with PIL |
| `pixel_diff.py A.png B.png` | Bit-exact check of a re-render vs the original | any with numpy + PIL |
| `composite_mask.py BASE INPAINTED MASK OUT` | Paste an inpainted region back; reports the changed box | any with numpy + PIL |
| `sam_mask.py IMAGE OUT --box x0,y0,x1,y1 [--pos x,y ...] [--neg x,y ...]` | SAM 2.1 mask | ComfyUI venv (torch + transformers) |
| `cutout_mask.py IMAGE OUT [--crop ...] [--keep ...]` | anime-seg cutout mask (isnetis.onnx, CPU) | a venv with onnxruntime + scipy |
| `typeset_poster.py BASE ORIGINAL KEEP_MASK LAYOUT.json OUT` | Layered typography: text / scrap / tape / patch items | a venv with opencv-python + scipy |
| `glitch_slice.py IN OUT --band y,h,shift ...` | VHS strip glitch with RGB split | any with numpy + PIL |
| `download_models.py --root DIR` | Download + SHA-256-verify the model manifest | 3.11+ stdlib |

`run_workflow.py` extras: `--as-is` (frozen preset, unchanged), `--lora name:strength` (repeatable), `--image/--mask --upload` (push inputs over HTTP), `--denoise`, `--sampler`, `--front`, `--server`/`COMFY_URL`, `--output-dir`/`COMFY_OUTPUT`. Exit code 4 means ComfyUI reported an error.

## 5. Speed, memory and the queue

- **Speed:** about 4–5 minutes per 1920×1080 Turbo image on the reference machine; the first job after a model switch is slower.
- **RAM is the bottleneck, not the GPU.** Between batches, unload with `POST /free {"unload_models": true, "free_memory": true}`. Avoid queueing many different jobs at once.
- **Queue:** ComfyUI runs one job at a time. Full recipes for stalls, paging, leftover loop processes and interrupts: [../../../docs/troubleshooting.md](../../../docs/troubleshooting.md).
- **Metadata:** every output PNG carries its API graph in the `prompt` text chunk. That is why `freeze_preset.py` and `--as-is` re-renders work — and how the reference poster's real recipe was recovered from its PNG metadata.
