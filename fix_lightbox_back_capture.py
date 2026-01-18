#!/usr/bin/env python3
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SNIPPET_MARK = "/* JOEL-HILJUTI-BACK-OVERRIDE */"

SNIPPET = f"""
<script>
{SNIPPET_MARK}
(function(){{
  // Püüame kinni klikid lightboxi "← Tagasi" nupul
  const referrer = document.referrer;

  window.addEventListener('click', function(e){{
    const t = e.target;
    if (!t || !t.closest) return;
    const btn = t.closest('#lb-back-recent');
    if (!btn) return;

    // Meie võtame üle – ära lase algsel handleril joosta
    e.preventDefault();
    e.stopPropagation();

    if (referrer && history.length > 1) {{
      history.back();
    }} else {{
      // varuvariant, kui tuldi otse lingiga
      location.href = '../index.html';
    }}
  }}, true); // capture-faasis, enne teisi kuulajaid
}})();
</script>
""".strip() + "\n"


def is_brand_index(path: Path) -> bool:
    """Kas see on automargi alamkausta index.html (mitte juur, mudelid, hiljuti)?"""
    if path.name != "index.html":
        return False

    rel = path.relative_to(ROOT).as_posix()

    # välista juur
    if rel in ("index.html", "mudelid.html", "hiljuti.html"):
        return False

    parts = rel.split("/")
    # ootame kujul "acura/index.html"
    if len(parts) != 2:
        return False

    if parts[0] in ("img", "fonts", "css", "js"):
        return False

    return True


def patch_file(path: Path) -> bool:
    """Lisa override-skript enne </body>, kui:
       - failis on #lb-back-recent
       - ja meie snippetit veel pole.
       Tagastab True, kui muudeti."""
    text = path.read_text(encoding="utf-8")

    # kui pole üldse back-nuppu, pole mõtet midagi lisada
    if "#lb-back-recent" not in text:
        return False

    # kui juba lisatud, ei tee topelt
    if SNIPPET_MARK in text:
        return False

    lower = text.lower()
    idx = lower.rfind("</body>")
    if idx == -1:
        return False  # mingil põhjusel pole </body>

    new_text = text[:idx] + "\n" + SNIPPET + text[idx:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    checked = 0
    modified = 0

    for root, dirs, files in os.walk(ROOT):
        for name in files:
            p = Path(root) / name
            if not is_brand_index(p):
                continue
            checked += 1
            if patch_file(p):
                modified += 1
                print(f"✔ Muutsin: {p.relative_to(ROOT)}")
            else:
                print(f"… Vahele jätsin: {p.relative_to(ROOT)}")

    print()
    print(f"Brand-lehti kontrollitud: {checked}")
    print(f"Brand-lehti muudetud:     {modified}")


if __name__ == "__main__":
    main()
