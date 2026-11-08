"""Inscription par code d'invitation (US-36, US-37, US-42) : courriel vérifié, pot de miel, limite par IP."""

import hashlib
import hmac
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from carnet.acces import GROUPE_APPRENANT

from .models import CodeInvitation, LimiteInscription, Profil


class JetonVerification(PasswordResetTokenGenerator):
    """Jeton à usage unique : il change dès que le compte est activé ou vérifié."""

    key_salt = "comptes.inscription.JetonVerification"

    def _make_hash_value(self, user, timestamp):
        verifie = Profil.objects.filter(user=user, email_verifie=True).exists()
        return f"{user.pk}{timestamp}{user.is_active}{verifie}{user.email}"


jeton_verification = JetonVerification()


def jamais_confirmes():
    """Comptes de l'inscription publique dont le lien n'a jamais servi."""
    return User.objects.filter(is_active=False, profil__inscrit_par_formulaire=True, profil__email_verifie=False)


def confirmes_ou_actifs():
    return User.objects.exclude(pk__in=jamais_confirmes())


class FormulaireInscription(UserCreationForm):
    code = forms.CharField(label="Code d'invitation", max_length=20,
                           help_text="Huit caractères, remis par votre formateur.")
    avertissement_photos = forms.BooleanField(
        label="J'ai compris que mes photos sont accessibles par leur lien et gardent leur position GPS.")
    site_web = forms.CharField(required=False, label="Site web")  # pot de miel, masqué en CSS

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nom in ("first_name", "last_name", "email"):
            self.fields[nom].required = True
        # Aides courtes : celles de Django allongent le formulaire au téléphone
        self.fields["username"].label = "Identifiant"
        self.fields["username"].help_text = "Lettres, chiffres et @ . + - _ ; il servira à vous connecter."
        self.fields["password1"].help_text = "8 caractères au moins, pas seulement des chiffres, ni proche de votre nom."
        self.fields["password2"].help_text = ""
        self.fields["email"].label = "Courriel"
        self.fields["email"].help_text = "Le lien de confirmation y sera envoyé."
        attributs = {"first_name": "given-name", "last_name": "family-name", "username": "username",
                     "email": "email", "password1": "new-password", "password2": "new-password"}
        for nom, auto in attributs.items():
            self.fields[nom].widget.attrs["autocomplete"] = auto
        self.fields["username"].widget.attrs["autocapitalize"] = "none"
        self.fields["username"].widget.attrs.pop("autofocus", None)  # le 2e champ ne doit pas ouvrir le clavier
        self.fields["code"].widget.attrs.update({"autocapitalize": "characters", "autocomplete": "off",
                                                "spellcheck": "false"})

    def clean_code(self):
        saisi = self.cleaned_data["code"].strip().upper()
        code = CodeInvitation.objects.filter(code=saisi).first()
        if code is None or not code.est_utilisable():
            raise forms.ValidationError("Ce code est inconnu, désactivé, expiré ou déjà utilisé au maximum.")
        return code

    def clean_username(self):
        nom = self.cleaned_data.get("username")
        if nom and not confirmes_ou_actifs().filter(username__iexact=nom).exists():
            return nom  # libre, ou tenu par un compte jamais confirmé que l'inscription remplacera
        raise forms.ValidationError("Cet identifiant est déjà pris.")

    def clean_email(self):
        courriel = self.cleaned_data["email"].strip()
        if confirmes_ou_actifs().filter(email__iexact=courriel).exists():
            raise forms.ValidationError("Un compte utilise déjà cette adresse.")
        return courriel

    def validate_unique(self):
        exclude = self._get_validation_exclusions() | {"username"}  # jugé par clean_username
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            self._update_errors(e)

    @property
    def est_un_robot(self):
        return bool(self.data.get("site_web"))


def empreinte_ip(request):
    """HMAC de l'adresse IP : jamais stockée en clair."""
    ip = request.META.get(settings.INSCRIPTION_IP_HEADER) or request.META.get("REMOTE_ADDR", "")
    ip = ip.split(",")[0].strip()
    return hmac.new(force_bytes(settings.SECRET_KEY), force_bytes(ip), hashlib.sha256).hexdigest()


