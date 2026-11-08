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
1. **Comptes et cloisonnement** (A1, A13, A32) : inscription libre en tant qu'apprenant (B19). Un
   apprenant ne voit que ses propres stages et peut en avoir plusieurs. Plus de compte formateur (B17) : son
   nom est un libellé de la couverture.
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
- Connexion via un réseau social (A13 revu par B19 : inscription libre et réinitialisation par courriel,
  incrément 4 ci-dessous). Compte formateur (B17).
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

Ouvrir le Carnet à tout apprenant par une inscription libre, sur le modèle de comptafiscaventisax.pythonanywhere.com
(source locale : `c-fiscalite-syscohada/accounts/`, lue directement : REA est inutile sur du code source), et
corriger les défauts d'interface relevés : champs invisibles, bouton « Ajouter un utilisateur » absent,
déconnexion inaccessible quand le menu est long. Décisions : journal B1–B19 (B15 à B19, issus du scénario
apprenant du 2026-11-08, remplacent B1, B2, B7 et la partie formateur de B8 à B11).

### 1. Objectifs fonctionnels prioritaires

**Lot 1 : interface**
1. **Gestion des utilisateurs dans Unfold** (B12, B15) : `User` et `Group` avec les classes et formulaires
   d'Unfold, bouton libellé « Ajouter un utilisateur ». Un utilisateur = **un profil**, seul champ de droits du
   formulaire : Apprenant ou Administrateur. Groupes, statut équipe et superutilisateur en découlent.
   Colonnes : identifiant, nom, courriel, profil, courriel vérifié, actif, inscrit le. Réservé à
   l'administrateur.
2. **Menu court et déconnexion partout** (B11) : navigation Unfold en groupes repliables (Mon stage, Journal,
   Données, Références, Administration réservée à l'administrateur) ; « Se déconnecter » toujours visible
   dans l'en-tête de l'admin, de la Note rapide et du Tri des photos.
3. **Revue UI/UX de tous les écrans** (B13) : bords de champ au contraste ≥ 3:1, libellé et focus visibles,
   aucun débordement, en clair et en sombre, à 390 et 1440 px.

**Lot 2 : comptes ouverts**
4. **Inscription libre en tant qu'apprenant** (B19, B9) : prénom, nom, identifiant, courriel, mot de passe
   deux fois, case d'avertissement A22 (photos publiques par leur lien, GPS conservé), pot de miel. Aucun
   code. Compte créé inactif, profil Apprenant ; prénom et nom préremplissent `apprenant_nom` du premier stage.
5. **Vérification du courriel** (B4) : lien à usage unique ; comptes jamais confirmés purgés après 7 jours,
   au plus une fois par heure lors d'une requête (pas de tâche planifiée).
6. **Connexion unique et protégée** (B4, B6, B16) : `/connexion/` (et `/admin/login/` y redirige), blocage de
   15 min après 5 échecs pour un même identifiant. L'apprenant arrive sur la Note rapide, l'administrateur
   sur le tableau de bord.
7. **Mot de passe oublié** (B4) : lien par courriel valable 24 h ; compte démo exclu.
8. **Garde-fous du compte gratuit** (B8, B19) : 5 inscriptions par heure et par IP (HMAC), inscription fermée
   au-delà de 80 % de 512 Mo ou de `MAX_APPRENANTS` (6) apprenants actifs, compte démo non compté.
9. **Le formateur est un libellé** (B17) : pas de compte formateur. Son nom et son poste se saisissent dans la
   couverture du stage, champ « Formateur (responsable académique) », et s'impriment sur le rapport.
10. **L'accueil guide le premier pas** (B18) : héros « Par où commencer » → trois étapes (créer le compte,
    décrire le stage, première note), rappel que le formateur n'a pas de compte, lien vers la démo.
11. **Comptes existants et démo** (B10, B15) : chaque compte reçoit un profil (superutilisateur →
    Administrateur, autres → Apprenant, droits réappliqués) ; le compte démo ne change ni de mot de passe ni
    de courriel.

