"""Pages publiques des comptes (P4-4)."""

import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from . import inscription as svc
from .models import LimiteInscription, Profil

journal = logging.getLogger(__name__)


def inscription(request):
    if svc.inscription_fermee():
        return render(request, "comptes/inscription.html", {"inscription_fermee": True})
    form = svc.FormulaireInscription(request.POST or None)
    if request.method == "POST":
        if form.est_un_robot:
            return redirect("comptes:inscription_envoyee")
        ip = svc.empreinte_ip(request)
        if svc.limite_atteinte(ip):
            return HttpResponse("Trop d'inscriptions depuis cette connexion. Réessayez dans une heure.",
                                status=429, content_type="text/plain; charset=utf-8")
        if form.is_valid():
            LimiteInscription.objects.create(ip_hachee=ip)
            user = svc.creer_apprenant_en_attente(form)
            try:
                svc.envoyer_courriel_verification(request, user)
            except OSError:
                journal.exception("Échec de l'envoi du courriel de vérification")
                svc.supprimer_compte_en_attente(user)
                form.add_error(None, "Le courriel de confirmation n'a pas pu partir. Réessayez plus tard.")
            else:
                return redirect("comptes:inscription_envoyee")
    return render(request, "comptes/inscription.html", {"form": form, "inscription_fermee": False})


def inscription_envoyee(request):
    return render(request, "comptes/inscription_envoyee.html")


def verifier(request, uidb64, jeton):
    try:
        user = User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
    except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
        user = None
    if user is None or not svc.jeton_verification.check_token(user, jeton):
        return render(request, "comptes/lien_invalide.html", status=400)
    user.is_active = True
    user.save(update_fields=["is_active"])
    Profil.objects.update_or_create(user=user, defaults={"email_verifie": True})
    messages.success(request, "Votre courriel est confirmé : vous pouvez vous connecter.")
    return redirect("comptes:connexion")
