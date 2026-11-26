from django.db import models


class CountryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Country(models.Model):
    """Pays où la plateforme est disponible. Seuls les pays actifs sont proposés."""

    name = models.CharField("nom", max_length=80, unique=True)
    code = models.CharField("code ISO", max_length=2, unique=True, help_text="Code ISO 3166-1 à 2 lettres, ex. CD")
    phone_prefix = models.CharField("indicatif téléphonique", max_length=5, help_text="Ex. +243")
    is_active = models.BooleanField("actif", default=False)

    objects = CountryQuerySet.as_manager()

    class Meta:
        verbose_name = "pays"
        verbose_name_plural = "pays"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CityQuerySet(models.QuerySet):
    def active(self):
        # Une ville n'est proposée que si elle ET son pays sont actifs
        return self.filter(is_active=True, country__is_active=True)


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities", verbose_name="pays")
    name = models.CharField("nom", max_length=80)
    is_active = models.BooleanField("active", default=True)

    objects = CityQuerySet.as_manager()

    class Meta:
        verbose_name = "ville"
        verbose_name_plural = "villes"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["country", "name"], name="unique_city_per_country"),
        ]

    def __str__(self):
        return self.name