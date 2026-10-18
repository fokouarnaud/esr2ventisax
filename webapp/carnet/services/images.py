"""Compression des photos (A5) en conservant l'EXIF (A22), lecture du GPS et de la date de prise de vue."""

import datetime
import io
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

COTE_MAX_PX = 1600
QUALITE_JPEG = 82
IFD_GPS = 0x8825
IFD_EXIF = 0x8769
TAG_ORIENTATION = 0x0112
TAG_DATE_ORIGINALE = 0x9003
TAG_DATE = 0x0132


@dataclass
class ImageTraitee:
    contenu: bytes
    latitude: float | None
    longitude: float | None
    prise_le: datetime.datetime | None


def _degres(dms, reference):
    d, m, s = (float(x) for x in dms)
    valeur = d + m / 60 + s / 3600
    return -valeur if reference in ("S", "W") else valeur


def _gps(exif):
    gps = exif.get_ifd(IFD_GPS)
    try:
        return _degres(gps[2], gps.get(1, "N")), _degres(gps[4], gps.get(3, "E"))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None, None


def _date(exif):
    brute = exif.get_ifd(IFD_EXIF).get(TAG_DATE_ORIGINALE) or exif.get(TAG_DATE)
    try:
        naive = datetime.datetime.strptime(str(brute).strip("\x00"), "%Y:%m:%d %H:%M:%S")
    except (TypeError, ValueError):
        return None
    return timezone.make_aware(naive)


def traiter_image(fichier):
    try:
        image = Image.open(fichier)
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("Ce fichier n'est pas une image lisible.") from exc

    exif = image.getexif()
    latitude, longitude = _gps(exif)
    prise_le = _date(exif)

    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((COTE_MAX_PX, COTE_MAX_PX))
    exif.pop(TAG_ORIENTATION, None)  # l'orientation est déjà appliquée aux pixels

    tampon = io.BytesIO()
    image.save(tampon, "JPEG", quality=QUALITE_JPEG, optimize=True, exif=exif.tobytes())
    return ImageTraitee(tampon.getvalue(), latitude, longitude, prise_le)
