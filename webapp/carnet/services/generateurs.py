"""Fichiers LaTeX générés pour le modèle tex_export_src/ (contrat d'export P4)."""

import math

from carnet.models import Equipement, Lieu, NoeudOrganigramme, Reference, Tache

from .latex import echapper

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]
NOMBRES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze"]
JOURS_PAR_MOIS = 30.44
COULEURS_GANTT = ["vertfonce", "vertmoyen"]


# --- infos.tex --------------------------------------------------------------------

def date_fr(date):
    jour = r"1\textsuperscript{er}" if date.day == 1 else str(date.day)
    return f"{jour} {MOIS[date.month - 1]} {date.year}"


def duree_fr(debut, fin):
    jours = (fin - debut).days + 1
    if jours < 28:
        n, unite = max(round(jours / 7), 1), "semaine"
    else:
        n, unite = max(round(jours / JOURS_PAR_MOIS), 1), "mois"
    mot = NOMBRES[n] if n < len(NOMBRES) else str(n)
    pluriel = "s" if n > 1 and unite == "semaine" else ""
    return f"{mot} ({n:02d}) {unite}{pluriel}"


def _macro(nom, valeur, a_completer):
    valeur = (valeur or "").strip()
    contenu = echapper(valeur) if valeur else f"\\AC{{{a_completer}}}"
    return f"\\newcommand{{\\{nom}}}{{{contenu}}}"


def infos_tex(stage):
    fiche = stage.fiche_entreprise
    chantier = Lieu.objects.filter(stage=stage, type=Lieu.Type.CHANTIER).order_by("cree_le").first()
    lignes = [
        "% Généré par le Carnet de stage. \\AC{...} = donnée non saisie dans l'application.",
        _macro("InfoEtudiant", stage.apprenant_nom, "NOM et Prénoms du stagiaire"),
        _macro("InfoEtudiantCourt", stage.apprenant_nom, "NOM Prénom"),
        _macro("InfoCFP", stage.cfp, "Nom du centre de formation professionnelle"),
        _macro("InfoCFPSigle", stage.cfp_sigle, "CFP"),
        _macro("InfoSpecialite", stage.specialite, "Spécialité"),
        _macro("InfoDiplome", stage.diplome, "Diplôme préparé"),
        _macro("InfoAnneeEtude", stage.annee_etude, "Année d'étude"),
        _macro("InfoSession", stage.session, "Session"),
        _macro("InfoEntreprise", stage.entreprise, "Raison sociale de l'entreprise"),
        _macro("InfoEntrepriseSigle", stage.entreprise_sigle, "SIGLE"),
        _macro("InfoEntrepriseVille", fiche.ville, "Ville"),
        _macro("InfoEntrepriseQuartier", fiche.quartier, "Quartier, repères"),
        _macro("InfoEntrepriseCreation", fiche.annee_creation, "année de création"),
        _macro("InfoEntrepriseDirigeant", fiche.dirigeant, "Nom du directeur général"),
        _macro("InfoEntrepriseCapital", fiche.capital, "capital social en F CFA"),
        _macro("InfoEntrepriseEffectif", fiche.effectif, "effectif"),
        _macro("InfoEntrepriseContact", fiche.contact, "BP, téléphone, courriel, site web"),
        _macro("InfoChantier", chantier.nom if chantier else "", "Nom du chantier"),
        _macro("InfoChantierVille", chantier.ville if chantier else "", "Ville du chantier"),
        _macro("InfoChantierNiveaux", chantier.niveaux if chantier else "", "R+N"),
        _macro("InfoTuteurAcad", stage.tuteur_acad, "M./Mme NOM Prénom"),
        _macro("InfoTuteurAcadPoste", stage.tuteur_acad_poste, "Poste"),
        _macro("InfoTuteurPro", stage.tuteur_pro, "M./Mme NOM Prénom"),
        _macro("InfoTuteurProPoste", stage.tuteur_pro_poste, "Poste"),
        f"\\newcommand{{\\InfoDateDebut}}{{{date_fr(stage.date_debut)}}}",
        f"\\newcommand{{\\InfoDateFin}}{{{date_fr(stage.date_fin)}}}",
        f"\\newcommand{{\\InfoDuree}}{{{duree_fr(stage.date_debut, stage.date_fin)}}}",
        _macro("InfoTheme", stage.theme, "Thème"),
        _macro("InfoSousTheme", stage.sous_theme, "Sous-thème"),
    ]
    return "\n".join(lignes) + "\n"


# --- Organigramme ---------------------------------------------------------------------

ENTETE_ORGANIGRAMME = r"""% Organigramme généré par le Carnet de stage
\begin{tikzpicture}[font=\scriptsize\bfseries, level distance=8mm,
  growth parent anchor=south, every child node/.style={anchor=north},
  edge from parent path={(\tikzparentnode.south) -- (\tikzchildnode.north)},
  level 1/.style={sibling distance=40mm}, level 2/.style={sibling distance=28mm},
  level 3/.style={sibling distance=24mm},
  bloc/.style={draw=vertfonce, fill=vertclair, rounded corners=3pt, align=center,
               minimum height=8mm, text width=2.15cm, inner sep=2pt},
  stagiaire/.style={bloc, fill=vertmoyen, text=white},
  edge from parent/.style={draw=vertfonce, line width=0.6pt}]"""


