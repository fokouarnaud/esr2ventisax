# Déploiement du Carnet de stage sur PythonAnywhere (compte gratuit)

Compte : `esrventisax` → `https://esrventisax.pythonanywhere.com`. Aucun identifiant ni secret dans ce dépôt public.

## Première installation

Dans une console **Bash** de PythonAnywhere :

```bash
git clone https://github.com/fokouarnaud/esr2ventisax.git
cd esr2ventisax/webapp
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt          # pas requirements-local.txt (cartes : local uniquement)
python3.13 -c "import secrets; print(secrets.token_urlsafe(50))"   # copier la valeur dans .env
nano .env
```

Contenu de `webapp/.env` (voir `.env.example`) :

```
DJANGO_SECRET_KEY=<valeur générée>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=esrventisax.pythonanywhere.com
EMAIL_HOST_USER=<adresse Gmail d'envoi>
EMAIL_HOST_PASSWORD=<mot de passe d'application Gmail>
MAX_APPRENANTS=6
INSCRIPTION_IP_HEADER=HTTP_X_REAL_IP
```

Sans `DJANGO_SECRET_KEY`, l'application refuse de démarrer en production (test `test_deploiement.py`).

**Courriels (B5, US-44).** L'inscription et le mot de passe oublié envoient un courriel par Gmail SMTP
(port 587, TLS), avec le même compte que comptafisca. **Le superutilisateur colle lui-même**
`EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD` dans `webapp/.env` (console Bash, `nano .env`), puis *Reload*.
Ce mot de passe d'application ne figure jamais dans le dépôt, dans une conversation ni dans une commande
exécutée par un agent. Sans lui, `python manage.py check --deploy` affiche `comptes.E001`.
`INSCRIPTION_IP_HEADER=HTTP_X_REAL_IP` : derrière le proxy de PythonAnywhere, `REMOTE_ADDR` est commun à
tous les visiteurs ; la limite de 5 inscriptions par heure utilise donc l'IP réelle (stockée en HMAC).

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py creer_groupes
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py charger_demo            # compte demo.apprenant + stage fictif complet (≈ 3 Mo)
```

## Onglet **Web**

- *Add a new web app* → *Manual configuration* → Python 3.13.
- **Virtualenv** : `/home/esrventisax/esr2ventisax/webapp/.venv`
- **Source code** et **Working directory** : `/home/esrventisax/esr2ventisax/webapp`
- **WSGI** (fichier proposé par PythonAnywhere, tout remplacer par) :

  ```python
  import os, sys
  chemin = "/home/esrventisax/esr2ventisax/webapp"
  if chemin not in sys.path:
      sys.path.insert(0, chemin)
  os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
  from django.core.wsgi import get_wsgi_application
  application = get_wsgi_application()
  ```

- **Static files** :

  | URL | Directory |
  |---|---|
  | `/static/` | `/home/esrventisax/esr2ventisax/webapp/staticfiles` |
  | `/media/` | `/home/esrventisax/esr2ventisax/webapp/media` |

  `/media/` est public par décision (A22) : noms en UUID, EXIF conservé.
- **Force HTTPS** : activé.
- *Reload*.

## Comptes

- **Formateurs** : créés par le superutilisateur seulement. Admin → *Administration* → *Utilisateurs* →
  « Ajouter », choisir le groupe **Formateur** (le statut équipe est réglé automatiquement).
- **Apprenants** : ils s'inscrivent eux-mêmes sur `/inscription/` avec un **code d'invitation** que le
  formateur crée dans *Administration* → *Codes d'invitation* (5 usages, 90 jours par défaut). Le compte
  s'active par le lien reçu par courriel ; sans confirmation, il est supprimé après 7 jours. Le
  superutilisateur peut toujours créer un apprenant à la main (groupe **Apprenant**).
- L'inscription se ferme d'elle-même au-delà de 80 % du disque ou de `MAX_APPRENANTS` apprenants actifs.
- Le quota d'un stage (80 Mo par défaut) se règle dans l'onglet *Suivi* du stage.

## Mise à jour

```bash
cd ~/esr2ventisax && git pull
cd webapp && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate && .venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py creer_groupes      # met à jour les permissions des nouveaux modèles
.venv/bin/python manage.py charger_demo       # facultatif : remet la démo à neuf
```

Puis *Reload* dans l'onglet Web.

## Compte de démonstration (A38)

`charger_demo` crée ou réinitialise `demo.apprenant` (mot de passe `demo-local-2026`, public par choix, voir
README) et un stage fictif complet. La commande supprime d'abord l'ancien stage démo et ses fichiers : la relancer
ne remplit pas le disque. `--mot-de-passe` permet d'en choisir un autre.

## Maintien du compte gratuit (A17)

- Au moins **tous les 3 mois** : onglet Web → **Run until 3 months from today**, sinon l'application est désactivée.
- Pas de sauvegarde automatique de SQLite : chaque apprenant télécharge son **dossier terrain** au moins une fois
  par semaine (le tableau de bord passe en orange après 7 jours). Restauration :
  `python manage.py restaurer_dossier <zip> --proprietaire <identifiant>`.
- Disque : 512 Mo au total ; le tableau de bord du superutilisateur alerte au-delà de 80 %.
