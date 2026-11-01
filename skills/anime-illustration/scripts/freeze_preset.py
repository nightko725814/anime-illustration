"""Freeze a ComfyUI render the user picked into a preset folder that can be re-rendered as-is.

Copies the PNG to PRESET_DIR/best.png, exports the API graph stored in its metadata to
workflow_api.json (prompt, seed and every setting baked in), saves the prompt text to prompt.txt,
and writes a README with SHA-256 hashes and the re-render command. Refuses to touch an existing folder.

Afterwards verify it: re-run with run_workflow.py --as-is --prefix verify, then pixel_diff.py.

Usage:
    python freeze_preset.py RENDER.png PRESET_DIR [--title "..."] [--note "the user's words"]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render", type=Path)
    parser.add_argument("preset_dir", type=Path)
    parser.add_argument("--title", default=None)
    parser.add_argument("--note", default="", help="Why this one was picked, ideally in the user's words")
    args = parser.parse_args()

    info = Image.open(args.render).info
    if "prompt" not in info:
        parser.error(f"{args.render} has no ComfyUI 'prompt' metadata; it cannot be re-rendered as-is")
    graph = json.loads(info["prompt"])

    dst = args.preset_dir
    dst.mkdir(parents=True, exist_ok=False)
    shutil.copy2(args.render, dst / "best.png")
    (dst / "workflow_api.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    texts = [n["inputs"]["text"] for n in graph.values()
             if n["class_type"] == "CLIPTextEncode" and isinstance(n["inputs"].get("text"), str)]
    if texts:
        (dst / "prompt.txt").write_text(texts[0], encoding="utf-8")

    sampler = next((n["inputs"] for n in graph.values() if n["class_type"] == "KSampler"), {})
    rows = "\n".join(f"| `{f.name}` | `{sha256(f)}` |" for f in sorted(dst.iterdir()))
    readme = f"""# {args.title or dst.name}

{args.note}

Frozen from `{args.render}`. Do not edit this folder; start new experiments elsewhere.

Seed {sampler.get('seed')}, {sampler.get('steps')} steps, {sampler.get('sampler_name')} / {sampler.get('scheduler')}, CFG {sampler.get('cfg')}.

| File | SHA-256 |
|---|---|
{rows}

## Re-render

```
python run_workflow.py "{dst / 'workflow_api.json'}" --as-is --prefix repro
```

## Verification

Not verified yet. Re-render with `--prefix verify`, then `python pixel_diff.py best.png <the verify output>`.
"""
    (dst / "README.md").write_text(readme, encoding="utf-8")
    print(f"frozen into {dst}")
    for f in sorted(dst.iterdir()):
        print(f"  {f.name}  {sha256(f)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
