#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(".").resolve()

BACK_BTN_ID = "lb-back-recent"

BACK_CSS = r"""
/* === AUTO: Lightbox back-to-recent button === */
#%s{
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 10001;

  background: rgba(255,255,255,.95);
  border: 2px solid #fff;
  color: #fff;

  /* sama “stiil” nagu su lightboxi nupud, aga tekstiga */
  border-radius: 12px;
  padding: 8px 12px;

  font-family: 'BebasKai', sans-serif;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  user-select: none;

  background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.5);
  backdrop-filter: blur(4px);
}
#%s:hover{
  background: rgba(255,255,255,.25);
}
@media (max-width: 600px){
  #%s{ font-size: 16px; padding: 6px 10px; }
}
""" % (BACK_BTN_ID, BACK_BTN_ID, BACK_BTN_ID)

# Nupp läheb overlay.innerHTML template'i sisse kohe lb-close järel
BACK_BUTTON_HTML = f'    <button id="{BACK_BTN_ID}" aria-label="Tagasi hiljuti lisatud juurde">← Tagasi</button>\n'

# JS handler lisatakse lightboxi IIFE sisse (sama koht, kus btnClose defineeritakse)
BACK_JS = f"""
  const btnBackRecent = overlay.querySelector('#{BACK_BTN_ID}');
  if (btnBackRecent) {{
    btnBackRecent.addEventListener('click', () => {{
      // mine avalehele ja ava “Hiljuti lisatud”
      location.href = '../index.html#recent';
    }});
  }}
"""

# Root index.html: kui hash on #recent, avame “Hiljuti lisatud”
INDEX_HASH_JS = r"""
<script>
document.addEventListener("DOMContentLoaded", () => {
  if (location.hash === "#recent") {
    const btn = document.getElementById("recentToggle");
    if (btn) {
      // kui su nupp on button ja avamine toimub clickiga
      if (btn.getAttribute("aria-expanded") === "false") btn.click();
      // kerime igaks juhuks plokini
      const wrap = document.getElementById("recentWrap");
      if (wrap) wrap.scrollIntoView({behavior:"smooth", block:"start"});
    }
  }
});
</script>
"""


def insert_before_first_style_close(html: str, css: str) -> tuple[str, bool]:
    # kui juba olemas, ära dubleeri
    if f"#{BACK_BTN_ID}" in html:
        return html, False
    m = re.search(r"</style\s*>", html, flags=re.IGNORECASE)
    if not m:
        return html, False
    return html[:m.start()] + css + "\n" + html[m.start():], True


def patch_overlay_template(html: str) -> tuple[str, bool]:
    # kui nupp juba olemas
    if f'id="{BACK_BTN_ID}"' in html:
        return html, False

    # Leia overlay.innerHTML = ` ... `;
    # ja süsti lb-close järel.
    pat = re.compile(r"(overlay\.innerHTML\s*=\s*`)(.*?)(`\s*;)", re.DOTALL)
    m = pat.search(html)
    if not m:
        return html, False

    prefix, body, suffix = m.group(1), m.group(2), m.group(3)
    if 'id="lb-close"' not in body:
        return html, False

    # Pane nupp kohe pärast lb-close rida
    body2, n = re.subn(
        r'(\s*<button[^>]*id="lb-close"[^>]*>.*?</button>\s*\n)',
        r"\1" + BACK_BUTTON_HTML,
        body,
        count=1,
        flags=re.DOTALL
    )
    if n == 0:
        # fallback: pane template algusesse
        body2 = BACK_BUTTON_HTML + body

    new_chunk = prefix + body2 + suffix
    new_html = html[:m.start()] + new_chunk + html[m.end():]
    return new_html, True


def patch_lightbox_js(html: str) -> tuple[str, bool]:
    # kui handler juba olemas
    if "index.html#recent" in html and BACK_BTN_ID in html:
        return html, False

    # Leia koht, kus sul on:
    # const btnClose = overlay.querySelector('#lb-close');
    anchor = re.search(r"(const\s+btnClose\s*=\s*overlay\.querySelector\(\s*['\"]#lb-close['\"]\s*\)\s*;)", html)
    if not anchor:
        return html, False

    insert_at = anchor.end()
    new_html = html[:insert_at] + BACK_JS + html[insert_at:]
    return new_html, True


def patch_brand_page(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="ignore")
    html = original
    changed = False

    html, c1 = insert_before_first_style_close(html, BACK_CSS)
    changed |= c1

    html, c2 = patch_overlay_template(html)
    changed |= c2

    html, c3 = patch_lightbox_js(html)
    changed |= c3

    if changed and html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def patch_root_index(index_path: Path) -> bool:
    if not index_path.exists():
        return False
    original = index_path.read_text(encoding="utf-8", errors="ignore")
    # kui juba sees, ära lisa
    if 'location.hash === "#recent"' in original and "recentToggle" in original:
        return False

    m = re.search(r"</body\s*>", original, flags=re.IGNORECASE)
    if not m:
        return False

    new_html = original[:m.start()] + INDEX_HASH_JS + "\n" + original[m.start():]
    if new_html != original:
        index_path.write_text(new_html, encoding="utf-8")
        return True
    return False


def main():
    modified = 0
    checked = 0

    # tootjalehed: kõik alamkaustade index.html (mitte repo root index.html)
    for p in ROOT.rglob("index.html"):
        rel = p.relative_to(ROOT)
        if rel.parts == ("index.html",):  # root index.html
            continue
        # ignore hidden folders
        if any(part.startswith(".") for part in rel.parts):
            continue

        checked += 1
        if patch_brand_page(p):
            modified += 1

    # patch root index.html (#recent auto-open)
    root_index = ROOT / "index.html"
    idx_changed = patch_root_index(root_index)

    print(f"Brand pages checked: {checked}")
    print(f"Brand pages modified: {modified}")
    print(f"Root index.html modified: {'YES' if idx_changed else 'NO'}")
    print("Done.")


if __name__ == "__main__":
    main()