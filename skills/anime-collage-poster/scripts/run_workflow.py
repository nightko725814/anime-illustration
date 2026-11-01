"""Queue an API-format ComfyUI workflow, wait for it, and print the saved image paths.

Usage:
    python run_workflow.py WORKFLOW.json --prompt-file PROMPT.txt [--seed N] [--denoise 0.4]

Images/masks for inpaint workflows live in ComfyUI's input directory. Either copy them
there yourself, or pass --upload to push the local files through ComfyUI's HTTP API.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import urllib.request
from pathlib import Path


def call(url: str, payload: dict | None = None, timeout: int = 60) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data is not None else {}
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def upload_file(server: str, local: Path, subfolder: str) -> str:
    """POST a local file to ComfyUI's /upload/image and return the LoadImage value."""
    boundary = "----AnimeIllustration" + secrets.token_hex(8)
    body = bytearray()

    def field(name: str, value: str) -> None:
        body.extend(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8")
        )

    field("subfolder", subfolder)
    field("overwrite", "true")
    body.extend(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{local.name}\"\r\n"
        "Content-Type: application/octet-stream\r\n\r\n".encode("utf-8")
    )
    body.extend(local.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{server}/upload/image",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    name, sub = out["name"], out.get("subfolder", "")
    return f"{name}[{sub}]" if sub else name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--prompt-file", type=Path, default=None)
    parser.add_argument("--as-is", action="store_true",
                        help="Submit a frozen workflow unchanged: keep its prompt, seeds and denoise")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--denoise", type=float, default=None, help="Pass 2 denoise")
    parser.add_argument("--prefix", default=None, help="Prepended to every SaveImage filename_prefix")
    parser.add_argument("--image", default=None,
                        help="Image for every LoadImage node: a name inside ComfyUI/input, or a local "
                             "file path when --upload is set")
    parser.add_argument("--mask", default=None,
                        help="Mask for every LoadImageMask node: a name inside ComfyUI/input, or a "
                             "local file path when --upload is set")
    parser.add_argument("--upload", action="store_true",
                        help="Upload --image/--mask from local disk to ComfyUI via /upload/image")
    parser.add_argument("--lora-strength", type=float, default=None,
                        help="strength_model for every LoraLoaderModelOnly node")
    parser.add_argument("--lora-name", default=None,
                        help="lora_name (a file in your loras folder) for every LoraLoaderModelOnly node")
    parser.add_argument("--sampler", default=None,
                        help="sampler_name for every KSampler / KSamplerSelect node (e.g. euler, er_sde)")
    parser.add_argument("--lora", action="append", default=[],
                        help="name.safetensors:strength for the LoRA chain, in order (repeatable); "
                             "the n-th --lora sets the n-th LoraLoaderModelOnly node by node id")
    parser.add_argument("--front", action="store_true", help="Put this job at the front of ComfyUI's queue")
    parser.add_argument("--server", default=os.environ.get("COMFY_URL", "http://127.0.0.1:8188"))
    parser.add_argument("--output-dir", default=os.environ.get("COMFY_OUTPUT"),
                        help="ComfyUI's output directory (default: env COMFY_OUTPUT). Without it the "
                             "printed paths are relative to that directory")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    graph = json.loads(args.workflow.read_text(encoding="utf-8"))
    if not args.as_is and args.prompt_file is None:
        parser.error("--prompt-file is required unless --as-is is given")
    prompt = None if args.as_is else args.prompt_file.read_text(encoding="utf-8").strip()
    seed = "as-is" if args.as_is else (args.seed if args.seed is not None else secrets.randbits(48))

    for arg_name, node_type in (("--image", "LoadImage"), ("--mask", "LoadImageMask")):
        value = getattr(args, arg_name.lstrip("-"))
        if value and args.upload:
            staged = upload_file(args.server, Path(value), subfolder="anime-illustration")
            print(f"uploaded {value} -> {staged}", flush=True)
            setattr(args, arg_name.lstrip("-"), staged)

    for node in graph.values():
        inputs = node["inputs"]
        if node["class_type"] == "SaveImage" and args.prefix:
            inputs["filename_prefix"] = f"{args.prefix}_{inputs['filename_prefix']}"
        if args.as_is:
            continue
        for key in ("text", "prompt"):
            if inputs.get(key) == "PROMPT_PLACEHOLDER":
                inputs[key] = prompt
        if node["class_type"] == "KSampler":
            inputs["seed"] = seed
        if node["class_type"] == "RandomNoise":
            inputs["noise_seed"] = seed
        if node["class_type"] in ("KSampler", "BasicScheduler"):
            if args.denoise is not None and inputs["denoise"] < 1.0:
                inputs["denoise"] = args.denoise
        if node["class_type"] == "LoadImage" and args.image:
            inputs["image"] = args.image
        if node["class_type"] == "LoadImageMask" and args.mask:
            inputs["image"] = args.mask
        if node["class_type"] == "LoraLoaderModelOnly" and args.lora_strength is not None:
            inputs["strength_model"] = args.lora_strength
        if node["class_type"] == "LoraLoaderModelOnly" and args.lora_name:
            inputs["lora_name"] = args.lora_name
        if node["class_type"] in ("KSampler", "KSamplerSelect") and args.sampler:
            inputs["sampler_name"] = args.sampler

    if args.lora and not args.as_is:
        lora_nodes = sorted((k for k, n in graph.items() if n["class_type"] == "LoraLoaderModelOnly"), key=int)
        if len(args.lora) > len(lora_nodes):
            parser.error(f"{len(args.lora)} --lora given but the workflow has {len(lora_nodes)} LoRA nodes")
        for node_id, spec in zip(lora_nodes, args.lora):
            name, _, strength = spec.rpartition(":")
            graph[node_id]["inputs"]["lora_name"] = name
            graph[node_id]["inputs"]["strength_model"] = float(strength)

    payload = {"prompt": graph, "client_id": "anime-illustration"}
    if args.front:
        payload["front"] = True
    queued = call(f"{args.server}/prompt", payload, timeout=120)
    prompt_id = queued.get("prompt_id")
    if not prompt_id:
        print(json.dumps(queued, ensure_ascii=False, indent=2), file=sys.stderr)
        return 3
    print(f"queued {prompt_id} seed={seed}", flush=True)

    started = time.monotonic()
    while time.monotonic() - started < args.timeout:
        record = call(f"{args.server}/history/{prompt_id}").get(prompt_id)
        if record:
            status = record.get("status", {})
            if status.get("status_str") == "error":
                print(json.dumps(status.get("messages", []), ensure_ascii=False, indent=2), file=sys.stderr)
                return 4
            if status.get("completed"):
                paths = [
                    img.get("subfolder", "") + img["filename"]
                    for out in record.get("outputs", {}).values()
                    for img in out.get("images", [])
                ]
                if args.output_dir:
                    out_dir = Path(args.output_dir)
                    paths = [str(out_dir / p) for p in paths]
                print(json.dumps({"prompt_id": prompt_id, "seed": seed,
                                  "seconds": round(time.monotonic() - started),
                                  "images": paths}, ensure_ascii=False))
                return 0
        time.sleep(3)

    print(f"timed out waiting for {prompt_id}", file=sys.stderr)
    return 7


if __name__ == "__main__":
    raise SystemExit(main())
