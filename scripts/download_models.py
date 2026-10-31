"""Download and SHA-256-verify the models listed in models/models.toml.

Hugging Face files download automatically. Civitai files cannot be scripted (login
required): download them manually from the `page` link, then run this script again
to verify their SHA-256.

Usage:
    python download_models.py --root D:/models              # download missing + verify all
    python download_models.py --root D:/models --check-only # verify only, no downloads
    python download_models.py --root D:/models --role base  # one role only (repeatable)

Requires Python 3.11+ (stdlib only).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tomllib
import urllib.request
from pathlib import Path

CHUNK = 1 << 20


def sha256_of(path: Path, expected_size: int | None = None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    part = dst.with_suffix(dst.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "anime-illustration-skill"})
    with urllib.request.urlopen(req) as resp, part.open("wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while chunk := resp.read(CHUNK):
            f.write(chunk)
            done += len(chunk)
            if total and done % (256 << 20) < CHUNK:
                print(f"    {done / 1e9:.2f} / {total / 1e9:.2f} GB", flush=True)
    part.replace(dst)


def main() -> int:
    script_dir = Path(__file__).resolve().parent.parent
    manifest = script_dir / "models" / "models.toml"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Models root directory (files land in its subfolders)")
    parser.add_argument("--check-only", action="store_true", help="Verify existing files, download nothing")
    parser.add_argument("--role", action="append", default=[],
                        help="Only handle models with this role (repeatable)")
    args = parser.parse_args()

    entries = tomllib.loads(manifest.read_text(encoding="utf-8"))["model"]
    if args.role:
        entries = [e for e in entries if e["role"] in args.role]

    root = Path(args.root)
    failures = 0
    for e in entries:
        dst = root / e["file"]
        expected = e["sha256"]
        label = f"[{e['role']}] {e['file']}"
        if dst.is_file():
            actual = sha256_of(dst)
            if actual == expected:
                print(f"OK       {label}")
                continue
            print(f"MISMATCH {label}\n    expected {expected}\n    actual   {actual}"
                  "\n    delete the file and rerun to re-download (Hugging Face) or check the source (Civitai)")
            failures += 1
            continue
        if args.check_only or not e.get("url"):
            page = e.get("page", "")
            print(f"MISSING  {label}"
                  + (f"  - download manually from {page}, then rerun to verify" if page else ""))
            failures += e.get("required", False)
            continue
        print(f"DOWNLOAD {label}  ({e['size_bytes'] / 1e9:.2f} GB)")
        try:
            download(e["url"], dst)
        except Exception as err:  # noqa: BLE001 - report any network/HTTP failure per file
            print(f"    download failed: {err}")
            failures += 1
            continue
        actual = sha256_of(dst)
        if actual == expected:
            print(f"OK       {label}")
        else:
            print(f"MISMATCH {label}: got {actual}")
            failures += 1

    if failures:
        print(f"\n{failures} problem(s) found. Required files marked MISSING or MISMATCH must be fixed "
              "before the workflows will run.")
        return 1
    print("\nAll listed models present and verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
