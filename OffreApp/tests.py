from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculeApp.models import Vehicule
from ExpeditionApp.models import Expedition
from .models import Offre


class OffreModelTest(TestCase):
    def setUp(self):
        # Chargeur & Entreprise chargeur
        self.user_charg = Utilisateur(email='chargeur.test@gmail.com', role='chargeur')
        self.user_charg.save()
        self.charg = Entreprise.objects.create(
            raison_sociale="Société Chargeur Test",
            matricule_fiscal="1234567AAM000",
            adresse="Zone Industrielle Charguia, Tunis, Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_charg
        )

        # Transporteur 1 & Entreprise transporteur 1
        self.user_trans1 = Utilisateur(email='trans1.test@gmail.com', role='transporteur')
        self.user_trans1.save()
        self.trans1 = Entreprise.objects.create(
            raison_sociale="Société Transport 1",
            matricule_fiscal="2345678BBM000",
            adresse="Zone Portuaire de Rades, Ben Arous, Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans1
        )

        # Transporteur 2 & Entreprise transporteur 2
        self.user_trans2 = Utilisateur(email='trans2.test@gmail.com', role='transporteur')
        self.user_trans2.save()
        self.trans2 = Entreprise.objects.create(
            raison_sociale="Société Transport 2",
            matricule_fiscal="3456789CAM000",
            adresse="Route de Gabes Km 3, Sfax, Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans2
        )

        # Expédition publiée
        self.expedition = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal('1000.00'),
            date_souhaitee=timezone.now().date(),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.charg
        )

        # Véhicule appartenant à Trans1 (camionnette, dispo, cap 1200kg)
        self.vehicule1 = Vehicule.objects.create(
            immatriculation="111TN1111",
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            capacite_kg=1200,
            disponible=True,
            entreprise=self.trans1
        )

        # Véhicule appartenant à Trans2
        self.vehicule2 = Vehicule.objects.create(
            immatriculation="222TN2222",
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            capacite_kg=1200,
            disponible=True,
            entreprise=self.trans2
        )

    def test_prix_et_delai_validators(self):
        # Prix <= 0 invalide
        offre_prix_invalide = Offre(
            prix=Decimal('0.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1
        )
        with self.assertRaises(ValidationError):
            offre_prix_invalide.save()

        # Délai < 1 invalide
        offre_delai_invalide = Offre(
            prix=Decimal('250.00'),
            delai_jours=0,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1
        )
        with self.assertRaises(ValidationError):
            offre_delai_invalide.save()

    def test_regle_1_transporteur_uniquement(self):
        # Une offre ne peut pas être créée par un chargeur
        offre = Offre(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.charg,
            vehicule=None
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_2_vehicule_doit_appartenir_au_transporteur(self):
        # Trans1 propose le véhicule de Trans2
        offre = Offre(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule2
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_3_nouvelle_offre_uniquement_sur_expedition_publiee(self):
        self.expedition.statut = Expedition.Statut.ATTRIBUEE
        self.expedition.save()

        offre = Offre(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_4_pas_deux_offres_proposees_actives_par_entreprise(self):
        # Première offre proposée
        Offre.objects.create(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1,
            statut=Offre.Statut.PROPOSEE
        )

        # Deuxième offre proposée par la même entreprise sur la même expédition
        offre2 = Offre(
            prix=Decimal('280.00'),
            delai_jours=1,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1,
            statut=Offre.Statut.PROPOSEE
        )
        with self.assertRaises(ValidationError):
            offre2.save()

    def test_regle_5_cascade_acceptation(self):
        offre1 = Offre.objects.create(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1,
            statut=Offre.Statut.PROPOSEE
        )
        offre2 = Offre.objects.create(
            prix=Decimal('320.00'),
            delai_jours=3,
            expedition=self.expedition,
            transporteur=self.trans2,
            vehicule=self.vehicule2,
            statut=Offre.Statut.PROPOSEE
        )

        # Accepter offre1
        offre1.statut = Offre.Statut.ACCEPTEE
        offre1.save()

        self.expedition.refresh_from_db()
        offre2.refresh_from_db()

        # L'expédition passe à 'attribuee'
        self.assertEqual(self.expedition.statut, Expedition.Statut.ATTRIBUEE)
        # L'offre concurrente passe à 'refusee'
        self.assertEqual(offre2.statut, Offre.Statut.REFUSEE)

    def test_regle_6_vehicule_indisponible_refuse_sur_nouvelle_offre(self):
        self.vehicule1.disponible = False
        self.vehicule1.save()

        offre = Offre(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=self.expedition,
            transporteur=self.trans1,
            vehicule=self.vehicule1
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_7_compatibilite_type_vehicule_et_poids(self):
        # Camionnette avec poids > 1500 kg
        exp_lourde = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Gabes",
            poids_kg=Decimal('2000.00'),
            date_souhaitee=timezone.now().date(),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.charg
        )

        offre = Offre(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=exp_lourde,
            transporteur=self.trans1,
            vehicule=self.vehicule1  # camionnette max 1500 kg
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_7_capacite_vehicule_insuffisante(self):
        # Poids = 1400 kg (compatible camionnette <= 1500 kg), mais capacité véhicule = 1200 kg
        exp = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Nabeul",
            poids_kg=Decimal('1400.00'),
            date_souhaitee=timezone.now().date(),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.charg
        )
        offre = Offre(
            prix=Decimal('200.00'),
            delai_jours=1,
            expedition=exp,
            transporteur=self.trans1,
            vehicule=self.vehicule1  # capacite_kg = 1200 < 1400
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_7_fourgon_et_camion_porteur(self):
        # Fourgon (max 3500 kg)
        fourgon = Vehicule.objects.create(
            immatriculation="333TN3333",
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            capacite_kg=3500,
            entreprise=self.trans1
        )
        exp_fourgon_ok = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Bizerte",
            poids_kg=Decimal('3000.00'),
            date_souhaitee=timezone.now().date(),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.charg
        )
        offre_ok = Offre(
            prix=Decimal('400.00'),
            delai_jours=1,
            expedition=exp_fourgon_ok,
            transporteur=self.trans1,
            vehicule=fourgon
        )
        offre_ok.save()
        self.assertIsNotNone(offre_ok.pk)

        # Camion porteur (3500 à 19000 kg)
        porteur = Vehicule.objects.create(
            immatriculation="444TN4444",
            type_vehicule=Vehicule.TypeVehicule.CAMION_PORTEUR,
            capacite_kg=15000,
            entreprise=self.trans1
        )
        # Trop léger pour camion porteur (< 3500 kg)
        exp_trop_legere = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal('2000.00'),
            date_souhaitee=timezone.now().date(),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.charg
        )
        offre_invalide = Offre(
            prix=Decimal('800.00'),
            delai_jours=2,
            expedition=exp_trop_legere,
            transporteur=self.trans1,
            vehicule=porteur
        )
        with self.assertRaises(ValidationError):
            offre_invalide.save()
