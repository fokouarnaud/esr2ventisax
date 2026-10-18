"""Admin Unfold cloisonnée (A1, A13, A32) : chaque requête passe par carnet.acces."""

import unicodedata

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .acces import GROUPE_FORMATEUR, est_formateur, filtrer_modifiables, filtrer_visibles, stages_modifiables, \
    stages_visibles
from .models import (
    Abreviation, Absence, BilanPersonnel, DonneeTechnique, EntreeJournal, Equipement, FicheEntreprise, Lieu,
    Mission, NoeudOrganigramme, Personne, Photo, Reference, Rubrique, Stage, Tache,
)

admin.site.site_header = admin.site.site_title = "Carnet de stage"
admin.site.index_title = "Tableau de bord"

_get_app_list = admin.site.get_app_list


def _get_app_list_sans_accents(request, app_label=None):
    """Tri à la française : « Équipements » se range après « Données », pas après « Tâches »."""
    apps = _get_app_list(request, app_label)
    for app in apps:
        app["models"].sort(key=lambda m: unicodedata.normalize("NFKD", str(m["name"])).encode("ascii", "ignore").lower())
    return apps


admin.site.get_app_list = _get_app_list_sans_accents

MODELES_DE_STAGE = {Lieu, Tache, Equipement, Personne, EntreeJournal, Photo, Reference, DonneeTechnique,
                    NoeudOrganigramme}


