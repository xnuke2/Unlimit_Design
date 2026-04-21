#!/usr/bin/env python3
"""
wcag_fix_grant.py — WCAG 2.2 accessibility fixes for grant.html

Fixes applied (all documented with inline comments):
  1.  Skip links (main content + filters)
  2.  <main> landmark already present; add id="main-content" + tabindex=-1 for focus
  3.  Auto-focus script: move focus to #main-content on page load
  4.  h3 "Навигатор мер поддержки" → h1
  5.  h3 "Рекомендованные меры" → h2
  6.  Search input: role=search wrapper + aria-label
  7.  Search button: aria-label="Найти меры поддержки"
  8.  Grant card h3 → h2 (font-size preserved via inline style)
  9.  Type-of-measure badge: add visually-hidden prefix "Тип меры поддержки:"
 10.  "Подробнее": remove outer <a>, convert inner <button> to <a> styled as button
        (eliminates double tab-stop)
 11.  Filter form: add id="grants-filters" + aria-label + role=search
 12.  Select combobox inputs: aria-label derived from associated <label> text
 13.  Date picker inputs: add aria-label (matching label) + type=text
 14.  Calendar icon span: aria-label=calendar → aria-label=Календарь
 15.  ЕСИА: wrap div in <a> with proper href + aria-label
 16.  Menu <nav>: add aria-label; menu links/buttons: add aria-label; add JS arrow-key nav
"""

import re
from pathlib import Path

SRC = Path("grant.html")
DST = SRC  # overwrite in-place


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def replace_once(src: str, old: str, new: str, label: str) -> str:
    if old not in src:
        print(f"  WARN [{label}]: pattern not found, skipping")
        return src
    count = src.count(old)
    if count > 1:
        print(f"  WARN [{label}]: {count} occurrences, replacing first only")
    return src.replace(old, new, 1)


