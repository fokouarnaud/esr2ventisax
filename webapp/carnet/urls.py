from django.urls import path

from . import views

app_name = "carnet"

urlpatterns = [
    path("note/", views.note_rapide, name="note_rapide"),
    path("stage-actif/", views.changer_stage_actif, name="stage_actif"),
    path("photos/", views.tri_photos, name="tri_photos"),
    path("photos/<uuid:pk>/destination/", views.destination_photo, name="destination_photo"),
    path("export/<uuid:pk>/", views.export, name="export"),
]
