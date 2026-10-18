# esr2ventisax : rapport de stage et Carnet de stage

Ce dépôt réunit deux outils qui travaillent ensemble pour produire le **rapport de stage** d'un apprenant
(examens nationaux de fin de cycle de formation professionnelle, MINEFOP, Cameroun) :

| Dossier | Rôle |
|---|---|
| `webapp/` | **Carnet de stage** : application Django où l'apprenant note son stage au jour le jour (texte, photos, GPS), puis l'exporte en « dossier terrain ». |
| `tex_export_src/` | **Modèle LaTeX** du rapport (plan imposé par le cours « Module 2 »), avec sa présentation de soutenance. |
| `demo/` | Rapport PDF et présentation PPTX **produits par la chaîne complète** à partir du stage de démonstration. |
| `rapports/` | Rapports réels importés en local. Jamais versionné (dépôt public). |

Les consignes détaillées, le PRD (user stories, modèle de données, Definition of Done) et le journal des
décisions sont dans [AGENTS.md](AGENTS.md).

## Essayer la démo en ligne

<https://esrventisax.pythonanywhere.com>

| Identifiant | Mot de passe |
|---|---|
| `demo.apprenant` | `demo-local-2026` |

Le compte de démonstration contient un stage **entièrement fictif** et complet : « Entreprise de démonstration »
(EDEMO) avec son logo, chantier « Résidence Démo » (R+10, Douala), fiche entreprise, mission, bilan personnel,
une note complétée pour chaque jour travaillé (16 semaines), 12 photos triées, organigramme, tâches du Gantt,
équipements, données techniques sourcées, références, personnes et abréviations. Le tableau de bord est donc
entièrement au vert.

> Toutes les personnes, entreprises et valeurs de la démo sont inventées. Le compte est réinitialisé à chaque
> `charger_demo` : n'y saisissez rien d'important.

À voir :
- **Note rapide** (`/carnet/note/`) : la page mobile de saisie sur le terrain.
- **Tri des photos** (`/carnet/photos/`) : destination corps, annexe, preuve ou à trier.
- **Tableau de bord** (`/admin/`) : ce qui manque au rapport, et le bouton **Dossier terrain** qui télécharge le zip.

Le résultat final de la chaîne, obtenu à partir du zip téléchargé sur le site en ligne, est dans
[`demo/rapport_demo.pdf`](demo/rapport_demo.pdf) (50 pages, aucun champ « À COMPLÉTER », aucune image factice) et
[`demo/presentation_demo.pptx`](demo/presentation_demo.pptx) (15 diapositives).

## La chaîne complète

```
Carnet de stage (en ligne)  →  zip « dossier terrain »  →  importer_dossier (local)
      →  rédaction (Claude Code)  →  PDF (latexmk)  →  présentation (PPTX)
```

1. L'apprenant saisit son stage dans l'application, puis télécharge le **dossier terrain** depuis le tableau de bord.
2. En local, `importer_dossier` copie le modèle `tex_export_src/` dans `rapports/<slug>-<uuid8>/` et y dépose
   `infos.tex`, les photos, l'organigramme, le Gantt, les tableaux d'équipement, la bibliographie et les plans de
   situation OpenStreetMap. Chaque photo `img/fig_<slug>.jpg` remplace l'image factice de même nom ; le plan du siège
   devient la figure de localisation.
3. Claude Code rédige les parties à partir de `donnees_terrain/terrain.md` (procédure dans AGENTS.md, US-30).
4. Le PDF et la présentation sont produits avec le skill `latex-pdf-soutenance`.

## Après le téléchargement du zip : produire le rapport en local

Cette procédure transforme le **dossier terrain** d'un apprenant en rapport PDF et en présentation. Elle se fait
entièrement sur votre machine : rien n'est compilé sur le serveur (A4).

Deux façons de faire, qui produisent le même résultat :

| | Option 1 : pas à pas | Option 2 : skill `rapport-dossier-terrain` |
|---|---|---|
| Pour qui | comprendre chaque étape, reprendre une étape isolée | produire le rapport en une seule demande à Claude Code |
| Comment | commandes des étapes 1 à 8 ci-dessous | « Produis le rapport à partir de `<zip>` » dans Claude Code |
| Rédaction | demandée à Claude Code à l'étape 4 | incluse |

