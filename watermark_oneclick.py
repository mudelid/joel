#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# ---- SEADED (sama mis sul bashis) ----
WMARK = Path("/Users/joel/Desktop/kollektsioon/img/logo3.png")
SRC   = Path("/Users/joel/Desktop/kollektsioon/laadimata")
OUT   = SRC / "wm_out"

# ---- Filtrid ----
EXTS = {".jpg", ".jpeg", ".png"}

def have_magick() -> bool:
    try:
        subprocess.run(["magick", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def main():
    if not WMARK.exists():
        print(f"❌ Logo ei leitud: {WMARK}")
        sys.exit(1)

    if not SRC.exists():
        print(f"❌ Allika kaust ei leitud: {SRC}")
        sys.exit(1)

    if not have_magick():
        print("❌ ImageMagick 'magick' käsku ei leitud.")
        print("Paigalda näiteks: brew install imagemagick")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    files = [p for p in SRC.iterdir() if p.is_file() and p.suffix.lower() in EXTS]
    if not files:
        print(f"⚠️ Pilte ei leitud kaustast: {SRC}")
        sys.exit(0)

    ok = 0
    fail = 0

    for f in sorted(files):
        out_file = OUT / (f.stem + ".jpg")

        cmd = [
            "magick",
            str(f),
            "(",
            str(WMARK),
            "-resize", "50%",
            ")",
            "-gravity", "northeast",
            "-geometry", "+15+15",
            "-composite",
            str(out_file),
        ]

        try:
            subprocess.run(cmd, check=True)
            ok += 1
        except subprocess.CalledProcessError:
            fail += 1
            print(f"❌ Fail: {f.name}")

    print(f"✅ Valmis. Õnnestus: {ok}, ebaõnnestus: {fail}")
    print(f"📁 Kaust: {OUT}")

if __name__ == "__main__":
    main()