class CloisonneAdmin(ModelAdmin):
    """Base de toutes les admins : queryset, objets, choix de clés étrangères et droits limités au stage."""

    def _stages_visibles(self, request):
        return stages_visibles(request.user)

    def get_queryset(self, request):
        return filtrer_visibles(request.user, super().get_queryset(request))

    def get_object(self, request, object_id, from_field=None):
        objet = super().get_object(request, object_id, from_field)
        if objet is None:
            raise Http404("Objet introuvable.")
        return objet

    def _modifiable(self, request, obj):
        return obj is None or stages_modifiables(request.user).filter(pk=obj.stage_id).exists()

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and self._modifiable(request, obj)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) and self._modifiable(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        cible = db_field.related_model
        if cible is Stage:
            kwargs["queryset"] = stages_modifiables(request.user)
        elif cible in MODELES_DE_STAGE:
            kwargs["queryset"] = filtrer_modifiables(request.user, cible.objects.all())
        elif cible is Rubrique:
            kwargs["queryset"] = _rubriques_permises(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        cible = db_field.related_model
        if cible is Rubrique:
            kwargs["queryset"] = _rubriques_permises(request)
        elif cible in MODELES_DE_STAGE:
            kwargs["queryset"] = filtrer_modifiables(request.user, cible.objects.all())
        return super().formfield_for_manytomany(db_field, request, **kwargs)


def _rubriques_permises(request):
    return Rubrique.objects.filter(Q(stage__isnull=True) | Q(stage__in=stages_modifiables(request.user)))


# --- Stage et formulaires du cours ------------------------------------------------------

@admin.register(Stage)
class StageAdmin(CloisonneAdmin):
    list_display = ["intitule", "entreprise", "date_debut", "date_fin", "lien_export"]
    search_fields = ["intitule", "entreprise", "theme"]
    readonly_fields = ["derniere_sauvegarde"]
    fieldsets = [
        (None, {"fields": ["intitule", "specialite", "theme", "sous_theme", "date_debut", "date_fin"]}),
        ("Couverture", {"classes": ["tab"], "fields": [
            "apprenant_nom", "titre_rapport", "type_rapport", "entreprise", "entreprise_sigle", "logo_entreprise",
            "cfp", "cfp_sigle", "logo_cfp", "diplome", "annee_etude", "session",
            "tuteur_pro", "tuteur_pro_poste", "tuteur_acad", "tuteur_acad_poste"]}),
        ("Suivi", {"classes": ["tab"], "fields": [
            "formateur_referent", "jours_travailles", "quota_mo", "derniere_sauvegarde"]}),
    ]

    def get_queryset(self, request):
        return stages_visibles(request.user)

    def _modifiable(self, request, obj):
        return obj is None or stages_modifiables(request.user).filter(pk=obj.pk).exists()

    def get_readonly_fields(self, request, obj=None):
        champs = list(super().get_readonly_fields(request, obj))
        return champs if request.user.is_superuser else champs + ["quota_mo"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "formateur_referent":
            kwargs["queryset"] = get_user_model().objects.filter(groups__name=GROUPE_FORMATEUR)
            return super(CloisonneAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.proprietaire = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Dossier terrain")
    def lien_export(self, obj):
        return format_html('<a href="{}">Télécharger le zip</a>', reverse("carnet:export", args=[obj.pk]))


class FormulaireDuStageAdmin(CloisonneAdmin):
    """Fiche entreprise, mission et bilan : créés avec le stage, ni ajout ni suppression."""

    list_display = ["stage"]
    exclude = ["stage"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(FicheEntreprise, FormulaireDuStageAdmin)
admin.site.register(Mission, FormulaireDuStageAdmin)
admin.site.register(BilanPersonnel, FormulaireDuStageAdmin)


# --- Journal ------------------------------------------------------------------------------

@admin.register(EntreeJournal)
class EntreeJournalAdmin(CloisonneAdmin):
    list_display = ["date", "apercu", "completee", "stage"]
    list_filter = ["completee", "rubriques", "date"]
    search_fields = ["texte", "activites"]
    date_hierarchy = "date"
    filter_horizontal = ["rubriques", "equipements", "personnes"]
    fieldsets = [
        (None, {"fields": ["stage", "date", "heure", "texte", "completee", "rubriques"]}),
        ("Rapport d'activité", {"classes": ["tab"], "fields": [
            "objectifs", "moyens_humains", "moyens_materiels", "methodologie", "activites", "elements_theoriques",
            "difficultes", "solutions", "appreciation"]}),
        ("Intervention", {"classes": ["tab"], "fields": [
            "intervention_nature", "intervention_duree_h", "intervention_cout", "intervention_ressources"]}),
        ("Liens", {"classes": ["tab"], "fields": [
            "lieu", "tache", "equipements", "personnes", "latitude", "longitude"]}),
        ("Formateur", {"classes": ["tab"], "fields": ["remarque_formateur"]}),
    ]

    @admin.display(description="note")
    def apercu(self, obj):
        return obj.texte[:80]

    def _referent(self, request, obj):
        return obj is not None and est_formateur(request.user) and obj.stage.formateur_referent_id == request.user.pk

    def has_change_permission(self, request, obj=None):
        if self._referent(request, obj):
            return True
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if self._referent(request, obj):
            tous = [f.name for f in EntreeJournal._meta.get_fields() if f.concrete and f.editable and not f.auto_created]
            return [c for c in tous if c != "remarque_formateur"]
        return ["remarque_formateur"] if not request.user.is_superuser else []


@admin.register(Photo)
class PhotoAdmin(CloisonneAdmin):
    list_display = ["miniature", "legende", "slug", "destination", "prise_le"]
    list_editable = ["destination"]
    list_filter = ["destination", "rubriques"]
    readonly_fields = ["miniature", "fichier", "taille_octets", "prise_le", "latitude", "longitude"]
    filter_horizontal = ["rubriques"]
    exclude = ["stage"]

    def has_add_permission(self, request):
        return False  # les photos arrivent par la note rapide (compression + quota)

    @admin.display(description="aperçu")
    def miniature(self, obj):
        return format_html('<img src="{}" style="height:56px;border-radius:12px">', obj.fichier.url) if obj.fichier else ""


@admin.register(Rubrique)
class RubriqueAdmin(CloisonneAdmin):
    list_display = ["libelle", "partie", "parent", "ordre", "stage"]
    list_filter = ["partie"]

    def get_queryset(self, request):
        qs = ModelAdmin.get_queryset(self, request)
        return qs.filter(Q(stage__isnull=True) | Q(stage__in=stages_visibles(request.user)))

    def _modifiable(self, request, obj):
        if obj is not None and obj.est_du_cours:
            return request.user.is_superuser
        return super()._modifiable(request, obj)


@admin.register(Absence)
class AbsenceAdmin(RubriqueAdmin):
    list_display = ["__str__", "date_debut", "date_fin", "motif", "stage"]
    list_filter = ["motif"]

    def _modifiable(self, request, obj):
        if obj is not None and obj.stage_id is None:
            return request.user.is_superuser
        return CloisonneAdmin._modifiable(self, request, obj)


@admin.register(Lieu)
class LieuAdmin(CloisonneAdmin):
    list_display = ["nom", "type", "ville", "quartier"]


@admin.register(Tache)
class TacheAdmin(CloisonneAdmin):
    list_display = ["libelle", "date_debut", "date_fin", "lieu"]


@admin.register(Equipement)
class EquipementAdmin(CloisonneAdmin):
    list_display = ["designation", "categorie", "caracteristiques"]
    list_filter = ["categorie"]
    filter_horizontal = ["rubriques"]


@admin.register(Personne)
class PersonneAdmin(CloisonneAdmin):
    list_display = ["nom", "fonction", "role", "a_remercier", "nom_publiable"]


@admin.register(Reference)
class ReferenceAdmin(CloisonneAdmin):
    list_display = ["cle_bibtex", "auteur", "titre", "annee", "type"]
    readonly_fields = ["cle_bibtex"]


@admin.register(DonneeTechnique)
class DonneeTechniqueAdmin(CloisonneAdmin):
    list_display = ["grandeur", "valeur", "unite", "nature", "reference"]
    list_filter = ["nature"]


@admin.register(NoeudOrganigramme)
class NoeudOrganigrammeAdmin(CloisonneAdmin):
    list_display = ["poste", "nom", "parent", "est_stagiaire"]


@admin.register(Abreviation)
class AbreviationAdmin(CloisonneAdmin):
    list_display = ["sigle", "signification"]
