"""Routes principales de Global Service Congo."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Adresse d'admin lue depuis l'environnement (plus difficile à trouver pour les robots)
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("core.urls")),
]