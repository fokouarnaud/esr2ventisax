"""Référentiel figé du cours « Module 2 » (p. 23–27) : rubriques et jours fériés fixes du Cameroun."""

import uuid


def uuid_rubrique_cours(code):
    """Identifiant identique dans toutes les bases : un zip restauré ailleurs garde ses étiquettes."""
    return uuid.uuid5(uuid.NAMESPACE_URL, f"carnet-de-stage:rubrique:{code}")


# (code, libellé) ; le suffixe du code = nom du champ de FicheEntreprise / Mission
RUBRIQUES_ENTREPRISE = [
    ("entreprise.presentation", "Présentation"),
    ("entreprise.organisation", "Organisation générale (organigramme)"),
    ("entreprise.historique", "Historique de l'entreprise"),
    ("entreprise.secteurs", "Secteur(s) d'activité"),
    ("entreprise.marches", "Marchés de l'entreprise"),
    ("entreprise.clients_fournisseurs", "Clients et fournisseurs"),
    ("entreprise.concurrence", "Situation concurrentielle"),
    ("entreprise.chiffres_cles", "Chiffres clés"),
    ("entreprise.perspectives", "Perspectives d'évolution"),
    ("entreprise.mutations_technologiques", "Mutations technologiques"),
    ("entreprise.volonte_dirigeants", "Volonté des dirigeants"),
]

RUBRIQUES_MISSION = [
    ("mission.poste", "Poste occupé"),
    ("mission.position_organigramme", "Position du poste dans l'organigramme"),
    ("mission.faits_importants", "Faits importants"),
    ("mission.objectifs_enjeux", "Objectifs et enjeux de la mission"),
    ("mission.methodes_moyens", "Méthodes et moyens employés"),
    ("mission.collaborateurs", "Personnes avec lesquelles vous avez collaboré"),
    ("mission.responsabilites", "Responsabilités exercées"),
    ("mission.resultats", "Résultats obtenus"),
    ("mission.difficultes_solutions", "Difficultés rencontrées et solutions apportées"),
]

RUBRIQUES_AUTRES = [
    ("introduction", "intro.introduction", "Introduction"),
    ("critiques", "critiques.critiques_suggestions", "Critiques et suggestions"),
    ("conclusion", "conclusion.conclusion", "Conclusion"),
    ("bilan", "bilan.bilan_personnel", "Bilan personnel"),
    ("annexes", "annexes.annexes", "Annexes"),
]

# (mois, jour, libellé)
FERIES_FIXES_CAMEROUN = [
    (1, 1, "Jour de l'an"),
    (2, 11, "Fête de la jeunesse"),
    (5, 1, "Fête du travail"),
    (5, 20, "Fête nationale"),
    (8, 15, "Assomption"),
    (12, 25, "Noël"),
]
