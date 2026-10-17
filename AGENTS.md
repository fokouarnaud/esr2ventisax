# AGENTS.md — Rapport de stage « Froid et climatisation » (thème : plomberie sanitaire)

Consignes pour tout agent (Claude Code, Codex…) qui travaille dans ce dépôt.

## Contexte

- `tex_export_src/` contient le **rapport de stage** LaTeX d'un apprenant en spécialité
  **Froid et climatisation** (examens nationaux de fin de cycle de formation professionnelle,
  MINEFOP, Cameroun). Le thème technique principal est la **plomberie sanitaire**, rattaché
  explicitement à la spécialité.
- Sources de référence (non versionnées, voir `.gitignore`) :
  - `exemple_rapport/01.jpeg` … `26.jpeg` : rapport d'exemple. Il sert de modèle de **forme et de
    niveau** uniquement : ne jamais recopier ses phrases ni ses identités.
  - `reference/cours/01_partie1/02_module2/22.jpeg` … `27.jpeg` : cours « Module 2 : Techniques de
    rédaction des rapports ». C'est lui qui **fixe le plan obligatoire** et l'emporte sur l'exemple
    en cas de conflit.
- `archive/memoire_featherface/` : ancien mémoire de Master (détection faciale ECA-CBAM), archivé.
  Ne pas le modifier.

## Structure de `tex_export_src/`

```
main.tex                 # assemble tout, ne contient pas de texte
config/infos.tex         # TOUTES les données personnelles et d'entreprise (macros \Info...)
config/preambule.tex     # packages
config/style.tex         # bannières vertes, en-tête et pied de page, légendes
liminaires/              # couverture, dédicace, remerciements, abréviations, avant-propos
parties/                 # introduction, partie1..4, conclusion
annexes/                 # annexes (chacune annoncée par un renvoi dans le texte)
bib/references.bib       # bibliographie
img/                     # images ; img/fig_<sujet>.png = image factice à remplacer
figures/                 # schémas TikZ (.tex)
outils/                  # scripts de génération (images factices, présentation)
```

## Conventions

- **Données à compléter** : uniquement dans `config/infos.tex`, sous la forme `\Info<Nom>`.
  Les valeurs encore inconnues s'écrivent `\AC{texte}`, qui s'affiche « [À COMPLÉTER : texte] »
  en orange. Avant le rendu final, chercher `\AC{` dans tout le dossier.
