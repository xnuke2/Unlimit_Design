#!/usr/bin/env python3
"""Inline header + menu + footer from partials/layout-common.html into root *.html.

Single source of truth: edit partials/layout-common.html, then run:
  python3 scripts/apply_layout_regex.py

All site pages in the repo root (*.html) are updated; do not duplicate header/menu/footer by hand.
"""

from __future__ import annotations

import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = ROOT / "partials" / "layout-common.html"

HEADER_MARK = "<!-- site:header -->"
MENU_MARK = "<!-- site:menu-inner -->"
FOOT_MARK = "<!-- site:footer -->"


def trim_edges(s: str) -> str:
    lines = s.splitlines(keepends=True)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "".join(lines)


def load_chunks() -> tuple[str, str, str]:
    text = PARTIAL.read_text(encoding="utf-8")
    i0 = text.index(HEADER_MARK)
    i1 = text.index(MENU_MARK)
    i2 = text.index(FOOT_MARK)
    if not (i0 < i1 < i2):
        raise SystemExit("Invalid partial: marker order must be header < menu < footer")
    header = trim_edges(text[i0 + len(HEADER_MARK) : i1])
    menu = trim_edges(text[i1 + len(MENU_MARK) : i2])
    footer = trim_edges(text[i2 + len(FOOT_MARK) :])
    if not header or not menu or not footer:
        raise SystemExit("Empty header, menu or footer in partial")
    return header, menu, footer


def strip_merge_conflicts(s: str) -> str:
    s = re.sub(r"^<<<<<<<[^\n]*\n", "", s, flags=re.MULTILINE)
    s = re.sub(r"^=======\n", "", s, flags=re.MULTILINE)
    s = re.sub(r"^>>>>>>>[^\n]*\n", "", s, flags=re.MULTILINE)
    return s


# From id=site-header through closing of affixMenu (nav + two wrapper divs).
# Leading whitespace before <div id="site-header" must be consumed or it duplicates on each run.
CHROME_WITH_HEADER_RE = re.compile(
    r"[ \t]*<div\s+id=[\"']site-header[\"'][^>]*>.*?[ \t]*<div\s+class=[\"']?affixMenu[\"']?\s*>.*?</nav>\s*</div>\s*</div>",
    re.DOTALL | re.IGNORECASE,
)

MENU_ONLY_RE = re.compile(
    r"[ \t]*<div\s+class=[\"']?affixMenu[\"']?\s*>.*?</nav>\s*</div>\s*</div>",
    re.DOTALL | re.IGNORECASE,
)

FOOTER_RE = re.compile(
    r"[ \t]*<footer\s+id=[\"']site-footer[\"'][^>]*>.*?</footer>",
    re.DOTALL | re.IGNORECASE,
)

SCRIPT_RE = re.compile(
    r'\n?<script\s+src="js/layout-include\.js"\s+defer></script>\s*',
    re.MULTILINE,
)


def apply_page(path: Path, header_html: str, menu_html: str, footer_html: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    content = strip_merge_conflicts(raw)
    chrome = header_html.rstrip() + "\n" + menu_html.rstrip() + "\n"
    out = content

    if re.search(r'id=["\']site-header["\']', out):
        out, n = CHROME_WITH_HEADER_RE.subn(chrome, out, count=1)
        if n != 1:
            raise SystemExit(f"{path.name}: expected 1 chrome (header+menu) replace, got {n}")
    elif MENU_ONLY_RE.search(out):
        out, n = MENU_ONLY_RE.subn(chrome, out, count=1)
        if n != 1:
            raise SystemExit(f"{path.name}: expected 1 menu-only replace, got {n}")
    else:
        raise SystemExit(f"{path.name}: no site-header and no affixMenu — cannot apply layout")

    # Do not append an extra newline after </footer> (avoids one-byte drift vs saved HTML).
    out, nf = FOOTER_RE.subn(footer_html.rstrip(), out, count=1)
    if nf != 1:
        raise SystemExit(f"{path.name}: expected 1 footer replace, got {nf}")

    # One newline between top menu chrome and <main> (avoids newline drift on re-apply).
    out, _ = re.subn(
        r"(</nav>\s*</div>\s*</div>)\s+(?=<main\b)",
        r"\1\n",
        out,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    out, _ = SCRIPT_RE.subn("\n", out, count=1)

    if "css/pages/index.css" not in out and "css/pages/grant.css" not in out and "css/pages/details.css" not in out:
        css_link = '\n<link rel="stylesheet" href="css/pages/index.css">\n'
        out, _ = re.subn(r"(</head>)", css_link + r"\1", out, count=1, flags=re.IGNORECASE)
        out = re.sub(
            r"body\s*\{[^}]*display:\s*flex[^}]*\}",
            "body { margin: 0; min-height: 100vh; background: #eaedef; color: #1a1a1a; line-height: 1.5; }",
            out,
            count=1,
            flags=re.DOTALL,
        )

    if out != raw:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> None:
    header, menu, footer = load_chunks()
    for name in sorted(glob.glob(str(ROOT / "*.html"))):
        path = Path(name)
        if path.name == "layout-common.html":
            continue
        if not path.is_file():
            continue
        try:
            changed = apply_page(path, header, menu, footer)
        except SystemExit as e:
            raise SystemExit(f"{path}: {e}") from e
        print("updated" if changed else "unchanged", path.name)


if __name__ == "__main__":
    main()
