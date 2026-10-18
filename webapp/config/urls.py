from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.templatetags.static import static as static_url
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("carnet/", include("carnet.urls")),
    path("favicon.ico", lambda request: redirect(static_url("carnet/favicon.svg"))),
    path("", RedirectView.as_view(pattern_name="carnet:note_rapide", permanent=False)),
]

if settings.DEBUG:  # en production, PythonAnywhere sert /media/ par un mapping statique (A22)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