### 2. Contraintes techniques

- **Modèle utilisateur** (B3, B15) : `django.contrib.auth.User` conservé, sans `AUTH_USER_MODEL` personnalisé.
  `Profil` 1-1 porte le rôle (`apprenant`, `administrateur`) ; `comptes.droits.appliquer_role` règle groupes et
  statuts à chaque enregistrement du profil. `creer_groupes` définit les droits du groupe Apprenant et supprime
  l'ancien groupe Formateur.
- **Port de comptafisca** : vues `django.contrib.auth` écrites à la main, sans django-allauth ni captcha
  externe ; jeton de vérification dérivé de `PasswordResetTokenGenerator` ; IP stockée seulement en HMAC.
- **Courriel** (B5) : SMTP Gmail du compte de comptafisca, `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD`
  uniquement dans le `.env` du serveur, collés par l'utilisateur ; contrôle `comptes.E001` sous `check --deploy`.
- **Restauration** : `restaurer_dossier` ignore les champs disparus (`formateur_referent`, `remarque_formateur`)
  d'un ancien zip.
- **Interface, qualité, déploiement** : gabarits Django et `carnet.css` ; TDD pytest-django ; P5 et P4-5
  s'appliquent ; un déploiement par lot avec le skill `deploy` ; aucun secret dans le dépôt.

### 3. Hors périmètre (strict)

- Compte formateur, suivi ou annotation des notes par un formateur, codes d'invitation (B17, B19).
- Inscription d'un administrateur par le formulaire public ; connexion via un réseau social, django-allauth,
  captcha externe, double authentification.
- `AUTH_USER_MODEL` personnalisé ; version anglaise ; tâche planifiée sur le serveur ; fournisseur de courriel
  autre que Gmail SMTP.
- Le reste du hors-périmètre de la section générale demeure.

## PRD — incrément 4 : comptes ouverts et revue UI/UX

Complète le PRD général (conventions : UUID, `cree_le`/`modifie_le`, français, cloisonnement). Les stories
renvoient au journal B1–B19. US-41 (codes du formateur) est **retirée** par B17 et B19.

### P4-1. Problème, utilisateurs, mesure du succès

- **Problème** : chaque compte devait être créé par le superutilisateur ; un mot de passe oublié n'avait pas
  d'issue ; dans l'admin, champs illisibles, bouton d'ajout absent, déconnexion cachée. Le scénario du
  2026-11-08 a montré en plus qu'un compte formateur et un code d'invitation bloquaient l'apprenant seul.
- **Personas** : l'apprenant (téléphone, connexion médiocre) et l'administrateur. Le formateur n'est plus un
  utilisateur : c'est un nom sur la couverture.
- **Mesures du succès** : un visiteur crée son compte et arrive sur la Note rapide en moins de 3 minutes en
  ne lisant que l'accueil ; déconnexion en un clic sans défiler ; aucun champ sous 3:1 ; l'administrateur
  n'intervient plus pour créer les comptes.

### P4-2. User stories

