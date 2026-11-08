# CLAUDE.md

Les consignes du projet sont dans AGENTS.md, partagé avec les autres agents. On y trouve :

- la structure et les conventions du rapport LaTeX ;
- la section **GOALS** de l'application « Carnet de stage » (`webapp/`) : objectifs prioritaires,
  contraintes techniques et hors périmètre ;
- la section **GOALS — incrément 4** : comptes ouverts (inscription par code d'invitation, vérification du
  courriel, connexion protégée, mot de passe oublié, port de `c-fiscalite-syscohada/accounts/`) et revue
  UI/UX (utilisateurs dans Unfold, menu court, déconnexion partout, contraste des champs). Elle lève en
  partie le hors-périmètre A13 ;
- le **PRD de l'incrément 4**, juste après : user stories US-32 à US-44 (lot 1 interface US-32–35, lot 2
  comptes ouverts US-36–44), entités `Profil`, `CodeInvitation`, `EchecConnexion`, `LimiteInscription`
  (application `comptes/`), contrat des URL et des courriels, et sa Definition of Done (P4-5), qui
  s'ajoute à P5 ;
- le **PRD** de l'application : user stories US-01 à US-31, modèle logique des données, contrat d'export
  et Definition of Done ;
- les journaux des décisions : **Q1–Q16** pour le rapport, **A1–A40** pour l'application, **B1–B14** pour
  les comptes ouverts et la revue UI/UX.

Pour l'incrément 4 : lire le code de comptafisca directement (REA est inutile sur du code source local), ne
jamais lire, écrire ni afficher le mot de passe SMTP (il est collé par l'utilisateur dans le `.env` du serveur).

Avant toute tâche sur `webapp/` :
- relire GOALS et le PRD ;
- refuser ce qui relève du hors périmètre sans validation explicite de l'utilisateur ;
- ne déclarer une story terminée que si **tous** les critères de la Definition of Done (P5) sont remplis,
  plus ceux de P4-5 pour US-32 à US-44.

## Quand l'utilisateur fournit un zip « dossier terrain »

**Utiliser le skill global `rapport-dossier-terrain`**, qui enchaîne tout (scripts `preparer.ps1`, rédaction,
`finaliser.ps1` ; source dans `skills/rapport-dossier-terrain/`, à garder identique à la copie de `~/.claude/skills/`).
La procédure complète, pas à pas, est dans `docs/rapport-local.md` et dans AGENTS.md
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
