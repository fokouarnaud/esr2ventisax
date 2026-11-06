from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.templatetags.static import static as static_url

from carnet.views import accueil

urlpatterns = [
    path("admin/", admin.site.urls),
    path("carnet/", include("carnet.urls")),
    path("favicon.ico", lambda request: redirect(static_url("carnet/favicon.svg"))),
    path("", accueil, name="accueil"),  # publique ; un utilisateur connecté va à la note rapide
]

if settings.DEBUG:  # en production, PythonAnywhere sert /media/ par un mapping statique (A22)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
