"""Illustrations et logos du jeu de démonstration, dessinés avec Pillow (aucune photo réelle, aucun réseau)."""

import io
import math

from PIL import Image, ImageDraw, ImageFont

MARINE = (11, 45, 70)
TURQUOISE = (104, 221, 206)
TURQUOISE_ENCRE = (13, 102, 94)
MUR = (233, 239, 241)
SOL = (201, 214, 220)
PPR = (46, 125, 50)
LAITON = (201, 162, 39)
INOX = (168, 178, 186)
NOIR = (35, 40, 45)
BLANC = (252, 254, 254)
ORANGE = (230, 120, 20)
LARGEUR, HAUTEUR = 1600, 1200


def police(taille):
    for nom in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(nom, taille)
        except OSError:
            continue
    return ImageFont.load_default(size=taille)


def _fond(d):
    for y in range(HAUTEUR):  # mur dégradé puis sol
        t = y / HAUTEUR
        couleur = MUR if y < 860 else SOL
        d.line((0, y, LARGEUR, y), fill=tuple(int(c - 18 * t) for c in couleur))


def _tube(d, x1, y1, x2, y2, couleur=PPR, epaisseur=56):
    d.line((x1, y1, x2, y2), fill=couleur, width=epaisseur)
    d.line((x1, y1 - epaisseur // 4, x2, y2 - epaisseur // 4), fill=tuple(min(255, c + 45) for c in couleur), width=8)


def _collier(d, x, y):
    d.rectangle((x - 18, y - 46, x + 18, y + 46), fill=INOX, outline=NOIR, width=3)
    d.rectangle((x - 8, y - 120, x + 8, y - 46), fill=INOX)


def _cadran(d, cx, cy, r):
    d.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=INOX, outline=NOIR, width=4)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLANC)
    for i in range(11):
        a = math.radians(225 - i * 27)
        d.line((cx + r * 0.78 * math.cos(a), cy - r * 0.78 * math.sin(a),
                cx + r * 0.95 * math.cos(a), cy - r * 0.95 * math.sin(a)), fill=NOIR, width=6)
    a = math.radians(225 - 4.3 * 27)
    d.line((cx, cy, cx + r * 0.75 * math.cos(a), cy - r * 0.75 * math.sin(a)), fill=ORANGE, width=12)
    d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=NOIR)
    d.text((cx, cy + r * 0.45), "bar", fill=NOIR, font=police(int(r * 0.22)), anchor="mm")


def _vanne(d, cx, cy):
    d.rounded_rectangle((cx - 120, cy - 80, cx + 120, cy + 80), 30, fill=LAITON, outline=NOIR, width=4)
    d.rectangle((cx - 30, cy - 200, cx + 30, cy - 80), fill=LAITON, outline=NOIR, width=4)
    d.ellipse((cx - 110, cy - 260, cx + 110, cy - 190), fill=MARINE)
    d.polygon([(cx - 50, cy + 20), (cx + 40, cy + 20), (cx + 40, cy - 5), (cx + 90, cy + 30),
               (cx + 40, cy + 65), (cx + 40, cy + 40), (cx - 50, cy + 40)], fill=NOIR)


def _immeuble(d):
    d.rectangle((0, 0, LARGEUR, 900), fill=(190, 225, 240))
    d.rectangle((420, 90, 1180, 900), fill=(236, 232, 222), outline=MARINE, width=6)
    for etage in range(11):
        y = 830 - etage * 68
        for col in range(7):
            x = 460 + col * 102
            d.rectangle((x, y - 44, x + 62, y), fill=(120, 170, 200), outline=MARINE, width=2)
    d.rectangle((740, 820, 860, 900), fill=MARINE)
    d.rectangle((0, 900, LARGEUR, HAUTEUR), fill=(150, 150, 140))
    d.text((800, 60), "R+10", fill=MARINE, font=police(56), anchor="mm")


