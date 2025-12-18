#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(".").resolve()

CSS_MARK_START = "/* === JOEL BRAND PILL v3 START === */"
CSS_MARK_END   = "/* === JOEL BRAND PILL v3 END === */"
JS_MARK_START  = "<!-- === JOEL BRAND PILL v3 START === -->"
JS_MARK_END    = "<!-- === JOEL BRAND PILL v3 END === -->"

CSS_BLOCK = f"""{CSS_MARK_START}
/* Mobiili pill: eelmine + järgmine tootja nimega + keskel eraldusjoon */
.joel-brand-pill {{
  position: fixed;
  left: 50%;
  bottom: max(10px, env(safe-area-inset-bottom));
  transform: translateX(-50%);
  z-index: 9999;

  display: none;
  width: min(92vw, 560px);
  padding: 8px 10px;         /* madalam */
  border-radius: 999px;

  background: rgba(0,0,0,.35);
  border: 1px solid rgba(255,255,255,.40);
  backdrop-filter: blur(6px);

  align-items: stretch;
  gap: 8px;
}}

.joel-brand-pill a {{
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  text-decoration: none !important;
  color: #fff !important;
  min-width: 0;
}}

.joel-brand-pill .left {{ justify-content: flex-start; }}
.joel-brand-pill .right{{ justify-content: flex-end; }}

.joel-brand-pill .arr {{
  font-size: 26px;
  line-height: 1;
  opacity: .95;
  user-select: none;
}}

.joel-brand-pill .name {{
  font-size: 16px;
  line-height: 1.05;
  text-transform: uppercase;
  max-width: 100%;
  min-width: 0;

  /* lubab 2 rida */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}}

.joel-brand-pill .right .name{{ text-align: right; }}
.joel-brand-pill .left  .name{{ text-align: left; }}

/* Keskmine eraldusjoon */
.joel-brand-pill .sep {{
  width: 1px;
  align-self: stretch;
  margin: 2px 2px;
  background: rgba(255,255,255,.45);
  border-radius: 999px;
  flex: 0 0 1px;
}}

/* Näita ainult mobiilis */
@media (max-width: 800px){{
  .joel-brand-pill{{ display: flex; }}
}}
{CSS_MARK_END}
"""

JS_BLOCK = f"""{JS_MARK_START}
<script>
/* === JOEL: mobile brand pill with names (v3) === */
(function(){{
  // ära dubleeri
  const existing = document.querySelector('.joel-brand-pill');
  if (existing) return;
  if (location.protocol === 'file:') return;

  // Korista vanad alumised ribad/elemendid kui kuskil jäänud
  document.querySelectorAll('.joel-brand-bar, .brand-bar, .brand-nav-mobile').forEach(el => el.remove());

  // Loo pill
  const pill = document.createElement('nav');
  pill.className = 'joel-brand-pill';
  pill.innerHTML = `
    <a class="left" href="#" aria-label="Eelmine tootja">
      <span class="arr">‹</span><span class="name">...</span>
    </a>
    <span class="sep" aria-hidden="true"></span>
    <a class="right" href="#" aria-label="Järgmine tootja">
      <span class="name">...</span><span class="arr">›</span>
    </a>
  `;
  document.body.appendChild(pill);

  // Leia praegune slug (kausta nimi)
  const herePath = location.pathname.replace(/\\/index\\.html$/,'/').replace(/\\/+$|^$/,'/');
  const slug = herePath.split('/').filter(Boolean).pop();

  fetch('../mudelid.html', {{ cache:'no-store' }})
    .then(r => r.ok ? r.text() : Promise.reject())
    .then(html => {{
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const cards = [...doc.querySelectorAll('.brand-card[href]')];

      // järjestus = mudelid.html, võtame ka nime
      const list = cards.map(c => {{
        const href = (c.getAttribute('href') || '').trim();
        const name = (c.querySelector('.brand-name')?.textContent || '').trim();
        const s = href.replace(/\\/index\\.html$/,'').split('/').filter(Boolean).pop();
        return {{ href, slug: s, name: name || s }};
      }}).filter(x => x.slug);

      const i = list.findIndex(x => x.slug === slug);
      if (i < 0 || list.length < 2) {{ pill.remove(); return; }}

      const prev = list[(i - 1 + list.length) % list.length];
      const next = list[(i + 1) % list.length];

      const prevA = pill.querySelector('.left');
      const nextA = pill.querySelector('.right');

      prevA.href = '../' + prev.href.replace(/^\\.\\//,'');
      nextA.href = '../' + next.href.replace(/^\\.\\//,'');

      prevA.querySelector('.name').textContent = (prev.name || '').toUpperCase();
      nextA.querySelector('.name').textContent = (next.name || '').toUpperCase();

      // Kui lightbox lahti, peida pill
      function lbOpen(){{
        const lb = document.getElementById('lb-overlay');
        return lb && lb.classList.contains('open');
      }}
      const lb = document.getElementById('lb-overlay');
      if (lb){{
        const obs = new MutationObserver(() => {{
          pill.style.display = lbOpen() ? 'none' : '';
        }});
        obs.observe(lb, {{ attributes:true, attributeFilter:['class'] }});
      }}
    }})
    .catch(() => {{
      pill.remove();
    }});
}})();
</script>
{JS_MARK_END}
"""

