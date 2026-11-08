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
- `demo/` : rapport PDF et présentation PPTX produits par toute la chaîne à partir du stage fictif de
  `charger_demo` (A38). Données inventées, versionnées.
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
  Elles portent la mention « IMAGE À REMPLACER ». Les `\includegraphics` et `\figureimg` les appellent
  **sans extension** (`img/fig_manometre`) : `importer_dossier` supprime la factice `.png` quand la photo
  `img/fig_<slug>.jpg` du même nom arrive, et le plan de situation du siège devient `img/fig_localisation.png`.
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

### Rapport réel à partir du Carnet de stage (US-30)

Skill global **`rapport-dossier-terrain`** (source versionnée : `skills/rapport-dossier-terrain/`, à recopier dans `~/.claude/skills/` après modification) : il automatise les étapes 2 à 5 ci-dessous (`preparer.ps1` importe et
contrôle, Claude rédige, `finaliser.ps1` compile et génère la présentation, puis fait le bilan des `\AC{}`).

1. Dans l'application : Tableau de bord → « Télécharger le dossier terrain » (zip). L'export est refusé tant qu'une
   photo « corps » ou « annexe » n'a pas de slug et de légende ; le message indique lesquelles.
2. En local, depuis `webapp/` :
   `.venv\Scripts\python manage.py importer_dossier <zip>` → `rapports/<slug>-<uuid8>/` (ignoré par git).
   L'import copie le modèle `tex_export_src/`, vérifie les sommes de contrôle, remplace `config/infos.tex`,
   `figures/organigramme.tex`, `figures/gantt.tex`, ajoute `img/`, `tableaux/`, les plans de situation OSM,
   complète `bib/references.bib` (les entrées du modèle sont gardées) et dépose `donnees_terrain/`
   (`terrain.md`, `terrain.json`, `catalogue.tex`). Options : `--force`, `--sans-carte`.
3. Rédaction par Claude Code dans `rapports/<dossier>/parties/` **uniquement à partir de `donnees_terrain/terrain.md`** :
   synthèse, jamais de récit au jour le jour ; chiffres repris de la section « Données techniques » avec leur `\cite{}` ;
   personnes citées comme indiqué (fonction si le nom n'est pas publiable) ; chaque photo, tableau et plan du
   `catalogue.tex` inséré là où il sert ; aucune information inventée, ce qui manque reste en `\AC{}`.
   Pour la démo, `manage.py rediger_demo rapports/<dossier>` tient lieu de cette étape (textes de `carnet/demo/donnees.py`).
4. Contrôle : `latexmk -pdf catalogue.tex` (tous les fragments générés), puis le rapport :
   `powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\latex-pdf-soutenance\scripts\compile-latex.ps1" -Dir rapports\<dossier>`
5. Présentation : `python tex_export_src\outils\build_presentation.py rapports\<dossier> rapports\<dossier>\presentation.pptx`.
6. Ne jamais commiter `rapports/` (dépôt public, A14).

## GOALS — application « Carnet de stage » (`webapp/`)

Une application web qui permet à un apprenant de noter **au jour le jour**, pendant son stage, tout ce
que le cours « Module 2 » exige pour le rapport. L'entreprise, le thème et la spécialité ne sont pas
connus à l'avance. Ces données sont exportées puis importées en local dans une copie de `tex_export_src/`.
Claude Code y rédige le rapport, puis produit le PDF et la présentation avec `latex-pdf-soutenance`.
Les décisions détaillées sont dans le journal A1–A38 ci-dessous.

### 1. Objectifs fonctionnels prioritaires

Par ordre de livraison (A20) :

**Incrément 1 : saisie et déploiement**
1. **Comptes et cloisonnement** (A1, A13, A32) : comptes créés par le superutilisateur. Un apprenant ne
   voit que ses propres stages et peut en avoir plusieurs. Un formateur ne voit que les stages dont il
   est référent et peut laisser une remarque sur chaque note.
2. **Stage et couverture** (A3, A11) : les 9 champs de couverture du cours, les logos de l'entreprise et du
   CFP, la spécialité, le thème et le sous-thème, tous saisis librement (A2).
3. **Note rapide sur mobile** (A29) : une page hors de l'admin. Date et heure sont préremplies ; on saisit
   un texte, on prend des photos avec l'appareil, la position GPS est captée automatiquement, les
   étiquettes sont facultatives. Trois actions au plus, et un brouillon gardé dans le navigateur (A6).
4. **Complétion dans l'admin Unfold** (A9, A23) : chaque note se complète avec les champs du rapport
   d'activité (objectifs, moyens, méthodologie, éléments théoriques, difficultés, solutions,
   appréciation, intervention). S'y ajoutent les formulaires **Fiche entreprise** (11 rubriques du cours)
   et **Mission** (9 rubriques), et le **Bilan personnel** (questions de la p. 24, critiques et suggestions).
5. **Rubriques** (A24) : celles du cours sont fixes. Les chapitres du thème sont créés librement pour
   chaque stage. Une note ou une photo peut porter plusieurs étiquettes.
6. **Photos** (A5, A22, A35) : compressées (1600 px, environ 300 Ko), avec GPS et EXIF conservés,
   une légende et un slug. Chaque photo a une destination : à trier, corps, annexe ou preuve seulement.
   Une vue en grille sert au tri.
7. **Lieux** (A31) : position choisie sur une carte Leaflet/OpenStreetMap ou par le GPS, description par
   repères. Une note ou une photo est rattachée automatiquement au lieu le plus proche (moins de 200 m).
8. **Données structurées** :
   - Organigramme (A25).
   - Tâches pour le Gantt (A26).
   - Équipements : outillage, matériel, EPI, appareils de mesure (A27).
   - Données techniques : relevés ou valeurs de référence, une valeur de référence exigeant sa source (A28).
   - Références bibliographiques, personnes (« à remercier », « nom publiable », A36) et abréviations.
9. **Calendrier** (A30) : jours travaillés, absences, jours fériés fixes du Cameroun préchargés, taux de
   présence.
10. **Tableau de bord** : rubriques vides, notes non complétées, jours ouvrés sans note, photos par
    destination, quota du stage, dernière sauvegarde.
11. **Déploiement** sur PythonAnywhere (`esrventisax`) avec Playwright MCP (A7, A19).

**Incrément 2 : export et sauvegarde**

12. **Export zip « dossier terrain »** généré en flux (A4, A33) :
    - `infos.tex`, avec `\AC{}` pour les champs vides ;
    - les photos de destination corps et annexe ;
    - `organigramme.tex` et `gantt.tex` ;
    - `references.bib` ;
    - les tableaux d'équipement ;
    - `terrain.json` et `terrain.md`, classés selon le plan du cours.
13. **Sauvegarde** : le zip sert de sauvegarde. Il est restaurable avec `restaurer_dossier`, et une alerte
    s'affiche après 7 jours sans sauvegarde (A16).

**Incrément 3 : import local et rédaction**

14. **`importer_dossier`** (A15, A21) : copie le modèle `tex_export_src/` dans
    `rapports/<slug>-<uuid8>/`, y dépose les fichiers du zip et génère les plans de situation à partir
    d'OpenStreetMap. Il refuse d'écraser un dossier existant sans `--force`.
15. **Procédure documentée** : zip, puis import, puis rédaction par Claude Code à partir de
    `terrain.md`, puis `latex-pdf-soutenance` (PDF et PPTX).

### 2. Contraintes techniques

- **Pile** : Django 5.2 LTS, **SQLite**, django-unfold récent, Pillow, python-dotenv. Python 3.13 sur
  PythonAnywhere, venv local dans `webapp/.venv`. Versions vérifiées avec context7 avant l'installation (A12).
- **Hébergement** : compte gratuit PythonAnywhere de **512 Mo** et 100 s de CPU par jour ; liste blanche
  des sites joignables depuis le serveur ; renouvellement tous les 3 mois, documenté dans
  `webapp/DEPLOIEMENT.md` (A17). Le code arrive par un `git clone` HTTPS du dépôt public, sans jeton, et
  se met à jour par `git pull`.
