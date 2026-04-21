#!/usr/bin/env python3
"""Swap list / filters columns in grant.html so tab order is search → filters → list.

Large-screen layout: list ant-col-lg-order-0 (left), filters ant-col-lg-order-1 (right).
"""
from pathlib import Path


def extract_div_block(html: str, start: int) -> tuple[str, int, int]:
    if not html.startswith("<div", start):
        raise SystemExit(f"expected <div at {start}, got {repr(html[start : start + 12])}")
    gt = html.find(">", start)
    if gt == -1:
        raise SystemExit("no closing > on opening tag")
    pos = gt + 1
    depth = 1
    while depth:
        nxt_open = html.find("<div", pos)
        nxt_close = html.find("</div>", pos)
        if nxt_close == -1:
            raise SystemExit("unbalanced divs")
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + 4
        else:
            depth -= 1
            pos = nxt_close + len("</div>")
            if depth == 0:
                return html[start:pos], start, pos
    raise SystemExit("unreachable")


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "grant.html"
    html = path.read_text(encoding="utf-8")

    list_mid = html.find('ant-col-lg-16 ant-col-lg-order-0 css-1ce7347"')
    if list_mid == -1:
        raise SystemExit("list column marker not found")
    i_list = html.rfind("<div", 0, list_mid + 1)

    filter_mid = html.find('ant-col-xs-24 ant-col-md-24 ant-col-lg-8 css-1ce7347"')
    if filter_mid == -1:
        raise SystemExit("filter column marker not found")
    i_filter = html.rfind("<div", 0, filter_mid + 1)

    if i_list == -1 or i_filter == -1:
        raise SystemExit(f"column opens not found i_list={i_list} i_filter={i_filter}")

    list_block, _, list_end = extract_div_block(html, i_list)
    filter_block, _, filter_end = extract_div_block(html, i_filter)

    if not (i_list < i_filter and list_end <= i_filter):
        raise SystemExit(
            f"unexpected geometry i_list={i_list} i_filter={i_filter} list_end={list_end} — refuse to swap"
        )

    nl = filter_block.find("\n")
    first, rest = filter_block[:nl], filter_block[nl:]
    if "ant-col-lg-order-1" not in first:
        first = first.replace("ant-col-lg-8 css", "ant-col-lg-8 ant-col-lg-order-1 css", 1)
    filter_new = first + rest

    new_html = html[:i_list] + filter_new + html[list_end:i_filter] + list_block + html[filter_end:]
    path.write_text(new_html, encoding="utf-8")
    print("grant.html: columns swapped (DOM: filters before list); lg-order-1 on filters.")


if __name__ == "__main__":
    main()
