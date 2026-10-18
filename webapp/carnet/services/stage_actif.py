"""Stage actif mémorisé en session (US-04) : la note rapide s'y rattache."""

from django.core.exceptions import PermissionDenied

from carnet.acces import stages_modifiables

CLE_SESSION = "carnet_stage_actif"


def stage_actif(request):
    stages = stages_modifiables(request.user)
    choisi = request.session.get(CLE_SESSION)
    if choisi:
        stage = stages.filter(pk=choisi).first()
        if stage:
            return stage
    return stages.order_by("-date_debut").first()


def choisir_stage_actif(request, stage):
    if not stages_modifiables(request.user).filter(pk=stage.pk).exists():
        raise PermissionDenied("Ce stage ne vous appartient pas.")
    request.session[CLE_SESSION] = str(stage.pk)
