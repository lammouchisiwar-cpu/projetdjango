from django.test import TestCase
from django.core.exceptions import ValidationError
from EntrepriseApp.models import Utilisateur, Entreprise
from .models import Vehicule


class VehiculeModelTest(TestCase):
    def setUp(self):
        self.user_trans = Utilisateur(email='transporteur@gmail.com', role='transporteur')
        self.user_trans.save()

        self.user_charg = Utilisateur(email='chargeur@gmail.com', role='chargeur')
        self.user_charg.save()

        self.trans = Entreprise.objects.create(
            raison_sociale="Transport Rapide SARL",
            matricule_fiscal="1234567AAM000",
            adresse="Avenue Habib Bourguiba, Tunis, Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans
        )

        self.charg = Entreprise.objects.create(
            raison_sociale="Chargeur SARL",
            matricule_fiscal="7654321BBM000",
            adresse="Avenue Habib Bourguiba, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_charg
        )

    def test_vehicule_must_belong_to_transporteur(self):
        # Valide si transporteur
        veh = Vehicule(
            immatriculation="123TN4567",
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            capacite_kg=1000,
            entreprise=self.trans
        )
        veh.save()
        self.assertIsNotNone(veh.pk)

        # Invalide si chargeur
        veh_invalid = Vehicule(
            immatriculation="999TN9999",
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            capacite_kg=1000,
            entreprise=self.charg
        )
        with self.assertRaises(ValidationError):
            veh_invalid.save()

    def test_capacite_kg_strictly_positive(self):
        veh_zero = Vehicule(
            immatriculation="000TN0000",
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            capacite_kg=0,
            entreprise=self.trans
        )
        with self.assertRaises(ValidationError):
            veh_zero.save()
