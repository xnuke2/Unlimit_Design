#!/usr/bin/env python3
"""
Extract data:image/* URLs from HTML into assets/images/, dedupe by SHA-256 of raw bytes.

  python3 scripts/extract_html_images.py

Re-run safe: same hash -> same filename. Edit HTML in place; paths are assets/images/<id>.<ext>
"""

from __future__ import annotations

import base64
import hashlib
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "images"

HTML_FILES = [
    ROOT / "index.html",
    ROOT / "grant.html",
    ROOT / "details.html",
    ROOT / "details_2.html",
    ROOT / "partials" / "layout-common.html",
]

# Raster / icon base64 (also matches inside url(...))
RE_BASE64 = re.compile(
    r"data:image/(?:png|jpeg|jpe?g|gif|webp|x-icon);base64,[A-Za-z0-9+/=]+",
    re.IGNORECASE,
)

# SVG base64
RE_SVG_B64 = re.compile(
    r"data:image/svg\+xml(?:;[^,]+)?;base64,[A-Za-z0-9+/=]+",
    re.IGNORECASE,
)

# Inline SVG after comma (SingleFile style); non-greedy to first </svg>
RE_SVG_INLINE = re.compile(
    r"data:image/svg\+xml,<svg.*?</svg>",
    re.IGNORECASE | re.DOTALL,
)


def mime_and_bytes(data_url: str) -> tuple[str, bytes]:
    if not data_url.startswith("data:"):
        raise ValueError("not a data URL")
    rest = data_url[5:]  # after "data:"
    if ";base64," in rest:
        meta, b64 = rest.split(";base64,", 1)
        mime = meta.split(";")[0].lower()
        raw = base64.b64decode(b64, validate=False)
        return mime, raw
    if "," not in rest:
        raise ValueError("no comma in data url")
    meta, payload = rest.split(",", 1)
    mime = meta.split(";")[0].lower()
    if mime != "image/svg+xml":
        raise ValueError(f"unsupported non-base64 mime: {mime}")
    if payload.lstrip().startswith("<"):
        return mime, payload.encode("utf-8")
    return mime, urllib.parse.unquote_to_bytes(payload.replace("+", " "))


def ext_for_mime(mime: str) -> str:
    m = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/x-icon": "ico",
        "image/svg+xml": "svg",
    }.get(mime.lower())
    if not m:
        raise ValueError(f"unknown mime {mime}")
    return m


def collect_urls(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(m: re.Match[str]) -> None:
        s = m.group(0)
        if s not in seen:
            seen.add(s)
            found.append(s)

    for rx in (RE_BASE64, RE_SVG_B64, RE_SVG_INLINE):
        for m in rx.finditer(text):
            add(m)
    return found


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # url -> replacement path (same for identical content)
    url_to_path: dict[str, str] = {}
    hash_to_path: dict[str, str] = {}

    for path in HTML_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for url in collect_urls(text):
            if url in url_to_path:
                continue
            try:
                mime, raw = mime_and_bytes(url)
            except Exception as e:
                raise SystemExit(f"decode failed ({path.name}): {e}\n…{url[:80]}…") from e
            h = hashlib.sha256(raw).hexdigest()[:16]
            ext = ext_for_mime(mime)
            key = f"{h}.{ext}"
            if key not in hash_to_path:
                out_path = OUT_DIR / key
                if not out_path.exists():
                    out_path.write_bytes(raw)
                hash_to_path[key] = key
            fname = hash_to_path[key]
            url_to_path[url] = f"assets/images/{fname}"

    # Replace longest URLs first (avoid partial overlap)
    ordered = sorted(url_to_path.keys(), key=len, reverse=True)

    for path in HTML_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for url in ordered:
            rep = url_to_path[url]
            text = text.replace(url, rep)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print("patched", path.relative_to(ROOT), "saved", len(orig) - len(text), "chars")

    print("unique images (by hash):", len(hash_to_path))
    print("total data-url occurrences replaced:", len(url_to_path))


if __name__ == "__main__":
    main()
