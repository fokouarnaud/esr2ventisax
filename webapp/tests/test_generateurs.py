"""US-05, US-09, US-19, US-21, US-23 : fichiers LaTeX générés (attendus écrits à la main)."""

import datetime

import pytest

from carnet.models import Equipement, Lieu, NoeudOrganigramme, Reference, Tache
from carnet.services import generateurs as g

D = datetime.date


# --- infos.tex (US-05) ---------------------------------------------------------

def test_infos_valeur_saisie_echappee(stage):
    stage.entreprise = "B&T Sarl"
    assert r"\newcommand{\InfoEntreprise}{B\&T Sarl}" in g.infos_tex(stage)


def test_infos_valeur_vide_devient_a_completer(stage):
    assert r"\newcommand{\InfoCFP}{\AC{Nom du centre de formation professionnelle}}" in g.infos_tex(stage)


def test_infos_champ_de_la_fiche_entreprise(stage):
    stage.fiche_entreprise.ville = "Douala"
    assert r"\newcommand{\InfoEntrepriseVille}{Douala}" in g.infos_tex(stage)


def test_infos_dates_en_francais(stage):
    stage.date_debut = D(2026, 4, 1)
    texte = g.infos_tex(stage)
    assert r"\newcommand{\InfoDateDebut}{1\textsuperscript{er} avril 2026}" in texte
    assert r"\newcommand{\InfoDateFin}{26 juin 2026}" in texte


def test_infos_duree_en_mois(stage):  # 02/03 → 26/06/2026 : 117 jours ≈ 4 mois
    assert r"\newcommand{\InfoDuree}{quatre (04) mois}" in g.infos_tex(stage)


def test_infos_duree_courte_en_semaines(stage):
    stage.date_fin = D(2026, 3, 20)  # 19 jours → 3 semaines
    assert r"\newcommand{\InfoDuree}{trois (03) semaines}" in g.infos_tex(stage)


def test_infos_chantier_pris_du_premier_lieu_chantier(stage):
    Lieu.objects.create(stage=stage, nom="Résidence Bonapriso", type=Lieu.Type.CHANTIER, latitude=4, longitude=9.7,
                        ville="Douala")
    texte = g.infos_tex(stage)
    assert r"\newcommand{\InfoChantier}{Résidence Bonapriso}" in texte
    assert r"\newcommand{\InfoChantierVille}{Douala}" in texte


def test_infos_niveaux_du_chantier(stage):
    Lieu.objects.create(stage=stage, nom="Résidence", type=Lieu.Type.CHANTIER, latitude=4, longitude=9.7, niveaux="R+8")
    assert r"\newcommand{\InfoChantierNiveaux}{R+8}" in g.infos_tex(stage)


def test_infos_definit_toutes_les_macros_du_modele(stage):
    texte = g.infos_tex(stage)
    for macro in ["InfoEtudiant", "InfoEtudiantCourt", "InfoCFPSigle", "InfoSpecialite", "InfoDiplome",
                  "InfoAnneeEtude", "InfoSession", "InfoEntrepriseSigle", "InfoEntrepriseQuartier",
                  "InfoEntrepriseCreation", "InfoEntrepriseDirigeant", "InfoEntrepriseCapital",
                  "InfoEntrepriseEffectif", "InfoEntrepriseContact", "InfoChantierNiveaux", "InfoTuteurAcad",
                  "InfoTuteurAcadPoste", "InfoTuteurPro", "InfoTuteurProPoste", "InfoTheme", "InfoSousTheme"]:
        assert f"\\newcommand{{\\{macro}}}" in texte


# --- organigramme (US-09) -------------------------------------------------------