| ID | En tant que… | je veux… | afin de… | Critères d'acceptation | Prio |
|---|---|---|---|---|---|
| US-32 | administrateur | gérer les utilisateurs dans Unfold, un profil par utilisateur | attribuer les droits sans erreur | Classes et formulaires Unfold ; bouton « Ajouter un utilisateur » ; seul champ de droits : **Profil** (pas de groupes, permissions, équipe, superutilisateur) ; colonnes et filtre par profil ; 403 pour l'apprenant. (B12, B15) | M |
| US-33 | utilisateur | un menu court en groupes repliables | trouver vite un écran | Navigation définie à la main, filtrée par les droits, chaque modèle présent ; Administration réservée à l'administrateur. (B11) | M |
| US-34 | utilisateur connecté | « Se déconnecter » toujours visible | quitter ma session | Formulaire POST dans l'en-tête admin et public, visible à 390 et 1440 px, retour à `/`. (B11) | M |
| US-35 | utilisateur | des formulaires lisibles | ne plus chercher où saisir | Bord ≥ 3:1, libellé et focus visibles, aucun débordement, clair et sombre, 390 et 1440 px. (B13) | M |
| US-36 | visiteur | créer mon compte librement, en tant qu'apprenant | commencer sans attendre personne | `/inscription/` sans code ; refus par champ (courriel déjà confirmé, mot de passe faible, case A22) ; pot de miel ; 429 au-delà de 5 par heure et par IP ; compte inactif, profil Apprenant. (B9, B19) | M |
| US-37 | visiteur | confirmer mon courriel | activer mon compte | Lien à usage unique ; 400 si faux ou réutilisé ; erreur SMTP : compte supprimé ; purge à 7 jours par middleware. (B4) | M |
| US-38 | apprenant | que mon premier stage connaisse mon nom | gagner du temps | `apprenant_nom` prérempli au premier stage seulement. (B9) | S |
| US-39 | utilisateur | une connexion unique et protégée | éviter les essais en série | `/connexion/`, `/admin/login/` y redirige ; blocage 5 échecs / 15 min ; destination selon le profil ; un compte sans accès à l'admin voit « Accès refusé » (403) sans boucle. (B6, B16) | M |
| US-40 | utilisateur | réinitialiser mon mot de passe | ne pas rester bloqué | Réponse identique pour un courriel inconnu ; lien 24 h ; compte démo exclu. (B4, B10) | M |
| US-42 | administrateur | que l'inscription se ferme quand le disque est plein | protéger les stages en cours | Fermeture au-delà de 80 % ou de `MAX_APPRENANTS` actifs, démo non comptée ; message sans formulaire. (B8) | M |
| US-43 | administrateur | que les comptes existants et la démo restent sûrs | ne rien casser | Migration : profil et droits pour chaque compte, anciens formateurs → apprenants ; démo verrouillée. (B10, B15) | M |
| US-44 | administrateur | configurer le SMTP sans exposer le secret | mettre l'inscription en ligne | `.env` seulement ; console en local ; `comptes.E001`. (B5) | M |
| US-45 | apprenant | saisir moi-même le nom de mon formateur | l'imprimer sur la couverture sans lui créer de compte | Champ « Formateur (responsable académique) » avec aide ; plus de `formateur_referent` ni de `remarque_formateur` ; ancien zip restaurable. (B17) | M |
| US-46 | visiteur | que l'accueil me dise par où commencer | avancer sans aide extérieure | Héros « Par où commencer » + « Se connecter » ; section `#commencer` en trois étapes avec le lien d'inscription ; aucune mention de code ni de formateur référent ; message du premier stage explicite. (B18) | M |

### P4-3. Modèle logique des données

| Entité | Attributs principaux | Relations | Règles |
|---|---|---|---|
| **User** (Django) | identifiant, courriel, prénom, nom, `is_active` | — | Droits jamais réglés à la main : ils viennent du profil (B15). |
| **Profil** | `role` (apprenant, administrateur), `email_verifie`, `inscrit_par_formulaire` | 1–1 → User | Créé par signal (rôle déduit) ; `save()` applique groupes et statuts. Purgeable seulement si inscrit par le formulaire, non vérifié, inactif, plus de 7 jours. |
| **EchecConnexion** | `identifiant`, `survenu_le` | — | Compté sur 15 min. |
| **LimiteInscription** | `ip_hachee` (HMAC), `survenu_le` | — | Lignes de plus d'1 h supprimées ; jamais d'IP en clair. |
| **Stage** (existant) | `tuteur_acad` = « Formateur (responsable académique) », libellé saisi librement | — | `formateur_referent` supprimé (B17). |
| **EntreeJournal** (existant) | — | — | `remarque_formateur` supprimé (B17). |

