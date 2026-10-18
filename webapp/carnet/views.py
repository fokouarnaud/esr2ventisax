from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .acces import filtrer_modifiables, stages_modifiables
from .forms import NoteRapideForm
from .models import EntreeJournal, Lieu, Photo, Rubrique, Stage
from .services.export import ExportImpossible, iter_zip
from .services.quota import QuotaDepasse, octets_restants
from .services.stage_actif import choisir_stage_actif, stage_actif


@login_required
def note_rapide(request):
    stage = stage_actif(request)
    if stage is None:
        messages.warning(request, "Créez d'abord votre stage.")
        return redirect("admin:carnet_stage_add")
    form = NoteRapideForm(request.POST or None, stage=stage)
    if request.method == "POST" and form.is_valid():
        try:
            note = _enregistrer_note(stage, form.cleaned_data, request.FILES.getlist("photos"))
        except (QuotaDepasse, ValidationError) as exc:
            form.add_error(None, exc.messages[0] if isinstance(exc, ValidationError) else str(exc))
        else:
            n = note.photos.count()
            messages.success(request, f"Note enregistrée{f' avec {n} photo' + ('s' if n > 1 else '') if n else ''}.")
            return redirect(reverse("carnet:note_rapide") + "?enregistree=1")
    coches = {str(pk) for pk in request.POST.getlist("rubriques")}
    return render(request, "carnet/note_rapide.html", {
        "form": form, "stage": stage, "stages": stages_modifiables(request.user),
        "restant_mo": octets_restants(stage) / (1024 * 1024),
        "groupes": _groupes_rubriques(stage, coches),
        "enregistree": request.GET.get("enregistree") == "1",
        "maintenant": timezone.localtime(),
    })


def _groupes_rubriques(stage, coches):
    """Étiquettes regroupées dans l'ordre du plan du cours : Partie I, II, III…"""
    groupes = {valeur: [] for valeur in Rubrique.Partie.values}
    for r in Rubrique.pour_stage(stage).select_related("parent"):
        groupes[r.partie].append({"pk": r.pk, "libelle": str(r), "coche": str(r.pk) in coches})
    return [(Rubrique.Partie(p).label, items) for p, items in groupes.items() if items]


def _enregistrer_note(stage, donnees, fichiers):
    lat, lon = donnees.get("latitude"), donnees.get("longitude")
    photos = []
    try:
        with transaction.atomic():
            note = EntreeJournal.objects.create(
                stage=stage, date=timezone.localdate(), heure=timezone.localtime().time(), texte=donnees["texte"],
                latitude=lat, longitude=lon,
                lieu=Lieu.le_plus_proche(stage, lat, lon) if lat is not None and lon is not None else None,
            )
            note.etiqueter(list(donnees["rubriques"]))
            for fichier in fichiers:
                photos.append(Photo.ajouter(stage, fichier, latitude=lat, longitude=lon, entree=note, lieu=note.lieu))
    except Exception:
        for photo in photos:  # la base est annulée : ne pas laisser de fichiers orphelins
            photo.fichier.delete(save=False)
        raise
    return note


@login_required
@require_POST
def changer_stage_actif(request):
    stage = get_object_or_404(Stage, pk=request.POST.get("stage"))
    choisir_stage_actif(request, stage)  # 403 si le stage n'est pas le sien
    return redirect(request.POST.get("suivant") or "carnet:note_rapide")


LIBELLES_COURTS = {"a_trier": "À trier", "corps": "Corps", "annexe": "Annexe", "preuve": "Preuve"}


@login_required
def tri_photos(request):
    photos = filtrer_modifiables(request.user, Photo.objects.all()).select_related("stage").prefetch_related(
        "rubriques")
    comptes = {valeur: 0 for valeur in Photo.Destination.values}
    for d in photos.values_list("destination", flat=True):
        comptes[d] += 1
    destination = request.GET.get("destination")
    if destination in Photo.Destination.values:
        photos = photos.filter(destination=destination)
    return render(request, "carnet/tri_photos.html", {
        "photos": photos, "filtre": destination,
        "destinations": [(v, l, LIBELLES_COURTS[v]) for v, l in Photo.Destination.choices],
        "filtres": [(v, l, comptes[v]) for v, l in Photo.Destination.choices], "total": sum(comptes.values()),
    })


@login_required
@require_POST
def destination_photo(request, pk):
    photo = get_object_or_404(filtrer_modifiables(request.user, Photo.objects.all()), pk=pk)
    destination = request.POST.get("destination")
    if destination not in Photo.Destination.values:
        return HttpResponseBadRequest("Destination inconnue.")
    photo.destination = destination
    photo.save(update_fields=["destination", "modifie_le"])
    return redirect(request.POST.get("suivant") or "carnet:tri_photos")


@login_required
def export(request, pk):
    stage = get_object_or_404(stages_modifiables(request.user), pk=pk)
    try:
        morceaux = iter_zip(stage)
    except ExportImpossible as exc:
        messages.error(request, str(exc))
        return redirect("admin:index")
    reponse = StreamingHttpResponse(morceaux, content_type="application/zip")
    reponse["Content-Disposition"] = (
        f'attachment; filename="dossier-terrain-{stage.slug}-{timezone.localdate():%Y%m%d}.zip"'
    )
    return reponse
