from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("core:home"))

    def test_accueil_repond_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_accueil_utilise_les_bons_templates(self):
        self.assertTemplateUsed(self.response, "base.html")
        self.assertTemplateUsed(self.response, "core/home.html")

    def test_bouton_de_theme_present(self):
        self.assertContains(self.response, "data-theme-toggle")

    def test_metiers_affiches_et_echappes(self):
        # Le "É" accentué arrive tel quel : l'auto-échappement de Django protège sans abîmer le texte
        self.assertContains(self.response, "Électricité")