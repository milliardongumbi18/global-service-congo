"""Compétences de départ, et profils pour les comptes créés avant cette étape."""
from django.db import migrations
from django.utils.text import slugify

from core.text import normaliser

COMPETENCES = [
    "Développement web", "Développement mobile", "Design graphique", "UI/UX design",
    "Montage vidéo", "Photographie", "Rédaction", "Traduction", "Marketing digital",
    "Gestion des réseaux sociaux", "Comptabilité", "Secrétariat", "Saisie de données",
    "Cours particuliers", "Électricité", "Plomberie", "Maçonnerie", "Menuiserie",
    "Peinture bâtiment", "Climatisation et froid", "Soudure", "Mécanique automobile",
    "Couture", "Coiffure", "Esthétique", "Cuisine et traiteur", "Nettoyage",
    "Déménagement", "Livraison", "Chauffeur", "Réparation de téléphones",
    "Réparation d'ordinateurs", "Réseaux informatiques", "Installation de caméras",
    "Énergie solaire", "Événementiel", "Décoration", "DJ et animation",
    "Agriculture", "Conseil juridique", "Architecture", "Topographie",
]


def creer_competences(apps, schema_editor):
    # Le modèle « historique » n'a pas notre save() personnalisé : on calcule slug et nom normalisé ici
    Skill = apps.get_model("accounts", "Skill")
    Skill.objects.bulk_create(
        [Skill(name=nom, slug=slugify(nom)[:70], search_name=normaliser(nom)) for nom in COMPETENCES],
        ignore_conflicts=True,
    )


def supprimer_competences(apps, schema_editor):
    Skill = apps.get_model("accounts", "Skill")
    Skill.objects.filter(name__in=COMPETENCES).delete()


def creer_profils_manquants(apps, schema_editor):
    # Le signal n'existait pas quand tes comptes de test ont été créés : on rattrape ici
    User = apps.get_model("accounts", "User")
    FreelanceProfile = apps.get_model("accounts", "FreelanceProfile")
    CompanyProfile = apps.get_model("accounts", "CompanyProfile")
    for user in User.objects.filter(account_type="FREELANCE", freelance_profile__isnull=True):
        FreelanceProfile.objects.create(user=user)
    for user in User.objects.filter(account_type="ENTREPRISE", company_profile__isnull=True):
        CompanyProfile.objects.create(user=user)


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_profils")]

    operations = [
        migrations.RunPython(creer_competences, supprimer_competences),
        migrations.RunPython(creer_profils_manquants, migrations.RunPython.noop),
    ]