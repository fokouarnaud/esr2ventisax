"""Menu de gauche d'Unfold défini à la main (US-33, B11) : court, en groupes, filtré par les droits.

Importé par config/settings.py : aucun modèle n'est chargé ici.
"""

from django.urls import reverse_lazy


def _liste(app, modele):
    return reverse_lazy(f"admin:{app}_{modele}_changelist")


def peut_voir(app, modele):
    def verifier(request):
        return request.user.has_perm(f"{app}.view_{modele}")
    return verifier


def superutilisateur(request):
    return request.user.is_superuser


def gere_des_codes(request):
    return request.user.is_superuser or request.user.groups.filter(name="Formateur").exists()


def _entree(titre, icone, app, modele, permission=None):
    return {"title": titre, "icon": icone, "link": _liste(app, modele),
            "permission": permission or peut_voir(app, modele)}


NAVIGATION = [
    {"title": "Mon stage", "separator": False, "collapsible": False, "items": [
        {"title": "Tableau de bord", "icon": "dashboard", "link": reverse_lazy("admin:index")},
        {"title": "Note rapide", "icon": "edit_note", "link": reverse_lazy("carnet:note_rapide")},
        _entree("Stages", "school", "carnet", "stage"),
        _entree("Fiches entreprise", "apartment", "carnet", "ficheentreprise"),
        _entree("Missions", "assignment", "carnet", "mission"),
        _entree("Bilans personnels", "psychology", "carnet", "bilanpersonnel"),
    ]},
    {"title": "Journal", "separator": True, "collapsible": True, "items": [
        _entree("Journal", "menu_book", "carnet", "entreejournal"),
        _entree("Photos", "photo_library", "carnet", "photo"),
        _entree("Lieux", "location_on", "carnet", "lieu"),
        _entree("Tâches", "event_note", "carnet", "tache"),
        _entree("Absences", "event_busy", "carnet", "absence"),
    ]},
    {"title": "Données", "separator": True, "collapsible": True, "items": [
        _entree("Organigramme", "account_tree", "carnet", "noeudorganigramme"),
        _entree("Équipements", "construction", "carnet", "equipement"),
        _entree("Données techniques", "speed", "carnet", "donneetechnique"),
        _entree("Rubriques", "label", "carnet", "rubrique"),
    ]},
    {"title": "Références", "separator": True, "collapsible": True, "items": [
        _entree("Références", "library_books", "carnet", "reference"),
        _entree("Personnes", "groups", "carnet", "personne"),
        _entree("Abréviations", "abc", "carnet", "abreviation"),
    ]},
    {"title": "Administration", "separator": True, "collapsible": True, "items": [
        _entree("Codes d'invitation", "key", "comptes", "codeinvitation", gere_des_codes),
        _entree("Utilisateurs", "person", "auth", "user", superutilisateur),
        _entree("Groupes", "group", "auth", "group", superutilisateur),
    ]},
]
