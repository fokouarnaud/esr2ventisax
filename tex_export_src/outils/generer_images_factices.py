"""Génère les images factices du rapport (img/*.png), toutes marquées « IMAGE À REMPLACER ».

Pour remplacer une image : déposer une vraie photo sous le même nom dans img/.
Le script n'écrase pas une image réelle : il ignore tout fichier qui ne porte pas le marqueur
de métadonnée « factice ». Utiliser --force pour tout régénérer.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

IMG = Path(__file__).resolve().parent.parent / "img"
VERT = (46, 125, 50)
VERT_CLAIR = (220, 239, 217)
ORANGE = (230, 81, 0)

# nom de fichier -> (légende, icône simplifiée)
IMAGES = {
    "fig_localisation": ("Plan de localisation du siège", "carte"),
    "fig_facade_chantier": ("Façade principale du bâtiment", "immeuble"),
    "fig_manometre": ("Manomètre", "cadran"),
    "fig_reducteur_pression": ("Réducteur de pression", "vanne"),
    "fig_flexible": ("Flexible de raccordement", "tuyau"),
    "fig_coupe_tube": ("Coupe-tube", "outil"),
    "fig_polyfuseur": ("Polyfuseur", "outil"),
    "fig_reducteur_montage": ("Montage réducteur + manomètre", "vanne"),
    "fig_isolation_pose": ("Pose de l'isolant sur canalisation", "tuyau"),
    "fig_condensats_split": ("Évacuation des condensats d'un split", "split"),
    "fig_epi_chantier": ("EPI portés sur le chantier", "casque"),
    "fig_essai_etancheite": ("Pompe d'épreuve - essai d'étanchéité", "cadran"),
}
LOGOS = {"logo_cfp": "LOGO\nCENTRE DE\nFORMATION", "logo_entreprise": "LOGO\nENTREPRISE"}


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def icon(d: ImageDraw.ImageDraw, kind: str, cx: int, cy: int) -> None:
    c = VERT
    if kind == "cadran":
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=c, width=12)
        d.line((cx, cy, cx + 60, cy - 60), fill=ORANGE, width=10)
        d.rectangle((cx - 20, cy + 110, cx + 20, cy + 170), fill=c)
    elif kind == "vanne":
        d.rectangle((cx - 220, cy - 30, cx + 220, cy + 30), fill=c)
        d.polygon([(cx - 70, cy - 90), (cx + 70, cy - 90), (cx + 40, cy + 90), (cx - 40, cy + 90)], fill=(90, 150, 90))
        d.ellipse((cx - 40, cy - 170, cx + 40, cy - 90), outline=ORANGE, width=10)
    elif kind == "tuyau":
        d.arc((cx - 230, cy - 160, cx + 230, cy + 200), 200, 340, fill=c, width=40)
        d.rectangle((cx - 250, cy + 20, cx - 190, cy + 70), fill=ORANGE)
    elif kind == "outil":
        d.rounded_rectangle((cx - 200, cy - 40, cx + 120, cy + 40), 20, fill=c)
        d.ellipse((cx + 100, cy - 90, cx + 240, cy + 90), outline=ORANGE, width=14)
    elif kind == "immeuble":
        d.rectangle((cx - 120, cy - 180, cx + 120, cy + 180), outline=c, width=10)
        for i in range(5):
            for j in range(3):
                x, y = cx - 90 + j * 70, cy - 150 + i * 65
                d.rectangle((x, y, x + 40, y + 40), fill=(150, 190, 150))
    elif kind == "carte":
        d.line((cx - 260, cy + 60, cx + 260, cy - 40), fill=(170, 170, 170), width=30)
        d.line((cx - 60, cy - 180, cx + 20, cy + 180), fill=(170, 170, 170), width=24)
        d.ellipse((cx - 30, cy - 120, cx + 30, cy - 60), fill=ORANGE)
        d.polygon([(cx - 26, cy - 85), (cx + 26, cy - 85), (cx, cy - 30)], fill=ORANGE)
    elif kind == "split":
        d.rounded_rectangle((cx - 230, cy - 80, cx + 230, cy + 20), 25, outline=c, width=10)
        d.line((cx + 150, cy + 20, cx + 150, cy + 170), fill=(80, 120, 200), width=12)
    elif kind == "casque":
        d.chord((cx - 160, cy - 140, cx + 160, cy + 140), 180, 360, fill=(250, 200, 30))
        d.rectangle((cx - 190, cy - 10, cx + 190, cy + 20), fill=(220, 170, 20))


def make_figure(name: str, legend: str, kind: str) -> Image.Image:
    w, h = 1600, 1000
    im = Image.new("RGB", (w, h), VERT_CLAIR)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line((0, y, w, y), fill=(int(236 - 20 * t), int(245 - 15 * t), int(234 - 25 * t)))
    d.rectangle((20, 20, w - 20, h - 20), outline=VERT, width=8)
    for i in range(-h, w, 60):
        d.line((i, h - 20, i + 60, h - 80), fill=(200, 225, 200), width=2)
    icon(d, kind, w // 2, 380)
    d.rounded_rectangle((300, 640, 1300, 740), 20, fill=ORANGE)
    d.text((w // 2, 690), "IMAGE À REMPLACER", font=font(64), fill="white", anchor="mm")
    d.text((w // 2, 810), legend, font=font(48), fill=(27, 77, 31), anchor="mm")
    d.text((w // 2, 900), f"img/{name}.png", font=font(34), fill=(90, 110, 90), anchor="mm")
    return im


def make_logo(text: str) -> Image.Image:
    im = Image.new("RGB", (600, 600), "white")
    d = ImageDraw.Draw(im)
    d.ellipse((30, 30, 570, 570), fill=VERT_CLAIR, outline=VERT, width=18)
    d.multiline_text((300, 300), text, font=font(60), fill=VERT, anchor="mm", align="center", spacing=10)
    return im


def is_placeholder(path: Path) -> bool:
    try:
        with Image.open(path) as im:
            return im.info.get("factice") == "oui"
    except OSError:
        return False


def save(im: Image.Image, path: Path, force: bool) -> str:
    if path.exists() and not force and not is_placeholder(path):
        return f"conservée (image réelle) : {path.name}"
    meta = PngInfo()
    meta.add_text("factice", "oui")
    im.save(path, pnginfo=meta)
    return f"générée : {path.name}"


def main() -> int:
    force = "--force" in sys.argv
    IMG.mkdir(exist_ok=True)
    for name, (legend, kind) in IMAGES.items():
        print(save(make_figure(name, legend, kind), IMG / f"{name}.png", force))
    for name, text in LOGOS.items():
        print(save(make_logo(text), IMG / f"{name}.png", force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