- **Quota disque** : environ 4 apprenants, **80 Mo par stage** par défaut (réglable), envoi refusé
  au-delà, alerte globale à 80 %. Les zips ne sont jamais stockés sur le serveur (A33).
- **Identifiants** : **UUID** comme clé primaire de tous les modèles métier ; fichiers médias nommés par
  UUID (A21).
- **Textes** : Markdown minimal (paragraphes, listes, gras), converti en LaTeX par un convertisseur maison.
  L'échappement des caractères `& % $ # _ { } ~ ^ \` est testé (A34, A18).
- **Interface** : en français, avec les libellés du cours (A10). Nom « Carnet de stage », logo neutre,
  palette et police de ventisax.pythonanywhere.com : Lexend, bleu marine `#0b2d46`, turquoise
  `#68ddce` et `#0d665e`, coins arrondis de 24/20/12 px, boutons en pilule, clair et sombre (A11).
  Note rapide conçue avec le skill `design-taste-frontend`.
- **Dépôt public** (A14) : ne jamais versionner la base SQLite, `media/`, `.env`, les zips ni
  `rapports/`. Secrets dans un `.env` sur le serveur. Aucun identifiant dans le dépôt ni dans les fichiers.
- **Médias** : `/media/` servi publiquement par PythonAnywhere, EXIF conservé. Choix assumé (A22).
- **Qualité** : TDD avec pytest-django sur le cloisonnement, le quota, l'EXIF, l'échappement LaTeX et
  l'aller-retour export/restauration. Vérification visuelle avec Playwright MCP, y compris sur mobile
  (390 px) (A18).
- **Git** : code dans `webapp/` sur `develop`, commits conventionnels. Push autorisé uniquement pour le
  code et la documentation (A7, A8).

### 3. Hors périmètre (strict)

- Application hors ligne ou PWA, application mobile native, synchronisation différée (A6).
- Inscription sans code d'invitation, connexion via un réseau social (A13, revu par B1 : l'inscription
  avec code et la réinitialisation par courriel relèvent désormais de l'incrément 4 ci-dessous).
- Rédaction automatique dans l'application, appel à l'API Claude ou à un autre LLM depuis le serveur (A4).
- Compilation LaTeX, génération du PDF ou du PPTX, et génération des cartes sur PythonAnywhere : tout
  cela se fait en local (A4, A31).
- Éditeur de texte visuel (WYSIWYG), titres, tableaux ou images dans les champs texte (A34).
- Contrôle d'accès aux photos et retrait de l'EXIF (A22).
- Front-end séparé (React, Vue…) : seuls l'admin Unfold, les pages Note rapide et Tri des photos (A9) et
  l'accueil public (A39).
- Base de données autre que SQLite, hébergement payant, tâches planifiées sur le serveur.
- Code en dur pour une spécialité ou un thème donné (A2).
- Tout ce qui touche à `archive/` et à `exemple_rapport/`. Aucun commit ni push de données réelles d'un
  apprenant.

## GOALS — incrément 4 : comptes ouverts et revue UI/UX (`webapp/`)

Reprendre le système de connexion et d'inscription de comptafiscaventisax.pythonanywhere.com (source
locale : `c-fiscalite-syscohada/accounts/`, lue directement : REA est inutile sur du code source), en le
limitant aux apprenants munis d'un code d'invitation, et corriger les défauts d'interface relevés :
champs de formulaire invisibles, bouton « Ajouter un utilisateur » absent, déconnexion inaccessible
quand le menu de gauche est long. Décisions détaillées : journal B1–B14 ci-dessous.

### 1. Objectifs fonctionnels prioritaires

Par ordre de livraison (B14) : deux lots, chacun testé puis déployé.

**Lot 1 : interface (aucune dépendance à l'inscription)**
1. **Gestion des utilisateurs dans Unfold** (B12) : `User` et `Group` réenregistrés avec les classes et
   les formulaires d'Unfold (champs enfin stylés et visibles). Bouton « Ajouter un utilisateur » sur la
   liste. Colonnes : identifiant, nom, courriel, groupe, courriel vérifié, actif, inscrit le, code utilisé.
   Filtres : groupe, actif, vérifié. Le formulaire d'ajout choisit le groupe (Apprenant ou Formateur),
   qui règle `is_staff`. Réservé au superutilisateur.
2. **Menu court et déconnexion partout** (B11) : navigation Unfold définie à la main, en groupes
   repliables (Mon stage, Journal, Données, Références, Administration réservée au superutilisateur),
   sans la liste automatique de toutes les applications. Bouton « Se déconnecter » toujours visible dans
   l'en-tête de l'admin et dans celui des pages Note rapide et Tri des photos ; retour à l'accueil après
   déconnexion.
3. **Revue UI/UX de tous les écrans** (B13), avec `design-taste-frontend` et Playwright : pages
   d'authentification, tous les formulaires d'ajout et de modification de l'admin, Note rapide, Tri des
   photos, accueil ; en clair et en sombre, à 390 et à 1440 px. Chaque champ a un bord au contraste d'au
   moins 3:1, un libellé et un focus visibles, sans débordement. Résultat consigné dans « Charte
   appliquée ».

**Lot 2 : comptes ouverts**
4. **Inscription par code d'invitation** (B1, B2, B9) : prénom, nom, identifiant, courriel, mot de passe
   deux fois, code, pot de miel, et une case obligatoire « mes photos sont accessibles par leur lien et
   gardent leur position GPS » (A22). Le compte est créé inactif, `is_staff`, dans le groupe Apprenant ;
   le formateur du code devient le référent par défaut de ses stages ; prénom et nom préremplissent
   `apprenant_nom` du premier stage.
5. **Vérification du courriel** (B4) : lien à usage unique qui active le compte ; les comptes jamais
   confirmés sont purgés après 7 jours, au plus une fois par heure lors d'une requête (pas de tâche
   planifiée).
6. **Connexion unique et protégée** (B4, B6) : une seule page publique `/connexion/`, aussi utilisée par
   l'admin (`/admin/login/` y redirige) ; blocage de 15 min après 5 échecs pour un même identifiant.
7. **Mot de passe oublié** (B4) : réinitialisation par courriel, lien valable 24 h. Le changement de mot
   de passe d'un utilisateur connecté reste celui de l'admin Unfold.
8. **Codes du formateur** (B2, B7) : chaque formateur crée, désactive et régénère ses propres codes dans
   l'admin et voit combien d'apprenants les ont utilisés. Un code a 5 usages et 90 jours de validité par
   défaut. Les comptes formateurs restent créés par le superutilisateur.
9. **Garde-fous du disque** (B8) : inscription refusée, avec un message clair, au-delà de 80 % de 512 Mo
   ou quand le nombre d'apprenants actifs atteint `MAX_APPRENANTS` (6 par défaut).
10. **Comptes existants et démo** (B10) : un profil vérifié est créé pour chaque compte existant ; le
    compte `demo.apprenant` ne peut ni changer son mot de passe, ni demander une réinitialisation, ni
    changer son courriel.

### 2. Contraintes techniques

- **Modèle utilisateur** (B3) : on garde `django.contrib.auth.User` et les groupes Apprenant et
  Formateur, sans `AUTH_USER_MODEL` personnalisé. Nouveaux modèles à clé UUID : `Profil` (1-1 avec User :
  `email_verifie`, `code_utilise`), `CodeInvitation` (formateur, code, `expire_le`, `usages_max`, actif),
  `EchecConnexion`, `LimiteInscription`.
- **Port de comptafisca** : vues `django.contrib.auth` écrites à la main, sans django-allauth ni service
  de captcha. Jeton de vérification dérivé de `PasswordResetTokenGenerator`. Codes de 8 caractères sans
  0, O, 1, I ni L. Limite de 5 inscriptions par heure et par IP, l'IP n'étant stockée que sous forme de
  HMAC. Pas d'`i18n_patterns` : URL en français seulement.
