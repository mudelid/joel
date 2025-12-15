import os

ROOT = os.getcwd()

CSS_FIX = """
/* --- FIX: disable mobile purple swipe arrows --- */
html, body { overflow-x: hidden; }
body { overscroll-behavior-x: none; touch-action: pan-y; }
"""

def is_root_index(path: str) -> bool:
    return os.path.abspath(path) == os.path.abspath(os.path.join(ROOT, "index.html"))

def should_process(path: str) -> bool:
    base = os.path.basename(path).lower()
    if base == "mudelid.html":
        return False
    if base != "index.html":
        return False
    if is_root_index(path):
        return False  # ära puutu avalehte
    return True

def process_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if "overscroll-behavior-x" in html and "touch-action: pan-y" in html:
        return False  # juba olemas

    if "</style>" in html:
        html = html.replace("</style>", CSS_FIX + "\n</style>", 1)
    elif "</head>" in html:
        html = html.replace("</head>", f"<style>{CSS_FIX}</style>\n</head>", 1)
    else:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

changed = 0
scanned = 0

for root, _, files in os.walk(ROOT):
    for file in files:
        if file.lower() not in ("index.html", "mudelid.html"):
            continue
        full = os.path.join(root, file)
        if should_process(full):
            scanned += 1
            if process_file(full):
                changed += 1

print(f"Leitud tootjalehti: {scanned}")
print(f"Muudetud faile: {changed}")