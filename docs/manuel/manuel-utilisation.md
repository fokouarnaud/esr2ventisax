# Manuel d'utilisation : « Carnet de stage »

Ce manuel s'adresse à l'**apprenant**. Il décrit chaque écran de l'application à partir du **compte de
démonstration**. Les données du compte sont fictives : entreprise EDEMO, chantier Résidence Démo (R+10) à Douala,
stage du 1er juin au 19 septembre 2026.

Le scénario complet, du premier au dernier jour du stage, est dans [scenario-stage.md](scenario-stage.md).

## Sommaire

1. [Accès et compte de démonstration](#1-accès-et-compte-de-démonstration)
2. [Tableau de bord](#2-tableau-de-bord)
3. [Décrire le stage](#3-décrire-le-stage)
4. [Note rapide sur le téléphone](#4-note-rapide-sur-le-téléphone)
5. [Compléter une note dans le journal](#5-compléter-une-note-dans-le-journal)
6. [Fiche entreprise, Mission et Bilan personnel](#6-fiche-entreprise-mission-et-bilan-personnel)
7. [Photos](#7-photos)
8. [Lieux](#8-lieux)
9. [Rubriques, chapitres et étiquettes](#9-rubriques-chapitres-et-étiquettes)
10. [Données structurées](#10-données-structurées)
11. [Calendrier et absences](#11-calendrier-et-absences)
12. [Dossier terrain : export et sauvegarde](#12-dossier-terrain--export-et-sauvegarde)
13. [Et ensuite : le rapport](#13-et-ensuite--le-rapport)
14. [Le formateur et le rapport](#14-le-formateur-et-le-rapport)
15. [Questions fréquentes](#15-questions-fréquentes)

---

## 1. Accès et compte de démonstration

| | |
|---|---|
| Site en ligne | <https://esrventisax.pythonanywhere.com> |
| En local | `http://127.0.0.1:8000`, après `manage.py charger_demo` (voir le [README](../../README.md)) |
| Identifiant | `demo.apprenant` |
| Mot de passe | `demo-local-2026` (public par choix, décision A38) |

Chaque apprenant crée lui-même son compte sur la page **Créer un compte** (inscription libre, sans code) et
l'active par le lien reçu par courriel. Mot de passe oublié : lien **Mot de passe oublié ?** sous la connexion.
Le formateur n'a pas de compte : son nom se saisit dans la couverture du stage (section 14).

![Page de connexion](img/01_connexion.jpg)

*Figure 1 : page de connexion.*

L'adresse racine ouvre directement la **Note rapide** : c'est l'écran du terrain. Le **tableau de bord** est sur
`/admin/`. Sur le téléphone, les trois icônes de l'en-tête mènent à la Note rapide, au Tri des photos et au
Tableau de bord.

> Le compte de démonstration est partagé. Tout ce que vous y saisissez peut être effacé à tout moment par
> `charger_demo`, qui remet la démo à neuf.

## 2. Tableau de bord

![Tableau de bord du stage de démonstration](img/02_tableau_de_bord.jpg)

*Figure 2 : tableau de bord du stage de démonstration en fin de stage : tous les indicateurs sont au vert.*

En haut, l'intitulé et les dates du **stage actif**, puis trois boutons : **Note rapide**, **Trier les photos** et
**Dossier terrain** (téléchargement du zip). En dessous, huit indicateurs. Une case passe en **orange** quand il
faut agir.

| Indicateur | Ce qu'il compte | Orange quand… |
|---|---|---|
| Notes à compléter | Notes rapides pas encore complétées dans le journal | au moins une note |
| Jours sans note | Jours travaillés écoulés sans aucune note | au moins un jour |
| Rubriques du cours remplies | Rubriques de la Fiche entreprise et de la Mission remplies (sur 20) | — (« Voir les rubriques encore vides » les liste) |
| Présence | Jours travaillés moins les absences, sur les jours prévus | — |
| Photos corps / annexe | Photos qui iront dans le rapport | plus de 25 photos dans le corps |
| Photos à trier | Photos sans destination | au moins une photo |
| Espace utilisé | Place occupée par les photos du stage (quota : 80 Mo) | — |
| Dernière sauvegarde | Âge du dernier zip téléchargé | jamais, ou plus de 7 jours |

Sous les indicateurs, la liste des formulaires (Abréviations, Absences, Journal, Lieux…) donne accès à tout le
reste. Le menu latéral offre la même liste, avec une recherche.

Sur le téléphone, le tableau de bord s'affiche sur deux colonnes :

<img src="img/35_tableau_de_bord_mobile.jpg" alt="Tableau de bord sur téléphone" width="300">

*Figure 3 : tableau de bord à 390 px, juste après une note rapide : une note à compléter et une photo à trier.*

### Plusieurs stages

Un apprenant peut avoir plusieurs stages. Le **stage actif** est choisi dans la liste déroulante en haut de la
Note rapide ; ce choix est gardé pour toute la session et vaut aussi pour le tableau de bord. La liste n'apparaît
que si vous avez au moins deux stages.

## 3. Décrire le stage

Au tout premier accès, sans stage, le tableau de bord affiche **Bienvenue** et le bouton **Créer mon stage**.
Le formulaire du stage se trouve aussi dans **Stages**.

![Formulaire du stage](img/03_stage_general.jpg)

*Figure 4 : formulaire du stage, partie générale.*

- **Partie générale** : intitulé, spécialité, thème, sous-thème, dates de début et de fin. Rien n'est imposé :
  l'application ne connaît à l'avance ni l'entreprise, ni la spécialité, ni le thème.
- **Onglet Couverture** : les champs de la page de couverture exigés par le cours (nom du stagiaire, titre du
  rapport, entreprise et sigle, centre de formation professionnelle et sigle, diplôme, année d'étude, session, responsable professionnel et
  **formateur (responsable académique)** avec leurs postes), ainsi que les logos de l'entreprise et du centre de formation professionnelle.
- **Onglet Suivi** : jours travaillés (lundi à samedi par défaut), quota (réglé par l'administrateur, en
  lecture seule) et date de la dernière sauvegarde.

![Onglet Couverture](img/03b_stage_couverture.jpg)

*Figure 5 : onglet Couverture.*

Tous les champs sont facultatifs à la saisie. Un champ vide n'empêche rien : il devient « [À COMPLÉTER] » dans le
rapport.

## 4. Note rapide sur le téléphone

C'est l'écran que l'on utilise **chaque jour, sur le chantier**. Il tient en **trois actions** :

1. écrire quelques phrases ;
2. prendre une photo (**Prendre** ouvre l'appareil photo, **Galerie** choisit des images existantes) ;
3. toucher **Enregistrer la note**.

<img src="img/30_note_rapide_vide.jpg" alt="Note rapide vide" width="300"> <img src="img/31_note_rapide_remplie.jpg" alt="Note rapide remplie" width="300">

*Figures 6 et 7 : la Note rapide avant et après saisie. La position est captée, la photo est prête à partir.*

Ce qui se fait tout seul :

- **date et heure** : celles de l'enregistrement, affichées sous le titre ;
- **position GPS** : l'étiquette passe de « Position non captée » à « Position captée (± n m) ». Autorisez la
  localisation dans le navigateur. La note est rattachée au **lieu** le plus proche, à moins de 200 m ;
- **brouillon** : le texte et les étiquettes cochées restent dans le navigateur. Une page rechargée ou une
  coupure de réseau ne fait rien perdre ; le brouillon s'efface après l'enregistrement ;
- **quota** : l'espace restant est affiché (« 79,4 Mo disponibles »). Au-delà du quota, l'envoi est refusé avec le
  message « Quota de 80 Mo atteint pour ce stage… ».

**Étiquettes du rapport** (facultatif) : ouvrez ce volet pour indiquer la partie du rapport où la note servira.
Les étiquettes suivent le plan du cours : Introduction, Partie I Entreprise, Partie II Mission, Partie III Thème
(vos chapitres), Partie IV Critiques et suggestions, Conclusion, Bilan personnel, Annexes. On peut en cocher
plusieurs. Le sens de chaque étiquette, avec des exemples, est expliqué en
[section 9](#que-veut-dire-chaque-étiquette--exemples).

<img src="img/32_note_rapide_etiquettes.jpg" alt="Étiquettes de la note rapide" width="300"> <img src="img/33_note_enregistree.jpg" alt="Note enregistrée" width="300">

*Figures 8 et 9 : une étiquette de la Partie III cochée, puis le message « Note enregistrée avec 1 photo. »*

Le mode sombre suit le réglage du téléphone :

<img src="img/30_note_rapide_sombre.jpg" alt="Note rapide en mode sombre" width="300">

*Figure 10 : Note rapide en mode sombre.*

> L'application fonctionne **en ligne** uniquement. Sans réseau, écrivez quand même : le brouillon est gardé,
> et vous enregistrerez dès que le réseau revient.

## 5. Compléter une note dans le journal

Le soir ou en fin de semaine, au calme, ouvrez **Journal** (ou le lien « Compléter mes notes » en bas de la Note
rapide). La liste se filtre par mois, par rubrique et par état « Complétée ».

![Liste du journal](img/07_journal_liste.jpg)

*Figure 11 : le journal du stage de démonstration : 95 notes, toutes complétées.*

Une note s'ouvre sur sa partie générale (date, heure, texte saisi sur le terrain, étiquettes, case
**Complétée**), puis quatre onglets :

| Onglet | Champs | Sert à… |
|---|---|---|
| Rapport d'activité | objectifs visés, moyens humains, moyens matériels, méthodologie, activités, éléments théoriques, difficultés, solutions, appréciation | la Partie II et la Partie III |
| Intervention | nature, durée d'immobilisation (h), coût (F CFA), ressources | les interventions de dépannage ou de reprise |
| Liens | lieu, tâche, équipements, personnes | relier les faits entre eux (la tâche situe la note dans le planning) |

![Onglet Rapport d'activité](img/08b_note_rapport_activite.jpg)

*Figure 12 : onglet Rapport d'activité de la note du 17 août 2026 (réglage des réducteurs).*

![Onglet Intervention](img/08c_note_intervention.jpg)

*Figure 13 : onglet Intervention.*

![Onglet Liens](img/08d_note_liens.jpg)

*Figure 14 : onglet Liens.*

Cochez **Complétée** quand la note est prête : elle sort du compteur « Notes à compléter ».

### Plusieurs activités le même jour

**Une note par activité ou intervention**, même si elles ont lieu le même jour. Trois activités dans la journée
donnent trois notes, à la même date mais à des heures différentes.

- Une note n'a qu'**un seul bloc Intervention** (nature, durée, coût, ressources) : deux interventions dans la
  même note obligeraient à en perdre une ou à tout mélanger.
- Chaque note a ses propres étiquettes, son lieu, sa tâche et ses photos. Séparées, les notes se rangent sous la
  bonne rubrique du dossier terrain, donc dans la bonne partie du rapport.
- Chaque note se coche **Complétée** à part : le tableau de bord montre exactement ce qui reste à faire.

En pratique :

1. **Sur le terrain** : une Note rapide juste après chaque activité. La date et l'**heure** se remplissent seules
   et distinguent les notes de la journée ; la position et les photos vont à la bonne note.
2. **Le soir, dans Journal** : complétez chaque note. La liste range les notes par date, puis par heure.
3. **Une activité oubliée** : **Journal → Ajouter**, même date, heure de l'activité.

À éviter : une seule note « fourre-tout » (« matin : X, après-midi : Y, soir : Z »). Le rapport n'est pas un récit
au jour le jour ; ce sont des notes séparées et bien étiquetées qui permettent d'en faire la synthèse par rubrique.

Les textes acceptent un **Markdown minimal** : paragraphes séparés par une ligne vide, listes commençant par
« - » ou « 1. », **gras** entre deux astérisques. Pas de titres, de tableaux ni d'images dans le texte. Les
caractères spéciaux (`& % $ # _ { } ~ ^ \`, « 50 % ») sont échappés à l'export : écrivez-les normalement.

## 6. Fiche entreprise, Mission et Bilan personnel

Ces trois formulaires existent en un seul exemplaire par stage. Ils reprennent les rubriques du cours
« Module 2 ».

**Fiche entreprise** (Partie I) : présentation, organisation générale, historique, secteurs d'activité, marchés,
clients et fournisseurs, concurrence, chiffres clés, perspectives (forces, faiblesses, opportunités, menaces),
mutations technologiques, volonté des dirigeants ; puis les données d'identité (ville, quartier, année de
création, dirigeant, capital, effectif, contact).

![Fiche entreprise](img/04_fiche_entreprise.jpg)

*Figure 15 : Fiche entreprise. Le Markdown est visible dans le champ (gras, listes de l'historique).*

**Mission** (Partie II) : poste occupé, position dans l'organigramme, faits importants, objectifs et enjeux,
méthodes et moyens, collaborateurs, responsabilités, résultats, difficultés et solutions.

![Mission](img/05_mission.jpg)

*Figure 16 : Mission.*

**Bilan personnel** (Partie IV et conclusion) : pourquoi ce stage, appréciation, attentes atteintes, appréciation
comme stagiaire, résultats et remarques, travail en équipe, conséquence sur la carrière, critiques, suggestions.

![Bilan personnel](img/06_bilan.jpg)

*Figure 17 : Bilan personnel.*

Remplissez ces rubriques **au fil du stage**, dès que l'information est disponible. Le cours le rappelle : une
fois sorti de l'entreprise, certaines informations deviennent difficiles à obtenir. Une rubrique compte comme
remplie si son champ contient du texte **ou** si une note du journal porte son étiquette.

### Mission, tâches et notes : trois échelles différentes

Ces trois mots se ressemblent mais ne décrivent pas la même chose. Ils vont du plus large au plus détaillé :

```
MISSION ............ 1 par stage ......... « Quel est mon rôle dans l'entreprise ? »
 └─ TÂCHES ......... 6 à 12 par stage .... « Quelles grandes étapes ai-je suivies, et quand ? »
     └─ NOTES ...... 1 par activité ....... « Qu'ai-je fait, vu, mesuré à ce moment-là ? »
```

| | **Mission** | **Tâche** | **Note du journal** |
|---|---|---|---|
| Échelle | tout le stage | quelques jours à quelques semaines | une activité, à une date et une heure |
| Combien | une seule fiche | 6 à 12 en général | une par activité (souvent plus de 100) |
| Répond à | quel est mon poste, mon rôle, mon bilan ? | quelle étape, de quand à quand ? | que s'est-il passé exactement ? |
| Où la saisir | **Mission** | **Tâches** | **Note rapide**, puis **Journal** |
| Quand | au fil du stage, puis relue à la fin | au début de chaque étape ; la date de fin à la fin de l'étape | le jour même, sur le terrain |
| Devient dans le rapport | la section « mission » de la Partie II | le diagramme de Gantt (Partie II) | la matière de toutes les parties, selon ses étiquettes |

**Un exemple suivi du début à la fin** (chantier d'un immeuble R+10, stage en plomberie sanitaire) :

**1. La Mission**, rédigée en synthèse. Elle décrit le rôle, pas les journées :

> *Poste* : stagiaire technicien dans l'équipe plomberie du chantier.
> *Objectifs et enjeux* : réaliser la distribution d'eau froide et d'eau chaude des étages dans les délais, sans
> fuite à l'essai.
> *Responsabilités* : préparation des tubes, assemblages par polyfusion, montage des réducteurs de pression,
> autocontrôles.
> *Résultats* : six niveaux distribués (RDC au R+5), cinq réducteurs montés, environ 280 m de canalisations isolées.

**2. Les Tâches**, les grandes étapes du stage. Chacune devient une barre du Gantt :

| Tâche | Début | Fin |
|---|---|---|
| Accueil et sécurité | 1er juin | 5 juin |
| Préparation et traçage | 8 juin | 19 juin |
| Canalisations des étages hauts | 22 juin | 10 juillet |
| Réducteurs de pression et essais | 13 juillet | 24 juillet |

**3. Les Notes**, ce qui s'est passé un jour donné. Par exemple le mercredi 1er juillet, pendant la tâche
« Canalisations des étages hauts » :

| Heure | Note (texte de la Note rapide) | Tâche (onglet Liens) | Étiquette |
|---|---|---|---|
| 8 h 15 | Soudure de 14 raccords PPR de 25 mm au R+4. Un raccord mal soudé, coupé et refait. | Canalisations des étages hauts | Mise en œuvre : modes opératoires (chapitre du thème) |
| 11 h 00 | Plus de raccords de 40 mm au magasin : livraison dans deux jours. On passe au R+5. | Canalisations des étages hauts | Difficultés rencontrées et solutions apportées (rubrique du cours) |
| 15 h 30 | Pression relevée en pied de colonne : 4,3 bar. Photo du manomètre. | Réducteurs de pression et essais | Dimensionnement d'une colonne d'eau froide (chapitre du thème) |

**Comment les trois se nourrissent** :

- Les **notes** sont la matière première. La Mission se rédige **à partir des notes**, et non l'inverse. Par
  exemple, le raccord refait du 1er juillet devient un « fait important » de la Mission, et le nombre de niveaux
  terminés vient des notes de la tâche.
- Une note se rattache à **une tâche au plus** (onglet **Liens**, facultatif). Ce lien situe la note dans le
  planning : le Journal se filtre par **tâche**, et le dossier terrain indique sous chaque note « Tâche : … ». Une
  note peut porter sur une autre tâche que celle de la journée, comme la note de 15 h 30.
- Un chiffre mesuré, comme les 4,3 bar de 15 h 30, se saisit **en plus** dans **Données techniques** comme un
  relevé rattaché à la note : c'est ce qui permet de le citer dans le rapport.
- Une tâche ne contient pas de texte de journée : son libellé, ses dates, son lieu et éventuellement le chapitre
  du thème suffisent.

**Règle simple pour savoir où écrire** :

- **Ça s'est passé à un moment précis** (j'ai fait, vu, mesuré, appris) : une **note**.
- **Ça a un début et une fin, et ça dure plusieurs jours** : une **tâche**.
- **Ça décrit mon rôle sur l'ensemble du stage** : la **Mission**.

**Erreurs fréquentes** :

- **Une tâche par jour** (« lundi : traçage », « mardi : traçage »…) : le Gantt devient illisible. Regroupez en une
  seule tâche « Préparation et traçage » du 8 au 19 juin.
- **Le détail des journées dans la Mission** : la Mission est une synthèse de quelques phrases par rubrique. Le
  détail reste dans les notes.
- **Une seule tâche « Stage »** du premier au dernier jour : le Gantt n'apprend rien au lecteur. Découpez selon
  les étapes réelles du travail.
- **Attendre la fin du stage pour créer les tâches** : créez chaque tâche au début de l'étape, sans date de fin,
  pour pouvoir y rattacher les notes au fur et à mesure.

## 7. Photos

### Tri en grille

**Trier les photos** affiche toutes les photos du stage. Les filtres en haut donnent le nombre de photos par
destination.

![Tri des photos](img/09_tri_photos.jpg)

*Figure 18 : tri des photos. Chaque carte porte la légende, la date et le slug (`fig_<slug>`).*

Un seul clic change la destination :

| Destination | Exportée ? | Usage |
|---|---|---|
| À trier | non | valeur par défaut de toute nouvelle photo |
| Corps | oui | figure dans le texte du rapport (25 au plus conseillées) |
| Annexe | oui | figure en annexe, annoncée dans le texte |
| Preuve | non | justificatif gardé dans le carnet (ex. bon de livraison) |

<img src="img/34_tri_photos_mobile.jpg" alt="Tri des photos sur téléphone" width="300">

*Figure 19 : tri des photos sur téléphone. La photo de la note rapide arrive « À trier ».*

### Légende et slug

**Légende et slug** ouvre la fiche de la photo. Une photo **Corps** ou **Annexe** doit avoir une **légende**
(elle devient « Figure N : … ») et un **slug** unique dans le stage (le nom du fichier, `fig_<slug>.jpg`). Sans
eux, l'export est refusé et le message liste les photos à compléter.

![Liste des photos](img/09b_photos_liste.jpg)

*Figure 20 : liste des photos dans l'admin : la destination se modifie aussi depuis la liste.*

Chaque photo est réduite à 1600 px et à environ 300 Ko. Ses coordonnées GPS et sa date de prise de vue (EXIF)
sont conservées.

> Les photos sont accessibles publiquement par leur adresse (choix assumé, A22). Ne photographiez ni
> documents confidentiels ni visages sans accord.

## 8. Lieux

**Lieux** recense le siège, les chantiers, les fournisseurs. Pour chacun : nom, type, latitude, longitude,
**repères** (« derrière la station-service, portail vert »), ville, quartier et nombre de niveaux du bâtiment.

![Fiche d'un lieu](img/10_lieu_carte.jpg)

*Figure 21 : le chantier Résidence Démo.*

**Saisir la position.** Chaque coordonnée se saisit en deux parties : la valeur en degrés décimaux, **sans signe**,
puis l'hémisphère dans la liste à côté.

| Champ | Valeur | Hémisphère | Au Cameroun |
|---|---|---|---|
| Latitude | distance à l'équateur, de 0 à 90 | **Nord** ou **Sud** | toujours Nord (Douala ≈ 4,05° N) |
| Longitude | distance au méridien de Greenwich, de 0 à 180 | **Est** ou **Ouest** | toujours Est (Douala ≈ 9,70° E) |

La liste des lieux affiche ensuite la position en toutes lettres, par exemple « 4,02550° N ; 9,69410° E ».

**Obtenir la position**, au choix :

1. **Sur place** : touchez **Utiliser ma position** sous la latitude et acceptez la localisation demandée par le
   navigateur. Latitude, longitude et hémisphères se remplissent ; la précision s'affiche (« ± 8 m »). Faites-le à
   l'extérieur, loin des murs, pour une meilleure précision.
2. **À distance** : dans OpenStreetMap ou Google Maps, faites un clic droit (appui long sur téléphone) sur le lieu,
   puis copiez les deux nombres affichés, par exemple « 4.0496, 9.6942 ». Collez-les dans la **latitude** : les deux
   champs et les hémisphères se remplissent. Le premier nombre est la latitude, le second la longitude ; un nombre
   négatif signifie Sud ou Ouest.
3. **Depuis une note** : une note rapide prise sur place capte la position ; elle s'affiche dans l'onglet **Liens**
   de la note.

Les plans de situation sont dessinés plus tard, en local, à partir d'OpenStreetMap : le siège donne la figure de
localisation du rapport.

## 9. Rubriques, chapitres et étiquettes

**Rubriques** contient deux niveaux :

- les **rubriques du cours**, fixes et communes à tous ;
- les **chapitres du thème**, propres à votre stage, que vous créez et ordonnez librement, avec un niveau de
  sous-chapitres. Ils forment le plan de la Partie III.

![Rubriques](img/11_rubriques.jpg)

*Figure 22 : rubriques du stage de démonstration, dont les sept chapitres du thème « Plomberie sanitaire ».*

Les chapitres d'un stage sont invisibles des autres stages.

### À quoi sert une étiquette

Une **étiquette** est une rubrique ou un chapitre que l'on accroche à une note. Elle répond à la question :
**« Dans quelle partie du rapport cette note servira-t-elle ? »**

Pensez à un classeur à intercalaires : chaque rubrique est un intercalaire (Historique, Clients et fournisseurs,
Difficultés rencontrées…), et l'étiquette dit derrière quel intercalaire ranger la note. Une même note peut se
ranger derrière plusieurs intercalaires.

Concrètement, une étiquette a trois effets :

1. **Dans le dossier terrain**, la note est recopiée **sous chaque rubrique cochée**. C'est à partir de ces notes
   que la partie correspondante du rapport est rédigée.
2. **Une note sans étiquette n'est pas perdue**, mais elle part en fin de dossier, dans « Journal chronologique
   (notes sans étiquette) ». Elle est alors plus difficile à placer et risque d'être peu exploitée.
3. **Au tableau de bord**, une rubrique de l'Entreprise ou de la Mission compte comme remplie dès qu'une note
   porte son étiquette, même si le champ du formulaire est encore vide.

L'étiquette ne dit pas **quand**, mais **où** : le *quand* est donné par la date et par la tâche (voir
[Mission, tâches et notes](#mission-tâches-et-notes--trois-échelles-différentes)).

### Que veut dire chaque étiquette ? Exemples

La liste mélange les rubriques du cours, classées par partie, et vos chapitres. Voici, pour chacune, le genre de
note qu'elle attend. Les exemples viennent d'un stage de plomberie sur un chantier d'immeuble.

**Partie I : Entreprise** (ce que vous apprenez sur l'entreprise)

| Étiquette | Cochez-la quand la note parle de… | Exemple de note |
|---|---|---|
| Présentation | ce qu'est l'entreprise, en bref | « Entreprise de second œuvre : plomberie, climatisation, électricité. » |
| Organisation générale (organigramme) | les services, qui dirige quoi | « Trois divisions : plomberie, froid, électricité ; un chef par division. » |
| Historique de l'entreprise | les dates et étapes de sa vie | « Créée en 2009 par le directeur actuel ; agence de Yaoundé ouverte en 2018. » |
| Secteur(s) d'activité | les métiers exercés | « 60 % du travail en plomberie, le reste en climatisation. » |
| Marchés de l'entreprise | le type de chantiers visés | « Surtout des immeubles d'habitation et des hôtels. » |
| Clients et fournisseurs | qui commande, chez qui on achète | « Les tubes PPR viennent d'un grossiste de Bonabéri. » |
| Situation concurrentielle | les concurrents et leur place | « Deux concurrents directs sur les chantiers de grande hauteur à Douala. » |
| Chiffres clés | effectif, chiffre d'affaires, nombre de chantiers | « 45 employés, dont 12 plombiers. » |
| Perspectives d'évolution | projets, forces, faiblesses | « Projet d'ouvrir une activité de maintenance. » |
| Mutations technologiques | nouveaux matériaux, nouvelles méthodes | « Passage du tube galvanisé au PPR soudé depuis 2020. » |
| Volonté des dirigeants | ce que veut la direction | « Le directeur veut certifier l'entreprise en qualité. » |

**Partie II : Mission** (ce que vous faites, vous)

| Étiquette | Cochez-la quand la note parle de… | Exemple de note |
|---|---|---|
| Poste occupé | votre poste et son intitulé | « Affecté comme aide-plombier dans l'équipe du chef d'équipe. » |
| Position du poste dans l'organigramme | à qui vous rendez compte | « Je rends compte au chef d'équipe plomberie. » |
| Faits importants | un événement marquant | « Fuite à l'essai du R+2 : tout l'étage repris. » |
| Objectifs et enjeux de la mission | ce qu'on attend de vous, et pourquoi | « Finir la distribution du R+4 avant la pose des faux plafonds. » |
| Méthodes et moyens employés | comment vous travaillez, avec quoi | « Traçage au cordeau, puis polyfusion à 260 °C. » |
| Personnes avec lesquelles vous avez collaboré | une collaboration | « Réunion avec l'équipe climatisation pour partager la gaine. » |
| Responsabilités exercées | ce qu'on vous a confié | « Le chef d'équipe me confie seul le montage des manomètres. » |
| Résultats obtenus | ce qui est terminé, mesuré | « R+3 terminé : 48 m de tube posés, essai sans fuite. » |
| Difficultés rencontrées et solutions apportées | un problème et sa solution | « Raccords de 40 mm manquants : on passe à l'étage suivant. » |

**Partie III : vos chapitres du thème** (la technique)

Ce sont les chapitres que vous avez créés, par exemple « Généralités sur la plomberie sanitaire », « Matériaux et
matériels utilisés » ou « Mise en œuvre : modes opératoires ». Un sous-chapitre s'affiche avec son chapitre :
« Mise en œuvre : modes opératoires › Soudure PPR ». Exemple : « Soudure d'un raccord de 25 mm : chauffe de 7 s,
emboîtement sans rotation » → chapitre **Mise en œuvre : modes opératoires**.

**Les autres parties**

| Étiquette | Cochez-la quand la note… | Exemple de note |
|---|---|---|
| Introduction | explique le contexte ou le choix du stage | « Ce chantier est le plus haut immeuble en cours à Douala. » |
| Critiques et suggestions | relève ce qui pourrait être mieux fait | « Pas de harnais pour les travaux en gaine : à prévoir. » |
| Conclusion | tire une leçon générale | « J'ai compris l'importance de l'essai avant de refermer. » |
| Bilan personnel | parle de votre ressenti, de votre progression | « Première soudure validée sans reprise : je suis plus sûr de moi. » |
| Annexes | décrit un document à joindre en fin de rapport | « Fiche d'autocontrôle de l'essai du R+3, signée. » |

Les chiffres de ces exemples sont inventés pour l'illustration : dans vos notes, écrivez ce que vous avez
réellement vu ou appris.

### Combien d'étiquettes cocher ?

**Une à trois**, celles où la note servira vraiment. Exemples :

- « Le chef d'équipe me confie seul le montage des réducteurs au R+3. J'ai réglé la pression à 3 bar. »
  → **Responsabilités exercées** (on me confie une tâche) **et** le chapitre **Mise en œuvre : modes
  opératoires** (comment on règle un réducteur).
- « Fuite à l'essai : raccord mal chauffé. Coupé et refait, nouvel essai bon. »
  → **Difficultés rencontrées et solutions apportées** (le problème et sa solution) **et** **Faits importants**
  (l'événement a marqué le chantier).
- « Arrivée sur le chantier à 7 h 30, rangement du matériel. »
  → **aucune étiquette** : rien d'utile pour le rapport. Ce n'est pas grave, mais une telle note n'a pas besoin
  d'être complétée en détail.

À éviter : **tout cocher** « pour être sûr ». La note serait recopiée partout, et chaque partie du rapport
devrait trier ce qui la concerne vraiment.

### Comment poser les étiquettes

- **Note rapide** : ouvrez le volet **Étiquettes du rapport** ; les étiquettes y sont regroupées par partie ;
  cochez-les.
- **Journal** (fiche d'une note) : le champ **Étiquettes** a deux listes. À gauche, les « étiquettes
  disponibles » ; à droite, les étiquettes choisies. Tapez quelques lettres dans **Filtrer** (par exemple
  « diffic ») pour trouver une rubrique, sélectionnez-la (Ctrl, ou Cmd sur Mac, pour en prendre plusieurs), puis
  cliquez sur la flèche **Choisir**. Pour en enlever une, sélectionnez-la à droite et cliquez sur la flèche
  **Retirer**.
- **Retrouver** les notes d'une rubrique : dans **Journal**, bouton **Filtres**, puis **Étiquettes**.

Les **photos** ont aussi des étiquettes. Elles servent à **retrouver** une photo (filtre de la liste des Photos),
pas à la placer dans le rapport : c'est sa **destination** (corps ou annexe) et sa légende qui décident de sa
place (voir [Photos](#7-photos)).

## 10. Données structurées

Ces listes produisent directement des figures, des tableaux et la bibliographie du rapport.

### Organigramme

Un poste par ligne, avec son nom (facultatif) et son **parent**. Un seul poste est marqué **Poste du stagiaire**.
Une boucle (un poste parent de lui-même, directement ou non) est refusée.

![Organigramme](img/12_organigramme.jpg)

*Figure 23 : organigramme saisi : il devient `figures/organigramme.tex`.*

### Tâches (Gantt)

Libellé, dates, lieu, chapitre. Une tâche sans date de fin s'arrête à la fin du stage. Les tâches donnent le
diagramme de Gantt de la Partie II. Une tâche est une **étape de plusieurs jours**, pas une journée : voir
[Mission, tâches et notes](#mission-tâches-et-notes--trois-échelles-différentes).

![Tâches](img/13_taches.jpg)

*Figure 24 : les dix tâches du stage de démonstration.*

### Équipements

Outillage, matériel ou matériau, EPI, appareils de mesure : désignation, caractéristiques, rôle, quantité, photo.
Chaque catégorie produit un tableau du rapport.

![Équipements](img/14_equipements.jpg)

*Figure 25 : équipements.*

### Données techniques

Chaque chiffre du rapport doit être traçable :

- un **relevé** (mesuré sur le chantier) est rattaché à une **note du journal** ;
- une **valeur de référence** (norme, notice) exige une **source** de la bibliographie. Sans source, elle est
  refusée.

![Données techniques](img/15_donnees_techniques.jpg)

*Figure 26 : données techniques : relevés de pression et valeurs de référence.*

![Valeur de référence](img/15b_donnee_reference.jpg)

*Figure 27 : une valeur de référence et sa source.*

### Références

Normes, ouvrages, notices, pages web, informations orales. La clé BibTeX est générée (auteur et année) et
unique dans le stage.

![Références](img/16_references.jpg)

*Figure 28 : références bibliographiques.*

### Personnes

Nom, fonction, rôle, téléphone, et deux cases :

- **À remercier** : la personne figure dans les remerciements ;
- **Nom publiable** : sinon, le rapport la cite par sa **fonction**.

Le téléphone n'est **jamais** exporté.

![Personnes](img/17_personnes.jpg)

*Figure 29 : personnes.*

### Abréviations

Sigle (unique dans le stage) et signification : elles forment la liste des abréviations.

![Abréviations](img/18_abreviations.jpg)

*Figure 30 : abréviations.*

## 11. Calendrier et absences

Les jours travaillés se règlent dans l'onglet **Suivi** du stage (lundi à samedi par défaut). **Absences**
recense ce qui n'est pas travaillé : jour férié, maladie, congé, intempérie, cours au centre de formation professionnelle. Les jours fériés fixes
du Cameroun sont déjà chargés pour tous ; ajoutez seulement vos absences.

![Absences](img/19_absences.jpg)

*Figure 31 : absences : les jours fériés communs sont préchargés.*

Les absences évitent les fausses alertes « Jours sans note » et donnent le taux de présence.

## 12. Dossier terrain : export et sauvegarde

Le bouton **Dossier terrain** du tableau de bord (ou le lien « Télécharger le zip » de la liste **Stages**)
télécharge un zip nommé
`dossier-terrain-<slug>-<date>.zip`. Il sert à deux choses :

- **sauvegarde** : téléchargez-le **chaque semaine**. Après 7 jours sans sauvegarde, l'indicateur passe en orange ;
- **rapport** : c'est ce zip que le superutilisateur importe en local pour rédiger le rapport.

![Sauvegarde du jour](img/20_sauvegarde_faite.jpg)

*Figure 32 : après le téléchargement, « Dernière sauvegarde » indique « Aujourd'hui ».*

Contenu du zip de la démo (1,3 Mo) : `terrain.md` et `terrain.json` (toutes les données, classées selon le plan
du cours), `config/infos.tex` (couverture), `figures/organigramme.tex`, `figures/gantt.tex`, quatre tableaux
d'équipements, `bib/references.bib`, les 11 photos Corps et Annexe, les logos, une copie de sauvegarde de toutes
les photos et un `manifest.json` avec les sommes de contrôle.

Le zip est fabriqué à la volée et n'est jamais stocké sur le serveur. Gardez-le en lieu sûr (clé USB, disque) ;
le superutilisateur peut le restaurer dans l'application avec `restaurer_dossier` en cas de perte.

Si l'export est refusé, le message commence par « Export impossible : » et liste les photos Corps ou Annexe
sans légende ou sans slug. Complétez-les (section 7), puis recommencez.

## 13. Et ensuite : le rapport

L'application ne rédige rien et ne compile rien. En fin de stage :

1. vous téléchargez le dossier terrain et le remettez au superutilisateur ;
2. il l'importe en local (`importer_dossier`), Claude Code rédige le rapport **uniquement** à partir de
   `terrain.md`, puis le PDF et la présentation sont produits ;
3. ce qui n'a pas été saisi apparaît en « [À COMPLÉTER] » dans le PDF.

La procédure est dans [docs/rapport-local.md](../rapport-local.md). Le résultat de la démo :
[demo/rapport_demo.pdf](../../demo/rapport_demo.pdf), sa version Word [demo/rapport_demo.docx](../../demo/rapport_demo.docx)
et [demo/presentation_demo.pptx](../../demo/presentation_demo.pptx).

## 14. Le formateur et le rapport

Le formateur n'a pas de compte dans le Carnet (B17). Son nom est un simple libellé : saisissez-le dans le
stage, onglet **Couverture**, champ **Formateur (responsable académique)**, avec son poste. Il est imprimé sur
la couverture du rapport. Pour faire relire votre travail, montrez-lui vos notes sur le téléphone ou
envoyez-lui le dossier terrain. Personne d'autre que vous (et l'administrateur du centre) ne voit vos notes.

## 15. Questions fréquentes

**Je ne vois pas les données d'un camarade.** C'est voulu : chaque apprenant ne voit que ses stages.

**La position reste « non captée ».** Autorisez la localisation pour le site dans le navigateur, activez le GPS
du téléphone, puis rechargez : le brouillon est conservé.

**J'ai écrit une note sans réseau.** Le texte est gardé dans le navigateur. Enregistrez quand le réseau revient.
Les photos choisies, elles, doivent être sélectionnées à nouveau.

**La date de ma note est fausse.** La Note rapide prend la date du jour. Pour une note oubliée, créez-la depuis
**Journal → Ajouter** et choisissez la date.

**J'ai fait trois activités le même jour.** Créez trois notes à la même date, une par activité ou intervention
(voir [Plusieurs activités le même jour](#plusieurs-activités-le-même-jour)).

**Quelle différence entre Mission, tâche et note ?** La Mission décrit votre rôle sur tout le stage, une tâche
est une étape datée du Gantt, une note raconte une activité précise. Voir
[Mission, tâches et notes](#mission-tâches-et-notes--trois-échelles-différentes).

**Quelle étiquette choisir pour ma note ?** Celle de la partie du rapport où la note servira : une à trois au
plus. Voir [Que veut dire chaque étiquette ?](#que-veut-dire-chaque-étiquette--exemples)

**Le quota est atteint.** Passer une photo en « Preuve » ne libère pas de place : supprimez les photos inutiles
dans **Photos**, ou demandez une augmentation au superutilisateur.

**Ce qui n'est pas prévu** : application hors ligne, application mobile, compte formateur, rédaction automatique
dans l'application.

---

*Captures prises le 6 novembre 2026 avec le compte `demo.apprenant`, en local, par
[capturer_ecrans.py](capturer_ecrans.py) (Playwright : 1280 px pour le bureau, 390 px pour le téléphone, GPS
simulé sur le chantier).*
