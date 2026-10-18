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

Le résultat final de la chaîne est dans [`demo/rapport_demo.pdf`](demo/rapport_demo.pdf) (50 pages, aucun champ
« À COMPLÉTER ») et [`demo/presentation_demo.pptx`](demo/presentation_demo.pptx) (15 diapositives).

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
