from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify

from core.choices import Currency
from core.text import normaliser

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Numéro invalide : chiffres uniquement, avec l'indicatif (ex. +243812345678).",
)


# ============================================================== Utilisateur
class UserManager(BaseUserManager):
    """Création des utilisateurs avec l'email comme identifiant (pas de nom d'utilisateur)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        if not extra_fields.get("account_type"):
            raise ValueError("Le type de compte est obligatoire.")
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("account_type", self.model.AccountType.CLIENT)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superutilisateur doit avoir is_staff=True et is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class AccountType(models.TextChoices):
        CLIENT = "CLIENT", "Client (particulier)"
        FREELANCE = "FREELANCE", "Freelance"
        ENTREPRISE = "ENTREPRISE", "Entreprise"

    username = None
    email = models.EmailField("adresse e-mail", unique=True)
    account_type = models.CharField("type de compte", max_length=12, choices=AccountType.choices)
    phone = models.CharField("téléphone", max_length=16, blank=True, validators=[phone_validator])
    city = models.ForeignKey(
        "locations.City", on_delete=models.PROTECT, null=True, blank=True,
        related_name="users", verbose_name="ville",
    )
    district = models.CharField("commune / quartier", max_length=80, blank=True)
    is_suspended = models.BooleanField("compte suspendu", default=False)
    accepted_terms_at = models.DateTimeField("conditions acceptées le", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        return self.email

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_account_type = instance.__dict__.get("account_type")
        return instance

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        loaded = getattr(self, "_loaded_account_type", None)
        if loaded and loaded != self.account_type:
            raise ValidationError({"account_type": "Le type de compte ne peut pas être modifié après l'inscription."})
        super().save(*args, **kwargs)
        self._loaded_account_type = self.account_type

    @property
    def can_publish_missions(self):
        return self.account_type in {self.AccountType.CLIENT, self.AccountType.ENTREPRISE}

    @property
    def can_apply_to_missions(self):
        return self.account_type in {self.AccountType.FREELANCE, self.AccountType.ENTREPRISE}

    @property
    def profile(self):
        """Profil correspondant au type de compte (None pour un client)."""
        if self.account_type == self.AccountType.FREELANCE:
            return getattr(self, "freelance_profile", None)
        if self.account_type == self.AccountType.ENTREPRISE:
            return getattr(self, "company_profile", None)
        return None


# ============================================================== Compétences
class Skill(models.Model):
    """Compétence ou métier (ex. Électricité). Liste gérée par l'administration."""

    name = models.CharField("nom", max_length=60, unique=True)
    slug = models.SlugField("adresse courte", max_length=70, unique=True, editable=False)
    search_name = models.CharField("nom normalisé", max_length=60, db_index=True, editable=False)
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "compétence"
        verbose_name_plural = "compétences"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.split())  # espaces superflus retirés
        self.search_name = normaliser(self.name)
        if not self.slug:
            self.slug = slugify(self.name)[:70]
        super().save(*args, **kwargs)


# ============================================================== Profils
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        abstract = True


class FreelanceProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="freelance_profile", verbose_name="utilisateur")
    title = models.CharField("titre", max_length=100, blank=True, help_text="Ex. Développeur web, Électricien")
    bio = models.TextField("présentation", max_length=2000, blank=True)
    hourly_rate = models.DecimalField(
        "tarif indicatif", max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField("devise", max_length=3, choices=Currency.choices, default=Currency.USD)
    skills = models.ManyToManyField(Skill, blank=True, related_name="freelances", verbose_name="compétences")
    is_available = models.BooleanField("disponible", default=True)

    class Meta:
        verbose_name = "profil freelance"
        verbose_name_plural = "profils freelance"

    def __str__(self):
        return f"Profil freelance de {self.user}"

    def clean(self):
        if self.user_id and self.user.account_type != User.AccountType.FREELANCE:
            raise ValidationError("Un profil freelance ne peut appartenir qu'à un compte freelance.")


class CompanyProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile", verbose_name="utilisateur")
    company_name = models.CharField("raison sociale", max_length=150, blank=True)
    sector = models.CharField("secteur d'activité", max_length=100, blank=True)
    description = models.TextField("présentation", max_length=3000, blank=True)
    website = models.URLField("site web", blank=True)
    rccm = models.CharField("RCCM", max_length=50, blank=True, help_text="Registre du commerce (facultatif)")
    skills = models.ManyToManyField(Skill, blank=True, related_name="companies", verbose_name="compétences proposées")

    class Meta:
        verbose_name = "profil entreprise"
        verbose_name_plural = "profils entreprise"

    def __str__(self):
        return self.company_name or f"Entreprise {self.user}"

    def clean(self):
        if self.user_id and self.user.account_type != User.AccountType.ENTREPRISE:
            raise ValidationError("Un profil entreprise ne peut appartenir qu'à un compte entreprise.")