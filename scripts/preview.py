#!/usr/bin/env python3
"""Prévia ilustrativa com os assets e as posições do XML; não emula o console."""

from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
THEME = ET.parse(ROOT / "theme.xml").getroot()
VARS = {v.tag: v.text for v in THEME.find("variables")}
VARS.update({"system.theme": "snes", "system.fullName": "Super Nintendo"})
WIDTH, HEIGHT = 1024, 768
OUT = ROOT / "docs"


def resolve(value):
    for key, replacement in VARS.items():
        value = value.replace("${" + key + "}", replacement)
    return value


def elements(view):
    result = {}
    for node in THEME.findall("view"):
        if view not in node.get("name").split(","):
            continue
        for item in node:
            for name in item.get("name").split(","):
                data = result.setdefault((item.tag, name), {})
                data.update({p.tag: resolve(p.text) for p in item})
                if item.get("extra"):
                    data["extra"] = item.get("extra")
    return result


def pair(value):
    x, y = map(float, value.split())
    return round(x * WIDTH), round(y * HEIGHT)


def font(data):
    return ImageFont.truetype(str(ROOT / data["fontPath"]), round(float(data["fontSize"]) * HEIGHT))


def text(canvas, data, value=None):
    if data.get("visible") == "false":
        return
    value = value if value is not None else data.get("text", "")
    if data.get("forceUppercase") == "true":
        value = value.upper()
    draw, face = ImageDraw.Draw(canvas), font(data)
    x, y = pair(data["pos"])
    width, height = pair(data.get("size", "0 0"))
    left, top, right, bottom = draw.textbbox((0, 0), value, font=face)
    if data.get("alignment") == "center":
        x += (width - (right - left)) / 2
    elif data.get("alignment") == "right":
        x += width - (right - left)
    y += (0 if data.get("verticalAlignment") == "top" else max(0, (height - (bottom - top)) / 2)) - top
    draw.text((x, y), value, font=face, fill="#" + data.get("color", VARS["text"]))


def image(canvas, path, center, bounds, tint=None):
    if path.suffix == ".svg":
        graphic = Image.open(BytesIO(cairosvg.svg2png(url=str(path)))).convert("RGBA")
    else:
        graphic = Image.open(path).convert("RGBA")
    scale = min(bounds[0] / graphic.width, bounds[1] / graphic.height)
    graphic = graphic.resize((round(graphic.width * scale), round(graphic.height * scale)), Image.Resampling.LANCZOS)
    if tint:
        colored = Image.new("RGBA", graphic.size, "#" + tint)
        colored.putalpha(graphic.getchannel("A"))
        graphic = colored
    canvas.paste(graphic, (round(center[0] - graphic.width / 2), round(center[1] - graphic.height / 2)), graphic)


def screen(view):
    items = elements(view)
    canvas = Image.open(ROOT / items["image", "background"]["path"]).convert("RGB")
    for (kind, name), data in items.items():
        if kind == "text" and data.get("extra"):
            text(canvas, data)
    status = elements("screen")
    text(canvas, status["text", "clock"], "20:45")
    battery = status["batteryIndicator", "batteryIndicator"]
    bx, by = pair(battery["pos"])
    image(canvas, ROOT / battery["full"], (bx + 35, by + 13), (46, 24), VARS["accent"])
    helpdata = items["helpsystem", "help"]
    text(canvas, {**helpdata, "color": VARS["text"], "size": "0.9 0.03"},
         "<  >  SISTEMA       A  ENTRAR       START  MENU" if view == "system" else "^  v  JOGO       A  JOGAR       B  VOLTAR       START  MENU")
    if view == "system":
        carousel = items["carousel", "systemcarousel"]
        x, y = pair(carousel["pos"])
        width, height = pair(carousel["size"])
        image(canvas, ROOT / items["image", "logo"]["path"], (x + width / 2, y + height / 2), pair(carousel["logoSize"]), VARS["accent"])
        text(canvas, items["text", "systemInfo"], "128 jogos disponíveis")
    else:
        games = ["Chrono Trigger", "Donkey Kong Country 2", "F-Zero", "Mega Man X", "Super Mario World", "Super Metroid", "Super Castlevania IV", "The Legend of Zelda"]
        data = items["textlist", "gamelist"]
        x, y = pair(data["pos"])
        width, _ = pair(data["size"])
        row = round(float(data["fontSize"]) * HEIGHT * float(data["lineSpacing"]))
        for index, game in enumerate(games):
            selected = game == "Super Metroid"
            if selected:
                ImageDraw.Draw(canvas).rectangle((x, y + index * row, x + width, y + index * row + float(data["selectorHeight"]) * HEIGHT), fill="#" + data["selectorColor"])
            text(canvas, {**data, "pos": f"{(x + 12) / WIDTH} {(y + index * row) / HEIGHT}", "size": f"{width / WIDTH} {float(data['selectorHeight'])}", "color": data["selectedColor" if selected else "primaryColor"]}, game)
        media = items["image", "md_image"]
        image(canvas, ROOT / media["default"], pair(media["pos"]), pair(media["maxSize"]))
        text(canvas, items["text", "md_name"], "Super Metroid")
        description = {**items["text", "md_description"], "verticalAlignment": "top"}
        text(canvas, description, "Explore Zebes com Samus Aran.\nNovos poderes, segredos e uma\naventura em outro planeta.")
    return canvas


def main():
    OUT.mkdir(exist_ok=True)
    combined = Image.new("RGB", (2112, 880), "#10081D")
    face = ImageFont.truetype(str(ROOT / VARS["titleFont"]), 24)
    draw = ImageDraw.Draw(combined)
    for index, (view, label) in enumerate((("system", "SISTEMAS"), ("detailed", "JOGOS"))):
        canvas = screen(view)
        canvas.save(OUT / ("preview-system.png" if index == 0 else "preview-gamelist.png"))
        x = 24 + index * 1040
        draw.text((x, 16), label, font=face, fill="#B6FF43")
        combined.paste(canvas, (x, 56))
    draw.text((24, 842), "Prévia ilustrativa • 1024 × 768 • jogos e indicadores de exemplo", font=face, fill="#A99ABE")
    combined.save(OUT / "preview.png")


if __name__ == "__main__":
    main()
