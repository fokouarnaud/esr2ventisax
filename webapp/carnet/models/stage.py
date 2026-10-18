from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.text import slugify

from .base import ModeleBase


def jours_lundi_samedi():
    return [0, 1, 2, 3, 4, 5]


class Stage(ModeleBase):
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stages"
    )
    formateur_referent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stages_suivis",
    )
    intitule = models.CharField("intitulé", max_length=200)
    slug = models.SlugField(max_length=80, blank=True)
    specialite = models.CharField("spécialité", max_length=150, blank=True)
    theme = models.CharField("thème", max_length=200, blank=True)
    sous_theme = models.CharField("sous-thème", max_length=250, blank=True)

    # Couverture : 9 champs obligatoires du cours (p. 25)
    apprenant_nom = models.CharField("nom et prénoms du stagiaire", max_length=200, blank=True)
    titre_rapport = models.CharField("titre du rapport", max_length=250, blank=True)
    type_rapport = models.CharField("type de rapport", max_length=100, default="Rapport de stage")
    tuteur_pro = models.CharField("responsable professionnel", max_length=200, blank=True)
    tuteur_pro_poste = models.CharField("poste du responsable professionnel", max_length=200, blank=True)
    tuteur_acad = models.CharField("responsable académique", max_length=200, blank=True)
    tuteur_acad_poste = models.CharField("poste du responsable académique", max_length=200, blank=True)
    entreprise = models.CharField("entreprise", max_length=200, blank=True)
    entreprise_sigle = models.CharField("sigle de l'entreprise", max_length=50, blank=True)
    cfp = models.CharField("centre de formation", max_length=200, blank=True)
    cfp_sigle = models.CharField("sigle du centre", max_length=50, blank=True)
    diplome = models.CharField("formation / diplôme préparé", max_length=200, blank=True)
    annee_etude = models.CharField("année d'étude", max_length=50, blank=True)
    session = models.CharField("session", max_length=50, blank=True)
    date_debut = models.DateField("date de début")
    date_fin = models.DateField("date de fin")
    logo_entreprise = models.ImageField(upload_to="logos/", blank=True)
    logo_cfp = models.ImageField(upload_to="logos/", blank=True)

    jours_travailles = models.JSONField("jours travaillés", default=jours_lundi_samedi)
    quota_mo = models.PositiveIntegerField("quota (Mo)", default=80)
    derniere_sauvegarde = models.DateTimeField("dernière sauvegarde", null=True, blank=True)

    class Meta:
        ordering = ["-date_debut"]

    def __str__(self):
        return self.intitule

    def clean(self):
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError({"date_fin": "La date de fin précède la date de début."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.intitule)[:80] or "stage"
        creation = self._state.adding
        with transaction.atomic():
            super().save(*args, **kwargs)
            if creation:
                FicheEntreprise.objects.create(stage=self)
                Mission.objects.create(stage=self)
                BilanPersonnel.objects.create(stage=self)


class FicheEntreprise(ModeleBase):
    """Les 11 rubriques « entreprise » du cours (p. 26), plus l'identité pour infos.tex."""

    stage = models.OneToOneField(Stage, on_delete=models.CASCADE, related_name="fiche_entreprise")
    presentation = models.TextField("présentation", blank=True)
    organisation = models.TextField("organisation générale", blank=True)
    historique = models.TextField("historique de l'entreprise", blank=True)
    secteurs = models.TextField("secteur(s) d'activité", blank=True)
    marches = models.TextField("marchés de l'entreprise", blank=True)
    clients_fournisseurs = models.TextField("clients et fournisseurs", blank=True)
    concurrence = models.TextField("situation concurrentielle", blank=True)
    chiffres_cles = models.TextField("chiffres clés", blank=True)
    perspectives = models.TextField("perspectives d'évolution (atouts, faiblesses, menaces, opportunités)", blank=True)
    mutations_technologiques = models.TextField("mutations technologiques", blank=True)
    volonte_dirigeants = models.TextField("volonté des dirigeants", blank=True)
    ville = models.CharField(max_length=100, blank=True)
    quartier = models.CharField("quartier, repères", max_length=200, blank=True)
    annee_creation = models.CharField("année de création", max_length=20, blank=True)
    dirigeant = models.CharField("directeur général", max_length=200, blank=True)
    capital = models.CharField("capital social", max_length=100, blank=True)
    effectif = models.CharField(max_length=50, blank=True)
    contact = models.CharField("BP, téléphone, courriel, site web", max_length=250, blank=True)

    class Meta:
        verbose_name = "fiche entreprise"
        verbose_name_plural = "fiches entreprise"

    def __str__(self):
        return f"Fiche entreprise : {self.stage}"


class Mission(ModeleBase):
    """Les 9 rubriques « mission » du cours (p. 26)."""

    stage = models.OneToOneField(Stage, on_delete=models.CASCADE, related_name="mission")
    poste = models.TextField("poste occupé", blank=True)
    position_organigramme = models.TextField("position du poste dans l'organigramme", blank=True)
    faits_importants = models.TextField("faits importants", blank=True)
    objectifs_enjeux = models.TextField("objectifs et enjeux de la mission", blank=True)
    methodes_moyens = models.TextField("méthodes et moyens employés", blank=True)
    collaborateurs = models.TextField("personnes avec lesquelles vous avez collaboré", blank=True)
    responsabilites = models.TextField("responsabilités exercées", blank=True)
    resultats = models.TextField("résultats obtenus", blank=True)
    difficultes_solutions = models.TextField("difficultés rencontrées et solutions apportées", blank=True)

    def __str__(self):
        return f"Mission : {self.stage}"


class BilanPersonnel(ModeleBase):
    """Questions de la p. 24 du cours, plus critiques et suggestions (Partie IV)."""

    stage = models.OneToOneField(Stage, on_delete=models.CASCADE, related_name="bilan")
    pourquoi_ce_stage = models.TextField("pourquoi avoir choisi ce stage ?", blank=True)
    appreciation = models.TextField("avez-vous apprécié ce stage ?", blank=True)
    attentes_atteintes = models.TextField("le stage a-t-il répondu à vos attentes ?", blank=True)
    apprecie_comme_stagiaire = models.TextField("avez-vous été apprécié comme stagiaire ?", blank=True)
    resultats_remarques = models.TextField("vos résultats ont-ils été remarqués ?", blank=True)
    travail_equipe = models.TextField("travail en équipe et relationnel", blank=True)
    consequence_carriere = models.TextField("conséquence sur votre projet de carrière", blank=True)
    critiques = models.TextField("critiques", blank=True)
    suggestions = models.TextField("suggestions", blank=True)

    class Meta:
        verbose_name = "bilan personnel"
        verbose_name_plural = "bilans personnels"

    def __str__(self):
        return f"Bilan : {self.stage}"
