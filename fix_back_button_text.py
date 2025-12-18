#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(".").resolve()

def is_brand_page(p: Path) -> bool:
    # ainult */index.html, aga mitte root index.html
    if p.name != "index.html":
        return False
    if p.parent.resolve() == ROOT:
        return False
    return True

def process_file(p: Path) -> bool:
    original = p.read_text(encoding="utf-8", errors="ignore")
    html = original

    # Asendame ainult back-nupu TEKSTI
    # jätame href-i puutumata
    html = re.sub(
        r'(<a[^>]*class=["\']back["\'][^>]*>\s*←\s*)TAGASI(\s*</a>)',
        r'\1KÕIK MUDELID\2',
        html,
        flags=re.IGNORECASE
    )

    if html != original:
        p.write_text(html, encoding="utf-8")
        return True
    return False

def main():
    checked = 0
    modified = 0

    for p in ROOT.rglob("index.html"):
        if not is_brand_page(p):
            continue
        checked += 1
        if process_file(p):
            modified += 1

    print(f"Brand pages checked: {checked}")
    print(f"Brand pages modified: {modified}")
    print("Done.")

if __name__ == "__main__":
    main()