- **Images factices** : `img/fig_*.png` sont générées par `outils/generer_images_factices.py`.
  Elles portent la mention « IMAGE À REMPLACER ». Pour en remplacer une, déposer une vraie photo
  **sous le même nom** (même extension `.png`, ou adapter l'`\includegraphics`).
- **Schémas** : en TikZ dans `figures/`, de vraies figures modifiables.
- **Légendes** : « Figure N : … » sous les figures, « Tableau N : … » au-dessus des tableaux.
- **Ton** : phrases courtes et précises, orthographe irréprochable, pas de récit au jour le jour.
- **Valeurs techniques** : toujours sourcées (`\cite{}`) vers `bib/references.bib`.

## Génération

Utiliser le skill global **`latex-pdf-soutenance`**, qui délègue les slides à `thesis-defense-pptx` :

```powershell
# PDF
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\latex-pdf-soutenance\scripts\compile-latex.ps1" -Dir tex_export_src
# Images factices (à relancer si la liste change)
python tex_export_src\outils\generer_images_factices.py
# Présentation
python tex_export_src\outils\build_presentation.py tex_export_src tex_export_src\presentation.pptx
```

Git : les fichiers intermédiaires LaTeX sont ignorés ; `main.pdf` et `presentation.pptx` sont versionnés.
Ne rien pousser vers le dépôt distant sans demande explicite.

## Journal des décisions (séance de cadrage du 2026-10-17)

| # | Question | Décision |
|---|---|---|
| Q1 | Que faire du mémoire FeatherFace dans `tex_export_src` ? | Archiver dans `archive/memoire_featherface/` (commit), puis restructurer `tex_export_src` sur place. |
| Q2 | Identités (étudiant, école, entreprise, encadreurs, dates) ? | Macros centralisées dans `config/infos.tex`, avec des valeurs marquées « à compléter ». Ne pas recopier l'exemple, ne pas inventer d'entreprise réelle. |
| Q3 | Images « par IA » ? | Images factices générées en local (« IMAGE À REMPLACER » + légende) pour les photos ; TikZ pour les schémas. Noms stables `img/fig_<sujet>.png`. |
| Q4 | Utiliser REA ? | Non : REA sert à la rétro-ingénierie. Recherches web ciblées (DTU, ouvrages), citées en bibliographie. |
| Q5 | Fidélité à l'exemple ? | Structure et style de l'exemple ; plan imposé par le cours ; texte entièrement original. |
| Q6 | AGENTS.md / CLAUDE.md ? | À la racine. `CLAUDE.md` importe `AGENTS.md` ; ce journal y est consigné. |
| Q7 | Plan final ? | Couverture (9 champs du cours), dédicace, **sommaire avant remerciements**, abréviations, listes des tableaux et des figures, avant-propos, introduction, Partie I Entreprise (enrichie selon le cours), Partie II Déroulement (mission selon le cours), Partie III Thème, Partie IV Critiques et suggestions, conclusion (bilan, limites, recommandations), **bibliographie**, annexes avec renvois, table des matières. Une conclusion partielle par partie. Le cours l'emporte sur l'exemple. |
| Q8 | Thème de la partie III ? | Plomberie sanitaire en thème principal, plus un chapitre de liens vers le froid et la climatisation (isolation Armaflex, eau chaude sanitaire, rappel du cycle frigorifique). |
| Q9 | Niveau et volume ? | 35 à 45 pages. Généralités, petit dimensionnement chiffré (débits de base, coefficient de simultanéité, diamètre, pertes de charge), tableaux matériel et travaux, modes opératoires, hygiène et sécurité. Valeurs sourcées (DTU 60.11…). |
| Q10 | Mise en forme ? | Esprit de l'exemple en version épurée : sans empattement, interligne 1,5, bannières vertes, intercalaires de parties, bandeau d'en-tête, pied « Rédigé et présenté par » + numéro dans un ruban vert, pagination romaine puis arabe. |
| Q11 | Couverture institutionnelle ? | Bandeau officiel bilingue République du Cameroun / MINEFOP, « Examens nationaux de fin de cycle… », « Spécialité : Froid et climatisation ». CFP, entreprise, noms et dates à compléter. Logos factices. |
| Q12 | Présentation ? | Via `latex-pdf-soutenance` / `thesis-defense-pptx` : 12 à 15 diapositives, en français, dans le style vert du rapport, avec des notes de présentateur. |
| Q13 | Contenu factuel ? | Texte descriptif générique complet ; tout ce qui est factuel et vérifiable (chiffres, noms, dates, adresse, clients) en `\AC{}` ; planning type d'environ 16 semaines « à adapter ». |
| Q14 | Nettoyage de `tex_export_src` ? | Supprimer tout ce qui concerne le mémoire (chapitres, 63 images, bibliographie, présentation, `main.*`) et recréer l'arborescence décrite plus haut. |
| Q15 | Git ? | Commits sur `develop` : archive, restructuration, PDF/PPTX et docs. Fichiers intermédiaires ignorés, PDF et PPTX versionnés, aucun push. |
| Q16 | Validation ? | Tout enchaîner (rédaction, compilation, contrôle, présentation), puis une seule relecture finale par l'utilisateur. |

## Points à valider par l'utilisateur

- Remplir `config/infos.tex` (noms, CFP, entreprise, chantier, dates, encadreurs et leurs postes).
- Remplacer les images factices `img/fig_*.png` et les logos factices.
- Adapter le planning type (partie II) aux activités réellement menées.
- Vérifier les données chiffrées de l'entreprise (`\AC{}` restants).
