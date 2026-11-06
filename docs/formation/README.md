# Formation de l'apprenant : une fiche par journée de stage

Supports imprimables (PDF A4) pour un apprenant dont le stage a lieu **uniquement le samedi**. Chaque fiche dit
quoi faire avant de partir, sur place et le soir dans le Carnet de stage, puis propose des exercices de
simulation sur le compte de démonstration.

| Journée | Date | Fiche | Contenu |
|---|---|---|---|
| Samedi 1 | 7 novembre 2026 | [samedi-01.pdf](samedi-01.pdf) | Créer le stage, régler les jours travaillés sur `[5]`, premières notes, questions à poser, soirée de complétion, sauvegarde ; 5 exercices et une réécriture de notes |
| Samedi 2 | 14 novembre 2026 | [samedi-02.pdf](samedi-02.pdf) | Relire et préparer ses questions, compléter la couverture ; recueillir matériel, mesures et planning ; le soir : Équipements, Références puis Données techniques, Tâches, Mission, Abréviations ; 5 exercices dont deux refus volontaires et un classement de chiffres |
| Samedi 3 | 21 novembre 2026 | à venir | |

## Régénérer les PDF

```bash
python docs/formation/generer_pdf.py            # toutes les fiches samedi-*.html
python docs/formation/generer_pdf.py samedi-01  # une seule
```

Python système avec Playwright (Chromium) et Pillow. Le script recadre les captures du manuel
(`docs/manuel/img/`), ajoute les espaces insécables de la typographie française, refuse les tirets longs et les
images manquantes, puis imprime le HTML en A4 avec la police Lexend du projet.

Mise en forme : `formation.css` (charte du Carnet, thème clair unique pour l'impression). Les captures de
`img/` (onglet Suivi, refus d'une valeur sans source, formulaire d'équipement) viennent du compte de démonstration
(données fictives) ; les versions recadrées sont régénérées par le script.
