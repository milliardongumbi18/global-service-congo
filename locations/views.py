from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import City


@require_GET
def city_options(request):
    """Renvoie les <option> des villes actives d'un pays (appelé par HTMX quand on change de pays)."""
    cities = City.objects.none()
    country_id = request.GET.get("country", "")
    if country_id.isdigit():  # on refuse tout ce qui n'est pas un nombre
        cities = City.objects.active().filter(country_id=int(country_id)).only("id", "name")
    return render(request, "locations/_city_options.html", {"cities": cities})