def is_brand_page(p: Path) -> bool:
  if p.name != "index.html":
    return False
  # root index.html ära puutu
  if p.parent.resolve() == ROOT:
    return False
  return True

def replace_or_insert_css(html: str) -> str:
  # replace olemasolev v3
  if CSS_MARK_START in html and CSS_MARK_END in html:
    return re.sub(
      rf"(?s){re.escape(CSS_MARK_START)}.*?{re.escape(CSS_MARK_END)}",
      CSS_BLOCK,
      html
    )

  # kui on v2 (joel-brand-pill) ilma markerita, lisame v3 ikka (ja jätame v2 alles)
  # aga et mitte duubeldada, proovime eemaldada vanad joel-brand-pill definitsioonid markeriteta
  # (agressiivselt ainult juhul kui leiame .joel-brand-pill alguse)
  html = re.sub(r"(?s)/\*.*?\*/\s*\.joel-brand-pill\{.*?\}\s*(?=@media|\n\.)", "", html)

  # lisa esimese <style> lõppu
  m = re.search(r"(?is)<style>(.*?)</style>", html)
  if not m:
    return html.replace("</head>", f"<style>\n{CSS_BLOCK}\n</style>\n</head>")
  start, end = m.span(1)
  inner = html[start:end].rstrip() + "\n\n" + CSS_BLOCK + "\n"
  return html[:start] + inner + html[end:]

def replace_or_insert_js(html: str) -> str:
  # replace olemasolev v3
  if JS_MARK_START in html and JS_MARK_END in html:
    return re.sub(
      rf"(?s){re.escape(JS_MARK_START)}.*?{re.escape(JS_MARK_END)}",
      JS_BLOCK,
      html
    )

  # eemalda vana v1/v2 mobile bar/pill skriptid kui leidub
  html = re.sub(r"(?is)<script>\s*/\*\s*JOEL:\s*mobile-brand-arrows.*?</script>", "", html)
  html = re.sub(r"(?is)<script>.*?joel-brand-bar.*?</script>", "", html)

  # lisa enne </body>
  if "</body>" in html:
    return html.replace("</body>", JS_BLOCK + "\n</body>")
  return html + "\n" + JS_BLOCK

def process_file(p: Path) -> bool:
  original = p.read_text(encoding="utf-8", errors="ignore")
  html = original

  # lisa/uuenda CSS+JS
  html = replace_or_insert_css(html)
  html = replace_or_insert_js(html)

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
