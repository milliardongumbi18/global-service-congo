from django.views.generic import TemplateView

# Métiers affichés dans la bande défilante de l'accueil.
# Ils viendront du modèle Category quand les missions existeront.
METIERS_VITRINE = [
    "Développement web", "Électricité", "Plomberie", "Design graphique",
    "Traduction", "Cours particuliers", "Montage vidéo", "Comptabilité",
    "Marketing digital", "Photographie", "Menuiserie", "Maçonnerie",
    "Couture", "Climatisation", "Réseaux informatiques", "Rédaction",
]


class HomeView(TemplateView):
    """Page d'accueil publique."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metiers"] = METIERS_VITRINE
        return context