"""US-31 : réglages de production (DEBUG=False, secrets dans .env, HTTPS, /static/ et /media/)."""

import os
import subprocess
import sys
from pathlib import Path

WEBAPP = Path(__file__).resolve().parent.parent
PROD = {"DJANGO_DEBUG": "0", "DJANGO_ALLOWED_HOSTS": "esrventisax.pythonanywhere.com"}


def lancer(code, **env):
    """Charge les réglages dans un processus neuf, sans .env (l'environnement est entièrement contrôlé)."""
    propre = {k: v for k, v in os.environ.items() if not k.startswith(("DJANGO_", "CARNET_"))}
    propre.update(env, DJANGO_SETTINGS_MODULE="config.settings", CARNET_SANS_DOTENV="1")
    return subprocess.run([sys.executable, "-c", f"import django; django.setup(); {code}"], cwd=WEBAPP,
                          env=propre, capture_output=True, text=True)


def test_production_sans_cle_secrete_refuse_de_demarrer():
    resultat = lancer("print('démarré')", **PROD)
    assert resultat.returncode != 0
    assert "DJANGO_SECRET_KEY" in resultat.stderr


def test_production_avec_cle_secrete_demarre_sans_debug():
    resultat = lancer("from django.conf import settings; print(settings.DEBUG, settings.SECURE_SSL_REDIRECT)",
                      DJANGO_SECRET_KEY="x" * 50, **PROD)
    assert resultat.stdout.strip() == "False True", resultat.stderr


def test_wsgi_redirige_http_vers_https():
    code = ("from django.test import Client; "
            "r = Client(HTTP_HOST='esrventisax.pythonanywhere.com').get('/'); "
            "print(r.status_code, r['Location'])")
    resultat = lancer(code, DJANGO_SECRET_KEY="x" * 50, **PROD)
    assert resultat.stdout.strip() == "301 https://esrventisax.pythonanywhere.com/", resultat.stderr


def test_developpement_sans_cle_reste_possible():
    resultat = lancer("from django.conf import settings; print(settings.DEBUG)", DJANGO_DEBUG="1")
    assert resultat.stdout.strip() == "True", resultat.stderr


def test_production_versionne_les_fichiers_statiques():
    code = "from django.conf import settings; print(settings.STORAGES['staticfiles']['BACKEND'])"
    resultat = lancer(code, DJANGO_SECRET_KEY="x" * 50, **PROD)
    assert resultat.stdout.strip() == "django.contrib.staticfiles.storage.ManifestStaticFilesStorage", resultat.stderr


def test_collectstatic_produit_des_noms_avec_empreinte(tmp_path):
    """Échoue si une url() de nos CSS pointe vers un fichier absent (le manifeste refuse alors de se construire)."""
    code = (
        "from django.core.management import call_command; "
        "call_command('collectstatic', interactive=False, verbosity=0); "
        "from django.templatetags.static import static; "
        "print(static('carnet/css/carnet.css')); print(static('carnet/css/admin.css'))"
    )
    resultat = lancer(code, DJANGO_SECRET_KEY="x" * 50, CARNET_STATIC_ROOT=str(tmp_path), **PROD)
    lignes = resultat.stdout.split()
    assert resultat.returncode == 0, resultat.stderr[-2000:]
    assert lignes[0].startswith("/static/carnet/css/carnet.") and lignes[0] != "/static/carnet/css/carnet.css"
    assert lignes[1].startswith("/static/carnet/css/admin.") and lignes[1] != "/static/carnet/css/admin.css"