Réglages : `MAX_APPRENANTS` (6), `LOGIN_MAX_ECHECS` (5), `LOGIN_BLOCAGE` (15 min), `INSCRIPTIONS_MAX_PAR_HEURE`
(5), `INSCRIPTION_IP_HEADER`, `PASSWORD_RESET_TIMEOUT` (24 h), `LOGOUT_REDIRECT_URL = "/"`, `COMPTE_DEMO`.

### P4-4. Contrat des URL et des courriels

```
/connexion/  /deconnexion/ (POST)  /inscription/  /inscription/envoye/  /inscription/verifier/<uidb64>/<jeton>/
/mot-de-passe/  /mot-de-passe/envoye/  /mot-de-passe/<uidb64>/<jeton>/  /mot-de-passe/termine/
/admin/login/ → 302 vers /connexion/?next=…
comptes/email/verifier.txt, mdp_oublie.txt, mdp_oublie_objet.txt   (texte brut, français)
```

### P4-5. Definition of Done (critères stricts)

**Pour chaque story** : les 7 critères de P5, et en plus :
1. **Cloisonnement** testé : apprenant contre apprenant, apprenant contre administrateur ; aucune page
   d'authentification ne révèle si un identifiant existe (hormis le doublon de courriel confirmé).
2. **Droits par le profil** : aucun code ne règle `groups`, `is_staff` ou `is_superuser` à la main pour un
   utilisateur de l'application ; les migrations de données suivent la même règle que `appliquer_role` et
   sont testées avec l'état historique des modèles.
3. **Sécurité** : CSRF partout, déconnexion en POST seulement, rien en clair dans les journaux, `check --deploy`
   sans nouveauté (hormis `comptes.E001` tant que le SMTP manque).
4. **Courriels** testés avec `mail.outbox` ; aucun appel SMTP réel.
5. **Écrans** : Playwright en clair, en sombre, à 390 et 1440 px, aucun débordement, déconnexion visible.
6. **Scénario apprenant** rejoué avec Playwright : depuis l'accueil seul, inscription, lien, connexion, premier
   stage avec le nom du formateur, Note rapide.
7. **Secret** : le mot de passe SMTP n'apparaît nulle part.

## PRD — « Carnet de stage »

### P1. Problème, utilisateurs, mesure du succès

- **Problème** : en fin de stage, l'apprenant doit rédiger un rapport conforme au cours (Module 2), mais
  les informations du terrain sont perdues, dispersées ou non sourcées. Le cours le dit lui-même : « une
  fois que vous aurez quitté les murs de l'entreprise, il vous sera peut-être difficile d'accéder à
  certaines informations ».
