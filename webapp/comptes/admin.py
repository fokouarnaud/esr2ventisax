"""Admin des comptes : connexion unique (B6), utilisateurs dans Unfold (B12), codes du formateur (B7), démo (B10)."""

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

from carnet.acces import GROUPE_APPRENANT, GROUPE_FORMATEUR, est_formateur

from .models import CodeInvitation, generer_code


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

class FormulaireAjoutUtilisateur(UserCreationForm):
    groupe = forms.ChoiceField(label="Groupe", choices=[(GROUPE_APPRENANT, GROUPE_APPRENANT),
                                                       (GROUPE_FORMATEUR, GROUPE_FORMATEUR)],
                               widget=UnfoldAdminSelectWidget,
                               help_text="Règle aussi l'accès à l'administration (statut équipe).")


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UtilisateurAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = FormulaireAjoutUtilisateur
    change_password_form = AdminPasswordChangeForm
    libelle_ajout = "Ajouter un utilisateur"
    list_display = ["username", "nom_complet", "email", "groupe", "courriel_verifie", "is_active", "date_joined",
                    "code_utilise"]
    list_filter = ["groups", "is_active", "profil__email_verifie"]
    add_fieldsets = [(None, {"classes": ["wide"], "fields": ["username", "usable_password", "password1",
                                                             "password2", "groupe"]})]

    def has_module_permission(self, request):
        return request.user.is_superuser

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profil__code_utilise").prefetch_related("groups")

    @admin.display(description="Nom")
    def nom_complet(self, obj):
        return obj.get_full_name()

    @admin.display(description="Groupe")
    def groupe(self, obj):
        return ", ".join(g.name for g in obj.groups.all())

    @admin.display(description="Courriel vérifié", boolean=True)
    def courriel_verifie(self, obj):
        return getattr(getattr(obj, "profil", None), "email_verifie", False)

    @admin.display(description="Code utilisé")
    def code_utilise(self, obj):
        profil = getattr(obj, "profil", None)
        return profil.code_utilise.code if profil and profil.code_utilise else "—"

    def save_model(self, request, obj, form, change):
        if not change and "groupe" in form.cleaned_data:
            obj.is_staff = True
        super().save_model(request, obj, form, change)
        if not change and "groupe" in form.cleaned_data:
            obj.groups.set([Group.objects.get_or_create(name=form.cleaned_data["groupe"])[0]])


@admin.register(Group)
class GroupeAdmin(BaseGroupAdmin, ModelAdmin):
    libelle_ajout = "Ajouter un groupe"
    def has_module_permission(self, request):
        return request.user.is_superuser


# --- Codes d'invitation (B2, B7) ---

@admin.register(CodeInvitation)
class CodeInvitationAdmin(ModelAdmin):
    list_display = ["code", "formateur", "usages_sur_max", "expire_le", "actif", "nombre_inscrits"]
    list_filter = ["actif"]
    search_fields = ["code"]
    readonly_fields = ["code", "usages"]
    actions = ["desactiver", "activer", "regenerer"]
    libelle_ajout = "Ajouter un code"

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("formateur")
        return qs if request.user.is_superuser else qs.filter(formateur=request.user)

    def get_object(self, request, object_id, from_field=None):
        objet = super().get_object(request, object_id, from_field)
        if objet is None:
            raise Http404("Code introuvable.")
        return objet

    def _autorise(self, request):
        return request.user.is_superuser or est_formateur(request.user)

    def has_module_permission(self, request):
        return self._autorise(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._autorise(request) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return self._autorise(request) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self._autorise(request) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._autorise(request) and super().has_delete_permission(request, obj)

    def get_fields(self, request, obj=None):
        champs = ["code", "usages", "usages_max", "expire_le", "actif"]
        return (["formateur"] + champs) if request.user.is_superuser else champs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "formateur":
            kwargs["queryset"] = User.objects.filter(groups__name=GROUPE_FORMATEUR) | User.objects.filter(
                is_superuser=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser or not obj.formateur_id:
            obj.formateur = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Usages")
    def usages_sur_max(self, obj):
        return f"{obj.usages} / {obj.usages_max}"

    @admin.display(description="Apprenants inscrits")
    def nombre_inscrits(self, obj):
        return obj.profils.filter(email_verifie=True).count()

    @admin.action(description="Désactiver les codes sélectionnés")
    def desactiver(self, request, queryset):
        n = queryset.update(actif=False)
        self.message_user(request, f"{n} code(s) désactivé(s).", messages.SUCCESS)

    @admin.action(description="Activer les codes sélectionnés")
    def activer(self, request, queryset):
        n = queryset.update(actif=True)
        self.message_user(request, f"{n} code(s) activé(s).", messages.SUCCESS)

    @admin.action(description="Régénérer les codes sélectionnés (usages remis à zéro)")
    def regenerer(self, request, queryset):
        for code in queryset:
            code.code, code.usages = generer_code(), 0
            code.save(update_fields=["code", "usages", "modifie_le"])
        self.message_user(request, f"{queryset.count()} code(s) régénéré(s).", messages.SUCCESS)
