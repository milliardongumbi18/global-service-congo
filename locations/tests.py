from django.db import IntegrityError
from django.test import TestCase

from .models import City, Country
from django.urls import reverse

class LocationsTests(TestCase):
    def test_rdc_et_kinshasa_crees_par_la_migration(self):
        rdc = Country.objects.get(code="CD")
        self.assertTrue(rdc.is_active)
        self.assertTrue(City.objects.filter(country=rdc, name="Kinshasa").exists())

    def test_villes_d_un_pays_inactif_non_proposees(self):
        congo = Country.objects.create(name="République du Congo", code="CG", phone_prefix="+242", is_active=False)
        City.objects.create(country=congo, name="Brazzaville")
        self.assertFalse(City.objects.active().filter(name="Brazzaville").exists())
        self.assertTrue(City.objects.active().filter(name="Kinshasa").exists())

    def test_meme_ville_interdite_deux_fois_dans_un_pays(self):
        rdc = Country.objects.get(code="CD")
        with self.assertRaises(IntegrityError):
            City.objects.create(country=rdc, name="Kinshasa")


class CityOptionsViewTests(TestCase):
    def test_villes_du_pays_renvoyees(self):
        rdc = Country.objects.get(code="CD")
        response = self.client.get(reverse("locations:city_options"), {"country": rdc.pk})
        self.assertContains(response, "Kinshasa")

    def test_parametre_non_numerique_ignore(self):
        response = self.client.get(reverse("locations:city_options"), {"country": "1 OR 1=1"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Kinshasa")