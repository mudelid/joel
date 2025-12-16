#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

MARKER = "/* JOEL: swipe-fix (desktop no browser arrows, mobile ok) */"

CSS_BLOCK = f"""
{MARKER}
/* --- DESKTOP: keela browser swipe / (lillad nooled) --- */
@media (hover:hover) and (pointer:fine) {{
  html, body {{
    overscroll-behavior-x: none;
    touch-action: pan-y;
  }}
}}

/* --- MOBIIL: luba swipe --- */
@media (hover:none) and (pointer:coarse) {{
  html, body {{
    overscroll-behavior-x: auto;
    touch-action: pan-x pan-y;
  }}
}}
"""

def should_process(path: Path, root: Path) -> bool:
    # ainult .html
    if path.suffix.lower() != ".html":
        return False

    # ära puutu juurkausta index.html ja mudelid.html
    if path.parent == root and path.name in ("index.html", "mudelid.html"):
        return False

    # eesmärk: tootjalehtede index.html (nt audi/index.html)
    # Kui tahad ka muid html-e töödelda, võid selle if-i ära võtta.
    if path.name != "index.html":
        return False

    # välista juurkausta index.html (igaks juhuks)
    if path.resolve() == (root / "index.html").resolve():
        return False

    return True

def inject_css(html: str) -> tuple[str, bool]:
    if MARKER in html:
        return html, False  # juba olemas

    lower = html.lower()

    # 1) proovi lisada olemasolevasse esimesse <style>...</style> plokki
    style_open = lower.find("<style")
    if style_open != -1:
        style_tag_end = lower.find(">", style_open)
        if style_tag_end != -1:
            style_close = lower.find("</style>", style_tag_end)
            if style_close != -1:
                new_html = html[:style_close] + CSS_BLOCK + "\n" + html[style_close:]
                return new_html, True

    # 2) kui <style> puudub, tee uus enne </head>
    head_close = lower.find("</head>")
    if head_close != -1:
        insert = "\n<style>\n" + CSS_BLOCK + "\n</style>\n"
        new_html = html[:head_close] + insert + html[head_close:]
        return new_html, True

    return html, False

def main():
    root = Path.cwd()
    changed = 0
    checked = 0

    for path in root.rglob("*.html"):
        if not should_process(path, root):
            continue

        checked += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # fallback kui mõni fail pole utf-8
            text = path.read_text(encoding="utf-8", errors="replace")

        new_text, did = inject_css(text)
        if did:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
            print(f"✅ Muudetud: {path}")
        else:
            print(f"— Vahele jäetud (juba olemas): {path}")

    print("\n---")
    print(f"Kontrollitud: {checked} faili")
    print(f"Muudetud:     {changed} faili")

if __name__ == "__main__":
    main()
