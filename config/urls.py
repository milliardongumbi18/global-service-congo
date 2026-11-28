"""Routes principales de Global Service Congo."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("compte/", include("accounts.urls")),
    path("lieux/", include("locations.urls")),
    path("", include("core.urls")),
]