- **Courriel** (B5) : SMTP Gmail du compte de comptafisca (port 587, TLS). `EMAIL_HOST_USER` et
  `EMAIL_HOST_PASSWORD` uniquement dans le `.env` du serveur, collés par l'utilisateur ; console en local
  quand `DEBUG` est actif sans mot de passe. Un contrôle `check --deploy` signale un SMTP absent.
  `.env.example` et `DEPLOIEMENT.md` mis à jour.
- **Interface** : gabarits Django et `carnet.css` (structure `.auth` en deux colonnes, `.panel`,
  `.field` reprise de comptafisca et adaptée aux jetons du Carnet), clair et sombre, 390 px. Pas de
  front-end séparé. Surcharges Unfold limitées aux blocs documentés, à revérifier après une montée de
  version.
- **Qualité** : TDD avec pytest-django. Tests repris de `accounts/tests/` de comptafisca et adaptés,
  plus le cloisonnement des codes (formateur A contre formateur B), le verrou du compte démo, la présence
  du bouton « Ajouter un utilisateur » et de la déconnexion. La Definition of Done (P5) s'applique à
  chaque story.
- **Déploiement** (B14) : un déploiement par lot avec le skill `deploy`, puis contrôle Playwright du site
  en ligne. Aucun secret dans le dépôt, la conversation ou les journaux.

### 3. Hors périmètre (strict)

- Inscription sans code d'invitation, et toute inscription d'un formateur ou d'un administrateur (B1, B7).
- Connexion via un réseau social, django-allauth, captcha externe, double authentification.
- `AUTH_USER_MODEL` personnalisé ou reprise des migrations initiales (B3).
- Promotions ou classes de comptafisca, import CSV d'apprenants (B2, B12).
- Page publique de changement du mot de passe hors de l'admin (B4).
- Version anglaise et sélecteur de langue.
- Tâche planifiée sur le serveur pour la purge (B4) ; fournisseur de courriel autre que Gmail SMTP (B5).
- Le reste du hors-périmètre de la section précédente demeure (PWA, LLM sur le serveur, contrôle d'accès
  aux photos, etc.).

## PRD — incrément 4 : comptes ouverts et revue UI/UX

Ce PRD complète le PRD général (section suivante), dont les conventions (UUID, `cree_le`/`modifie_le`,
français, cloisonnement) s'appliquent. Les stories US-32 à US-43 renvoient au journal B1–B14.

### P4-1. Problème, utilisateurs, mesure du succès

- **Problème** :
  - Chaque compte doit aujourd'hui être créé à la main par le superutilisateur, qui devient le goulot
    d'étranglement à chaque rentrée.
  - Un mot de passe oublié n'a pas d'issue sans lui.
  - Dans l'admin, les champs des utilisateurs s'affichent sans style (invisibles), le bouton « Ajouter un
    utilisateur » manque, et la déconnexion se cache au bas d'un menu trop long.
- **Personas** : ceux du PRD général, plus le **visiteur invité**, un futur apprenant qui a reçu un code
  de son formateur et s'inscrit depuis son téléphone.
- **Mesures du succès** :
  - Un invité crée son compte et arrive sur la Note rapide en **moins de 3 minutes**, ouverture du
    courriel comprise.
  - **Aucun compte** n'est créé sans code valide ; aucun inconnu n'occupe le disque.
  - La déconnexion est atteignable en **un clic, sans défiler**, sur chaque écran connecté, à 390 et à
    1440 px.
  - **Aucun champ de formulaire** n'a un bord sous 3:1 de contraste, en clair comme en sombre.
  - Le superutilisateur n'intervient plus que pour créer les formateurs.

### P4-2. User stories

**É9. Interface (lot 1)**

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-32 | superutilisateur | gérer les utilisateurs et les groupes dans l'admin Unfold, avec un bouton « Ajouter un utilisateur » | créer et suivre les comptes sans formulaire illisible | `User` et `Group` réenregistrés avec `unfold.admin.ModelAdmin` et les formulaires `unfold.forms` (création, modification, mot de passe). Le bouton « Ajouter un utilisateur » figure sur la liste. Colonnes : identifiant, nom, courriel, groupe, courriel vérifié, actif, inscrit le, code utilisé. Filtres : groupe, actif, vérifié. À l'ajout, le choix du groupe Apprenant ou Formateur règle `is_staff=True`. Apprenant et formateur : 403 sur ces pages et aucune entrée dans le menu. (B12) | M |
| US-33 | apprenant, formateur ou superutilisateur | un menu de gauche court, en groupes repliables | trouver vite un écran et voir la fin du menu | `UNFOLD["SIDEBAR"]["navigation"]` défini à la main : Mon stage, Journal, Données, Références, Administration ; `show_all_applications=False`. Chaque entrée n'apparaît qu'à qui a le droit de voir le modèle. Le groupe Administration (utilisateurs, groupes, codes de tous) est réservé au superutilisateur. (B11) | M |
| US-34 | utilisateur connecté | un bouton « Se déconnecter » toujours visible | quitter ma session sur un téléphone prêté | Le bouton (formulaire POST, jeton CSRF) est dans l'en-tête de l'admin et dans celui de `carnet/base.html` (Note rapide, Tri des photos). Il est visible sans défiler à 390 et à 1440 px. Après la déconnexion, on revient sur `/`. (B11) | M |
| US-35 | utilisateur | des formulaires lisibles sur tous les écrans | ne plus chercher où saisir | Revue `design-taste-frontend` + Playwright de chaque écran (auth, chaque formulaire d'ajout et de modification de l'admin, Note rapide, Tri des photos, accueil), en clair et en sombre, à 390 et à 1440 px. Chaque champ a un bord ≥ 3:1 sur son fond, un libellé visible et un focus visible ; aucun débordement horizontal. Écarts corrigés (dont `--trait` en sombre dans `carnet.css`) et consignés dans « Charte appliquée ». (B13) | M |

