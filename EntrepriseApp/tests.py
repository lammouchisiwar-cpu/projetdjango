from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Utilisateur, Entreprise


class UtilisateurModelTest(TestCase):
    def test_user_id_auto_generation_and_format(self):
        user = Utilisateur(email='test1@gmail.com')
        user.save()
        annee = timezone.now().strftime('%y')
        self.assertTrue(user.user_id.startswith(f"{annee}user"))
        self.assertEqual(len(user.user_id), 8)

    def test_user_id_sequential_counter(self):
        user1 = Utilisateur(email='user1@gmail.com')
        user1.save()
        user2 = Utilisateur(email='user2@gmail.com')
        user2.save()
        c1 = int(user1.user_id[-2:])
        c2 = int(user2.user_id[-2:])
        self.assertEqual(c2, c1 + 1)

    def test_email_gmail_only_accepted(self):
        user_valid = Utilisateur(email='valid.person@gmail.com')
        user_valid.save()
        self.assertIsNotNone(user_valid.user_id)

        user_invalid = Utilisateur(email='invalid@yahoo.com')
        with self.assertRaises(ValidationError):
            user_invalid.save()

        user_invalid_domain = Utilisateur(email='fake@gmail.com.tn')
        with self.assertRaises(ValidationError):
            user_invalid_domain.save()


class EntrepriseModelTest(TestCase):
    def setUp(self):
        self.user_chargeur = Utilisateur(email='chargeur@gmail.com', role='chargeur')
        self.user_chargeur.save()

        self.user_transporteur = Utilisateur(email='trans@gmail.com', role='transporteur')
        self.user_transporteur.save()

    def test_matricule_fiscal_valid_formats(self):
        # Format brut
        ent1 = Entreprise(
            raison_sociale="Entreprise Un",
            matricule_fiscal="1234567AAM000",
            adresse="123 Rue de la République, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_chargeur
        )
        ent1.save()
        self.assertIsNotNone(ent1.pk)

    def test_matricule_fiscal_with_separators(self):
        ent2 = Entreprise(
            raison_sociale="Entreprise Deux",
            matricule_fiscal="1234567/A/A/M/000",
            adresse="123 Rue de la République, Tunis, Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_transporteur
        )
        ent2.save()
        self.assertIsNotNone(ent2.pk)

    def test_matricule_fiscal_invalid(self):
        user = Utilisateur(email='autre@gmail.com')
        user.save()
        ent = Entreprise(
            raison_sociale="Entreprise Invalide",
            matricule_fiscal="ABC1234",
            adresse="123 Rue de la République, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=user
        )
        with self.assertRaises(ValidationError):
            ent.save()

    def test_adresse_minimum_20_chars(self):
        user = Utilisateur(email='autre2@gmail.com')
        user.save()
        ent = Entreprise(
            raison_sociale="Entreprise Courte",
            matricule_fiscal="1234567BBM000",
            adresse="Trop court",
            type_entreprise="chargeur",
            gerant=user
        )
        with self.assertRaises(ValidationError):
            ent.save()

    def test_retrocompatibility_properties(self):
        ent = Entreprise(
            raison_social="Entreprise Retro",
            matricules_fiscale="1234567AAM000",
            adresse="123 Rue de la République, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_chargeur
        )
        self.assertEqual(ent.raison_sociale, "Entreprise Retro")
        self.assertEqual(ent.matricule_fiscal, "1234567AAM000")
        self.assertEqual(ent.raison_social, "Entreprise Retro")
        self.assertEqual(ent.matricules_fiscale, "1234567AAM000")
