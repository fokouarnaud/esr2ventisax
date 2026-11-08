"""US-44 : envoi des courriels configuré sans exposer le secret (B5, B14)."""

from pathlib import Path

from tests.test_deploiement import PROD, WEBAPP, lancer

CLE = {"DJANGO_SECRET_KEY": "x" * 50}
SMTP = {"EMAIL_HOST_USER": "carnet@exemple.cm", "EMAIL_HOST_PASSWORD": "factice-pour-test"}
SANS_SMTP = {"EMAIL_HOST_USER": "", "EMAIL_HOST_PASSWORD": ""}
VERIFIER = ("from django.core.management import call_command; "
            "call_command('check', deploy=True, fail_level='CRITICAL')")


def test_check_deploy_signale_un_smtp_absent():
    resultat = lancer(VERIFIER, **CLE, **PROD, **SANS_SMTP)
    assert "comptes.E001" in resultat.stdout + resultat.stderr


def test_check_deploy_silencieux_quand_le_smtp_est_configure():
    resultat = lancer(VERIFIER, **CLE, **PROD, **SMTP)
    assert "comptes.E001" not in resultat.stdout + resultat.stderr
    assert "factice-pour-test" not in resultat.stdout + resultat.stderr


def test_production_envoie_par_gmail_avec_tls():
    code = ("from django.conf import settings as s; "
            "print(s.EMAIL_BACKEND, s.EMAIL_HOST, s.EMAIL_PORT, s.EMAIL_USE_TLS, s.DEFAULT_FROM_EMAIL)")
    resultat = lancer(code, **CLE, **PROD, **SMTP)
    assert resultat.stdout.strip() == ("django.core.mail.backends.smtp.EmailBackend smtp.gmail.com 587 True "
                                       "Carnet de stage <carnet@exemple.cm>"), resultat.stderr


def test_developpement_sans_mot_de_passe_affiche_les_courriels_dans_la_console():
    code = "from django.conf import settings; print(settings.EMAIL_BACKEND)"
    resultat = lancer(code, DJANGO_DEBUG="1", **SANS_SMTP)
    assert resultat.stdout.strip() == "django.core.mail.backends.console.EmailBackend", resultat.stderr


def test_env_example_documente_les_variables_sans_valeur_secrete():
    lignes = dict(l.split("=", 1) for l in (WEBAPP / ".env.example").read_text(encoding="utf-8").splitlines()
                  if "=" in l and not l.startswith("#"))
    for nom in ("EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "MAX_APPRENANTS", "INSCRIPTION_IP_HEADER"):
        assert nom in lignes
    assert lignes["EMAIL_HOST_PASSWORD"] == ""


def test_deploiement_explique_le_collage_du_mot_de_passe():
    texte = (WEBAPP / "DEPLOIEMENT.md").read_text(encoding="utf-8")
    assert "EMAIL_HOST_PASSWORD" in texte and "HTTP_X_REAL_IP" in texte
