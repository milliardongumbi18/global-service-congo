from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Numéro invalide : chiffres uniquement, avec l'indicatif (ex. +243812345678).",
)


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
        user.set_password(password)  # hachage Argon2, jamais le mot de passe en clair
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

    username = None  # on se connecte par email
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
    REQUIRED_FIELDS = []  # demandés par createsuperuser en plus de l'email et du mot de passe

    objects = UserManager()

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        return self.email

    # --- Type de compte non modifiable -------------------------------------
    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        # On mémorise le type lu en base pour détecter toute tentative de changement
        instance._loaded_account_type = instance.__dict__.get("account_type")
        return instance

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()  # évite les doublons « Jean@x.cd » / « jean@x.cd »
        loaded = getattr(self, "_loaded_account_type", None)
        if loaded and loaded != self.account_type:
            raise ValidationError({"account_type": "Le type de compte ne peut pas être modifié après l'inscription."})
        super().save(*args, **kwargs)
        self._loaded_account_type = self.account_type

    # --- Règles métier selon le type de compte -------------------------------
    @property
    def can_publish_missions(self):
        return self.account_type in {self.AccountType.CLIENT, self.AccountType.ENTREPRISE}

    @property
    def can_apply_to_missions(self):
        return self.account_type in {self.AccountType.FREELANCE, self.AccountType.ENTREPRISE}