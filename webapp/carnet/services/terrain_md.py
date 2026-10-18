"""terrain.md : matériau de rédaction pour Claude Code, classé selon le plan du cours (A4, A15)."""

from carnet.models import (
    Abreviation, DonneeTechnique, EntreeJournal, Equipement, Lieu, Personne, Photo, Rubrique, Tache,
)

from . import calendrier

CHAMPS_NOTE = [
    ("objectifs", "Objectifs"), ("moyens_humains", "Moyens humains"), ("moyens_materiels", "Moyens matériels"),
    ("methodologie", "Méthodologie"), ("activites", "Activités"), ("elements_theoriques", "Éléments théoriques"),
    ("difficultes", "Difficultés"), ("solutions", "Solutions"), ("appreciation", "Appréciation"),
    ("intervention_nature", "Intervention"), ("intervention_duree_h", "Immobilisation (h)"),
    ("intervention_cout", "Coût (F CFA)"), ("intervention_ressources", "Ressources"),
]


def _nombre(decimal):
    return format(decimal.normalize(), "f")


def _note(note):
    lignes = [f"- **{note.date:%d/%m/%Y}** — {note.texte.strip()}"]
    for champ, libelle in CHAMPS_NOTE:
        valeur = getattr(note, champ)
        if valeur not in (None, ""):
            lignes.append(f"  - {libelle} : {valeur}")
    personnes = [p.nom_exporte for p in note.personnes.all()]
    if personnes:
        lignes.append(f"  - Personnes : {', '.join(personnes)}")
    return "\n".join(lignes)


def _rubrique(sortie, titre, texte_formulaire, notes):
    sortie.append(f"### {titre}\n")
    if texte_formulaire.strip():
        sortie.append(texte_formulaire.strip() + "\n")
    sortie.extend(_note(n) for n in notes)
    if not texte_formulaire.strip() and not notes:
        sortie.append("_Rien de saisi._")
    sortie.append("")


def terrain_md(stage):
    notes = list(EntreeJournal.objects.filter(stage=stage).order_by("date", "heure").prefetch_related(
        "rubriques", "personnes"))
    par_rubrique = {}
    for n in notes:
        for r in n.rubriques.all():
            par_rubrique.setdefault(r.pk, []).append(n)

    s = [f"# Dossier terrain — {stage.intitule}", "",
         f"Stage du {stage.date_debut:%d/%m/%Y} au {stage.date_fin:%d/%m/%Y}, entreprise : {stage.entreprise or '?'}, "
         f"thème : {stage.theme or '?'}. Taux de présence : {calendrier.taux_presence(stage):.0%}.", ""]

    formulaires = {Rubrique.Partie.ENTREPRISE: stage.fiche_entreprise, Rubrique.Partie.MISSION: stage.mission}
    for partie, formulaire in formulaires.items():
        s.append(f"## {Rubrique.Partie(partie).label}\n")
        for r in Rubrique.objects.filter(stage__isnull=True, partie=partie):
            _rubrique(s, r.libelle, getattr(formulaire, r.code.split(".", 1)[1]), par_rubrique.get(r.pk, []))

    s.append(f"## {Rubrique.Partie.THEME.label}\n")
    for r in Rubrique.objects.filter(stage=stage).order_by("parent_id", "ordre"):
        _rubrique(s, str(r), "", par_rubrique.get(r.pk, []))

    bilan = stage.bilan
    s.append("## Bilan personnel, critiques et suggestions\n")
    for champ in [f for f in bilan._meta.fields if f.get_internal_type() == "TextField"]:
        if getattr(bilan, champ.name).strip():
            s.append(f"**{champ.verbose_name.capitalize()}** {getattr(bilan, champ.name).strip()}\n")
    for r in Rubrique.objects.filter(stage__isnull=True).exclude(partie__in=formulaires):
        if par_rubrique.get(r.pk):
            _rubrique(s, r.libelle, "", par_rubrique[r.pk])

    sans_etiquette = [n for n in notes if not n.rubriques.all()]
    s.append("## Journal chronologique (notes sans étiquette)\n")
    s.extend(_note(n) for n in sans_etiquette)
    s.append("")

    s.append("## Tâches\n")
    s.extend(f"- {t.libelle} : {t.date_debut:%d/%m/%Y} → {t.fin_effective:%d/%m/%Y}"
             for t in Tache.objects.filter(stage=stage))
    s.append("\n## Équipements\n")
    s.extend(f"- [{e.get_categorie_display()}] {e.designation} — {e.caracteristiques} — {e.role}"
             for e in Equipement.objects.filter(stage=stage))
    s.append("\n## Données techniques (citer la source indiquée)\n")
    for d in DonneeTechnique.objects.filter(stage=stage).select_related("reference", "entree"):
        source = f"\\cite{{{d.reference.cle_bibtex}}}" if d.reference else f"relevé du {d.entree.date:%d/%m/%Y}"
        s.append(f"- {d.grandeur} = {_nombre(d.valeur)} {d.unite} ({source})")
    s.append("\n## Personnes\n")
    s.extend(f"- {p.nom_exporte}, {p.fonction} ({p.get_role_display()})"
             + (" — à remercier" if p.a_remercier else "") for p in Personne.objects.filter(stage=stage))
    s.append("\n## Abréviations\n")
    s.extend(f"- {a.sigle} : {a.signification}" for a in Abreviation.objects.filter(stage=stage))
    s.append("\n## Lieux\n")
    s.extend(f"- {l.nom} ({l.get_type_display()}) : {l.latitude:.5f}, {l.longitude:.5f} — {l.reperes}"
             for l in Lieu.objects.filter(stage=stage))
    s.append("\n## Photos retenues\n")
    s.extend(f"- img/fig_{p.slug}.jpg [{p.get_destination_display()}] : {p.legende}"
             for p in Photo.objects.filter(stage=stage, destination__in=["corps", "annexe"]))
    return "\n".join(s) + "\n"
