# CLAUDE.md

Les consignes du projet sont dans AGENTS.md, partagé avec les autres agents. On y trouve :

- la structure et les conventions du rapport LaTeX ;
- la section **GOALS** de l'application « Carnet de stage » (`webapp/`) : objectifs prioritaires,
  contraintes techniques et hors périmètre ;
- le **PRD** de l'application : user stories US-01 à US-31, modèle logique des données, contrat d'export
  et Definition of Done ;
- les journaux des décisions : **Q1–Q16** pour le rapport, **A1–A38** pour l'application.

Avant toute tâche sur `webapp/` :
- relire GOALS et le PRD ;
- refuser ce qui relève du hors périmètre sans validation explicite de l'utilisateur ;
- ne déclarer une story terminée que si **tous** les critères de la Definition of Done (P5) sont remplis.

## Quand l'utilisateur fournit un zip « dossier terrain »

**Utiliser le skill global `rapport-dossier-terrain`**, qui enchaîne tout (scripts `preparer.ps1`, rédaction,
`finaliser.ps1`). La procédure complète, pas à pas, est dans le README (« Après le téléchargement du zip ») et dans AGENTS.md
(US-30). En résumé :

1. Importer : `webapp/.venv/Scripts/python webapp/manage.py importer_dossier <zip>` → `rapports/<slug>-<uuid8>/`.
   Ne jamais utiliser `--force` sur un dossier déjà rédigé sans l'accord de l'utilisateur : il écrase les textes.
2. Contrôler : `latexmk -pdf donnees_terrain/catalogue.tex` depuis la racine du rapport.
3. Rédiger dans `rapports/<dossier>/parties/` **uniquement à partir de `donnees_terrain/terrain.md`** :
   synthèse selon le plan du cours, jamais de récit au jour le jour ; chiffres de « Données techniques » avec leur
   `\cite{}` ; personnes par leur fonction si le nom n'est pas publiable ; photos, tableaux et plans du catalogue
   insérés là où ils servent ; rien d'inventé, ce qui manque reste en `\AC{}`.
4. Lister les `\AC{` restants à l'utilisateur, compiler avec `compile-latex.ps1 -Dir rapports\<dossier>`,
   puis générer la présentation avec `tex_export_src/outils/build_presentation.py` (Python système : PyMuPDF).
5. Ne jamais commiter `rapports/` ni un zip (dépôt public, A14).

La démo (A38) suit le même chemin : `charger_demo --zip`, puis `importer_dossier`, puis `rediger_demo` à la place
de l'étape 3. Ses identifiants (`demo.apprenant` / `demo-local-2026`) sont publics par choix.

@AGENTS.md
