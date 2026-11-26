from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompanyProfile, FreelanceProfile, User


@receiver(post_save, sender=User)
def creer_profil_selon_le_type(sender, instance, created, raw=False, **kwargs):
    """À la création d'un compte, crée le profil adapté à son type.

    raw=True quand on charge des données de test (loaddata) : on ne fait rien.
    """
    if not created or raw:
        return
    if instance.account_type == User.AccountType.FREELANCE:
        FreelanceProfile.objects.get_or_create(user=instance)
    elif instance.account_type == User.AccountType.ENTREPRISE:
        CompanyProfile.objects.get_or_create(user=instance)