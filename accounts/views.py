from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from .forms import EmailAuthenticationForm, SignupForm
from .models import User

TYPES_PAR_ADRESSE = {
    "client": User.AccountType.CLIENT,
    "freelance": User.AccountType.FREELANCE,
    "entreprise": User.AccountType.ENTREPRISE,
}

TEXTES = {
    User.AccountType.CLIENT: ("Créer un compte client", "Publiez vos missions et trouvez le bon prestataire."),
    User.AccountType.FREELANCE: ("Créer un compte freelance", "Proposez vos services et soyez payé en toute sécurité."),
    User.AccountType.ENTREPRISE: ("Créer un compte entreprise", "Recrutez des talents ou proposez les services de votre entreprise."),
}

# En dessous de ce nombre de freelances, on n'affiche pas de chiffres (ils feraient fuir au lancement)
SEUIL_STATISTIQUES = 20


def statistiques_plateforme():
    """Chiffres RÉELS de la plateforme : comptes actifs et non suspendus uniquement."""
    actifs = User.objects.filter(is_active=True, is_suspended=False)
    freelances = actifs.filter(account_type=User.AccountType.FREELANCE).count()
    entreprises = actifs.filter(account_type=User.AccountType.ENTREPRISE).count()
    return {"freelances": freelances, "entreprises": entreprises, "afficher": freelances >= SEUIL_STATISTIQUES}


class AnonymousRequiredMixin:
    """Un utilisateur déjà connecté n'a rien à faire sur l'inscription."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)


class SignupChoiceView(AnonymousRequiredMixin, TemplateView):
    template_name = "accounts/signup_choice.html"


class SignupView(AnonymousRequiredMixin, FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.account_type = TYPES_PAR_ADRESSE.get(kwargs.get("account_type"))

    def dispatch(self, request, *args, **kwargs):
        if self.account_type is None:
            raise Http404("Type de compte inconnu.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["account_type"] = self.account_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        heading, subheading = TEXTES[self.account_type]
        context.update(
            heading=heading,
            subheading=subheading,
            is_company=self.account_type == User.AccountType.ENTREPRISE,
            is_freelance=self.account_type == User.AccountType.FREELANCE,
            stats=statistiques_plateforme(),
        )
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, f"Bienvenue {user.first_name} ! Votre compte a été créé.")
        return redirect("core:home")


class GSCLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = statistiques_plateforme()
        return context


class GSCLogoutView(LogoutView):
    """Déconnexion uniquement par POST (protégée par le jeton CSRF)."""