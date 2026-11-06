---
name: deploy
description: Met en ligne une nouvelle version du Carnet de stage (dépôt esr2ventisax, webapp/ Django) sur le compte gratuit PythonAnywhere esrventisax, en suivant webapp/DEPLOIEMENT.md. Contrôles locaux (pytest, check --deploy, migrations), poussée de develop puis fusion dans main, mise à jour sur le serveur par une console Bash pilotée avec Playwright MCP (git pull, pip, migrate, collectstatic, creer_groupes), Reload, puis vérification visuelle du site en ligne. À utiliser quand l'utilisateur demande de « déployer », « mettre en ligne », « publier sur PythonAnywhere » ou « mettre à jour le site ».
---

# deploy : mettre en ligne le Carnet de stage

Source de vérité : `webapp/DEPLOIEMENT.md`. Ce skill l'applique dans l'ordre, sans sauter d'étape.
Compte : `esrventisax`, site `https://esrventisax.pythonanywhere.com`. Dépôt public : aucun secret, aucun
identifiant PythonAnywhere ne s'écrit dans un fichier, un commit ou un message.

## 0. Garde-fous

- Pousser vers GitHub et déployer sont des actions visibles : il faut l'accord explicite de l'utilisateur pour
  cette mise en ligne (AGENTS.md : « Ne rien pousser vers le dépôt distant sans demande explicite »).
- Seuls le code et la documentation partent (A7, A8, A14) : jamais `db.sqlite3`, `media/`, `.env`, `rapports/`,
  `*.zip`. Vérifier `git status` et `git diff origin/main..develop --stat` avant de pousser.
- Le mot de passe PythonAnywhere ne se demande pas dans la conversation : si la session du navigateur a expiré,
  demander à l'utilisateur de **se connecter lui-même** dans la fenêtre Playwright, puis attendre son « connecté ».
- Ne jamais lancer `charger_demo` sur le serveur sans accord : il remet le compte démo à zéro.

## 1. Contrôles locaux (depuis `webapp/`)

```bash
.venv/Scripts/python -m pytest -q
.venv/Scripts/python manage.py makemigrations --check --dry-run
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=<valeur longue jetable> DJANGO_ALLOWED_HOSTS=esrventisax.pythonanywhere.com \
  .venv/Scripts/python manage.py check --deploy
```

Tout doit passer. Un échec arrête le déploiement : le signaler, ne pas le contourner.

## 2. Branches

Le code vit sur `develop` ; le serveur suit la branche clonée (par défaut `main`, à vérifier à l'étape 3).

```bash
git push origin develop
# si le serveur suit main : fusion comme pour les livraisons précédentes
git checkout main && git pull --ff-only origin main
git merge --no-ff develop -m "Merge branch 'develop' : <résumé de la livraison>"
git push origin main && git checkout develop
```

## 3. Mise à jour sur le serveur (Playwright MCP)

1. Ouvrir `https://www.pythonanywhere.com/user/esrventisax/consoles/`. Page de connexion : demander à
   l'utilisateur de se connecter (voir 0).
2. Ouvrir une console **Bash** existante ou nouvelle, puis taper :

```bash
cd ~/esr2ventisax && git branch --show-current && git pull
cd webapp && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate && .venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py creer_groupes
```

3. Lire la sortie de chaque commande dans la console (snapshot) : un `git pull` en conflit, une migration ou un
   `collectstatic` en échec arrête tout. Rapporter le message exact.
4. Onglet **Web** (`/user/esrventisax/webapps/`) : bouton **Reload esrventisax.pythonanywhere.com**. Y vérifier au
   passage la date d'expiration (« Run until 3 months from today », A17) et la signaler si elle est proche.

## 4. Vérification en ligne

Avec Playwright, sur `https://esrventisax.pythonanywhere.com/` :
- la page concernée par la livraison s'affiche, en clair, en sombre et à 390 px, sans débordement horizontal
  (`document.documentElement.scrollWidth - clientWidth` = 0) ;
- connexion avec le compte démo (`demo.apprenant`, A38) : tableau de bord et note rapide s'ouvrent ;
- aucune erreur 500, aucune ressource statique en 404 (onglet réseau ou console).

## 5. Compte rendu

Dire ce qui est en ligne (commit déployé), ce qui a été vérifié et comment, et ce qui reste (échec, date
d'expiration proche). Un déploiement non vérifié en ligne n'est pas « terminé ».