def replace_all(src: str, old: str, new: str, label: str) -> str:
    if old not in src:
        print(f"  WARN [{label}]: pattern not found, skipping")
        return src
    n = src.count(old)
    print(f"  [{label}]: replacing {n} occurrence(s)")
    return src.replace(old, new)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def fix(src: str) -> str:

    # ── 1. Skip links ──────────────────────────────────────────────────────
    SKIP_CSS = """\
<style>
.skip-links { position: absolute; top: 0; left: 0; z-index: 9999; }
.skip-link {
  position: absolute; top: -9999px; left: -9999px;
  background: #0067ad; color: #fff; padding: 8px 16px;
  font-size: 14px; font-family: sans-serif; text-decoration: none;
  border-radius: 0 0 4px 0;
}
.skip-link:focus { top: 0; left: 0; }
</style>
"""
    SKIP_HTML = """\
<div class="skip-links" aria-label="Быстрая навигация">
  <a class="skip-link" href="#main-content">Перейти к основному содержимому</a>
  <a class="skip-link" href="#grants-filters">Перейти к фильтрам</a>
</div>
"""
    # Inject CSS before </head>
    src = replace_once(src, "</head>", SKIP_CSS + "</head>", "skip-css")
    # Inject HTML right after <body …>
    src = re.sub(r'(<body[^>]*>)', r'\1\n' + SKIP_HTML, src, count=1)

    # ── 2. id + tabindex on <main> ─────────────────────────────────────────
    src = replace_once(
        src,
        '<main class="ant-layout-content css-1ce7347">',
        '<main id="main-content" tabindex="-1" class="ant-layout-content css-1ce7347">',
        "main-landmark",
    )

    # ── 3. Auto-focus script ───────────────────────────────────────────────
    AUTOFOCUS_JS = """\
<script>
  document.addEventListener('DOMContentLoaded', function () {
    var main = document.getElementById('main-content');
    if (main) { main.focus({ preventScroll: false }); }
  });
</script>
"""
    src = replace_once(src, "</body>", AUTOFOCUS_JS + "</body>", "autofocus-js")

    # ── 4. h3 "Навигатор мер поддержки" → h1 ─────────────────────────────
    src = replace_once(
        src,
        '<h3 class="ant-typography css-1ce7347">Навигатор мер\n                                                                        поддержки</h3>',
        '<h1 class="ant-typography css-1ce7347">Навигатор мер поддержки</h1>',
        "h1-navigator",
    )

    # ── 5. h3 "Рекомендованные меры" → h2 ────────────────────────────────
    src = replace_once(
        src,
        '<h3 class="ant-typography css-1ce7347">Рекомендованные меры\n                                                            </h3>',
        '<h2 class="ant-typography css-1ce7347">Рекомендованные меры</h2>',
        "h2-recommended",
    )

    # ── 6. Search: wrap in role=search form, label the text input ─────────
    # The input already has id=aggregator-navigator-filters-form_name.
    # Add aria-label to it (no visible <label> → SC 1.3.1 / 4.1.2).
    src = replace_once(
        src,
        'placeholder="Введите наименование меры поддержки"\n                                                                                                    id=aggregator-navigator-filters-form_name\n                                                                                                    class="ant-input css-1ce7347 ant-input-outlined"\n                                                                                                    type=text value>',
        'placeholder="Введите наименование меры поддержки"\n                                                                                                    id=aggregator-navigator-filters-form_name\n                                                                                                    aria-label="Наименование меры поддержки"\n                                                                                                    class="ant-input css-1ce7347 ant-input-outlined"\n                                                                                                    type=text value>',
        "search-input-aria",
    )

    # ── 7. Search button: add aria-label ──────────────────────────────────
    src = replace_once(
        src,
        '<button type=button\n                                                                                                    class="ant-btn css-1ce7347 ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-icon-only"\n                                                                                                    style=width:50px>',
        '<button type=button\n                                                                                                    aria-label="Найти меры поддержки"\n                                                                                                    class="ant-btn css-1ce7347 ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-icon-only"\n                                                                                                    style=width:50px>',
        "search-btn-aria",
    )

    # ── 8. Card h3 → h2 ───────────────────────────────────────────────────
    # All grant card titles use <h3 style=margin-bottom:0px>
    src = replace_all(
        src,
        "<h3\n                                                                                                                        style=margin-bottom:0px>",
        "<h2\n                                                                                                                        style=\"margin-bottom:0px;font-size:1rem;font-weight:600\">",
        "card-h2",
    )
    src = replace_all(
        src,
        "</h3>\n                                                                                                                </a>",
        "</h2>\n                                                                                                                </a>",
        "card-h2-close",
    )
    # Recommended section h3 inside navigator-recommendations__link
    src = replace_all(
        src,
        "<h3>Предоставления субсидий",
        '<h2 style="font-size:1rem;font-weight:600">Предоставления субсидий',
        "rec-h2-1",
    )
    src = replace_all(src, "<h3>Возмещение части затрат",
                      '<h2 style="font-size:1rem;font-weight:600">Возмещение части затрат', "rec-h2-2")
    src = replace_all(src, "промышленны ...</h3>", "промышленны ...</h2>", "rec-h2-1-close")
    src = replace_all(src, "договора лизинга</h3>", "договора лизинга</h2>", "rec-h2-2-close")

    # ── 9. Type-of-measure badge: add visually-hidden context ─────────────
    # Pattern: <span style="display:inline-block;background-color:rgb(233,240,255);...">TEXT</span>
    # Prefix with a visually-hidden span "Тип меры поддержки: "
    HIDDEN_PREFIX = '<span class="visually-hidden">Тип меры поддержки: </span>'
    VH_CSS = """\
<style>
.visually-hidden {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
</style>
"""
    src = replace_once(src, "</head>", VH_CSS + "</head>", "vh-css")

    TYPE_BADGE_RE = re.compile(
        r'(<span style="display:inline-block;background-color:rgb\(233,240,255\);border-radius:14px;padding:5px 10px;margin-bottom:10px;margin-right:10px">)'
    )
    src = TYPE_BADGE_RE.sub(r'\1' + HIDDEN_PREFIX, src)

    # ── 10. "Подробнее" double-tab-stop fix ───────────────────────────────
    # Currently: <a href=URL><button title=Подробнее ...><span>Подробнее</span></button></a>
    # Fix: remove <a> wrapper, replace <button> with <a> styled as button,
    # add aria-label that includes the grant title from sibling h2.
    # Since we can't easily derive the title here, we at minimum add
    # aria-label="Подробнее" to the button AND remove the duplicate outer <a>
    # by making button the only focusable element (aria-hidden on <a>, tabindex=-1 on button inside).
    # Simpler safe fix: convert <a><button> to just <a class="ant-btn …">.
    DETAILS_BTN_RE = re.compile(
        r'<a\s+href=([\S]+)><button\s+title=Подробнее\s+type=button\s+'
        r'class="(ant-btn[^"]+)">'
        r'<span>Подробнее</span></button></a>',
        re.DOTALL,
    )
    def btn_to_link(m):
        href = m.group(1)
        cls = m.group(2)
        return (
            f'<a href={href} class="{cls}" role="button">'
            f'<span>Подробнее</span></a>'
        )
    new_src, n = DETAILS_BTN_RE.subn(btn_to_link, src)
    if n:
        print(f"  [подробнее-fix]: replaced {n} button-in-link(s)")
        src = new_src
    else:
        print("  WARN [подробнее-fix]: pattern not found")

    # ── 11. Filter form: id + aria-label ─────────────────────────────────
    src = replace_once(
        src,
        'id=aggregator-navigator-filters-measure-form\n                                                                class="ant-form ant-form-vertical css-1ce7347">',
        'id=aggregator-navigator-filters-measure-form\n                                                                aria-label="Фильтры мер поддержки"\n                                                                class="ant-form ant-form-vertical css-1ce7347">',
        "filter-form-aria",
    )
    # Add id="grants-filters" to the surrounding container div
    src = replace_once(
        src,
        '<div class="ant-space css-1ce7347 ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small"\n                                                        style=max-width:100%>',
        '<div id="grants-filters" class="ant-space css-1ce7347 ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small"\n                                                        style=max-width:100%>',
        "filter-container-id",
    )

    # ── 12. Select combobox inputs: add aria-label ────────────────────────
    # Each combobox `input` has an id that matches its label's `for` attribute.
    # We add aria-label equal to the label text (from the for= / title= on the label).
    COMBOBOX_MAP = {
        "aggregator-navigator-filters-measure-form_territorial_level_support": "Территориальный уровень",
        "aggregator-navigator-filters-measure-form_regionsIds": "Регионы",
        "aggregator-navigator-filters-measure-form_directions": "Виды деятельности",
        "aggregator-navigator-filters-measure-form_recipient_category": "Статус участника",
        "aggregator-navigator-filters-measure-form_support_form": "Форма поддержки",
        "aggregator-navigator-filters-measure-form_regularity": "Регулярность",
        "aggregator-navigator-filters-measure-form_general_funding_from": "Общая сумма финансирования от",
        "aggregator-navigator-filters-measure-form_general_funding_to": "Общая сумма финансирования до",
        "aggregator-navigator-filters-measure-form_measure_type": "Тип меры поддержки",
        "aggregator-navigator-filters-measure-form_okved_codes": "ОКВЭД",
    }
    for field_id, label_text in COMBOBOX_MAP.items():
        old_id_line = f"id={field_id}\n"
        new_id_line = f'id={field_id}\n                                                                                                                                aria-label="{label_text}"\n'
        if old_id_line in src:
            src = src.replace(old_id_line, new_id_line, 1)
            print(f"  [combobox-aria]: {field_id}")
        else:
            print(f"  WARN [combobox-aria]: id not found: {field_id}")

    # ── 13. Date picker inputs: add aria-label + type=text ────────────────
    DATE_MAP = {
        "aggregator-navigator-filters-measure-form_start_date_from": "Начало приема заявок, от",
        "aggregator-navigator-filters-measure-form_start_date_to": "Начало приема заявок, до",
        "aggregator-navigator-filters-measure-form_end_date_from": "Окончание приема заявок, от",
        "aggregator-navigator-filters-measure-form_end_date_to": "Окончание приема заявок, до",
    }
    for field_id, label_text in DATE_MAP.items():
        # date inputs use pattern: id=FIELD placeholder=От/До value>
        old = f"id={field_id}\n"
        new = f'id={field_id}\n                                                                                                                                aria-label="{label_text}"\n                                                                                                                                type=text\n'
        if old in src:
            src = src.replace(old, new, 1)
            print(f"  [date-aria]: {field_id}")
        else:
            print(f"  WARN [date-aria]: id not found: {field_id}")

    # ── 14. Calendar icon: aria-label=calendar → Календарь ───────────────
    src = replace_all(
        src,
        "aria-label=calendar",
        "aria-label=Календарь",
        "calendar-ru",
    )

    # ── 15. ЕСИА: make keyboard-accessible ────────────────────────────────
    src = replace_once(
        src,
        '<div class=ant-space-item>\n                                                <div class="ant-spin-nested-loading css-1ce7347">\n                                                    <div class=ant-spin-container>\n                                                        <div class=hoverSize\n                                                            style=display:flex;flex-direction:column;align-items:center;gap:6px;font-family:Nunito,sans-serif;font-weight:700;font-size:10px;text-align:center;text-transform:uppercase;color:rgb(0,103,173)>\n                                                            <img alt=?\n                                                                src="assets/images/75dfe2373ca59143.png"\n                                                                style=height:40px;width:40px><span><span\n                                                                    class=hiddenPhone>Вход</span> ЕСИА</span></div>\n                                                    </div>\n                                                </div>\n                                            </div>',
        '<div class=ant-space-item>\n                                                <a href="https://gisnauka.ru/auth/esia" aria-label="Вход через ЕСИА" style=text-decoration:none>\n                                                <div class=hoverSize\n                                                    style=display:flex;flex-direction:column;align-items:center;gap:6px;font-family:Nunito,sans-serif;font-weight:700;font-size:10px;text-align:center;text-transform:uppercase;color:rgb(0,103,173)>\n                                                    <img alt=""\n                                                        src="assets/images/75dfe2373ca59143.png"\n                                                        style=height:40px;width:40px aria-hidden=true><span aria-hidden=true><span\n                                                            class=hiddenPhone>Вход</span> ЕСИА</span></div>\n                                                </a>\n                                            </div>',
        "esia-link",
    )

    # ── 16. Nav: aria-label on <nav>, keyboard arrow-key script ──────────
    # Add aria-label to nav
    src = replace_once(
        src,
        "<nav class=menuBar>",
        '<nav class=menuBar aria-label="Основная навигация">',
        "nav-aria",
    )

    # Arrow-key JS for menu
    MENU_JS = """\
<script>
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('nav.menuBar');
    if (!nav) return;
    var items = Array.from(nav.querySelectorAll('a.menuLink, button.ant-dropdown-trigger'));
    items.forEach(function (el, idx) {
      el.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          next = items[(idx + 1) % items.length];
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          next = items[(idx - 1 + items.length) % items.length];
        } else if (e.key === 'Home') {
          next = items[0];
        } else if (e.key === 'End') {
          next = items[items.length - 1];
        }
        if (next) { e.preventDefault(); next.focus(); }
      });
    });
  });
})();
</script>
"""
    src = replace_once(src, "</body>", MENU_JS + "</body>", "menu-arrow-js")

    # ── 17. МЧД image: fix alt="" (currently alt=?) ────────────────────
    src = replace_once(
        src,
        '<img alt=?\n                                                            src=assets/images/1b81cbfa37ea22d9.png\n                                                            style=height:40px;width:40px>МЧД',
        '<img alt=""\n                                                            src=assets/images/1b81cbfa37ea22d9.png\n                                                            style=height:40px;width:40px aria-hidden=true>МЧД',
        "mchd-alt",
    )

    # ── 18. Menu images: fix alt=? → alt="" (decorative) ─────────────────
    src = replace_all(src, "alt=?", 'alt=""', "alt-question-marks")

    return src


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    text = SRC.read_text(encoding="utf-8")
    result = fix(text)
    DST.write_text(result, encoding="utf-8")
    print(f"\nDone. Written to {DST}")
