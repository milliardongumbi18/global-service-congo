from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import GSCAdminUserCreationForm, GSCUserChangeForm
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = GSCUserChangeForm
    add_form = GSCAdminUserCreationForm
    model = User

    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "account_type", "city", "is_suspended", "is_staff", "date_joined")
    list_filter = ("account_type", "is_suspended", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone")
    list_select_related = ("city",)
    autocomplete_fields = ("city",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("first_name", "last_name", "phone", "city", "district")}),
        ("Compte GSC", {"fields": ("account_type", "is_suspended", "accepted_terms_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "account_type", "usable_password", "password1", "password2"),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = ["last_login", "date_joined", "accepted_terms_at"]
        if obj is not None:
            readonly.append("account_type")  # non modifiable après création, même par l'admin
        return readonly