def _scene(sujet, d):
    if sujet == "immeuble":
        _immeuble(d)
        return
    _fond(d)
    if sujet in ("cadran", "manometre"):
        _tube(d, 0, 700, LARGEUR, 700)
        d.rectangle((775, 520, 825, 700), fill=LAITON, outline=NOIR, width=3)
        _cadran(d, 800, 380, 210)
    elif sujet == "vanne":
        _tube(d, 0, 640, LARGEUR, 640)
        _vanne(d, 800, 640)
        _cadran(d, 1220, 360, 130)
        d.rectangle((1205, 500, 1235, 640), fill=LAITON)
        for x in (250, 1450):
            _collier(d, x, 640)
    elif sujet == "tuyau":
        for i, couleur in enumerate((PPR, (200, 40, 40))):
            y = 420 + i * 260
            _tube(d, 0, y, LARGEUR, y, couleur)
            for x in (300, 800, 1300):
                _collier(d, x, y)
    elif sujet == "flexible":
        d.rounded_rectangle((420, 200, 1180, 420), 60, fill=BLANC, outline=INOX, width=6)
        d.arc((560, 380, 1040, 980), 200, 340, fill=INOX, width=34)
        d.rectangle((520, 860, 640, 920), fill=LAITON)
        d.rectangle((960, 860, 1080, 920), fill=LAITON)
    elif sujet == "outil":
        _tube(d, 150, 760, 1450, 760, PPR, 70)
        d.rounded_rectangle((520, 420, 1080, 560), 40, fill=ORANGE, outline=NOIR, width=4)
        d.polygon([(760, 560), (840, 560), (820, 720), (780, 720)], fill=INOX, outline=NOIR)
        d.rounded_rectangle((1080, 450, 1400, 530), 30, fill=NOIR)
    elif sujet == "polyfuseur":
        d.rounded_rectangle((300, 380, 1000, 640), 40, fill=INOX, outline=NOIR, width=5)
        for i, r in enumerate((60, 80, 100)):
            d.ellipse((420 + i * 200 - r // 2, 510 - r // 2, 420 + i * 200 + r // 2, 510 + r // 2), fill=NOIR)
        d.rounded_rectangle((1000, 470, 1450, 560), 40, fill=TURQUOISE_ENCRE)
        d.text((650, 330), "260 °C", fill=ORANGE, font=police(64), anchor="mm")
    elif sujet == "isolation":
        _tube(d, 0, 600, 700, 600, (200, 40, 40), 70)
        d.rounded_rectangle((640, 520, LARGEUR, 680), 70, fill=NOIR)
        d.line((700, 560, LARGEUR, 560), fill=(80, 85, 90), width=6)
    elif sujet == "split":
        d.rounded_rectangle((300, 180, 1300, 460), 50, fill=BLANC, outline=INOX, width=6)
        d.line((380, 400, 1220, 400), fill=INOX, width=10)
        d.line((1180, 460, 1180, 1000), fill=(110, 150, 210), width=26)
        d.line((1240, 460, 1240, 1000), fill=NOIR, width=34)
    elif sujet == "casque":
        d.chord((450, 260, 1150, 900), 180, 360, fill=(250, 200, 30), outline=NOIR, width=5)
        d.rectangle((400, 560, 1200, 610), fill=(220, 170, 20), outline=NOIR, width=4)
        d.rounded_rectangle((300, 800, 620, 1000), 60, fill=ORANGE)
        d.rounded_rectangle((980, 800, 1300, 1000), 60, fill=ORANGE)
    elif sujet == "document":
        d.rectangle((480, 120, 1120, 1000), fill=BLANC, outline=INOX, width=6)
        d.text((800, 200), "BON DE LIVRAISON", fill=MARINE, font=police(44), anchor="mm")
        for i in range(10):
            d.line((540, 300 + i * 60, 1060, 300 + i * 60), fill=SOL, width=6)


def illustration(sujet, legende):
    """JPEG 1600 × 1200 : une scène simple et un bandeau « Photo de démonstration »."""
    image = Image.new("RGB", (LARGEUR, HAUTEUR), MUR)
    d = ImageDraw.Draw(image)
    _scene(sujet, d)
    d.rectangle((0, HAUTEUR - 120, LARGEUR, HAUTEUR), fill=MARINE)
    d.text((40, HAUTEUR - 60), "PHOTO DE DÉMONSTRATION", fill=TURQUOISE, font=police(38), anchor="lm")
    d.text((LARGEUR - 40, HAUTEUR - 60), legende[:60], fill=BLANC, font=police(32), anchor="rm")
    tampon = io.BytesIO()
    image.save(tampon, "JPEG", quality=85)
    return tampon.getvalue()


def logo(sigle, sous_titre, fond=MARINE, accent=TURQUOISE):
    """Logo carré PNG : pastille, sigle et mention, clairement fictif."""
    cote = 600
    image = Image.new("RGBA", (cote, cote), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    d.ellipse((20, 20, cote - 20, cote - 20), fill=fond)
    d.arc((70, 70, cote - 70, cote - 70), 200, 340, fill=accent, width=22)
    d.text((cote // 2, cote // 2 - 10), sigle, fill=BLANC, font=police(130 if len(sigle) <= 3 else 92), anchor="mm")
    d.text((cote // 2, cote // 2 + 110), sous_titre, fill=accent, font=police(40), anchor="mm")
    tampon = io.BytesIO()
    image.save(tampon, "PNG")
    return tampon.getvalue()