**Prérequis** : l'installation locale de l'application (voir plus bas, avec `requirements-local.txt`), LaTeX
(`latexmk`, `biber`), Python avec `python-pptx` et `PyMuPDF` pour la présentation, Claude Code pour la rédaction,
et un accès Internet pour les plans OpenStreetMap.

### Option 1 : pas à pas

#### 1. Télécharger le zip

Dans l'application : **Tableau de bord → Dossier terrain**. Le fichier s'appelle
`dossier-terrain-<slug>-<AAAAMMJJ>.zip`. Si le téléchargement est refusé, le message liste les photos « corps » ou
« annexe » sans slug ni légende : compléter ces photos (Tri des photos → Légende et slug), puis recommencer.

Ranger le zip dans `rapports/`, dossier ignoré par git : il contient des données réelles et sert aussi de
sauvegarde (voir l'étape 8).

#### 2. Importer le zip

```bash
cd webapp
.venv/Scripts/python manage.py importer_dossier ../rapports/dossier-terrain-<slug>-<AAAAMMJJ>.zip
```

La commande vérifie les sommes de contrôle du zip, puis crée `rapports/<slug>-<uuid8>/` :

| Élément | Contenu |
|---|---|
| copie de `tex_export_src/` | le modèle complet du rapport : texte générique, schémas TikZ, style |
| `config/infos.tex` | couverture et identités ; `\AC{…}` pour chaque champ laissé vide dans l'application |
| `img/fig_<slug>.jpg` | photos « corps » et « annexe » ; chacune remplace l'image factice de même nom |
| `img/logo_entreprise.png`, `img/logo_cfp.png` | logos saisis dans l'application |
| `img/plan_situation_<lieu>.png` | un plan OpenStreetMap par lieu ; celui du siège devient `img/fig_localisation.png` |
| `figures/organigramme.tex`, `figures/gantt.tex` | organigramme et Gantt réels |
| `tableaux/equipements_<catégorie>.tex` | un tableau par catégorie d'équipement |
| `bib/references.bib` | références du modèle, plus celles du stage |
| `donnees_terrain/` | `terrain.md` (matériau de rédaction), `terrain.json` (toutes les données), `catalogue.tex` |

Options :
- `--force` écrase un dossier déjà importé, y compris les textes déjà rédigés : à utiliser avec prudence.
- `--sans-carte` saute les plans OpenStreetMap (pas de réseau) ; la figure de localisation reste alors factice.

#### 3. Contrôler les fragments générés

```bash
cd ../rapports/<slug>-<uuid8>
latexmk -pdf donnees_terrain/catalogue.tex
```

`catalogue.pdf` rassemble organigramme, Gantt, tableaux d'équipement, photos retenues, plans de situation et
bibliographie. S'il compile, chaque fragment généré est valide. Il permet aussi de voir d'un coup tout le matériau
disponible avant la rédaction.

#### 4. Rédiger avec Claude Code

Ouvrir Claude Code à la racine du dépôt et demander, par exemple :

> Rédige le rapport de `rapports/<slug>-<uuid8>/` à partir de `donnees_terrain/terrain.md`, en suivant la
> procédure US-30 d'AGENTS.md.

Claude Code écrit dans `parties/` (introduction, parties I à IV, conclusion) et respecte ces règles :
- une **synthèse** organisée selon le plan du cours, jamais un récit au jour le jour ;
- uniquement des informations présentes dans `terrain.md` : ce qui manque reste en `\AC{…}` ;
- les chiffres repris de la section « Données techniques », avec leur `\cite{}` ;
- les personnes citées comme indiqué (par leur fonction si le nom n'est pas publiable) ;
- chaque photo, tableau et plan du catalogue inséré là où il sert.

#### 5. Compléter ce qui manque

```bash
grep -rn '\\AC{' --include=*.tex .
```

Chaque `\AC{…}` restant s'affiche en orange « [À COMPLÉTER : …] » dans le PDF. Deux façons de le traiter :
- **corriger dans l'application**, puis retélécharger le zip et réimporter avec `--force` : c'est la bonne voie pour
  les données du stage, mais les textes rédigés sont écrasés, à refaire ou à sauvegarder avant ;
- **corriger directement** dans `config/infos.tex` ou `parties/` pour une retouche de dernière minute.

#### 6. Compiler le PDF

Depuis la racine du dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\latex-pdf-soutenance\scripts\compile-latex.ps1" -Dir rapports\<slug>-<uuid8>
```

Le script doit se terminer par « OK : aucune erreur ni référence indéfinie ». Le PDF est
`rapports/<slug>-<uuid8>/main.pdf`.

#### 7. Générer la présentation

```bash
python tex_export_src/outils/build_presentation.py rapports/<slug>-<uuid8> rapports/<slug>-<uuid8>/presentation.pptx
```

Quinze diapositives environ, dans le style du rapport, avec des notes de présentateur. Relire et ajuster dans
PowerPoint.

#### 8. Relire, livrer, conserver

- Relire le PDF en entier et vérifier que les photos et les noms sont publiables.
- Livrer `main.pdf` et `presentation.pptx`.
- **Ne jamais commiter `rapports/`** : le dépôt est public (A14). Les fichiers y sont ignorés par git.
- Garder le zip : il restaure le stage dans une base vide,
  `.venv/Scripts/python manage.py restaurer_dossier <zip> --proprietaire <identifiant>` (depuis `webapp/`).

### Option 2 : le skill Claude Code `rapport-dossier-terrain`

Le skill global **`rapport-dossier-terrain`** enchaîne à lui seul les étapes 2 à 8 : il importe, contrôle, rédige,
compile, génère la présentation, puis fait le bilan. Seul le téléchargement du zip (étape 1) reste à faire.

#### Comment l'appeler

Ouvrir Claude Code à la racine du dépôt (ou dans un de ses sous-dossiers), puis au choix :

```
/rapport-dossier-terrain rapports/dossier-terrain-<slug>-<AAAAMMJJ>.zip
```

ou en langage naturel :

> Produis le rapport et la présentation à partir de `rapports/dossier-terrain-<slug>-<AAAAMMJJ>.zip`.

Sans chemin, le skill prend le `dossier-terrain-*.zip` le plus récent de `rapports/` ou de `~/Downloads`, et
demande s'il y a un doute. Il se déclenche aussi seul quand on mentionne un zip « dossier terrain » ou la procédure
US-30.

#### Ce qu'il fait

| Étape | Outil | Résultat |
|---|---|---|
| Importer | `scripts/preparer.ps1` → `importer_dossier` | `rapports/<slug>-<uuid8>/` créé, sommes de contrôle vérifiées |
| Contrôler | `preparer.ps1` → `latexmk` sur `catalogue.tex` | figures, tableaux, photos et plans validés ; liste des `\AC{}` à rédiger |
| Rédiger | Claude, guidé par le skill | `parties/`, remerciements, abréviations et avant-propos écrits à partir de `terrain.md` (règles de l'étape 4) |
| Compiler | `scripts/finaliser.ps1` → `latex-pdf-soutenance` | `main.pdf`, sans erreur ni référence indéfinie |
| Présenter | `finaliser.ps1` → `build_presentation.py` | `presentation.pptx` (environ 15 diapositives) |
| Bilan | Claude | chemins des fichiers, `\AC{}` restants regroupés par donnée manquante, figures restées factices, rappels de relecture et de sauvegarde |

Il contrôle aussi visuellement quelques pages du PDF (couverture, organigramme, Gantt, photos). Pour la démo
(slug `stage-demo`), il lance `rediger_demo` au lieu de rédiger.

**Garde-fous** : le skill ne réimporte jamais un rapport existant sans votre accord, car `--force` écraserait les
textes rédigés. Il ne commite ni `rapports/` ni le zip, n'invente aucune donnée et n'installe rien de lui-même : il
indique la commande d'installation quand un prérequis manque.

#### Utiliser les scripts sans Claude

Les deux scripts fonctionnent seuls, de part et d'autre d'une rédaction faite à la main :

```powershell
# importer + contrôler ; la dernière ligne affiche DOSSIER=<chemin du rapport>
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skillsapport-dossier-terrain\scripts\preparer.ps1" -Zip <zip> [-SansCarte] [-Force]
# compiler + présenter + bilan des \AC{}
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skillsapport-dossier-terrain\scriptsinaliser.ps1" -Dossier <DOSSIER> [-SansPresentation]
```

| Code de sortie | Signification |
|---|---|
| 0 | tout s'est bien passé |
| 1 | échec de l'import, du catalogue, de la compilation ou de la présentation (le message indique le fichier à lire) |
| 2 | prérequis manquant (venv, LaTeX, skill `latex-pdf-soutenance`, PyMuPDF ou python-pptx) |
| 3 | `preparer.ps1` : le rapport existe déjà ; relancer avec `-Force` pour l'écraser |
| 4 | `finaliser.ps1` : PDF et présentation produits, mais il reste des `\AC{}` (listés) |

#### Installer le skill sur un autre poste

Le skill vit dans `~/.claude/skills/rapport-dossier-terrain/` (`SKILL.md` et `scripts/`), hors du dépôt. Copier ce
dossier au même endroit sur l'autre machine. Il s'appuie sur le skill `latex-pdf-soutenance` pour la compilation
et retrouve seul le dépôt (dossier courant ou parents) ; sinon, passer `-Depot <chemin>` aux scripts.

### En cas de problème

| Message | Cause et solution |
|---|---|
| `Archive altérée : somme de contrôle invalide pour …` | Zip modifié ou téléchargement incomplet : retélécharger. |
| `… existe déjà : relancer avec --force` | Le stage a déjà été importé : garder ce dossier, ou écraser avec `--force`. |
| `Plan de situation non généré pour …` | Pas de réseau ou serveur de tuiles indisponible : relancer plus tard, ou `--sans-carte`. |
| Erreur LaTeX sur une figure ou un tableau | Compiler `catalogue.tex` (étape 3) pour isoler le fragment fautif. |
| Le skill `rapport-dossier-terrain` n'apparaît pas dans Claude Code | Vérifier que `~/.claude/skills/rapport-dossier-terrain/SKILL.md` existe, puis redémarrer Claude Code. |

### Reproduire la démo en local

Depuis la racine du dépôt, une fois l'installation locale faite (voir plus bas) :

```bash
cd webapp
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py charger_demo --zip ../rapports/demo.zip     # compte + stage + export
.venv/Scripts/python manage.py importer_dossier ../rapports/demo.zip      # → rapports/stage-demo-<uuid8>/
.venv/Scripts/python manage.py rediger_demo ../rapports/stage-demo-<uuid8>  # étape 3, version démo
cd ..
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\latex-pdf-soutenance\scripts\compile-latex.ps1" -Dir rapports\stage-demo-<uuid8>
python tex_export_src/outils/build_presentation.py rapports/stage-demo-<uuid8> rapports/stage-demo-<uuid8>/presentation.pptx
```

`rediger_demo` remplace les quelques `\AC{}` du texte du modèle par le texte du stage fictif. Pour un stage réel,
cette étape est la rédaction par Claude Code.

## Installation locale de l'application

Prérequis : Python 3.13 ou plus récent. Pour le rapport : une distribution LaTeX avec `latexmk` et `biber`
(MiKTeX ou TeX Live). Pour la présentation : `python-pptx` et `PyMuPDF`.

```bash
cd webapp
python -m venv .venv
.venv/Scripts/pip install -r requirements-local.txt   # requirements.txt + staticmap (plans OSM)
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py creer_groupes
.venv/Scripts/python manage.py createsuperuser
.venv/Scripts/python manage.py runserver
```

Sous Linux ou macOS, remplacer `.venv/Scripts/` par `.venv/bin/`. Sans fichier `.env`, l'application démarre en
mode développement (`DEBUG` actif, clé locale) ; voir `webapp/.env.example`.

### Tests

```bash
cd webapp
.venv/Scripts/python -m pytest -m "not slow"   # suite rapide
.venv/Scripts/python -m pytest                 # y compris la compilation LaTeX réelle (plusieurs minutes)
```

## Déploiement

Hébergement gratuit PythonAnywhere (`esrventisax`). Procédure complète, mise à jour et maintien du compte :
[webapp/DEPLOIEMENT.md](webapp/DEPLOIEMENT.md).

## Pile technique

Django 5.2 LTS, SQLite, django-unfold (admin aux couleurs de ventisax : Lexend, bleu marine `#0b2d46`,
turquoise `#68ddce` / `#0d665e`), Pillow, python-dotenv ; Leaflet et OpenStreetMap côté navigateur ;
LaTeX (TikZ, biblatex) et python-pptx en local.

## Données personnelles

Le dépôt est **public** : la base SQLite, `media/`, `.env`, les zips et `rapports/` ne sont jamais versionnés.
Seules les données inventées de la démo y figurent.
