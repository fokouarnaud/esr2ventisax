# Formation de l'apprenant : une fiche par journée de stage

Supports imprimables (PDF A4) pour un apprenant dont le stage a lieu **uniquement le samedi**. Chaque fiche dit
quoi faire avant de partir, sur place et le soir dans le Carnet de stage, puis propose des exercices de
simulation sur le compte de démonstration.

| Journée | Date | Fiche | Contenu |
|---|---|---|---|
| Samedi 1 | 7 novembre 2026 | [samedi-01.pdf](samedi-01.pdf) | Créer le stage, régler les jours travaillés sur `[5]`, premières notes, questions à poser, soirée de complétion, sauvegarde ; 5 exercices et une réécriture de notes |
| Samedi 2 | 14 novembre 2026 | [samedi-02.pdf](samedi-02.pdf) | Relire et préparer ses questions, compléter la couverture ; recueillir matériel, mesures et planning ; le soir : Équipements, Références puis Données techniques, Tâches, Mission, Abréviations ; 5 exercices dont deux refus volontaires et un classement de chiffres |
| Samedi 3 | 21 novembre 2026 | [samedi-03.pdf](samedi-03.pdf) | Choisir le thème, créer les chapitres de la Partie III ; suivre une opération étape par étape, noter pannes et sécurité ; le soir : étiqueter, onglet Intervention, légende et slug ; exercices sur les chapitres, l'étiquetage et le refus d'export, remise en ordre d'un tirage au vide |
| Samedi 4 | 28 novembre 2026 | [samedi-04.pdf](samedi-04.pdf) | Lire `terrain.md` et ses « Rien de saisi », vérifier le nom du formateur sur la couverture ; rattraper un samedi (absence ou note datée) ; avis du tuteur, remarques du formateur à reporter, bilan personnel, critiques et suggestions ; transformer un reproche en constat suivi d'une suggestion |
| Samedi 5 | 5 décembre 2026 | [samedi-05.pdf](samedi-05.pdf) | Choisir le calcul du chapitre technique et lister ses données ; mesurer, lire, situer le siège ; le soir : Références, Données techniques, Lieux, Équipements ; suivre une donnée jusqu'au tableau du rapport, compléter des données incomplètes |
| Samedi 6 | 12 décembre 2026 | [samedi-06.pdf](samedi-06.pdf) | Relire ce qui sera dessiné (organigramme, tâches), photographier les chapitres sans photo ; corps, annexe ou preuve, légendes utiles ; comparer les listes de la démo et les figures du rapport |
| Samedi 7 | 19 décembre 2026 | à venir | |

## Publication

Les fiches sont téléchargeables sur l'accueil public du Carnet (section « Se former, samedi après samedi »,
décision A40). Le script copie chaque PDF et sa couverture dans `webapp/carnet/static/carnet/formation/` ;
une nouvelle fiche s'inscrit ensuite dans `webapp/carnet/formation.py`, puis se déploie (skill `deploy`).

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

Captures : `docs/manuel/capturer_ecrans.py` (manuel) puis `docs/formation/capturer_sources.py` (sources propres aux fiches),
avec `charger_demo` et le serveur local sur le port 8765 ; `generer_pdf.py` les recadre (RECADRAGES). Relancer
`charger_demo` ensuite. Le nombre de pages affiché sur l'accueil est lu dans le PDF publié.