def limite_atteinte(ip_hachee, maintenant=None):
    depuis = (maintenant or timezone.now()) - timedelta(hours=1)
    LimiteInscription.objects.filter(survenu_le__lt=depuis).delete()
    return LimiteInscription.objects.filter(ip_hachee=ip_hachee).count() >= settings.INSCRIPTIONS_MAX_PAR_HEURE


def inscription_fermee():
    """B8 : disque au-delà du seuil d'alerte, ou plafond d'apprenants actifs atteint."""
    from carnet.services.quota import OCTETS_PAR_MO
    from carnet.services.tableau_de_bord import occupation_globale

    disque = occupation_globale([settings.MEDIA_ROOT, settings.BASE_DIR / "db.sqlite3"],
                                total_octets=settings.CARNET_DISQUE_TOTAL_MO * OCTETS_PAR_MO)
    actifs = User.objects.filter(is_active=True, groups__name=GROUPE_APPRENANT).count()
    return disque["alerte"] or actifs >= settings.MAX_APPRENANTS


@transaction.atomic
def creer_apprenant_en_attente(form):
    """Compte inactif ; remplace un compte jamais confirmé du même identifiant ou courriel."""
    nom, courriel = form.cleaned_data["username"], form.cleaned_data["email"]
    for ancien in jamais_confirmes().filter(Q(username__iexact=nom) | Q(email__iexact=courriel)):
        supprimer_compte_en_attente(ancien)
    code = CodeInvitation.objects.select_for_update().get(pk=form.cleaned_data["code"].pk)
    user = form.save(commit=False)
    user.is_active = False
    user.is_staff = True
    user.save()
    user.groups.add(Group.objects.get_or_create(name=GROUPE_APPRENANT)[0])
    Profil.objects.filter(user=user).update(inscrit_par_formulaire=True, email_verifie=False, code_utilise=code)
    CodeInvitation.objects.filter(pk=code.pk).update(usages=F("usages") + 1)
    return user


@transaction.atomic
def supprimer_compte_en_attente(user):
    """Supprime un compte jamais confirmé et rend l'usage de son code."""
    code_id = Profil.objects.filter(user=user).values_list("code_utilise", flat=True).first()
    if code_id:
        CodeInvitation.objects.filter(pk=code_id, usages__gt=0).update(usages=F("usages") - 1)
    user.delete()


DUREE_SANS_CONFIRMATION = timedelta(days=7)
INTERVALLE_MAINTENANCE = 3600  # secondes, par processus : le compte gratuit n'a pas de tâche planifiée
_derniere_maintenance = 0.0


def purger_comptes_non_confirmes(maintenant=None):
    """Supprime les inscrits jamais confirmés depuis plus de 7 jours ; rend l'usage de leur code."""
    limite = (maintenant or timezone.now()) - DUREE_SANS_CONFIRMATION
    perimes = list(jamais_confirmes().filter(date_joined__lt=limite))
    for user in perimes:
        supprimer_compte_en_attente(user)
    return len(perimes)


def maintenance_si_due():
    global _derniere_maintenance
    import time

    if _derniere_maintenance and time.monotonic() - _derniere_maintenance < INTERVALLE_MAINTENANCE:
        return False
    _derniere_maintenance = time.monotonic()
    purger_comptes_non_confirmes()
    return True


def reinitialiser_maintenance():
    global _derniere_maintenance
    _derniere_maintenance = 0.0


def envoyer_courriel_verification(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    lien = request.build_absolute_uri(reverse("comptes:verifier", args=[uid, jeton_verification.make_token(user)]))
    send_mail(
        subject="Confirmez votre inscription au Carnet de stage",
        message=render_to_string("comptes/email/verifier.txt", {"user": user, "lien": lien}),
        from_email=None,
        recipient_list=[user.email],
    )
