r"""Étape 3 de la procédure (AGENTS.md) pour la démo : remplace les \AC{} des parties par le texte du stage fictif.

Pour un stage réel, cette rédaction est faite par Claude Code à partir de donnees_terrain/terrain.md.
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from carnet.demo.donnees import REDACTION

CHAMP = re.compile(r"\\AC\{([^{}]*)\}")


class Command(BaseCommand):
    help = r"Rédige les \AC{} des parties d'un rapport importé à partir du stage de démonstration."

    def add_arguments(self, parser):
        parser.add_argument("dossier", help="rapports/<slug>-<uuid8>/")

    def handle(self, *args, **opts):
        inconnus, total = [], 0
        for fichier in sorted(Path(opts["dossier"], "parties").glob("*.tex")):
            texte = fichier.read_text(encoding="utf-8")

            def remplacer(m):
                nonlocal total
                contexte = m.group(1) + "}" + m.string[m.end():m.end() + 60]
                for debut, valeur in REDACTION.items():
                    if contexte.startswith(debut):
                        total += 1
                        return valeur
                inconnus.append(f"{fichier.name} : {m.group(1)[:50]}")
                return m.group(0)

            fichier.write_text(CHAMP.sub(remplacer, texte), encoding="utf-8")
        if inconnus:
            raise CommandError("Champs à compléter sans texte de démo : " + " ; ".join(inconnus))
        self.stdout.write(self.style.SUCCESS(f"{total} champs rédigés."))
