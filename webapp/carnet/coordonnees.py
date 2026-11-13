"""Coordonnées GPS avec leur hémisphère : N/S pour la latitude, E/O pour la longitude.

En base, la valeur reste signée (sud et ouest négatifs). À l'écran, on saisit la valeur sans signe et on choisit
l'hémisphère dans une liste ; à l'affichage, l'hémisphère est écrit en toutes lettres (« 4,02550° N »).
"""

from django import forms
from django.core.exceptions import ValidationError
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

AIDE = {
    "latitude": "Distance à l'équateur en degrés décimaux, puis Nord ou Sud. "
                "Au Cameroun, toujours Nord (Douala ≈ 4,05° N).",
    "longitude": "Distance au méridien de Greenwich en degrés décimaux, puis Est ou Ouest. "
                 "Au Cameroun, toujours Est (Douala ≈ 9,70° E).",
}
AIDE_POSITION = (
    "Comment obtenir la position : sur place, touchez « Utiliser ma position » (le téléphone demande "
    "l'autorisation de localisation). À distance, ouvrez OpenStreetMap ou Google Maps, faites un clic droit "
    "(appui long sur téléphone) sur le lieu et copiez les deux nombres affichés, par exemple « 4.0496, 9.6942 » : "
    "collez-les dans la latitude, les deux champs se remplissent. Le premier nombre est la latitude, le second la "
    "longitude ; un nombre négatif signifie Sud ou Ouest."
)
AXES = {
    # axe : (maximum, hémisphère positif, hémisphère négatif)
    "latitude": (90, ("N", "Nord"), ("S", "Sud")),
    "longitude": (180, ("E", "Est"), ("O", "Ouest")),
}


def _hemisphere(valeur, axe):
    _, positif, negatif = AXES[axe]
    return (positif if valeur >= 0 else negatif)[0]


def formater_coordonnee(valeur, axe):
    if valeur is None:
        return ""
    return f"{abs(valeur):.5f}".replace(".", ",") + f"° {_hemisphere(valeur, axe)}"


def formater_position(latitude, longitude):
    """« 4,02550° N ; 9,69410° E », ou chaîne vide si la position manque."""
    if latitude is None or longitude is None:
        return ""
    return f"{formater_coordonnee(latitude, 'latitude')} ; {formater_coordonnee(longitude, 'longitude')}"


class SaisieCoordonnee(forms.MultiWidget):
    template_name = "carnet/widgets/coordonnee.html"

    class Media:
        js = ["carnet/js/coordonnees.js"]

    def __init__(self, axe, attrs=None):
        self.axe = axe
        _, positif, negatif = AXES[axe]
        valeur = UnfoldAdminTextInputWidget(attrs={"inputmode": "decimal", "placeholder": "0,00000",
                                                   "aria-label": f"{axe} en degrés"})
        sens = UnfoldAdminSelectWidget(choices=[positif, negatif], attrs={"aria-label": f"hémisphère ({axe})"})
        super().__init__([valeur, sens], attrs)

    def get_context(self, name, value, attrs):
        contexte = super().get_context(name, value, attrs)
        contexte["widget"]["axe"] = self.axe
        return contexte

    def decompress(self, value):
        if value in (None, ""):
            return [None, AXES[self.axe][1][0]]
        return [str(abs(float(value))).replace(".", ","), _hemisphere(float(value), self.axe)]


class ChampCoordonnee(forms.MultiValueField):
    """Valeur sans signe + hémisphère → nombre signé (sud et ouest négatifs)."""

    def __init__(self, axe, *, required=True, **kwargs):
        self.axe = axe
        maximum, positif, negatif = AXES[axe]
        kwargs.pop("max_length", None)
        kwargs.setdefault("help_text", AIDE[axe])
        champs = (
            forms.FloatField(required=False, min_value=0, max_value=maximum, localize=True, error_messages={
                "min_value": "Saisir la valeur sans signe moins, puis choisir l'hémisphère.",
                "max_value": f"La {axe} ne dépasse pas {maximum}°.",
            }),
            forms.ChoiceField(required=False, choices=[positif, negatif]),
        )
        super().__init__(champs, required=required, require_all_fields=False,
                         widget=SaisieCoordonnee(axe), **kwargs)

    def compress(self, data_list):
        if not data_list or data_list[0] in (None, ""):
            if self.required:
                raise ValidationError(self.error_messages["required"], code="required")
            return None
        valeur, sens = data_list
        if not sens:
            raise ValidationError("Choisir l'hémisphère.", code="hemisphere")
        return -valeur if sens == AXES[self.axe][2][0] else valeur
