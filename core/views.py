from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.views.generic import TemplateView

# Métiers de la bande défilante (viendront du modèle Category plus tard).
METIERS_VITRINE = [
    "Développement web", "Électricité", "Plomberie", "Design graphique",
    "Traduction", "Cours particuliers", "Montage vidéo", "Comptabilité",
    "Marketing digital", "Photographie", "Menuiserie", "Maçonnerie",
    "Couture", "Climatisation", "Réseaux informatiques", "Rédaction",
]

# Missions d'exemple pour l'accueil (remplacées par les vraies missions à l'étape « missions »).
# "couleur" choisit la pastille : valeurs fixées dans notre code, jamais saisies par un utilisateur.
MISSIONS_EXEMPLES = [
    {"titre": "Site vitrine pour un restaurant", "categorie": "Développement web", "couleur": "blue",
     "lieu": "Gombe", "delai": "3 semaines", "budget": "350 USD", "candidatures": 6},
    {"titre": "Réparation de l'installation électrique d'un appartement", "categorie": "Électricité",
     "couleur": "yellow", "lieu": "Limete", "delai": "3 jours", "budget": "180 000 CDF", "candidatures": 4},
    {"titre": "Logo et charte graphique pour une boutique de pagnes", "categorie": "Design",
     "couleur": "red", "lieu": "À distance", "delai": "10 jours", "budget": "120 USD", "candidatures": 11},
    {"titre": "Cours de mathématiques, niveau terminale (8 séances)", "categorie": "Cours particuliers",
     "couleur": "green", "lieu": "Ngaliema", "delai": "1 mois", "budget": "80 USD", "candidatures": 3},
    {"titre": "Traduction français-anglais d'un dossier de 20 pages", "categorie": "Traduction",
     "couleur": "blue", "lieu": "À distance", "delai": "5 jours", "budget": "60 USD", "candidatures": 7},
    {"titre": "Montage de 5 vidéos courtes pour une marque de cosmétiques", "categorie": "Vidéo",
     "couleur": "red", "lieu": "À distance", "delai": "1 semaine", "budget": "90 USD", "candidatures": 9},
]


def montant_net_prestataire(montant: Decimal) -> Decimal:
    """Montant reçu par le prestataire après la commission de la plateforme.

    Toujours en Decimal (jamais en float) et arrondi au centime.
    Cette fonction rejoindra l'app « payments » quand elle existera.
    """
    commission = (montant * settings.PLATFORM_FEE_PERCENT / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return montant - commission


class HomeView(TemplateView):
    """Page d'accueil publique."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exemple = Decimal("350")
        context.update(
            metiers=METIERS_VITRINE,
            missions=MISSIONS_EXEMPLES,
            commission_pct=settings.PLATFORM_FEE_PERCENT,
            exemple_montant=exemple,
            exemple_net=montant_net_prestataire(exemple),
        )
        return context