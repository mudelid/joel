# increase_lb_caption_font.py
from pathlib import Path

ROOT = Path.home() / "Desktop" / "kollektsioon"
PATCH_MARK = "/* PATCH: larger #lb-cap font-size */"

CSS_PATCH = f"""
{PATCH_MARK}
/* Suurem lightboxi pealdis */
#lb-cap {{
  font-size: 30px !important;
}}
@media (max-width:600px) {{
  #lb-cap {{
    font-size: 20px !important;
  }}
}}
""".strip()

def insert_before_last_style_close(html: str, css: str) -> str:
    lower = html.lower()
    i = lower.rfind("</style>")
    if i != -1:
        return html[:i] + "\n" + css + "\n" + html[i:]
    j = lower.rfind("</head>")
    if j != -1:
        return html[:j] + f"\n<style>\n{css}\n</style>\n" + html[j:]
    return f"<style>\n{css}\n</style>\n" + html

def process_file(p: Path) -> bool:
    html = p.read_text(encoding="utf-8", errors="ignore")

    if "#lb-cap" not in html:
        return False
    if PATCH_MARK in html:
        return False

    new_html = insert_before_last_style_close(html, CSS_PATCH)
    if new_html != html:
        p.write_text(new_html, encoding="utf-8")
        return True
    return False

def main():
    changed = 0
    for sub in ROOT.iterdir():
        if not sub.is_dir():
            continue
        f = sub / "index.html"
        if f.exists():
            if process_file(f):
                changed += 1
                print("✅ Muudetud:", f.relative_to(ROOT))
            else:
                print("➡️  Vahele jäetud:", f.relative_to(ROOT))
    print(f"\nKokku muudetud faile: {changed}")

if __name__ == "__main__":
    main()
