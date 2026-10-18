---
name: rapport-dossier-terrain
description: Transforme un zip « dossier terrain » exporté du Carnet de stage (dépôt esr2ventisax) en rapport de stage PDF et en présentation PPTX, en local et de bout en bout. Le skill importe le zip (importer_dossier), contrôle les fragments générés (catalogue.tex), rédige les parties à partir de donnees_terrain/terrain.md sans rien inventer, compile avec latex-pdf-soutenance, génère la présentation, puis dresse le bilan des champs à compléter. À utiliser quand l'utilisateur fournit ou mentionne un zip dossier-terrain-*.zip, veut « produire », « générer » ou « rédiger » le rapport d'un apprenant, ou cite la procédure US-30.
---

# rapport-dossier-terrain : du zip au PDF et à la présentation

Cinq étapes, dans l'ordre : **importer → contrôler → rédiger → compiler → présenter**.
Les étapes mécaniques passent par deux scripts ; la rédaction est ton travail.

```
preparer.ps1 (importer + contrôler)  →  rédaction (toi)  →  finaliser.ps1 (compiler + présenter)
```

Scripts : `~/.claude/skills/rapport-dossier-terrain/scripts/`. Ils trouvent seuls le dépôt esr2ventisax
(dossier courant ou parents, sinon `~/Desktop/sop_ai_coding/01_GREENFIELD/esr2ventisax`) ; sinon `-Depot <chemin>`.
La référence complète est `docs/rapport-local.md` du dépôt, ainsi que la
procédure US-30 d'AGENTS.md. Relis AGENTS.md (conventions, A14, A34, A36) avant de rédiger.

## 0. Garde-fous

- **Données réelles** : tout reste dans `rapports/` (ignoré par git). Ne commite jamais `rapports/` ni un zip,
  et n'envoie rien à un service externe (A14).
- **Rien d'inventé** : seuls `terrain.md`, `terrain.json` et le texte générique du modèle sont des sources.
  Une donnée absente reste en `\AC{…}`.
- **`-Force` écrase les textes déjà rédigés** : ne l'utilise qu'avec l'accord explicite de l'utilisateur.
- Prérequis : venv de l'application (`webapp/.venv`, avec `requirements-local.txt`), `latexmk` et `biber`,
  un Python avec `python-pptx` et `PyMuPDF`, le skill `latex-pdf-soutenance`. S'il en manque un, le script
  le signale : transmets la commande d'installation sans rien installer d'office.

## 1–2. Importer et contrôler

