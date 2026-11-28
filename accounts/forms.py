import re

from django import forms
from django.contrib.auth.forms import AdminUserCreationForm, AuthenticationForm, BaseUserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from locations.models import City, Country

from .models import User


# ------------------------------------------------------------------ Admin
class GSCAdminUserCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ("email", "account_type")
        field_classes = {}


class GSCUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        field_classes = {}


# ------------------------------------------------------------------ Outils
def normaliser_telephone(valeur: str, prefixe: str) -> str:
    """'081 234 5678' + '+243' -> '+243812345678'. Retire espaces, points, tirets et parenthèses."""
    chiffres = re.sub(r"[\s.\-()]", "", valeur or "")
    if chiffres.startswith("00"):
        return "+" + chiffres[2:]
    if chiffres.startswith("0") and prefixe:
        return prefixe + chiffres[1:]
    return chiffres


# ------------------------------------------------------------------ Inscription
class SignupForm(BaseUserCreationForm):
    country = forms.ModelChoiceField(
        label="Pays", queryset=Country.objects.active(), empty_label="Choisissez un pays",
    )
    city = forms.ModelChoiceField(
        label="Ville", queryset=City.objects.none(), empty_label="Choisissez une ville",
    )
    company_name = forms.CharField(label="Nom de l'entreprise", max_length=150, required=False)
    title = forms.CharField(
        label="Votre métier principal", max_length=100, required=False,
        help_text="Ex. Électricien, Développeur web. Modifiable plus tard.",
    )
    accept_terms = forms.BooleanField(
        label="J'accepte les conditions d'utilisation et la politique de confidentialité.",
        required=True,
        error_messages={"required": "Vous devez accepter les conditions pour créer un compte."},
    )

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "phone", "city", "district")
        field_classes = {}

    def __init__(self, *args, account_type, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = account_type
        self.instance.account_type = account_type  # connu dès la validation

        # Champs propres à chaque type de compte
        if account_type == User.AccountType.ENTREPRISE:
            self.fields["company_name"].required = True
        else:
            del self.fields["company_name"]
        if account_type != User.AccountType.FREELANCE:
            del self.fields["title"]

        # Libellés et obligations
        for name in ("first_name", "last_name", "phone"):
            self.fields[name].required = True
        self.fields["first_name"].label = "Prénom"
        self.fields["last_name"].label = "Nom"
        self.fields["email"].label = "Adresse e-mail"
        self.fields["phone"].help_text = "Ex. 081 234 5678 : l'indicatif du pays est ajouté automatiquement. Jamais affiché publiquement."
        self.fields["district"].label = "Commune / quartier"
        self.fields["district"].help_text = "Facultatif. Ex. Gombe, Limete."
        self.fields["password1"].help_text = "Au moins 10 caractères, pas uniquement des chiffres."

        # Villes : uniquement celles du pays choisi (ou du seul pays actif)
        country_id = self.data.get("country") if self.is_bound else None
        active_countries = Country.objects.active()
        if not country_id and active_countries.count() == 1:
            country_id = active_countries.first().pk
            self.fields["country"].initial = country_id
        if country_id and str(country_id).isdigit():
            self.fields["city"].queryset = City.objects.active().filter(country_id=int(country_id))

        # HTMX : changer de pays recharge la liste des villes
        self.fields["country"].widget.attrs.update({
            "hx-get": reverse("locations:city_options"),
            "hx-target": "#id_city",
            "hx-trigger": "change",
        })

        # Style et aide au remplissage sur téléphone
        autocomplete = {
            "first_name": "given-name", "last_name": "family-name", "email": "email",
            "phone": "tel", "password1": "new-password", "password2": "new-password",
        }
        for name, field in self.fields.items():
            if name == "accept_terms":
                continue
            field.widget.attrs.setdefault("class", "input")
            if name in autocomplete:
                field.widget.attrs["autocomplete"] = autocomplete[name]
        self.fields["phone"].widget.attrs["inputmode"] = "tel"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Un compte existe déjà avec cette adresse e-mail.")
        return email

    def clean(self):
        cleaned = super().clean()
        country = cleaned.get("country")
        city = cleaned.get("city")
        # Double contrôle côté serveur : on ne fait jamais confiance au navigateur
        if country and city and city.country_id != country.pk:
            self.add_error("city", "Cette ville n'appartient pas au pays choisi.")
        if cleaned.get("phone"):
            cleaned["phone"] = normaliser_telephone(cleaned["phone"], country.phone_prefix if country else "")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        """Crée le compte et complète son profil, en une seule opération : tout ou rien."""
        user = super().save(commit=False)
        user.account_type = self.account_type
        user.accepted_terms_at = timezone.now()  # preuve du consentement
        user.save()  # le signal crée le profil adapté

        profile = user.profile
        if self.account_type == User.AccountType.ENTREPRISE:
            profile.company_name = self.cleaned_data["company_name"]
            profile.save(update_fields=["company_name", "updated_at"])
        elif self.account_type == User.AccountType.FREELANCE and self.cleaned_data.get("title"):
            profile.title = self.cleaned_data["title"]
            profile.save(update_fields=["title", "updated_at"])
        return user


# ------------------------------------------------------------------ Connexion
class EmailAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        # Message volontairement vague : on ne révèle pas si l'email existe
        "invalid_login": "Adresse e-mail ou mot de passe incorrect.",
        "suspended": "Ce compte est suspendu. Contactez l'équipe Global Service Congo.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Adresse e-mail"
        self.fields["username"].widget.attrs.update({"class": "input", "autocomplete": "email"})
        self.fields["password"].widget.attrs.update({"class": "input", "autocomplete": "current-password"})

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)  # refuse les comptes désactivés
        if user.is_suspended:
            raise ValidationError(self.error_messages["suspended"], code="suspended")