**É10. Comptes ouverts (lot 2)**

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-36 | visiteur invité | créer mon compte avec le code de mon formateur | commencer mon carnet sans attendre l'administrateur | Page `/inscription/` : prénom, nom, identifiant, courriel, mot de passe ×2, code, case A22 obligatoire, pot de miel `site_web`. Refus avec un message par champ : code inconnu, désactivé, expiré ou épuisé ; courriel déjà utilisé par un compte confirmé (sans tenir compte de la casse) ; mot de passe refusé par les 4 validateurs Django ; case non cochée. Pot de miel rempli : fausse réussite, rien n'est créé. Plus de 5 inscriptions par heure pour une même IP (stockée en HMAC) : réponse 429. Succès : User inactif, `is_staff=True`, groupe Apprenant ; Profil avec `email_verifie=False` et `code_utilise` ; un usage de plus sur le code, compté dans la même transaction. (B1, B2, B9) | M |
| US-37 | visiteur invité | confirmer mon courriel par un lien | activer mon compte | Le courriel texte contient un lien `/inscription/verifier/<uidb64>/<jeton>/`. Le jeton couvre pk, horodatage, `is_active`, `email_verifie` et courriel, et ne sert donc qu'une fois. Lien valide : compte actif, `email_verifie=True`, message de réussite, redirection vers `/connexion/`. Lien faux ou déjà utilisé : 400 avec un message clair. Une erreur SMTP supprime le compte et affiche une erreur dans le formulaire. Une nouvelle inscription avec le même identifiant ou le même courriel remplace un compte jamais confirmé. Les comptes jamais confirmés sont purgés après 7 jours, au plus une fois par heure, par un middleware (sans tâche planifiée) ; l'usage du code est alors rendu. (B4, B10) | M |
| US-38 | apprenant inscrit | que mon premier stage connaisse déjà mon nom et mon formateur | gagner du temps et être suivi | À la création de son premier stage, `apprenant_nom` vaut « Prénom Nom » et `formateur_referent` le formateur du code utilisé. Les deux restent modifiables. (B2, B9) | S |
| US-39 | utilisateur | me connecter sur une page unique et protégée | accéder au Carnet sans risque d'attaque par essais | `/connexion/` est la seule page de connexion, et `/admin/login/` y redirige en gardant `next`. Après 5 échecs en 15 min pour un même identifiant (mis en minuscules), la connexion est bloquée 15 min, avec un message dédié ; une réussite remet le compteur à zéro. Un compte inactif ou non vérifié est refusé, avec un message générique. Liens « Créer un compte » et « Mot de passe oublié ». Une fois connecté, on arrive sur la Note rapide, et un utilisateur déjà connecté qui ouvre la page y est redirigé. `LOGIN_URL = "comptes:connexion"`. (B4, B6) | M |
| US-40 | utilisateur | réinitialiser mon mot de passe par courriel | ne pas rester bloqué | `/mot-de-passe/` puis `envoye/`, `<uidb64>/<jeton>/` et `termine/`, en français, avec le style des pages d'authentification. La réponse est la même que le courriel soit connu ou non. Le lien vaut 24 h (`PASSWORD_RESET_TIMEOUT`). Le compte démo est exclu : aucun courriel n'est envoyé. (B4, B10) | M |
| US-41 | formateur | créer et gérer mes codes d'invitation dans l'admin | inviter mes apprenants | `CodeInvitationAdmin` : un formateur ne voit, ne crée et ne modifie que ses codes (404 sur ceux d'un autre) ; le superutilisateur voit tout et choisit le formateur. Code généré de 8 caractères sans 0/O/1/I/L, unique. Par défaut : 5 usages et une expiration à 90 jours. Actions « désactiver », « activer » et « régénérer ». Colonnes : code, usages/maximum, expire le, actif, et le nombre d'apprenants inscrits avec le code. Apprenant : aucun accès. (B2, B7) | M |
| US-42 | superutilisateur | que l'inscription se ferme d'elle-même quand le compte gratuit est plein | protéger les stages en cours | L'inscription est refusée, avec un message qui invite à contacter le formateur, si l'occupation globale dépasse 80 % de 512 Mo (même calcul que US-26) ou si le nombre d'apprenants actifs atteint `MAX_APPRENANTS` (6 par défaut, lu dans le `.env`). La page affiche alors ce message sans formulaire. (B8) | M |
| US-43 | superutilisateur | que les comptes existants et le compte démo restent sûrs | ne rien casser en ouvrant l'inscription | Une migration de données crée un Profil avec `email_verifie=True` pour chaque User existant, et un signal en crée un pour tout User ajouté dans l'admin. La purge ne touche jamais un compte actif ni un compte vérifié. `demo.apprenant` ne peut changer ni son mot de passe (403 sur la page de l'admin) ni son courriel, et ne reçoit pas de réinitialisation ; `charger_demo` reste idempotent. (B10) | M |

**É11. Mise en service**

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-44 | superutilisateur | configurer l'envoi des courriels sans exposer le secret | mettre l'inscription en ligne | Réglages SMTP Gmail (587, TLS) lus dans le `.env` : `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (« Carnet de stage <…> »). Console si `DEBUG` et pas de mot de passe. Le check `comptes.E001` échoue sous `--deploy` si le SMTP manque. `.env.example` (sans valeur) et `DEPLOIEMENT.md` mis à jour. L'utilisateur colle lui-même le mot de passe. (B5, B14) | M |

### P4-3. Modèle logique des données

Conventions du PRD général (UUID, `cree_le`, `modifie_le`). Nouvelle application Django `comptes/`.

| Entité | Attributs principaux | Relations | Règles |
|---|---|---|---|
| **User** (Django, inchangé) | identifiant, courriel, prénom, nom, `is_active`, `is_staff`, groupes, `date_joined` | — | Pas d'`AUTH_USER_MODEL` personnalisé (B3). Inscrit : `is_active=False` jusqu'à la vérification, `is_staff=True`, groupe Apprenant. |
| **Profil** | `email_verifie` (booléen), `inscrit_par_formulaire` (booléen) | 1–1 → User ; → CodeInvitation `code_utilise`? | Créé par migration (existants : vérifié) et par signal. Purgeable seulement si `inscrit_par_formulaire`, non vérifié, inactif et `date_joined` de plus de 7 jours. |
| **CodeInvitation** | `code` (8 caractères), `usages_max` (5), `usages` (0), `expire_le` (+90 j), `actif` | → User `formateur` (groupe Formateur ou superutilisateur) | `code` unique, sans 0/O/1/I/L. Utilisable si actif, non expiré et `usages < usages_max`. L'incrément de `usages` se fait sous verrou (`select_for_update`) dans la transaction de l'inscription. Cloisonné par formateur. |
| **EchecConnexion** | `identifiant` (minuscules), `survenu_le` | — | Compté sur 15 min ; supprimé après une réussite ou au-delà de 24 h. |
| **LimiteInscription** | `ip_hachee` (HMAC-SHA256 avec `SECRET_KEY`), `survenu_le` | — | Lignes de plus d'1 h supprimées à chaque contrôle. Jamais d'IP en clair. |
| **Stage** (existant) | — | `formateur_referent` prérempli depuis `Profil.code_utilise.formateur` | Préremplissage au premier stage seulement (US-38). |

Réglages ajoutés : `MAX_APPRENANTS` (6), `LOGIN_MAX_ECHECS` (5), `LOGIN_BLOCAGE` (15 min),
`INSCRIPTIONS_MAX_PAR_HEURE` (5), `INSCRIPTION_IP_HEADER` (`REMOTE_ADDR`, `HTTP_X_REAL_IP` en production),
`PASSWORD_RESET_TIMEOUT` (24 h), `LOGOUT_REDIRECT_URL = "/"`.

### P4-4. Contrat des URL et des courriels

```
/connexion/                                    comptes:connexion        (GET, POST)
/deconnexion/                                  comptes:deconnexion      (POST seulement)
/inscription/                                  comptes:inscription      (GET, POST ; 429 si limite)
/inscription/envoye/                           comptes:inscription_envoyee
/inscription/verifier/<uidb64>/<jeton>/        comptes:verifier         (400 si jeton invalide)
/mot-de-passe/                                 comptes:mdp_oublie
/mot-de-passe/envoye/                          comptes:mdp_envoye
/mot-de-passe/<uidb64>/<jeton>/                comptes:mdp_nouveau
/mot-de-passe/termine/                         comptes:mdp_termine
/admin/login/                                  → redirection 302 vers /connexion/?next=…
comptes/email/verifier.txt, mdp_oublie.txt, mdp_oublie_objet.txt   (texte brut, français)
```

### P4-5. Definition of Done (critères stricts)

**Pour chaque story US-32 à US-44** : les 7 critères de P5 du PRD général s'appliquent tous, et en plus :
1. **Cloisonnement des comptes** testé : apprenant contre formateur contre superutilisateur pour l'admin
   des utilisateurs ; formateur A contre formateur B pour les codes ; aucune page d'authentification ne
   révèle si un identifiant ou un courriel existe (hormis le doublon de courriel d'un compte confirmé à
   l'inscription).
2. **Sécurité** : chaque formulaire porte un jeton CSRF ; la déconnexion n'accepte que POST ; aucun
   courriel, mot de passe, jeton ni IP en clair dans les journaux ; `check --deploy` ne signale rien de
   nouveau, `comptes.E001` compris.
3. **Courriels** testés avec `mail.outbox` (destinataire, objet, lien absolu, français) ; aucun appel SMTP
   réel dans les tests.
4. **Écrans** : capture Playwright en clair, en sombre, à 390 et à 1440 px pour chaque page touchée ;
   aucun débordement ; champs au contraste ≥ 3:1, libellé et focus visibles ; déconnexion visible sans
   défiler.
5. **Secret** : le mot de passe SMTP n'apparaît dans aucun fichier du dépôt, aucun message, aucune
   commande exécutée par l'agent.

**Lot 1 (US-32 à US-35)** : terminé quand, sur le site en ligne, Playwright montre :
- en superutilisateur, le bouton « Ajouter un utilisateur » et un formulaire d'ajout aux champs visibles ;
- en apprenant, un menu sans « Utilisateurs » et la déconnexion visible à 390 px ;
- la section « Charte appliquée » complétée.

**Lot 2 (US-36 à US-44)** : terminé quand :
- **En local** (courriel console) : Playwright enchaîne inscription avec code, ouverture du lien,
  connexion, Note rapide avec photo, puis déconnexion ; un code épuisé, un code expiré, la 6ᵉ inscription
  de l'heure et le 6ᵉ échec de connexion sont refusés.
- **En ligne, après le collage du mot de passe SMTP par l'utilisateur** : une inscription réelle avec un
  code de test reçoit le courriel et s'active, puis le compte et le code de test sont supprimés.
- **Comptes existants** : `fokou` et `demo.apprenant` se connectent toujours, et le compte démo reste
  verrouillé.

## PRD — « Carnet de stage »

### P1. Problème, utilisateurs, mesure du succès

- **Problème** : en fin de stage, l'apprenant doit rédiger un rapport conforme au cours (Module 2), mais
  les informations du terrain sont perdues, dispersées ou non sourcées. Le cours le dit lui-même : « une
  fois que vous aurez quitté les murs de l'entreprise, il vous sera peut-être difficile d'accéder à
  certaines informations ».
- **Personas** :
  - **Apprenant** : sur le chantier, au téléphone, avec une connexion médiocre. Il saisit vite.
  - **Formateur référent** : lit les notes et laisse des remarques.
  - **Superutilisateur** (le porteur du projet) : crée les comptes, règle les quotas, déploie, puis
    importe les dossiers en local pour produire le rapport.
- **Mesures du succès** :
  - Une note rapide prend **moins de 60 s** (texte et une photo) sur un téléphone de milieu de gamme.
  - En fin de stage, le tableau de bord n'affiche **aucune rubrique obligatoire vide**.
  - Le zip importé produit un PDF qui compile **sans erreur**, sans aucun `\AC{}` pour les données saisies.
  - Le disque du compte reste **sous 80 %** avec 4 stages actifs.

### P2. User stories

Priorités : **M** = indispensable (Must), **S** = souhaitable (Should). Chaque story renvoie à une
décision du journal A1–A36.

**É1. Comptes et accès** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-01 | superutilisateur | créer les comptes des apprenants et des formateurs, et les placer dans un groupe | contrôler qui accède | Pas de page d'inscription. Commande `creer_groupes` idempotente. (A13) | M |
| US-02 | apprenant | ne voir et ne modifier que mes stages et tout ce qui en dépend | protéger mes données | Accès à l'objet d'un autre apprenant, par la liste ou par l'URL : 404. Testé pour **chaque** modèle. (A1) | M |
| US-03 | formateur | voir en lecture les stages dont je suis référent et annoter une note | suivre l'apprenant | Seul `remarque_formateur` est modifiable. Les autres stages sont invisibles. (A32) | M |
| US-04 | apprenant | avoir plusieurs stages et choisir le stage actif | suivre plusieurs périodes | Le stage actif est mémorisé en session. La note rapide s'y rattache. (A1) | S |

**É2. Stage, fiche entreprise, mission** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-05 | apprenant | renseigner la couverture (9 champs du cours, logos, spécialité, thème) | produire `infos.tex` | Tous les champs sont facultatifs à la saisie. Les champs vides deviennent `\AC{}` à l'export. (A2, A3) | M |
| US-06 | apprenant | compléter au fil du stage les 11 rubriques de la fiche entreprise | décrire l'entreprise comme l'exige le cours | Un champ Markdown par rubrique. Les notes étiquetées s'affichent en dessous, en lecture. (A23) | M |
| US-07 | apprenant | compléter les 9 rubriques de la mission | décrire mon poste | Même fonctionnement que US-06. (A23) | M |
| US-08 | apprenant | répondre au bilan personnel (7 questions, critiques et suggestions) | nourrir la Partie IV et la conclusion | Un formulaire par stage. (A3) | M |
| US-09 | apprenant | saisir l'organigramme en arbre et marquer mon poste | générer la figure | Un seul nœud « stagiaire » par stage. Pas de cycle (validation). Aperçu en arbre. (A25) | M |

**É3. Journal et note rapide** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-10 | apprenant | créer une note rapide au téléphone : texte, photos, GPS automatique, étiquettes | ne rien perdre sur le terrain | Trois actions au plus. Le brouillon survit à un rechargement (stockage local du navigateur). Affichage correct à 390 px. (A29, A6) | M |
| US-11 | apprenant | compléter une note dans l'admin avec les champs du rapport d'activité et le bloc intervention | produire un journal exploitable | Onglets repliables. Bascule « complétée ». (A3, A29) | M |
| US-12 | apprenant | étiqueter une note avec plusieurs rubriques (cours ou thème) | la retrouver dans la bonne partie | Plusieurs étiquettes possibles. Filtre par rubrique. (A24) | M |
| US-13 | apprenant | créer et réordonner les chapitres de mon thème, avec un niveau de sous-chapitres | structurer la Partie III | Les chapitres d'un stage sont invisibles des autres. Les rubriques du cours ne sont pas modifiables. (A24) | M |
| US-14 | apprenant | rattacher une note à une tâche, à des équipements, à des personnes et à un lieu | relier les faits | Tous les liens sont facultatifs. (A26, A27, A31, A36) | S |

**É4. Photos et lieux** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-15 | apprenant | téléverser une photo compressée, avec ses coordonnées GPS lues dans l'EXIF ou fournies par le navigateur | illustrer et localiser | Image ramenée à 1600 px au plus, JPEG d'environ 300 Ko, nommée par UUID. Coordonnées enregistrées. (A5, A21, A22) | M |
| US-16 | apprenant | trier mes photos en grille (à trier, corps, annexe, preuve) avec légende et slug | choisir ce qui ira dans le rapport | Changement de destination en un clic. Alerte au-delà de 25 photos dans le corps. (A35) | M |
| US-17 | apprenant | créer des lieux sur une carte ou à partir de ma position, avec des repères | produire le plan de situation | Lieu proposé automatiquement à moins de 200 m. (A31) | M |
| US-18 | apprenant | être bloqué avec un message clair quand mon quota est atteint | protéger le compte commun | Envoi refusé au-delà du quota. Quota restant affiché. (A33) | M |

**É5. Données techniques et références** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-19 | apprenant | saisir des équipements réutilisables (outillage, matériel, EPI, appareils de mesure) | générer les tableaux | Un tableau LaTeX par catégorie à l'export. (A27) | M |
| US-20 | apprenant | saisir un relevé ou une valeur de référence | n'utiliser que des chiffres traçables | Une valeur de référence sans source est refusée. Un relevé est rattaché à une note. (A28) | M |
| US-21 | apprenant | saisir des références bibliographiques | produire `references.bib` | Clé BibTeX générée et unique pour chaque stage. (A28) | M |
| US-22 | apprenant | saisir des personnes (« à remercier », « nom publiable ») et des abréviations | rédiger les remerciements et la table des abréviations | Le téléphone n'est jamais exporté. Une personne dont le nom n'est pas publiable est exportée par sa fonction. (A36) | M |
| US-23 | apprenant | saisir des tâches avec leurs dates | générer le Gantt réel | Une tâche sans date de fin s'arrête à la fin du stage. (A26) | M |

**É6. Calendrier et tableau de bord** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-24 | apprenant | déclarer mes jours travaillés et mes absences | éviter les fausses alertes | Lundi–samedi par défaut. Jours fériés fixes du Cameroun préchargés. (A30) | M |
| US-25 | apprenant | voir un tableau de bord | savoir ce qui manque | Il affiche les rubriques vides, les notes non complétées, les jours ouvrés sans note, les photos par destination, le quota, l'âge de la dernière sauvegarde (orange après 7 jours) et le taux de présence. (A16, A23, A29, A30) | M |
| US-26 | superutilisateur | voir l'occupation globale du disque | anticiper la saturation | Alerte au-delà de 80 % de 512 Mo. (A33) | M |

**É7. Export, sauvegarde, import** (incréments 2 et 3)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-27 | apprenant | télécharger le zip « dossier terrain » de mon stage | sauvegarder et transmettre | Zip généré en flux, jamais stocké sur le serveur. Contenu conforme à P4. La date de dernière sauvegarde est mise à jour. (A4, A16) | M |
| US-28 | superutilisateur | restaurer un zip dans l'application | récupérer après une perte | La restauration conserve les UUID et les liens. Restaurer deux fois ne crée pas de doublons. (A16) | M |
| US-29 | superutilisateur | importer un zip en local dans `rapports/<slug>-<uuid8>/` | rédiger le rapport réel | Copie du modèle, fichiers générés, plans OSM. Refus sans `--force` si le dossier existe. (A15, A21, A31) | M |
| US-30 | superutilisateur | suivre la procédure documentée jusqu'au PDF et au PPTX | livrer le rapport | La procédure figure dans AGENTS.md. `compile-latex.ps1 -Dir rapports/<dossier>` se termine sans erreur. | M |

**É8. Déploiement** (incrément 1)

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-31 | superutilisateur | une application en ligne sur `esrventisax.pythonanywhere.com` | permettre la saisie sur le terrain | `DEBUG=False`, HTTPS, secrets dans un `.env`, `collectstatic` exécuté, mappings `/static/` et `/media/` en place. Procédure dans `webapp/DEPLOIEMENT.md`. (A7, A17, A19) | M |

### P3. Modèle logique des données

Conventions communes :
- Clé primaire `id` en **UUID** ; champs `cree_le` et `modifie_le` sur tous les modèles.
- Un `stage` en clé étrangère sur toute entité propre à un stage, ce qui sert au cloisonnement.
- Les champs texte sont en **Markdown minimal**.
- Notation : `?` = facultatif ; `→` = clé étrangère (FK) ; `↔` = relation plusieurs-à-plusieurs (M2M).

| Entité | Attributs principaux | Relations | Règles |
|---|---|---|---|
| **User** (Django) | identifiant, mot de passe, groupes | — | Groupes « Apprenant » et « Formateur ». |
| **Stage** | intitule, specialite, theme, sous_theme ; couverture : apprenant_nom, cfp, cfp_sigle, diplome, annee_etude, session, entreprise, entreprise_sigle, tuteur_pro, tuteur_pro_poste, tuteur_acad, tuteur_acad_poste ; date_debut, date_fin ; logo_entreprise?, logo_cfp? ; jours_travailles (liste de jours, lundi–samedi) ; quota_mo (80) ; derniere_sauvegarde? ; slug | → User `proprietaire` ; → User `formateur_referent`? | `date_fin` ≥ `date_debut`. |
| **FicheEntreprise** | presentation, organisation, historique, secteurs, marches, clients_fournisseurs, concurrence, chiffres_cles, perspectives_swot, mutations_technologiques, volonte_dirigeants ; adresse, contact, creation, effectif, capital | 1–1 avec Stage | 11 rubriques du cours, plus les champs d'identité de `infos.tex`. |
| **Mission** | poste, position_organigramme, faits_importants, objectifs_enjeux, methodes_moyens, collaborateurs, responsabilites, resultats, difficultes_solutions | 1–1 avec Stage | 9 rubriques du cours. |
| **BilanPersonnel** | pourquoi_ce_stage, appreciation, attentes_atteintes, apprecie_comme_stagiaire, resultats_remarques, travail_equipe, consequence_carriere, critiques, suggestions | 1–1 avec Stage | Questions de la p. 24 et Partie IV. |
| **Rubrique** | code, libelle, niveau (cours, thème), partie (entreprise, mission, intro, thème, critiques, conclusion, bilan), ordre | → Stage? (vide pour le cours) ; → Rubrique `parent`? | Rubrique du cours : sans stage, non modifiable. Rubrique de thème : `parent` toujours de niveau 1. |
| **Lieu** | nom, type (siège, chantier, fournisseur, autre), latitude, longitude, reperes, ville, quartier | → Stage | Coordonnées dans les bornes valides. |
| **Tache** | libelle, date_debut, date_fin?, description? | → Stage ; → Lieu? ; → Rubrique? | Fin vide : arrêt à la fin du stage pour le Gantt. |
| **EntreeJournal** | date, heure ; texte (note rapide) ; objectifs, moyens_humains, moyens_materiels, methodologie, activites, elements_theoriques, difficultes, solutions, appreciation ; intervention : nature?, duree_immobilisation?, cout?, ressources? ; completee (booléen) ; remarque_formateur? ; latitude?, longitude? | → Stage ; → Lieu? ; → Tache? ; ↔ Rubrique ; ↔ Equipement ; ↔ Personne | Plusieurs notes par jour. |
| **Photo** | fichier (nom UUID), latitude?, longitude?, prise_le?, legende?, slug?, destination (à trier, corps, annexe, preuve), taille_octets | → Stage ; → EntreeJournal? ; → Lieu? ; ↔ Rubrique | Corps ou annexe : slug et légende exigés à l'export ; slug unique pour chaque stage. |
| **Equipement** | designation, categorie (outillage, matériel ou matériau, EPI, mesure), caracteristiques, role, quantite? | → Stage ; → Photo? ; ↔ Rubrique | — |
| **Reference** | type (norme, ouvrage, notice, web, oral), auteur, titre, annee?, editeur?, url?, cle_bibtex | → Stage | Clé générée, unique pour chaque stage. |
| **DonneeTechnique** | grandeur, valeur (décimal), unite, nature (relevé, référence), date | → Stage ; → Rubrique? ; → EntreeJournal? ; → Reference? | Référence : `reference` exigée. Relevé : `entree` exigée. |
| **Personne** | nom, fonction, role (encadreur pro, encadreur acad, collègue, client, autre), telephone?, a_remercier, nom_publiable | → Stage | Le téléphone n'est jamais exporté. |
| **NoeudOrganigramme** | poste, nom?, est_stagiaire, ordre | → Stage ; → NoeudOrganigramme `parent`? | Un seul stagiaire par stage. Pas de cycle. |
| **Absence** | date_debut, date_fin, motif (férié, maladie, congé, intempérie, cours CFP), libelle? | → Stage? (vide pour les fériés communs) | Fériés fixes du Cameroun créés par une migration. |
| **Abreviation** | sigle, signification | → Stage | Sigle unique pour chaque stage. |

### P4. Contrat d'export (zip « dossier terrain »)

```
manifest.json                 # version du format, UUID et slug du stage, date, checksums
terrain.json                  # toutes les entités du stage (UUID conservés), sert à la restauration
terrain.md                    # lecture humaine et rédaction : classé selon le plan du cours, notes datées sous chaque rubrique
config/infos.tex              # macros \Info..., \AC{} pour chaque champ vide
img/fig_<slug>.jpg            # photos de destination corps et annexe uniquement
img/logo_entreprise.*, img/logo_cfp.*
figures/organigramme.tex, figures/gantt.tex
tableaux/equipements_<categorie>.tex
bib/references.bib
```

### P5. Definition of Done (critères stricts)

**Pour chaque user story**, la story n'est terminée que si tous ces points sont vrais :
1. Ses critères d'acceptation sont couverts par au moins un **test pytest** écrit avant le code (TDD), et
   `pytest` passe entièrement.
2. Le **cloisonnement** est testé pour tout nouveau modèle ou toute nouvelle vue : apprenant A contre
   apprenant B, formateur référent contre formateur non référent.
3. `python manage.py check --deploy` ne signale rien de nouveau, et `makemigrations --check` n'en génère
   aucune.
4. L'interface est en français et utilise les libellés du cours. Pour un écran, une capture Playwright en
   clair, en sombre et à **390 px** de large ne présente aucun débordement horizontal.
5. Tout texte exporté passe par l'échappement LaTeX : un test contient `& % $ # _ { } ~ ^ \` et « 50 % ».
6. Aucun secret, aucune donnée réelle, aucun fichier `db.sqlite3`, `media/`, `.env`, `rapports/` ni
   `*.zip` dans `git status` ou dans le diff.
7. Un commit conventionnel est fait sur `develop`, et AGENTS.md est mis à jour si une décision change.

**Pour chaque incrément** :
- **Incrément 1** : US-01 à US-26 et US-31 terminées. L'application est déployée sur PythonAnywhere. Sur le site en
  ligne, une note rapide avec photo et GPS (simulé) est créée par Playwright. Un apprenant ne voit pas les
  données d'un autre. Le quota bloque l'envoi d'une photo au-delà de la limite.
- **Incrément 2** : US-27 et US-28 terminées. L'aller-retour export → restauration dans une base vide
  redonne des entités **identiques**, UUID et relations compris. Le zip est conforme à P4.
- **Incrément 3** : US-29 et US-30 terminées. Pour un stage fictif complet, la chaîne
  `importer_dossier` → `compile-latex.ps1 -Dir rapports/<dossier>` produit un PDF sans erreur. Ce PDF contient
  l'organigramme, le Gantt, au moins un tableau d'équipement, un plan de situation, les photos du corps
  et une bibliographie non vide. Aucun `\AC{}` ne subsiste pour les champs saisis. `rapports/` reste
  ignoré par git.

**Pour la livraison finale** : l'utilisateur relit et valide une seule fois (comme Q16), puis le mot de passe
PythonAnywhere est changé.

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

## Journal des décisions : application « Carnet de stage » (grilling du 2026-10-17)

| # | Question | Décision |
|---|---|---|
| A1 | Qui se connecte ? | Plusieurs apprenants cloisonnés ; plusieurs stages par compte. |
| A2 | App générique ? | Oui : spécialité, thème et sous-thème sont des champs ; rien de codé en dur. |
| A3 | Modèle de données ? | Stage, FicheEntreprise, Mission, EntréeJournal (avec bloc intervention), Photo, Personne, Abréviation, Référence, BilanPersonnel, complétés par A24–A36. |
| A4 | Rôle de l'app dans la génération ? | Export d'un zip « dossier terrain » ; rédaction et compilation en local par Claude Code. |
| A5 | Photos et géolocalisation ? | Pillow (1600 px, environ 300 Ko), GPS lu dans l'EXIF ou fourni par le navigateur, Leaflet/OSM côté client. |
| A6 | Usage sur le terrain ? | Web responsive en ligne, brouillon gardé dans le navigateur, pas de PWA en v1. |
| A7 | Déploiement ? | Push GitHub autorisé, clone sur PythonAnywhere via Playwright, secrets dans un `.env` sur le serveur. |
| A8 | Emplacement du code ? | `webapp/` dans ce dépôt, branche `develop`. |
| A9 | Interface ? | Admin Unfold aux couleurs de ventisax et tableau de bord d'avancement. |
| A10 | Langue ? | Français, libellés repris du cours. |
| A11 | Identité visuelle ? | Nom « Carnet de stage », logo neutre, palette et police de ventisax. |
| A12 | Versions ? | Django 5.2 LTS, django-unfold récent, Python 3.13 sur PythonAnywhere. |
| A13 | Comptes ? | Créés par le superutilisateur ; groupes Apprenant et Formateur ; remarque du formateur sur les notes. |
| A14 | Données personnelles et dépôt ? | Le dépôt reste **public** : jamais de base, de médias, de `.env`, de zips ni de rapports réels versionnés. |
| A15 | Import local ? | `importer_dossier` : `infos.tex`, `img/fig_<slug>.jpg`, `donnees_terrain/{terrain.json, terrain.md}`. |
| A16 | Sauvegarde ? | Le zip sert de sauvegarde ; restauration par `restaurer_dossier` ; alerte après 7 jours. |
| A17 | Maintien du compte gratuit ? | Documenté dans `webapp/DEPLOIEMENT.md` (renouvellement tous les 3 mois). |
| A18 | Tests ? | TDD avec pytest-django (cloisonnement, EXIF, échappement LaTeX, export et import) et vérification avec Playwright. |
| A19 | Accès au code depuis PythonAnywhere ? | Dépôt public : `git clone` HTTPS sans jeton, mises à jour par `git pull`. |
| A20 | Livraison ? | 3 incréments : saisie et déploiement ; export et sauvegarde ; import local et documentation. |
| A21 | Où vit un rapport réel ? | Dans `rapports/<slug>-<uuid8>/` (ignoré par git), copie du modèle `tex_export_src/`, sans écrasement sauf `--force`. UUID comme clé primaire. |
| A22 | Accès aux photos ? | `/media/` public, EXIF conservé (choix assumé). |
| A23 | Lien entre fiche et journal ? | Fiche et Mission sont des formulaires ; une note peut porter l'étiquette d'une rubrique ; rubriques vides signalées. |
| A24 | Référentiel des rubriques ? | Deux niveaux : rubriques du cours, fixes ; chapitres du thème, libres pour chaque stage. Plusieurs étiquettes possibles. |
| A25 | Organigramme ? | Saisi en données, génération de `figures/organigramme.tex`, photo facultative en plus. |
| A26 | Planning ? | Modèle Tâche ; note rattachée à une tâche si on veut ; `figures/gantt.tex` généré par semaine. |
| A27 | Matériel ? | Équipement réutilisable (outillage, matériel, EPI, appareils de mesure) ; un tableau LaTeX par catégorie. |
| A28 | Valeurs techniques ? | DonnéeTechnique (relevé ou référence) ; source obligatoire pour une référence ; `references.bib` généré. |
| A29 | Saisie rapide ? | Page « Note rapide » mobile, complétée ensuite dans l'admin ; alertes pour les notes non complétées et les jours sans note. |
| A30 | Jours ouvrés ? | Jours travaillés (lundi–samedi), absences, jours fériés fixes du Cameroun, taux de présence. |
| A31 | Géolocalisation ? | Modèle Lieu, rattachement automatique à moins de 200 m, plan de situation OSM généré à l'import local. |
| A32 | Que voit un formateur ? | Seulement les stages dont il est référent. |
| A33 | Quota disque ? | Environ 4 apprenants : 80 Mo par stage, zips générés en flux, alerte globale à 80 %. |
| A34 | Format des textes ? | Markdown minimal, converti en LaTeX par un convertisseur testé. |
| A35 | Photos du rapport ? | Destination à trier, corps, annexe ou preuve ; seules corps et annexe sont exportées ; vue de tri en grille. |
| A36 | Personnes ? | Cases « à remercier » et « nom publiable » ; téléphone jamais exporté. |
| A38 | Démo publique (2026-10-18) ? | `charger_demo` : compte `demo.apprenant` / `demo-local-2026` (identifiant public assumé, données fictives) et stage complet (EDEMO, logo démo, chantier R+10). `rediger_demo` remplit les `\AC{}` des parties. Résultat versionné dans `demo/`. Champ `Lieu.niveaux` (→ `\InfoChantierNiveaux`). Organigramme : écart mesuré entre blocs (plus de chevauchement). |
| A39 | Aide en ligne avant la connexion (2026-11-06) ? | Page d'accueil publique sur `/` (gabarit Django, `carnet/accueil.css`, sans framework) conçue avec `design-taste-frontend` : héros avec capture réelle, rythme jour/soir/samedi, bento, pages du rapport de démo, identifiants démo (A38), liens vers `docs/manuel/` sur GitHub. Aucune donnée d'apprenant. Connecté : redirection vers la Note rapide. Lien « Découvrir le Carnet et la démo » sous la connexion, `SITE_URL` = `/`. Images WebP (≈ 175 Ko) dans `static/carnet/accueil/`. Tests : `tests/test_accueil.py`. |
| A40 | Formation des apprenants (2026-11-06) ? | Fiches imprimables d'un stage du samedi, une par journée, dans `docs/formation/` (HTML + `formation.css`, PDF par `generer_pdf.py`). Publiées sur l'accueil public, section « Se former, samedi après samedi » : la fiche du prochain samedi à la une avec sa couverture, les autres en lignes, libellé unique « Télécharger la fiche ». PDF et couvertures copiés par le script dans `static/carnet/formation/` ; liste dans `carnet/formation.py`. Chiffres des fiches sans valeur inventée (renvoi à la notice). |
| A37 | Revue visuelle Playwright (2026-10-18) ? | Voir « Charte appliquée » ci-dessous : traduction d'Unfold, primaire `#0d665e`, tri sans accents, accessibilité de la navigation mobile. |

### Charte appliquée (revue visuelle du 2026-10-18)

Contrôlée avec Playwright en clair et en sombre, à 390 et à 1440 px : aucun débordement horizontal.
- **Traduction d'Unfold** : django-unfold 0.110 n'a pas de catalogue français. `webapp/locale/fr/LC_MESSAGES/django.po`
  (`LOCALE_PATHS`) traduit ses chaînes : « Bon retour sur », « Rechercher… », « Filtres », etc. Le `.mo` est versionné.
  Après une montée de version d'Unfold, chercher les chaînes anglaises restantes et recompiler avec `msgfmt`.
- **Couleur primaire** : `primary-600` = `#0d665e`, le turquoise foncé de la charte, au lieu de `#12867a` (hors charte, blanc à
  4,3:1). Boutons Unfold et titres de connexion au contraste AA. Échelle : 700 `#0b5750`, 800 `#0e4a44`.
- **Tri des menus** : modèles triés sans accents (`carnet/admin.py`) : « Équipements » après « Données techniques ».
- **Tableau de bord** : titre du stage en `base-900` (`base-100` en sombre) au lieu du gris hérité.
- **Navigation mobile (≤ 520 px)** : libellés masqués visuellement, mais toujours lus par les lecteurs d'écran (le lien
  ne s'annonce plus « edit_note »).
- **Journal sur mobile** : la colonne « Note » garde au moins 15rem ; le tableau défile dans son cadre.
- Tests : `webapp/tests/test_interface.py`.

### Charte appliquée : comptes ouverts (revue UI/UX du 2026-11-08, B13)

Contrôlée avec Playwright en clair et en sombre, à 390 et à 1440 px, sur les pages d'authentification,
l'admin des utilisateurs, le formulaire d'un stage, la Note rapide, le Tri des photos et l'accueil : aucun
débordement horizontal.
- **Bords des champs ≥ 3:1** (WCAG 1.4.11). Le jeton `--trait` (`#e1e7ea`, 1,1:1 sur `--papier`) était la
  cause des « champs qui n'apparaissent pas ». Nouveau jeton `--trait-champ` : `#71889a` en clair (3,4:1),
  `#7f97a6` en sombre (4,9:1), appliqué aux champs, aux étiquettes `.choix` et aux boutons `.segments`.
  Dans l'admin, `admin.css` impose `base-500` aux champs Unfold (`border-base-200` donnait 1,3:1), sauf en
  erreur.
- **Pages d'authentification** (`comptes/templates/comptes/`) : deux colonnes au-delà de 900 px (arguments
  et capture réelle de la Note rapide à gauche, formulaire à droite), une seule colonne sur téléphone, le
  formulaire avant les arguments. Champs de 48 px, libellé au-dessus, aide puis erreur dessous, aides de
  Django raccourcies, pas de focus automatique, `autocomplete` renseigné. Pot de miel hors écran.
- **Bouton d'ajout libellé** : surcharge `templates/unfold/helpers/add_link.html`, libellé tiré de
  `libelle_ajout` (« Ajouter un utilisateur », « Ajouter un code »), absent de la page d'ajout elle-même,
  icône seule sous 520 px.
- **Déconnexion** : surcharge `templates/unfold/helpers/userlinks.html` (en-tête admin) et formulaire dans
  `carnet/base.html` ; libellé masqué visuellement sous 520 px, toujours lu par les lecteurs d'écran.
- **En-têtes étroits** : sous 400 px (Note rapide, Tri) et 560 px (accueil, deux boutons), le nom « Carnet
  de stage » est masqué visuellement à côté de la pastille.
- Message d'Unfold resté en anglais sur l'ajout d'un utilisateur : traduit dans `locale/fr` (`.mo`
  recompilé).
