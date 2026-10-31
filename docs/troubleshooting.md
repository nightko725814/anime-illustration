# Troubleshooting

All of these were hit on the reference machine (RTX 3060 Laptop 6 GB, 16 GB RAM, Windows 11) and resolved there.

## Renders suddenly 4–10× slower, then stall

**Symptom:** a Turbo render goes from ~18 s per step to 72–230 s per step, then makes no progress for tens of minutes. `POST /free` doesn't help.

**Cause:** ComfyUI offloaded weights to RAM; when RAM ran out, the offloaded weights started paging from disk. Check the ComfyUI process: if its commit charge is far above its working set, the pages are on disk.

**Fix:** interrupt the job, stop the ComfyUI server process entirely, and start it again. A fresh start got back to ~9 GB free RAM.

Prevention: don't queue many different jobs back-to-back when free RAM is low; unload between batches with `POST /free {"unload_models": true, "free_memory": true}`.

## RAM pressure in general

- Free RAM fell to ~1.7 GB once, and a local inpaint took 30 minutes instead of ~4.
- Three back-to-back Turbo renders under memory pressure took 328 s, 461 s and 1,046 s; a `POST /free` afterwards brought free RAM back to 7.5 GB.
- When free RAM is low, unload between every render.

## A background loop keeps submitting jobs after you stop it

Stopping a background shell task ends only the outer shell. On Windows, a loop's child `bash` keeps running and submits the next seed as soon as the current job ends — one interrupted 0.7 inpaint was followed by an unwanted 0.85 inpaint this way.

**Fix, in order:**

1. Stop the background task in your tool.
2. Also end the child processes whose command line names the loop script:
   ```powershell
   Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'render_xxx\.sh|<prefix>' }
   Stop-Process -Force -Id <pid>
   ```
3. Delete still-pending jobs: `POST /queue {"delete": [prompt_id]}`.
4. Re-check `GET /queue`, matching each job by its SaveImage prefix.

## Interrupting the right job

`POST /interrupt` kills **whichever job is running right now**. Read `GET /queue` first and match the running job's SaveImage prefix before interrupting, so you don't kill someone else's render.

## A frozen preset "re-renders" in 3 seconds

ComfyUI cached it — the graph was the last thing it ran, so the output came back from cache and the reproducibility check proves nothing. Send `POST /free {"unload_models": true, "free_memory": true}` first; a real Turbo re-render takes minutes.

## Model not found when the workflow runs

The workflows load model files by exact filename (`krea2_turbo-Q4_K_M.gguf`, `qwen3vl_4b_fp8_scaled.safetensors`, `qwen_image_vae.safetensors`, `z3zz4-k2-4_c1-st5000.safetensors`). Either keep those filenames, or edit the loader nodes in the JSON. Also confirm your `extra_model_paths.yaml` points at the right root and ComfyUI was restarted after editing it.

## Exit codes of run_workflow.py

| Code | Meaning |
|---|---|
| 0 | done, `images` has the paths |
| 3 | ComfyUI did not accept the submission (payload printed to stderr) |
| 4 | ComfyUI reported an execution error (messages printed to stderr); interrupts also surface here |
| 7 | timed out waiting for completion |