def test_organigramme_arbre_tikz_avec_stagiaire_mis_en_evidence(stage):
    dg = NoeudOrganigramme.objects.create(stage=stage, poste="Directeur général", nom="M. Ekotto")
    ct = NoeudOrganigramme.objects.create(stage=stage, poste="Conducteur & chef", parent=dg)
    NoeudOrganigramme.objects.create(stage=stage, poste="Stagiaire", parent=ct, est_stagiaire=True)
    texte = g.organigramme_tikz(stage)
    assert r"\node[bloc] {Directeur général\\M. Ekotto}" in texte
    assert r"child {node[bloc] {Conducteur \& chef}" in texte
    assert r"child {node[stagiaire] {Stagiaire}}" in texte
    assert texte.count("{") == texte.count("}")


def test_organigramme_espace_mesure_entre_les_blocs(stage):
    # Un bloc sur 3 ou 4 lignes ne doit pas chevaucher son parent : l'écart part du bas du parent
    NoeudOrganigramme.objects.create(stage=stage, poste="Directeur général")
    texte = g.organigramme_tikz(stage)
    assert "growth parent anchor=south" in texte
    assert "every child node/.style={anchor=north}" in texte


def test_organigramme_vide(stage):
    assert g.organigramme_tikz(stage) == ""


# --- Gantt (US-23) --------------------------------------------------------------

def test_gantt_semaines_et_barres(stage):
    stage.date_fin = D(2026, 3, 29)  # 28 jours = 4 semaines
    stage.save()
    Tache.objects.create(stage=stage, libelle="Accueil, sécurité", date_debut=D(2026, 3, 2), date_fin=D(2026, 3, 8))
    Tache.objects.create(stage=stage, libelle="Colonne", date_debut=D(2026, 3, 10))
    texte = g.gantt_tikz(stage)
    assert r"\foreach \s in {1,...,4}" in texte
    assert "{Accueil, sécurité}/0/1/vertfonce" in texte
    assert "{Colonne}/1/4/vertmoyen" in texte


def test_gantt_sans_tache(stage):
    assert g.gantt_tikz(stage) == ""


# --- BibTeX (US-21) -------------------------------------------------------------

def test_bibtex_norme_avec_organisme(stage):
    Reference.objects.create(stage=stage, type=Reference.Type.NORME, auteur="AFNOR", titre="NF DTU 60.11",
                             annee=2013, editeur="Association française de normalisation")
    assert g.bibtex(stage) == (
        "@standard{afnor2013,\n"
        "  author = {{AFNOR}},\n"
        "  title = {NF DTU 60.11},\n"
        "  date = {2013},\n"
        "  organization = {Association française de normalisation},\n"
        "  langid = {french}\n"
        "}\n"
    )


def test_bibtex_site_web_avec_personne(stage):
    Reference.objects.create(stage=stage, type=Reference.Type.WEB, auteur="Ndjock, Paul", titre="Le PER & vous",
                             url="https://exemple.cm/per")
    assert g.bibtex(stage) == (
        "@online{ndjock,\n"
        "  author = {Ndjock, Paul},\n"
        "  title = {Le PER \\& vous},\n"
        "  url = {https://exemple.cm/per},\n"
        "  langid = {french}\n"
        "}\n"
    )


# --- Tableaux d'équipements (US-19) -----------------------------------------------

def test_un_tableau_par_categorie_presente(stage):
    Equipement.objects.create(stage=stage, designation="Cintreuse", categorie="outillage",
                              caracteristiques="Ø 16–20 mm", role="Cintrer le PER")
    Equipement.objects.create(stage=stage, designation="Casque", categorie="epi", role="Protéger la tête")
    tableaux = g.tableaux_equipements(stage)
    assert set(tableaux) == {"outillage", "epi"}
    assert r"\caption{Outillage}" in tableaux["outillage"]
    assert r"Cintreuse & Ø 16–20 mm & Cintrer le PER \\" in tableaux["outillage"]
    # légende au-dessus du tableau (AGENTS.md)
    assert tableaux["epi"].index(r"\caption") < tableaux["epi"].index(r"\begin{tabularx}")
