from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from EntrepriseApp.models import Utilisateur, Entreprise
from .models import Expedition


class ExpeditionModelTest(TestCase):
    def setUp(self):
        self.user_charg = Utilisateur(email='chargeur.exp@gmail.com', role='chargeur')
        self.user_charg.save()

        self.user_trans = Utilisateur(email='trans.exp@gmail.com', role='transporteur')
        self.user_trans.save()

        self.charg = Entreprise.objects.create(
            raison_sociale="Expediteur SARL",
            matricule_fiscal="1111111AAM000",
            adresse="Zone Industrielle Charguia, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_charg
        )

        self.trans = Entreprise.objects.create(
            raison_sociale="Transporteur SARL",
            matricule_fiscal="2222222BBM000",
            adresse="Zone Industrielle Charguia, Tunis, Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans
        )

    def test_reference_auto_generation_format(self):
        exp = Expedition(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal('500.00'),
            date_souhaitee=timezone.now().date(),
            entreprise=self.charg
        )
        exp.save()
        annee = timezone.now().strftime('%y')
        self.assertTrue(exp.reference.startswith(f"EXP-{annee}-"))
        self.assertEqual(len(exp.reference), 12)  # EXP-AA-NNNNN = 3 + 1 + 2 + 1 + 5 = 12

    def test_expedition_must_belong_to_chargeur(self):
        exp_invalid = Expedition(
            ville_depart="Tunis",
            ville_arrivee="Sfax",
            poids_kg=Decimal('100.00'),
            date_souhaitee=timezone.now().date(),
            entreprise=self.trans
        )
        with self.assertRaises(ValidationError):
            exp_invalid.save()

    def test_poids_kg_strictly_positive(self):
        exp_zero = Expedition(
            ville_depart="Tunis",
            ville_arrivee="Bizerte",
            poids_kg=Decimal('0.00'),
            date_souhaitee=timezone.now().date(),
            entreprise=self.charg
        )
        with self.assertRaises(ValidationError):
            exp_zero.save()