def _noeud(noeud, enfants, profondeur):
    style = "stagiaire" if noeud.est_stagiaire else "bloc"
    libelle = echapper(noeud.poste) + (r"\\" + echapper(noeud.nom) if noeud.nom else "")
    texte = f"node[{style}] {{{libelle}}}"
    retrait = "  " * (profondeur + 2)
    for enfant in enfants.get(noeud.pk, []):
        texte += f"\n{retrait}child {{{_noeud(enfant, enfants, profondeur + 1)}}}"
    return texte


def organigramme_tikz(stage):
    noeuds = list(NoeudOrganigramme.objects.filter(stage=stage))
    if not noeuds:
        return ""
    enfants = {}
    for n in noeuds:
        enfants.setdefault(n.parent_id, []).append(n)
    arbres = []
    for i, racine in enumerate(enfants.get(None, [])):
        arbre = f"  \\{_noeud(racine, enfants, 0)};"
        if i:
            arbre = f"  \\begin{{scope}}[xshift={i * 9}cm]\n{arbre}\n  \\end{{scope}}"
        arbres.append(arbre)
    return "\n".join([ENTETE_ORGANIGRAMME, *arbres, r"\end{tikzpicture}"]) + "\n"


# --- Gantt ------------------------------------------------------------------------------

def gantt_tikz(stage):
    taches = list(Tache.objects.filter(stage=stage).select_related("stage"))
    if not taches:
        return ""
    semaines = math.ceil(((stage.date_fin - stage.date_debut).days + 1) / 7)
    barres = []
    for i, t in enumerate(taches):
        debut = (t.date_debut - stage.date_debut).days // 7
        fin = math.ceil(((t.fin_effective - stage.date_debut).days + 1) / 7)
        barres.append(f"      {{{echapper(t.libelle)}}}/{debut}/{fin}/{COULEURS_GANTT[i % 2]}")
    n = len(taches)
    return (
        "% Diagramme de Gantt généré par le Carnet de stage à partir des tâches réelles\n"
        "\\begin{tikzpicture}[x=0.72cm,y=0.55cm,font=\\scriptsize]\n"
        f"  \\foreach \\s in {{1,...,{semaines}}} {{\n"
        "    \\node[anchor=south] at (\\s-0.5,0.2) {S\\s};\n"
        f"    \\draw[gray!30] (\\s,0) -- (\\s,-{n});\n"
        "  }\n"
        f"  \\draw[gray!30] (0,0) -- (0,-{n});\n"
        "  \\foreach [count=\\i] \\lib/\\deb/\\fin/\\col in {\n"
        + ",\n".join(barres)
        + "} {\n"
        "    \\node[anchor=east] at (-0.15,-\\i+0.5) {\\lib};\n"
        "    \\fill[\\col, rounded corners=1.5pt] (\\deb+0.05,-\\i+0.15) rectangle (\\fin-0.05,-\\i+0.85);\n"
        "  }\n"
        "\\end{tikzpicture}\n"
    )


# --- Bibliographie ------------------------------------------------------------------------

TYPES_BIBLATEX = {
    Reference.Type.NORME: ("standard", "organization"),
    Reference.Type.OUVRAGE: ("book", "publisher"),
    Reference.Type.NOTICE: ("manual", "organization"),
    Reference.Type.WEB: ("online", "organization"),
    Reference.Type.ORAL: ("misc", "organization"),
}


def _entree_bib(ref):
    type_bib, champ_editeur = TYPES_BIBLATEX[ref.type]
    champs = []
    if ref.auteur:
        auteur = echapper(ref.auteur)
        champs.append(("author", auteur if "," in ref.auteur else f"{{{auteur}}}"))
    champs.append(("title", echapper(ref.titre)))
    if ref.annee:
        champs.append(("date", str(ref.annee)))
    if ref.editeur:
        champs.append((champ_editeur, echapper(ref.editeur)))
    if ref.url:
        champs.append(("url", ref.url))
    if ref.type == Reference.Type.ORAL:
        champs.append(("note", "Communication orale"))
    champs.append(("langid", "french"))
    corps = ",\n".join(f"  {k} = {{{v}}}" for k, v in champs)
    return f"@{type_bib}{{{ref.cle_bibtex},\n{corps}\n}}\n"


def bibtex(stage):
    return "\n".join(_entree_bib(r) for r in Reference.objects.filter(stage=stage))


# --- Tableaux d'équipements -------------------------------------------------------------------

def tableaux_equipements(stage):
    par_categorie = {}
    for e in Equipement.objects.filter(stage=stage):
        par_categorie.setdefault(e.categorie, []).append(e)
    tableaux = {}
    for categorie, equipements in par_categorie.items():
        titre = Equipement.Categorie(categorie).label
        lignes = "\n".join(
            f"{echapper(e.designation)} & {echapper(e.caracteristiques)} & {echapper(e.role)} \\\\" for e in equipements
        )
        tableaux[categorie] = (
            "\\begin{table}[H]\\centering\n"
            f"\\caption{{{titre}}}\\label{{tab:equipements-{categorie}}}\n"
            "\\begin{tabularx}{\\textwidth}{>{\\bfseries}p{3.5cm} p{4cm} >{\\raggedright\\arraybackslash}X}\n"
            "\\toprule\nDésignation & Caractéristiques & Rôle \\\\\n\\midrule\n"
            f"{lignes}\n"
            "\\bottomrule\n\\end{tabularx}\n\\end{table}\n"
        )
    return tableaux
