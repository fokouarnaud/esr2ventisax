"""Purge horaire des comptes jamais confirmés, déclenchée par les requêtes (US-37, pas de tâche planifiée)."""

from . import inscription


class MaintenanceComptes:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inscription.maintenance_si_due()
        return self.get_response(request)