- Surcharges à revérifier après une montée de version d'Unfold : `add_link.html`, `userlinks.html`, le
  sélecteur de bords dans `admin.css`.

## Journal des décisions : comptes ouverts et revue UI/UX (grilling du 2026-11-08)

| # | Question | Décision |
|---|---|---|
| B1 | Lever A13 et ouvrir l'inscription ? | Oui, comme comptafisca (courriel vérifié, pot de miel, limites), mais seulement avec un code d'invitation. Compte placé dans le groupe Apprenant. |
| B2 | Qui émet le code, que porte-t-il ? | Modèle `CodeInvitation` lié à un formateur : 8 caractères sans 0/O/1/I/L, expiration, usages max. Le formateur devient le référent par défaut des stages de l'apprenant. |
| B3 | Modèle utilisateur ? | Garder `django.contrib.auth.User` et les groupes ; nouveau `Profil` 1-1 (UUID, `email_verifie`, `code_utilise`). Pas d'`AUTH_USER_MODEL` personnalisé. |
| B4 | Parcours repris ? | Tout comptafisca : inscription, vérification, connexion avec blocage (5 échecs → 15 min), déconnexion, mot de passe oublié par courriel. Changement connecté : admin Unfold. |
| B5 | Compte d'envoi des courriels ? | Même Gmail SMTP que comptafisca, mot de passe d'application dans le `.env` du serveur seulement ; console en local. |
| B6 | Page de connexion ? | Une seule page publique `/connexion/` (et `/inscription/`, `/mot-de-passe/…`), style comptafisca adapté à `carnet.css` ; `/admin/login/` y redirige. Inscrit : `is_staff` et groupe Apprenant. |
| B7 | Formateurs et codes ? | Comptes formateurs créés par le superutilisateur seulement ; chaque formateur gère ses propres codes dans l'admin (cloisonnement testé) et voit leurs usages. |
| B8 | Garde-fou du disque ? | Code : 5 usages et 90 jours par défaut. Inscription refusée au-delà de 80 % de 512 Mo ou de `MAX_APPRENANTS` (6) apprenants actifs. |
| B9 | Champs d'inscription ? | Prénom, nom, identifiant, courriel, mot de passe ×2, code, pot de miel, case obligatoire d'avertissement A22. Prénom et nom préremplissent `apprenant_nom`. |
| B10 | Comptes existants et démo ? | Migration : profil vérifié pour chaque compte ; purge limitée aux inscrits inactifs non vérifiés. Compte démo verrouillé (mot de passe, réinitialisation, courriel). |
| B11 | Déconnexion inaccessible ? | Navigation Unfold à la main, en groupes repliables, sans liste automatique ; bouton « Se déconnecter » dans l'en-tête de l'admin et des pages publiques. |
| B12 | Liste des utilisateurs ? | `UserAdmin` et `GroupAdmin` Unfold avec leurs formulaires ; bouton « Ajouter un utilisateur », colonnes et filtres utiles, choix du groupe à l'ajout ; réservé au superutilisateur. |
| B13 | Portée de la revue UI/UX ? | Tous les écrans, en clair et en sombre, à 390 et 1440 px ; bord de champ ≥ 3:1, libellé et focus visibles, aucun débordement. |
| B14 | Livraison ? | Deux lots (interface, puis comptes ouverts), deux déploiements ; l'utilisateur colle lui-même le mot de passe SMTP dans le `.env` du serveur. |

## Points à valider par l'utilisateur

- Remplir `config/infos.tex` (noms, CFP, entreprise, chantier, dates, encadreurs et leurs postes).
- Remplacer les images factices `img/fig_*.png` et les logos factices.
- Adapter le planning type (partie II) aux activités réellement menées.
- Vérifier les données chiffrées de l'entreprise (`\AC{}` restants).
