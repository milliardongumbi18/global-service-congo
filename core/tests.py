from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from .views import montant_net_prestataire
from .text import normaliser

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
        self.assertContains(self.response, "Électricité")

    def test_sections_presentes(self):
        # Les liens du menu (#comment, #missions, #prestataires) doivent mener quelque part
        for ancre in ('id="comment"', 'id="missions"', 'id="prestataires"'):
            self.assertContains(self.response, ancre)

    def test_missions_exemples_affichees(self):
        self.assertContains(self.response, "Traduction français-anglais")

    @override_settings(PLATFORM_FEE_PERCENT=10)
    def test_montant_net_affiche_dans_le_bloc_sequestre(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "315 USD")


class CommissionTests(TestCase):
    @override_settings(PLATFORM_FEE_PERCENT=10)
    def test_commission_de_10_pourcent(self):
        self.assertEqual(montant_net_prestataire(Decimal("350")), Decimal("315.00"))

    @override_settings(PLATFORM_FEE_PERCENT=10)
    def test_arrondi_au_centime(self):
        # 10 % de 99,99 = 9,999 → arrondi à 10,00 → net 89,99
        self.assertEqual(montant_net_prestataire(Decimal("99.99")), Decimal("89.99"))


class NormalisationTests(TestCase):
    def test_minuscules_sans_accents_espaces_simplifies(self):
        self.assertEqual(normaliser("  Électricité   Générale "), "electricite generale")
        self.assertEqual(normaliser("Réparation d'ordinateurs"), "reparation d'ordinateurs")
        self.assertEqual(normaliser(""), "")