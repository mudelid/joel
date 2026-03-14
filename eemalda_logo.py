from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

# leiab <img class="logo" ...>
pattern = re.compile(
    r'<a[^>]*>\s*<img[^>]*class=["\']logo["\'][^>]*>\s*</a>',
    re.IGNORECASE
)

checked = 0
changed = 0

for file in ROOT.rglob("*"):
    if file.suffix.lower() not in {".html", ".htm"}:
        continue

    checked += 1

    text = file.read_text(encoding="utf-8")
    new_text, n = pattern.subn("", text)

    if n > 0:
        file.write_text(new_text, encoding="utf-8")
        changed += 1
        print("Logo eemaldatud:", file.relative_to(ROOT))

print()
print("Kontrollitud faile:", checked)
print("Muudetud faile:", changed)
print("Valmis.")