- **Personas** :
  - **Apprenant** : sur le chantier, au téléphone, avec une connexion médiocre. Il saisit vite.
  - **Formateur** : n'a plus de compte (B17) ; son nom figure sur la couverture, saisi par l'apprenant.
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
| US-01 | superutilisateur | créer des comptes et leur attribuer un profil | contrôler qui accède | Révisée par B15 et B19 : inscription libre en tant qu'apprenant, profil Apprenant ou Administrateur dans l'admin, `creer_groupes` idempotente. | M |
| US-02 | apprenant | ne voir et ne modifier que mes stages et tout ce qui en dépend | protéger mes données | Accès à l'objet d'un autre apprenant, par la liste ou par l'URL : 404. Testé pour **chaque** modèle. (A1) | M |
| US-03 | ~~formateur~~ | ~~voir en lecture les stages dont je suis référent et annoter une note~~ | — | **Retirée par B17** (2026-11-08) : plus de compte formateur ; `formateur_referent` et `remarque_formateur` supprimés. | — |
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
| **User** (Django) | identifiant, mot de passe, groupes | — | Droits portés par `comptes.Profil` (B15) : Apprenant ou Administrateur. Plus de groupe Formateur (B17). |
| **Stage** | intitule, specialite, theme, sous_theme ; couverture : apprenant_nom, cfp, cfp_sigle, diplome, annee_etude, session, entreprise, entreprise_sigle, tuteur_pro, tuteur_pro_poste, tuteur_acad, tuteur_acad_poste ; date_debut, date_fin ; logo_entreprise?, logo_cfp? ; jours_travailles (liste de jours, lundi–samedi) ; quota_mo (80) ; derniere_sauvegarde? ; slug | → User `proprietaire` ; → User `~~formateur_referent~~ (supprimé, B17) | `date_fin` ≥ `date_debut`. |
| **FicheEntreprise** | presentation, organisation, historique, secteurs, marches, clients_fournisseurs, concurrence, chiffres_cles, perspectives_swot, mutations_technologiques, volonte_dirigeants ; adresse, contact, creation, effectif, capital | 1–1 avec Stage | 11 rubriques du cours, plus les champs d'identité de `infos.tex`. |
| **Mission** | poste, position_organigramme, faits_importants, objectifs_enjeux, methodes_moyens, collaborateurs, responsabilites, resultats, difficultes_solutions | 1–1 avec Stage | 9 rubriques du cours. |
| **BilanPersonnel** | pourquoi_ce_stage, appreciation, attentes_atteintes, apprecie_comme_stagiaire, resultats_remarques, travail_equipe, consequence_carriere, critiques, suggestions | 1–1 avec Stage | Questions de la p. 24 et Partie IV. |
| **Rubrique** | code, libelle, niveau (cours, thème), partie (entreprise, mission, intro, thème, critiques, conclusion, bilan), ordre | → Stage? (vide pour le cours) ; → Rubrique `parent`? | Rubrique du cours : sans stage, non modifiable. Rubrique de thème : `parent` toujours de niveau 1. |
| **Lieu** | nom, type (siège, chantier, fournisseur, autre), latitude, longitude, reperes, ville, quartier | → Stage | Coordonnées dans les bornes valides. |
| **Tache** | libelle, date_debut, date_fin?, description? | → Stage ; → Lieu? ; → Rubrique? | Fin vide : arrêt à la fin du stage pour le Gantt. |
| **EntreeJournal** | date, heure ; texte (note rapide) ; objectifs, moyens_humains, moyens_materiels, methodologie, activites, elements_theoriques, difficultes, solutions, appreciation ; intervention : nature?, duree_immobilisation?, cout?, ressources? ; completee (booléen) ; ~~remarque_formateur~~ (supprimé, B17) ; latitude?, longitude? | → Stage ; → Lieu? ; → Tache? ; ↔ Rubrique ; ↔ Equipement ; ↔ Personne | Plusieurs notes par jour. |
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
   apprenant B, apprenant contre administrateur (plus de formateur, B17).
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
| A13 | Comptes ? | Créés par le superutilisateur ; groupes Apprenant et Formateur ; remarque du formateur sur les notes. **Remplacé par B15, B17 et B19.** |
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
| A32 | Que voit un formateur ? | Seulement les stages dont il est référent. **Retiré par B17.** |
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

## Journal des décisions : comptes ouverts et revue UI/UX (grilling et scénario du 2026-11-08)

| # | Question | Décision |
|---|---|---|
| B1 | Lever A13 et ouvrir l'inscription ? | Oui, comme comptafisca (courriel vérifié, pot de miel, limites), mais seulement avec un code d'invitation. Compte placé dans le groupe Apprenant. **Remplacé par B19 (sans code).** |
| B2 | Qui émet le code, que porte-t-il ? (**retiré par B19**) | Modèle `CodeInvitation` lié à un formateur : 8 caractères sans 0/O/1/I/L, expiration, usages max. Le formateur devient le référent par défaut des stages de l'apprenant. |
| B3 | Modèle utilisateur ? | Garder `django.contrib.auth.User` et les groupes ; nouveau `Profil` 1-1 (UUID, `email_verifie`, `code_utilise`). Pas d'`AUTH_USER_MODEL` personnalisé. |
| B4 | Parcours repris ? | Tout comptafisca : inscription, vérification, connexion avec blocage (5 échecs → 15 min), déconnexion, mot de passe oublié par courriel. Changement connecté : admin Unfold. |
| B5 | Compte d'envoi des courriels ? | Même Gmail SMTP que comptafisca, mot de passe d'application dans le `.env` du serveur seulement ; console en local. |
| B6 | Page de connexion ? | Une seule page publique `/connexion/` (et `/inscription/`, `/mot-de-passe/…`), style comptafisca adapté à `carnet.css` ; `/admin/login/` y redirige. Inscrit : `is_staff` et groupe Apprenant. |
| B7 | Formateurs et codes ? (**retiré par B17 et B19**) | Comptes formateurs créés par le superutilisateur seulement ; chaque formateur gère ses propres codes dans l'admin (cloisonnement testé) et voit leurs usages. |
| B8 | Garde-fou du disque ? | Code : 5 usages et 90 jours par défaut. Inscription refusée au-delà de 80 % de 512 Mo ou de `MAX_APPRENANTS` (6) apprenants actifs. |
| B9 | Champs d'inscription ? | Prénom, nom, identifiant, courriel, mot de passe ×2, code, pot de miel, case obligatoire d'avertissement A22. Prénom et nom préremplissent `apprenant_nom`. |
| B10 | Comptes existants et démo ? | Migration : profil vérifié pour chaque compte ; purge limitée aux inscrits inactifs non vérifiés. Compte démo verrouillé (mot de passe, réinitialisation, courriel). |
| B11 | Déconnexion inaccessible ? | Navigation Unfold à la main, en groupes repliables, sans liste automatique ; bouton « Se déconnecter » dans l'en-tête de l'admin et des pages publiques. |
| B12 | Liste des utilisateurs ? | `UserAdmin` et `GroupAdmin` Unfold avec leurs formulaires ; bouton « Ajouter un utilisateur », colonnes et filtres utiles, choix du groupe à l'ajout ; réservé au superutilisateur. |
| B13 | Portée de la revue UI/UX ? | Tous les écrans, en clair et en sombre, à 390 et 1440 px ; bord de champ ≥ 3:1, libellé et focus visibles, aucun débordement. |
| B14 | Livraison ? | Deux lots (interface, puis comptes ouverts), deux déploiements ; l'utilisateur colle lui-même le mot de passe SMTP dans le `.env` du serveur. |
| B15 | Où vivent les droits ? (2026-11-08) | Sur le **profil** : `Profil.role` (Apprenant ou Administrateur) ; on associe simplement un profil à chaque utilisateur. Groupes, statut équipe et superutilisateur en découlent (`comptes.droits.appliquer_role`). L'admin n'affiche qu'un champ « Profil ». |
| B16 | Où arrive chacun après la connexion ? | L'apprenant sur la Note rapide, l'administrateur sur le tableau de bord (le scénario avait montré un 403 brut pour un compte sans stage à créer). |
| B17 | Le compte formateur sert-il ? | Non : supprimé. Le nom du formateur n'est qu'un **libellé** de la couverture (« Formateur (responsable académique) »), saisi par l'apprenant. `formateur_referent`, `remarque_formateur`, groupe Formateur supprimés ; un ancien zip reste restaurable. |
| B18 | L'accueil suffit-il pour démarrer ? | Non (scénario du 2026-11-08) : héros « Par où commencer », section en trois étapes, message du premier stage explicite, ancres non masquées par l'en-tête. |
| B19 | Faut-il un code d'invitation ? | Non : **inscription libre pour tout le monde, en tant qu'apprenant**. Garde-fous conservés : courriel vérifié, pot de miel, 5 inscriptions par heure et par IP, fermeture à 80 % du disque ou à `MAX_APPRENANTS` (compte démo non compté). |

## Points à valider par l'utilisateur

- Remplir `config/infos.tex` (noms, CFP, entreprise, chantier, dates, encadreurs et leurs postes).
- Remplacer les images factices `img/fig_*.png` et les logos factices.
- Adapter le planning type (partie II) aux activités réellement menées.
- Vérifier les données chiffrées de l'entreprise (`\AC{}` restants).
