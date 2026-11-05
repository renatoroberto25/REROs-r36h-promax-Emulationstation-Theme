#!/usr/bin/env python3
"""Empacota apenas os arquivos usados pelo console."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "dist/RENATO-THEME.zip"
files = [ROOT / name for name in ("theme.xml", "splash.xml", "README.md", "docs/preview.png")]
files += list((ROOT / "_inc/neon").rglob("*.png"))
files += list((ROOT / "_inc/neon/logos").glob("*.svg"))
files += [ROOT / "_inc/fonts" / name for name in (
    "Rajdhani-Bold.ttf", "Rajdhani-OFL.txt", "Cabin-Bold.ttf", "Cabin-OFL.txt",
)]
files += [ROOT / "_inc/sounds/select_shorter.wav", ROOT / "_inc/images/wifi.svg"]
files += list((ROOT / "_inc/images/battery").glob("*.svg"))
target.parent.mkdir(exist_ok=True)
with ZipFile(target, "w", ZIP_DEFLATED) as archive:
    for file in sorted(files):
        archive.write(file, Path("RENATO-THEME") / file.relative_to(ROOT))
print(f"{target.relative_to(ROOT)}: {target.stat().st_size // 1024} KiB")
