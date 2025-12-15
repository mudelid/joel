#!/usr/bin/env python3
from pathlib import Path

MARKER_START = "/* === FIX: brand arrows link colors (no purple visited) === */"
MARKER_END   = "/* === /FIX: brand arrows link colors === */"

CSS_BLOCK = f"""
{MARKER_START}
.brand-nav a,
.brand-nav a:visited,
.brand-nav a:hover,
.brand-nav a:active,
.brand-nav a:focus,
.brand-bar a,
.brand-bar a:visited,
.brand-bar a:hover,
.brand-bar a:active,
.brand-bar a:focus,
.brand-nav-mobile a,
.brand-nav-mobile a:visited,
.brand-nav-mobile a:hover,
.brand-nav-mobile a:active,
.brand-nav-mobile a:focus {{
  color: #fff !important;
  text-decoration: none !important;
}}
{MARKER_END}
"""

def should_process(path: Path) -> bool:
    # ainult /<brand>/index.html (st mitte root index.html)
    if path.name != "index.html":
        return False
    if path.parent == path.anchor:  # väga ebatõenäoline
        return False
    if path.parent == Path("."):
        return False
    # välista juurkausta index.html
    if path.resolve() == Path("index.html").resolve():
        return False
    return True

def inject_css(html: str) -> tuple[str, bool]:
    if MARKER_START in html:
        return html, False

    # lisa esimese </style> ette (enamikel su lehtedel on <style> ... </style>)
    i = html.find("</style>")
    if i == -1:
        # fallback: lisa </head> ette eraldi <style>
        j = html.lower().find("</head>")
        if j == -1:
            return html, False
        return html[:j] + f"<style>\n{CSS_BLOCK}\n</style>\n" + html[j:], True

    return html[:i] + CSS_BLOCK + "\n" + html[i:], True

def main():
    root = Path(".")
    changed = 0
    scanned = 0

    for p in root.rglob("index.html"):
        # välista root index.html
        if p.resolve() == Path("index.html").resolve():
            continue
        # välista igasugused build/hidden kaustad soovi korral (siin jätame lihtsaks)

        scanned += 1
        if not should_process(p):
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        new_text, ok = inject_css(text)
        if ok and new_text != text:
            p.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"Skaneeritud index.html faile: {scanned}")
    print(f"Muudetud tootjalehti: {changed}")

if __name__ == "__main__":
    main()