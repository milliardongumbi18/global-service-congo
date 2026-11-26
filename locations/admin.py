from django.contrib import admin

from .models import City, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone_prefix", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "code")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active")
    list_filter = ("country", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)  # nécessaire pour la recherche de ville dans la fiche utilisateur
    list_select_related = ("country",)