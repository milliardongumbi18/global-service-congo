from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import User


class GSCAdminUserCreationForm(AdminUserCreationForm):
    """Formulaire de création d'utilisateur dans l'admin (email au lieu du nom d'utilisateur)."""

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ("email", "account_type")
        field_classes = {}


class GSCUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        field_classes = {}