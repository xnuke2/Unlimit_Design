#!/usr/bin/env python3
"""Extract <style> blocks from SingleFile HTML into css/chunks + css/pages/*.css with dedup."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "css" / "chunks"
PAGES = ROOT / "css" / "pages"
STYLE_RE = re.compile(r"<style\b[^>]*>([\s\S]*?)</style>", re.IGNORECASE)

# (source_html, output_css_basename)
PAGE_JOBS = [
    ("grant.html", "grant"),
    ("details.html", "details"),
    ("details_2.html", "details_2"),
    ("index.html", "index"),
]


def chunk_name(css: str) -> str:
    h = hashlib.sha256(css.encode("utf-8")).hexdigest()[:14]
    return f"c_{h}.css"


def main() -> None:
    CHUNKS.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)

    seen_hashes: dict[str, str] = {}  # full hash -> chunk filename for logging

    for html_name, page_key in PAGE_JOBS:
        html_path = ROOT / html_name
        raw = html_path.read_text(encoding="utf-8")
        blocks = STYLE_RE.findall(raw)
        if not blocks:
            print(f"Skip {html_name}: no <style> blocks (already extracted?)")
            continue

        import_lines: list[str] = []
        for css in blocks:
            normalized = css.strip("\n")
            if not normalized.strip():
                continue
            name = chunk_name(normalized)
            chunk_path = CHUNKS / name
            if not chunk_path.exists():
                chunk_path.write_text(normalized + "\n", encoding="utf-8")
                full = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                seen_hashes.setdefault(full, name)

            import_lines.append(f'@import "../chunks/{name}";')

        page_css = PAGES / f"{page_key}.css"
        page_css.write_text("\n".join(import_lines) + "\n", encoding="utf-8")

        stripped = STYLE_RE.sub("", raw)
        stripped = stripped.replace(
            "style-src 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
        )
        stripped = re.sub(r"\n{4,}", "\n\n\n", stripped)
        link = f'<link rel=stylesheet href=css/pages/{page_key}.css>'
        if "</head>" in stripped:
            stripped = stripped.replace("</head>", f"{link}\n</head>", 1)
        else:
            stripped = link + "\n" + stripped

        html_path.write_text(stripped, encoding="utf-8")
        print(f"{html_name}: {len(blocks)} style tags -> {len(import_lines)} imports, {page_css.name}")

    unique_chunks = len(list(CHUNKS.glob("c_*.css")))
    print(f"Unique chunk files: {unique_chunks}")


if __name__ == "__main__":
    main()