Trouve le zip : le chemin donné par l'utilisateur, sinon le plus récent `dossier-terrain-*.zip` dans
`rapports/` ou dans `~/Downloads`. Demande en cas d'ambiguïté. S'il est ailleurs, copie-le dans `rapports/`.

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\rapport-dossier-terrain\scripts\preparer.ps1" -Zip <zip> [-SansCarte] [-Force]
```

- La dernière ligne `DOSSIER=<chemin>` donne le rapport à rédiger.
- **Code 3** : le rapport existe déjà. Demande s'il faut le garder (passe alors directement à l'étape 3 ou 4)
  ou l'écraser (`-Force`).
- **Code 1** : lis le message. « Archive altérée » : il faut retélécharger le zip. Erreur LaTeX dans le catalogue :
  le fragment généré fautif est identifié dans `catalogue.log`.
- Sans réseau, relance avec `-SansCarte` : la figure de localisation reste alors factice (à signaler au bilan).

## 3. Rédiger

**Démo** : si le slug est `stage-demo`, lance `webapp/.venv/Scripts/python webapp/manage.py rediger_demo <DOSSIER>`
au lieu de rédiger, puis passe à l'étape 4.

Sinon, lis d'abord en entier `DOSSIER/donnees_terrain/terrain.md`, puis `catalogue.tex`, `config/infos.tex`
et chaque fichier de `parties/`. Le texte du modèle est générique et rédigé pour la **plomberie sanitaire** :
garde sa structure (plan du cours, Q7), mais adapte chaque affirmation au stage réel.

| Fichier | Source dans terrain.md |
|---|---|
| `parties/introduction.tex` | en-tête (dates, entreprise, thème), Mission › Objectifs, rubrique Introduction |
| `parties/partie1_entreprise.tex` | « Partie I : Entreprise » (11 rubriques), Personnes, Lieux |
| `parties/partie2_deroulement.tex` | « Partie II : Mission » (9 rubriques), Tâches (tableau de planning), Équipements |
| `parties/partie3_theme.tex` | « Partie III : Thème » (chapitres et notes), Données techniques, Photos retenues |
| `parties/partie4_critiques.tex` | Bilan › Critiques et Suggestions |
| `parties/conclusion.tex` | Bilan personnel (7 questions), Résultats |
| `liminaires/remerciements.tex` | Personnes « à remercier » |
| `liminaires/abreviations.tex` | Abréviations (garder celles du modèle encore utilisées dans le texte) |
| `liminaires/avant_propos.tex` | en-tête, Mission › Poste |

Règles (US-30) :
- une **synthèse** classée selon le plan, jamais un récit au jour le jour ; phrases courtes, orthographe soignée ;
- chiffres repris de « Données techniques » avec le `\cite{clé}` indiqué ; un relevé est daté (« relevé du … ») ;
- personnes : le nom tel qu'exporté, ou la fonction si le nom n'est pas publiable ; jamais de téléphone ;
- si le thème n'est pas la plomberie sanitaire, réécris la Partie III à partir des chapitres du stage et retire
  les développements techniques du modèle qui ne s'y rapportent pas (avec leurs figures, tableaux et `\cite`) ;
- insère chaque élément du catalogue là où il sert :
  - photo : `\figureimg{img/fig_<slug>}{0.6\textwidth}{<légende>}{fig:<slug>}`, annoncée dans le texte par `\ref` ;
  - tableau d'équipement : `\input{tableaux/equipements_<catégorie>}` ;
  - plan : `\figureimg{img/plan_situation_<lieu>}{0.75\textwidth}{plan de situation : <lieu>}{fig:plan-<lieu>}` ;
  - organigramme, Gantt et localisation du siège sont déjà branchés ;
- une figure du modèle sans photo réelle (`img/fig_X.png` factice encore présent et aucun `fig_X.jpg`) :
  remplace-la par une photo pertinente du stage, sinon retire la figure et ses renvois ;
- échappe les caractères spéciaux LaTeX dans ce que tu écris (`& % $ # _ { } ~ ^ \`, et « 50 \% ») ;
- ne touche pas à `config/` (sauf `infos.tex` pour une donnée présente dans terrain.md), `figures/` générées,
  `tableaux/`, `bib/`.

## 4–5. Compiler et présenter

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\rapport-dossier-terrain\scripts\finaliser.ps1" -Dossier <DOSSIER>
```

- **Code 1** (compilation) : lis `main.log`, corrige ta rédaction (syntaxe LaTeX, `\ref` vers une figure retirée…)
  et relance. Ne modifie pas le style ni le préambule sans accord.
- **Code 4** : le PDF et le PPTX sont produits, mais il reste des `\AC{}` (listés). C'est attendu quand
  l'application n'a pas tout saisi.
- Contrôle visuel : rends quelques pages avec `pdftoppm -r 50 -png -f N -l N main.pdf` (couverture,
  organigramme, Gantt, une page de photos, bibliographie), puis lis les images. Pour les diapositives, exporte-les
  en PNG via PowerPoint (COM) si disponible.

## 6. Bilan à l'utilisateur

Donne :
1. les chemins de `main.pdf` (nombre de pages) et de `presentation.pptx` ;
2. les `\AC{}` restants, regroupés par donnée manquante, avec la conduite à tenir : la compléter dans
   l'application, puis retélécharger et réimporter avec `-Force` (la rédaction est alors à refaire), ou la
   corriger directement dans `infos.tex` ou `parties/` ;
3. les figures restées factices et les plans non générés ;
4. le rappel de relire le PDF (noms et photos publiables) et de garder le zip, qui sert de sauvegarde
   (`manage.py restaurer_dossier <zip> --proprietaire <identifiant>`).
