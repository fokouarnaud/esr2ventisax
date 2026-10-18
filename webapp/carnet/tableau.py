"""Tableau de bord de l'accueil Unfold (US-25, US-26)."""

from django.conf import settings

from .acces import stages_visibles
from .referentiel import RUBRIQUES_ENTREPRISE, RUBRIQUES_MISSION
from .services.quota import OCTETS_PAR_MO
from .services.stage_actif import stage_actif
from .services.tableau_de_bord import indicateurs, occupation_globale


TOTAL_RUBRIQUES_FORMULAIRES = len(RUBRIQUES_ENTREPRISE) + len(RUBRIQUES_MISSION)


def dashboard_callback(request, context):
    stage = stage_actif(request)
    context["carnet_stage"] = stage
    context["carnet_indicateurs"] = indicateurs(stage) if stage else None
    if stage:
        context["carnet_rubriques_total"] = TOTAL_RUBRIQUES_FORMULAIRES
        context["carnet_rubriques_remplies"] = TOTAL_RUBRIQUES_FORMULAIRES - len(context["carnet_indicateurs"]["rubriques_vides"])
    context["carnet_stages_suivis"] = stages_visibles(request.user).exclude(proprietaire=request.user)
    if request.user.is_superuser:
        context["carnet_disque"] = occupation_globale(
            [settings.MEDIA_ROOT, settings.BASE_DIR / "db.sqlite3"],
            total_octets=settings.CARNET_DISQUE_TOTAL_MO * OCTETS_PAR_MO,
        )
    return context
