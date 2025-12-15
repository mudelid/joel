#!/usr/bin/env python3
from pathlib import Path

CSS_MARK_START = "/* === FIX: remove bottom brand arrows === */"
CSS_MARK_END   = "/* === /FIX: remove bottom brand arrows === */"

CSS_BLOCK = f"""
{CSS_MARK_START}
/* Peida alumised brändi-nooled/riba (mobiil) */
.brand-bar,
.brand-nav-mobile {{
  display: none !important;
}}
{CSS_MARK_END}
"""

JS_MARK_START = "<!-- === FIX: remove bottom brand arrows (js) === -->"
JS_MARK_END   = "<!-- === /FIX: remove bottom brand arrows (js) === -->"

JS_BLOCK = f"""
{JS_MARK_START}
<script>
(() => {{
  // Kui mingi skript lisas alumise riba/nupud, eemalda need
  document.querySelectorAll('.brand-bar, .brand-nav-mobile').forEach(el => el.remove());
}})();
</script>
{JS_MARK_END}
"""

def inject_css(html: str) -> tuple[str, bool]:
    if CSS_MARK_START in html:
        return html, False

    i = html.find("</style>")
    if i != -1:
        return html[:i] + CSS_BLOCK + "\n" + html[i:], True

    # fallback: lisa </head> ette
    j = html.lower().find("</head>")
    if j == -1:
        return html, False
    return html[:j] + f"<style>\n{CSS_BLOCK}\n</style>\n" + html[j:], True

def inject_js(html: str) -> tuple[str, bool]:
    if JS_MARK_START in html:
        return html, False

    # lisa enne </body>
    j = html.lower().rfind("</body>")
    if j == -1:
        return html, False
    return html[:j] + "\n" + JS_BLOCK + "\n" + html[j:], True

def is_brand_page_index(p: Path) -> bool:
    # ainult kaustade index.html (nt audi/index.html), mitte root index.html
    if p.name != "index.html":
        return False
    if p.resolve() == Path("index.html").resolve():
        return False
    return True

def main():
    root = Path(".")
    changed = 0

    for p in root.rglob("index.html"):
        if not is_brand_page_index(p):
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        new = text
        did_any = False

        new, did_css = inject_css(new)
        did_any = did_any or did_css

        new, did_js = inject_js(new)
        did_any = did_any or did_js

        if did_any and new != text:
            p.write_text(new, encoding="utf-8")
            changed += 1

    print(f"Muudetud tootjalehti: {changed}")

if __name__ == "__main__":
    main()