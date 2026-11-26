from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from decimal import Decimal

from .models import CompanyProfile, FreelanceProfile, Skill, User


class UserModelTests(TestCase):
    def creer(self, email="jean@exemple.cd", account_type=User.AccountType.CLIENT):
        return User.objects.create_user(email=email, password="MotDePasse-Solide-2026", account_type=account_type)

    def test_email_normalise_et_mot_de_passe_argon2(self):
        user = self.creer(email="  Jean@Exemple.CD ")
        self.assertEqual(user.email, "jean@exemple.cd")
        self.assertTrue(user.password.startswith("argon2"))
        self.assertTrue(user.check_password("MotDePasse-Solide-2026"))

    def test_email_obligatoire(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="x", account_type=User.AccountType.CLIENT)

    def test_email_unique_sans_tenir_compte_des_majuscules(self):
        self.creer(email="marie@exemple.cd")
        with self.assertRaises(IntegrityError):
            self.creer(email="MARIE@exemple.cd")

    def test_type_de_compte_non_modifiable(self):
        user = self.creer()
        user.account_type = User.AccountType.FREELANCE
        with self.assertRaises(ValidationError):
            user.save()
        # Même chose avec un utilisateur relu depuis la base
        relu = User.objects.get(pk=user.pk)
        relu.account_type = User.AccountType.ENTREPRISE
        with self.assertRaises(ValidationError):
            relu.save()

    def test_telephone_invalide_refuse(self):
        user = self.creer()
        user.phone = "081-ABC"
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_permissions_selon_le_type(self):
        client = self.creer("c@x.cd", User.AccountType.CLIENT)
        freelance = self.creer("f@x.cd", User.AccountType.FREELANCE)
        entreprise = self.creer("e@x.cd", User.AccountType.ENTREPRISE)
        self.assertTrue(client.can_publish_missions)
        self.assertFalse(client.can_apply_to_missions)
        self.assertFalse(freelance.can_publish_missions)
        self.assertTrue(freelance.can_apply_to_missions)
        self.assertTrue(entreprise.can_publish_missions)
        self.assertTrue(entreprise.can_apply_to_missions)

    def test_superutilisateur(self):
        admin = User.objects.create_superuser(email="admin@exemple.cd", password="MotDePasse-Solide-2026")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class UserAdminTests(TestCase):
    def test_liste_des_utilisateurs_accessible_au_superutilisateur(self):
        admin = User.objects.create_superuser(email="admin@exemple.cd", password="MotDePasse-Solide-2026")
        self.client.force_login(admin)
        response = self.client.get(reverse("admin:accounts_user_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_admin_interdit_aux_utilisateurs_normaux(self):
        user = User.objects.create_user(email="u@x.cd", password="MotDePasse-Solide-2026",
                                        account_type=User.AccountType.CLIENT)
        self.client.force_login(user)
        response = self.client.get(reverse("admin:accounts_user_changelist"))
        self.assertEqual(response.status_code, 302)  # redirigé vers la connexion admin


class ProfilsTests(TestCase):
    def creer(self, email, account_type):
        return User.objects.create_user(email=email, password="MotDePasse-Solide-2026", account_type=account_type)

    def test_profil_freelance_cree_automatiquement(self):
        user = self.creer("f@x.cd", User.AccountType.FREELANCE)
        self.assertIsInstance(user.profile, FreelanceProfile)

    def test_profil_entreprise_cree_automatiquement(self):
        user = self.creer("e@x.cd", User.AccountType.ENTREPRISE)
        self.assertIsInstance(user.profile, CompanyProfile)

    def test_aucun_profil_pour_un_client(self):
        user = self.creer("c@x.cd", User.AccountType.CLIENT)
        self.assertIsNone(user.profile)
        self.assertFalse(FreelanceProfile.objects.filter(user=user).exists())

    def test_profil_incompatible_avec_le_type_refuse(self):
        client = self.creer("c2@x.cd", User.AccountType.CLIENT)
        with self.assertRaises(ValidationError):
            FreelanceProfile(user=client).full_clean()

    def test_tarif_negatif_refuse(self):
        profil = self.creer("f2@x.cd", User.AccountType.FREELANCE).profile
        profil.hourly_rate = Decimal("-5")
        with self.assertRaises(ValidationError):
            profil.full_clean()


class CompetencesTests(TestCase):
    def test_nom_normalise_et_slug_calcules(self):
        skill = Skill.objects.create(name="  Électricité   industrielle ")
        self.assertEqual(skill.name, "Électricité industrielle")
        self.assertEqual(skill.search_name, "electricite industrielle")
        self.assertEqual(skill.slug, "electricite-industrielle")

    def test_competences_de_depart_trouvables_sans_accent(self):
        # Ce que fera l'autocomplétion quand on tape « elec »
        self.assertTrue(Skill.objects.filter(search_name__startswith="elec").exists())