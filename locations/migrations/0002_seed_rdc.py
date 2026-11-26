"""Données de départ : la RDC (active) et ses principales villes."""
from django.db import migrations

VILLES_RDC = [
    "Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kananga", "Kisangani", "Goma", "Bukavu",
    "Kolwezi", "Likasi", "Matadi", "Boma", "Moanda", "Mbanza-Ngungu", "Mbandaka",
    "Kikwit", "Tshikapa", "Uvira", "Butembo", "Beni", "Bunia", "Kalemie", "Kindu",
    "Gemena", "Gbadolite", "Lisala", "Isiro", "Buta", "Kamina", "Mwene-Ditu",
    "Kabinda", "Lodja", "Kenge", "Inongo",
]


def creer_rdc(apps, schema_editor):
    # apps.get_model : on utilise la version « historique » du modèle, pas l'import direct
    Country = apps.get_model("locations", "Country")
    City = apps.get_model("locations", "City")
    rdc, _ = Country.objects.get_or_create(
        code="CD",
        defaults={"name": "République démocratique du Congo", "phone_prefix": "+243", "is_active": True},
    )
    City.objects.bulk_create([City(country=rdc, name=nom) for nom in VILLES_RDC], ignore_conflicts=True)


def supprimer_rdc(apps, schema_editor):
    Country = apps.get_model("locations", "Country")
    City = apps.get_model("locations", "City")
    City.objects.filter(country__code="CD").delete()  # les villes d'abord (PROTECT sur le pays)
    Country.objects.filter(code="CD").delete()


class Migration(migrations.Migration):
    dependencies = [("locations", "0001_initial")]

    operations = [migrations.RunPython(creer_rdc, supprimer_rdc)]