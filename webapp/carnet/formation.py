"""Fiches de formation publiées sur l'accueil (A40) : une par samedi de stage.

Les PDF et leurs couvertures sont produits par docs/formation/generer_pdf.py, qui les copie dans
static/carnet/formation/. Ajouter une fiche : l'écrire dans docs/formation/, la générer, puis l'inscrire ici.
"""

import datetime
import functools
import re
from dataclasses import dataclass
from pathlib import Path

STATIQUE = Path(__file__).resolve().parent / "static"


@functools.lru_cache(maxsize=None)
def _pages(chemin):
    """Nombre de pages du PDF publié : jamais recopié à la main, donc jamais faux (B18)."""
    return len(re.findall(rb"/Type\s*/Page[^s]", (STATIQUE / chemin).read_bytes()))


@dataclass(frozen=True)
class Fiche:
    numero: int
    date: datetime.date
    titre: str
    resume: str

    @property
    def pdf(self):
        return f"carnet/formation/samedi-{self.numero:02d}.pdf"

    @property
    def pages(self):
        return _pages(self.pdf)

    @property
    def couverture(self):
        return f"carnet/formation/samedi-{self.numero:02d}.webp"


FICHES = [
    Fiche(1, datetime.date(2026, 11, 7), "Premier jour de stage",
          "Créer son compte et son stage, régler les jours travaillés sur le samedi, prendre ses premières notes "
          "et sauvegarder."),
    Fiche(2, datetime.date(2026, 11, 14), "Le matériel et les chiffres",
          "Recueillir outils, mesures et planning, puis ranger chaque chiffre avec sa source."),
    Fiche(3, datetime.date(2026, 11, 21), "Le thème du rapport",
          "Poser les chapitres de la Partie III, suivre une opération de bout en bout, légender les photos."),
    Fiche(4, datetime.date(2026, 11, 28), "Le point à mi-parcours",
          "Relire son dossier terrain, rattraper un samedi manqué, commencer le bilan, les critiques et les suggestions."),
    Fiche(5, datetime.date(2026, 12, 5), "Les données du chapitre technique",
          "Choisir le petit calcul du thème, recueillir ses données mesurées ou sourcées, compléter les lieux."),
    Fiche(6, datetime.date(2026, 12, 12), "Les figures du rapport",
          "Faire valider l'organigramme, dater les tâches du planning, choisir et légender les photos."),
]


def fiche_a_la_une(aujourd_hui):
    """La fiche du prochain samedi (ou du jour même) ; après la dernière publiée, la dernière."""
    return next((f for f in FICHES if f.date >= aujourd_hui), FICHES[-1])
