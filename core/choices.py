from django.db import models


class Currency(models.TextChoices):
    """Devises acceptées sur la plateforme."""

    USD = "USD", "Dollar américain (USD)"
    CDF = "CDF", "Franc congolais (CDF)"