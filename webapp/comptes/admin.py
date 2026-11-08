"""Admin des comptes : connexion unique (B6), utilisateurs dans Unfold (B12), démo (B10) ; plus de codes ni de formateur (B17, B19)."""

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminSelectWidget


from .models import Profil


# --- Connexion unique (B6) ---

def connexion_publique(request, extra_context=None):
    """/admin/login/ renvoie à /connexion/ en gardant la chaîne de requête (donc `next`).

    Un compte déjà connecté mais sans accès à l'admin irait sinon de /connexion/ à /admin/ sans fin.
    """
    if request.user.is_authenticated and not admin.site.has_permission(request):
        return render(request, "comptes/sans_acces.html", status=403)
    url = reverse("comptes:connexion")
    requete = request.META.get("QUERY_STRING", "")
    return redirect(f"{url}?{requete}" if requete else url)


admin.site.login = connexion_publique

_password_change = admin.site.password_change


def password_change_sauf_demo(request, extra_context=None):
    """Le compte démo a des identifiants publics : personne ne doit pouvoir les changer (B10)."""
    if request.user.get_username() == settings.COMPTE_DEMO:
        raise PermissionDenied("Le mot de passe du compte de démonstration ne se change pas.")
    return _password_change(request, extra_context)


admin.site.password_change = password_change_sauf_demo


# --- Utilisateurs et groupes (B12) ---

AIDE_PROFIL = ("Le profil porte les droits : Apprenant (ses propres stages) ou Administrateur (tout, dont les "
               "comptes). Groupes et statuts en découlent.")


def champ_profil():
    return forms.ChoiceField(label="Profil", choices=Profil.Role.choices, widget=UnfoldAdminSelectWidget,
                             help_text=AIDE_PROFIL)


class FormulaireAjoutUtilisateur(UserCreationForm):
    role = champ_profil()


class FormulaireUtilisateur(UserChangeForm):
    role = champ_profil()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profil = getattr(self.instance, "profil", None)
        if profil:
            self.fields["role"].initial = profil.role


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UtilisateurAdmin(BaseUserAdmin, ModelAdmin):
    """Un utilisateur = un profil (B15) : ni groupes, ni permissions, ni cases équipe/superutilisateur."""

    form = FormulaireUtilisateur
    add_form = FormulaireAjoutUtilisateur
    change_password_form = AdminPasswordChangeForm
    libelle_ajout = "Ajouter un utilisateur"
    list_display = ["username", "nom_complet", "email", "profil_role", "courriel_verifie", "is_active",
                    "date_joined"]
    list_filter = ["profil__role", "is_active", "profil__email_verifie"]
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Identité", {"fields": ["first_name", "last_name", "email"]}),
        ("Profil et accès", {"fields": ["role", "is_active"]}),
        ("Dates", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [(None, {"classes": ["wide"], "fields": ["username", "usable_password", "password1",
                                                             "password2", "role"]})]

    def has_module_permission(self, request):
        return request.user.is_superuser

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profil")

    @admin.display(description="Nom")
    def nom_complet(self, obj):
        return obj.get_full_name()

    @admin.display(description="Profil", ordering="profil__role")
    def profil_role(self, obj):
        profil = getattr(obj, "profil", None)
        return profil.get_role_display() if profil else "—"

    @admin.display(description="Courriel vérifié", boolean=True)
    def courriel_verifie(self, obj):
        return getattr(getattr(obj, "profil", None), "email_verifie", False)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "role" in form.cleaned_data:
            profil = Profil.objects.get(user=obj)
            profil.role = form.cleaned_data["role"]
            profil.save()  # applique groupes, statut équipe et superutilisateur


@admin.register(Group)
class GroupeAdmin(BaseGroupAdmin, ModelAdmin):
    libelle_ajout = "Ajouter un groupe"
    def has_module_permission(self, request):
        return request.user.is_superuser
