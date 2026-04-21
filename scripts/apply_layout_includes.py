#!/usr/bin/env python3
"""Legacy helper: expects <div data-include="site-menu-inner"> slots in HTML.

For the current static pages, run instead (inlines header + menu + footer):
  python3 scripts/apply_layout_regex.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = ROOT / "partials" / "layout-common.html"
MENU_MARK = "<!-- site:menu-inner -->"
FOOT_MARK = "<!-- site:footer -->"

PAGES = [
    ROOT / "index.html",
    ROOT / "grant.html",
    ROOT / "details.html",
    ROOT / "details_2.html",
]

SCRIPT_RE = re.compile(
    r'\n?<script src="js/layout-include\.js" defer></script>\s*',
    re.MULTILINE,
)


def trim_blank_lines_edges(s: str) -> str:
    """Strip only empty lines at start/end; keep indentation of first/last real line."""
    lines = s.splitlines(keepends=True)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "".join(lines)


def load_chunks() -> tuple[str, str]:
    text = PARTIAL.read_text(encoding="utf-8")
    i0 = text.index(MENU_MARK)
    i1 = text.index(FOOT_MARK)
    if i1 <= i0:
        raise SystemExit("Invalid partial: footer marker before menu marker")
    menu = trim_blank_lines_edges(text[i0 + len(MENU_MARK) : i1])
    footer = trim_blank_lines_edges(text[i1 + len(FOOT_MARK) :])
    if not menu or not footer:
        raise SystemExit("Empty menu or footer in partial")
    return menu, footer


MENU_SLOT_RE = re.compile(
    r"^[ \t]*<div data-include=\"site-menu-inner\"></div>\s*",
    re.MULTILINE,
)
FOOT_SLOT_RE = re.compile(
    r"^[ \t]*<div data-include=\"site-footer\"></div>\s*",
    re.MULTILINE,
)


def apply_page(path: Path, menu: str, footer: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    out = raw
    out, n1 = MENU_SLOT_RE.subn(menu + "\n", out, count=1)
    out, n2 = FOOT_SLOT_RE.subn(footer + "\n", out, count=1)
    if n1 != 1 or n2 != 1:
        raise SystemExit(f"{path.name}: expected 1 menu and 1 footer slot, got {n1=} {n2=}")
    out, ns = SCRIPT_RE.subn("\n", out, count=1)
    if ns == 0 and "layout-include.js" in out:
        raise SystemExit(f"{path.name}: could not remove layout-include.js script tag")
    path.write_text(out, encoding="utf-8")
    return True


def main() -> None:
    menu, footer = load_chunks()
    for p in PAGES:
        if not p.is_file():
            print("skip missing", p.name)
            continue
        if apply_page(p, menu, footer):
            print("updated", p.name)
        else:
            print("no change", p.name)


if __name__ == "__main__":
    main()
