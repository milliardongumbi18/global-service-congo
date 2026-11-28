from django.test import TestCase
from django.urls import reverse

from locations.models import City, Country

from .models import User

MOT_DE_PASSE = "MotDePasse-Solide-2026"


class SignupTests(TestCase):
    def setUp(self):
        self.rdc = Country.objects.get(code="CD")
        self.kinshasa = City.objects.get(country=self.rdc, name="Kinshasa")

    def donnees(self, **extra):
        data = {
            "first_name": "Grâce", "last_name": "Mbuyi", "email": "Grace@Exemple.cd",
            "phone": "081 234 5678", "country": self.rdc.pk, "city": self.kinshasa.pk,
            "district": "Gombe", "password1": MOT_DE_PASSE, "password2": MOT_DE_PASSE,
            "accept_terms": "on",
        }
        data.update(extra)
        return data

    def test_page_de_choix(self):
        response = self.client.get(reverse("accounts:signup_choice"))
        self.assertContains(response, reverse("accounts:signup", args=["freelance"]))
        self.assertContains(response, reverse("accounts:signup", args=["entreprise"]))

    def test_type_inconnu_renvoie_404(self):
        response = self.client.get(reverse("accounts:signup", args=["pirate"]))
        self.assertEqual(response.status_code, 404)

    def test_inscription_freelance_complete(self):
        response = self.client.post(
            reverse("accounts:signup", args=["freelance"]), self.donnees(title="Développeuse web")
        )
        self.assertRedirects(response, reverse("core:home"))
        user = User.objects.get(email="grace@exemple.cd")
        self.assertEqual(user.account_type, User.AccountType.FREELANCE)
        self.assertEqual(user.phone, "+243812345678")
        self.assertEqual(user.city, self.kinshasa)
        self.assertIsNotNone(user.accepted_terms_at)
        self.assertEqual(user.profile.title, "Développeuse web")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)  # connecté automatiquement

    def test_inscription_entreprise_enregistre_la_raison_sociale(self):
        self.client.post(
            reverse("accounts:signup", args=["entreprise"]), self.donnees(company_name="Kin Digital SARL")
        )
        user = User.objects.get(email="grace@exemple.cd")
        self.assertEqual(user.profile.company_name, "Kin Digital SARL")

    def test_consentement_obligatoire(self):
        data = self.donnees()
        del data["accept_terms"]
        response = self.client.post(reverse("accounts:signup", args=["client"]), data)
        self.assertContains(response, "Vous devez accepter les conditions")
        self.assertFalse(User.objects.exists())

    def test_ville_d_un_autre_pays_refusee(self):
        congo = Country.objects.create(name="République du Congo", code="CG", phone_prefix="+242", is_active=True)
        brazzaville = City.objects.create(country=congo, name="Brazzaville")
        response = self.client.post(reverse("accounts:signup", args=["client"]), self.donnees(city=brazzaville.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_email_deja_utilise_refuse(self):
        User.objects.create_user(email="grace@exemple.cd", password=MOT_DE_PASSE, account_type=User.AccountType.CLIENT)
        response = self.client.post(reverse("accounts:signup", args=["client"]), self.donnees())
        self.assertContains(response, "Un compte existe déjà")

    def test_utilisateur_connecte_redirige(self):
        user = User.objects.create_user(email="x@x.cd", password=MOT_DE_PASSE, account_type=User.AccountType.CLIENT)
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:signup_choice"))
        self.assertRedirects(response, reverse("core:home"))


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="jean@exemple.cd", password=MOT_DE_PASSE, account_type=User.AccountType.CLIENT
        )

    def test_connexion_insensible_aux_majuscules(self):
        response = self.client.post(reverse("accounts:login"), {"username": " JEAN@Exemple.cd ", "password": MOT_DE_PASSE})
        self.assertRedirects(response, reverse("core:home"))

    def test_mauvais_mot_de_passe_message_vague(self):
        response = self.client.post(reverse("accounts:login"), {"username": "jean@exemple.cd", "password": "faux"})
        self.assertContains(response, "Adresse e-mail ou mot de passe incorrect.")

    def test_compte_suspendu_bloque(self):
        self.user.is_suspended = True
        self.user.save()
        response = self.client.post(reverse("accounts:login"), {"username": "jean@exemple.cd", "password": MOT_DE_PASSE})
        self.assertContains(response, "Ce compte est suspendu")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_deconnexion_par_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)