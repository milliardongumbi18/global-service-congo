from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("villes/", views.city_options, name="city_options"),
]