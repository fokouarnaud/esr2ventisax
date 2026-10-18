# esr2ventisax : Carnet de stage et rapport de stage

Un apprenant note son stage au jour le jour dans une application web. En fin de stage, ses données deviennent un
**rapport PDF** et une **présentation de soutenance**, conformes au cours « Module 2 » des examens nationaux de fin
de cycle de formation professionnelle (MINEFOP, Cameroun).

```
Carnet de stage (en ligne) → zip « dossier terrain » → import local → rédaction (Claude Code) → PDF + PPTX
```

## Démo

**<https://esrventisax.pythonanywhere.com>**, avec l'identifiant `demo.apprenant` et le mot de passe `demo-local-2026`.

Le compte contient un stage fictif complet : « Entreprise de démonstration », chantier R+10 à Douala, une note par
jour travaillé et 12 photos. Le résultat de la chaîne est dans
[`demo/rapport_demo.pdf`](demo/rapport_demo.pdf) (50 pages) et [`demo/presentation_demo.pptx`](demo/presentation_demo.pptx).

> Données inventées ; le compte est réinitialisé régulièrement : n'y saisissez rien d'important.

## Démarrage rapide

Prérequis : Python 3.13 ou plus récent. Pour produire un rapport, ajouter LaTeX (`latexmk`, `biber`) et
`python-pptx` avec `PyMuPDF`.

```bash
cd webapp
python -m venv .venv
.venv/Scripts/pip install -r requirements-local.txt
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py creer_groupes
.venv/Scripts/python manage.py charger_demo      # facultatif : compte demo.apprenant
.venv/Scripts/python manage.py runserver
```

Sous Linux ou macOS, remplacer `.venv/Scripts/` par `.venv/bin/`. Tests : `.venv/Scripts/python -m pytest -m "not slow"`.

## Produire un rapport à partir d'un zip

Dans l'application : **Tableau de bord → Dossier terrain**. Ranger le zip dans `rapports/`, puis au choix :

- **Avec le skill Claude Code** `rapport-dossier-terrain` : `/rapport-dossier-terrain rapports/<zip>`. Le skill
  importe, contrôle, rédige, compile et génère la présentation, puis liste ce qui reste à compléter. Pour
  l'installer : `Copy-Item -Recurse skills\rapport-dossier-terrain "$HOME\.claude\skills\"`.
- **Pas à pas**, sans le skill : `importer_dossier`, rédaction, compilation, présentation.

Ces deux options, ainsi que le dépannage, sont détaillées dans **[docs/rapport-local.md](docs/rapport-local.md)**.

## Documentation

| Document | Contenu |
|---|---|
| [docs/rapport-local.md](docs/rapport-local.md) | Du zip au PDF et au PPTX : les deux options, le dépannage, la démo en local |
| [webapp/DEPLOIEMENT.md](webapp/DEPLOIEMENT.md) | Installation et mise à jour sur PythonAnywhere, maintien du compte gratuit |
| [AGENTS.md](AGENTS.md) | Consignes, GOALS, PRD (user stories, modèle de données, Definition of Done), décisions |
| [skills/rapport-dossier-terrain/](skills/rapport-dossier-terrain/) | Source du skill Claude Code |

## Structure

| Dossier | Rôle |
|---|---|
| `webapp/` | Application Django « Carnet de stage » |
| `tex_export_src/` | Modèle LaTeX du rapport et script de présentation |
| `skills/` | Skill Claude Code `rapport-dossier-terrain` |
| `demo/` | PDF et PPTX produits à partir du stage de démonstration |
| `rapports/` | Rapports réels importés en local (ignoré par git) |

**Pile** : Django 5.2 LTS, SQLite, django-unfold, Pillow ; Leaflet et OpenStreetMap ; LaTeX (TikZ, biblatex) et
python-pptx en local.

## Données personnelles

Le dépôt est public : la base SQLite, `media/`, `.env`, les zips et `rapports/` ne sont jamais versionnés.

## Licence

[MIT](LICENSE)
