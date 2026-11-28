from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.SignupChoiceView.as_view(), name="signup_choice"),
    path("inscription/<slug:account_type>/", views.SignupView.as_view(), name="signup"),
    path("connexion/", views.GSCLoginView.as_view(), name="login"),
    path("deconnexion/", views.GSCLogoutView.as_view(), name="logout"),
]