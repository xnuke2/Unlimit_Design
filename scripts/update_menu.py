#!/usr/bin/env python3
"""
update_menu.py — Replace the already-inlined affixMenu block in each page
with the current version from partials/layout-common.html.

Usage:  python3 scripts/update_menu.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = ROOT / "partials" / "layout-common.html"

PAGES = [
    ROOT / "index.html",
    ROOT / "grant.html",
    ROOT / "details.html",
    ROOT / "details_2.html",
]

MENU_MARK = "<!-- site:menu-inner -->"
FOOT_MARK = "<!-- site:footer -->"


def load_menu_from_partial() -> str:
    text = PARTIAL.read_text(encoding="utf-8")
    i0 = text.index(MENU_MARK)
    i1 = text.index(FOOT_MARK)
    chunk = text[i0 + len(MENU_MARK) : i1]
    # Strip only leading/trailing blank lines, preserve indentation
    lines = chunk.splitlines(keepends=True)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "".join(lines)


# The affixMenu block starts with the first <div class=affixMenu> (after the
# header area) and ends right before <main …>.  We use a regex that captures
# everything from the opening <div class=affixMenu> through the closing tag of
# the nav wrapper up to (but not including) <main.
# The block always ends with </div>\n</div>\n</div>\n (closing the three wrapper
# divs around the nav) followed optionally by whitespace and then <main.
AFFIX_MENU_RE = re.compile(
    r'(\s*<div class=affixMenu>.*?</div>\s*(?=<main))',
    re.DOTALL,
)


def update_page(path: Path, new_menu: str) -> None:
    text = path.read_text(encoding="utf-8")
    m = AFFIX_MENU_RE.search(text)
    if not m:
        print(f"  WARN {path.name}: affixMenu block not found, skipping")
        return
    # new_menu already starts with <div class=affixMenu> (trimmed from partial)
    # Preserve a leading newline to keep formatting
    replacement = "\n" + new_menu + "\n"
    new_text = text[: m.start()] + replacement + text[m.end() :]
    path.write_text(new_text, encoding="utf-8")
    print(f"  updated {path.name}")


if __name__ == "__main__":
    menu = load_menu_from_partial()
    for p in PAGES:
        if not p.is_file():
            print(f"  skip (missing): {p.name}")
            continue
        update_page(p, menu)
    print("Done.")
