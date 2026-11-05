#!/usr/bin/env python3
"""Regenera os PNGs do tema e os aliases dos logos existentes."""

from pathlib import Path
from shutil import copyfile
import xml.etree.ElementTree as ET

import cairosvg
from cairosvg.parser import Tree
from cairosvg.surface import Surface, cairo


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "_inc/neon"
LOGOS = ASSETS / "logos"


class Bounds(Surface):
    device_units_per_user_units = 1

    def _create_surface(self, width, height):
        return cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None), width, height


def normalize(source, target):
    root = ET.parse(source).getroot()
    if root.get("width") and root.get("height"):
        copyfile(source, target)
        return
    if root.get("viewBox"):
        _, _, width, height = map(float, root.get("viewBox").split())
    else:
        tree = Tree(url=str(source))
        tree.update(width="4096", height="4096", overflow="visible")
        x, y, width, height = Bounds(tree, None, 96).cairo.ink_extents()
        x, y, width, height = x - 1, y - 1, width + 2, height + 2
        root.set("viewBox", f"{x:g} {y:g} {width:g} {height:g}")
    root.set("width", f"{width:g}")
    root.set("height", f"{height:g}")
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)


def main():
    for source in sorted(ASSETS.glob("*.svg")):
        cairosvg.svg2png(url=str(source), write_to=str(source.with_suffix(".png")))

    LOGOS.mkdir(exist_ok=True)
    for source in sorted((ROOT / "_inc/systems/logo-white").rglob("*.svg")):
        normalize(source, LOGOS / source.name)

    aliases = {
        "favorites": "auto-favorites",
        "favourites": "auto-favorites",
        "auto-favourites": "auto-favorites",
        "allgames": "auto-allgames",
        "lastplayed": "auto-lastplayed",
        "ps1": "psx",
        "psone": "psx",
        "gameboy": "gb",
        "gameboycolor": "gbc",
        "gameboyadvance": "gba",
        "nintendo64": "n64",
        "supernintendo": "snes",
        "supernes": "snes",
        "pce": "pcengine",
        "pcenginecd": "pce-cd",
        "lynx": "atarilynx",
    }
    for name, source in aliases.items():
        target = LOGOS / f"{name}.svg"
        copyfile(LOGOS / f"{source}.svg", target)

    print(f"PNGs regenerados; {len(list(LOGOS.glob('*.svg')))} logos disponíveis.")


if __name__ == "__main__":
    main()
