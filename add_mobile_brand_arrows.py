#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re

MARKER = "/* JOEL: mobile-brand-arrows v1 */"

CSS_SNIP = f"""
<style>
{MARKER}
/* Brauseri back/forward swipe-indikaatorite vältimine desktopis */
@media (hover:hover) and (pointer:fine) {{
  html, body {{
    overscroll-behavior-x: none;
    touch-action: pan-y;
    overflow-x: hidden;
  }}
}}

/* Mobiilis lubame swipe'i (kui sinu lehel on muu swipe) */
@media (hover:none) and (pointer:coarse) {{
  html, body {{
    overscroll-behavior-x: auto;
    touch-action: pan-x pan-y;
  }}
}}

/* Mobiili alumine nav-pill */
.joel-brand-bar {{
  position: fixed;
  left: 50%;
  bottom: max(12px, env(safe-area-inset-bottom));
  transform: translateX(-50%);
  z-index: 9999;
  display: none;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(0,0,0,.35);
  backdrop-filter: blur(6px);
}}

.joel-brand-bar a {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  font-size: 44px;          /* umbes 2x lightbox nooltest */
  line-height: 1;
  color: #fff;
  text-decoration: none;
  user-select: none;
}}

@media (max-width: 800px) {{
  .joel-brand-bar {{ display: flex; }}
}}
</style>
"""

JS_SNIP = r"""
<script>
/* JOEL: mobile-brand-arrows v1 */
(function(){
  if (document.querySelector('.joel-brand-bar')) return;
  if (location.protocol === 'file:') return;

  const bar = document.createElement('nav');
  bar.className = 'joel-brand-bar';
  bar.innerHTML = `
    <a class="jb-prev" href="#" aria-label="Eelmine tootja">‹</a>
    <a class="jb-next" href="#" aria-label="Järgmine tootja">›</a>
  `;
  document.body.appendChild(bar);

  const herePath = location.pathname.replace(/\/index\.html$/,'/').replace(/\/+$/,'/') ;
  const slug = herePath.split('/').filter(Boolean).pop();

  fetch('../mudelid.html', { cache:'no-store' })
    .then(r => r.ok ? r.text() : Promise.reject())
    .then(html => {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const cards = [...doc.querySelectorAll('.brand-card[href]')];

      const list = cards.map(c => {
        const href = c.getAttribute('href') || '';
        // href stiil: audi/index.html  => slug = audi
        const s = href.replace(/\/index\.html$/,'').split('/').filter(Boolean).pop();
        return { href, slug: s };
      }).filter(x => x.slug);

      const i = list.findIndex(x => x.slug === slug);
      if (i < 0 || list.length < 2) { bar.remove(); return; }

      const prev = list[(i - 1 + list.length) % list.length].href;
      const next = list[(i + 1) % list.length].href;

      bar.querySelector('.jb-prev').href = '../' + prev.replace(/^\.\//,'');
      bar.querySelector('.jb-next').href = '../' + next.replace(/^\.\//,'');

      // Kiirklahvid (ainult kui lightbox pole lahti)
      function lbOpen(){
        const lb = document.getElementById('lb-overlay');
        return lb && lb.classList.contains('open');
      }
      window.addEventListener('keydown', (e) => {
        if (lbOpen()) return;
        if (e.key === 'ArrowLeft') location.href = bar.querySelector('.jb-prev').href;
        if (e.key === 'ArrowRight') location.href = bar.querySelector('.jb-next').href;
      });
    })
    .catch(() => { bar.remove(); });
})();
</script>
"""

def should_process(path: Path, root: Path) -> bool:
    if path.suffix.lower() != ".html":
        return False
    # ära puutu juurkausta index.html ja mudelid.html
    if path.parent == root and path.name in ("index.html", "mudelid.html"):
        return False
    # sihime tootjalehti: */index.html
    if path.name != "index.html":
        return False
    return True

def inject_before_close_tag(text: str, snippet: str, close_tag: str) -> tuple[str, bool]:
    low = text.lower()
    idx = low.rfind(close_tag)
    if idx == -1:
        return text, False
    return text[:idx] + snippet + "\n" + text[idx:], True

def main():
    root = Path.cwd()
    changed = 0
    checked = 0

    for f in root.rglob("*.html"):
        if not should_process(f, root):
            continue

        checked += 1
        txt = f.read_text(encoding="utf-8", errors="replace")

        if MARKER in txt:
            # juba olemas
            continue

        # 1) CSS enne </head>
        txt2, ok1 = inject_before_close_tag(txt, CSS_SNIP, "</head>")
        if not ok1:
            continue

        # 2) JS enne </body>
        txt3, ok2 = inject_before_close_tag(txt2, JS_SNIP, "</body>")
        if not ok2:
            continue

        f.write_text(txt3, encoding="utf-8")
        changed += 1
        print(f"✅ Muudetud: {f}")

    print("\n---")
    print(f"Kontrollitud: {checked}")
    print(f"Muudetud:     {changed}")

if __name__ == "__main__":
    main()
