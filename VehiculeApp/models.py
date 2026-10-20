from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = 'camionnette', 'Camionnette / utilitaire léger'
        FOURGON = 'fourgon', 'Fourgon'
        CAMION_PORTEUR = 'camion_porteur', 'Camion porteur'
        SEMI_REMORQUE = 'semi_remorque', 'Semi-remorque'

    immatriculation = models.CharField(max_length=30, unique=True)
    type_vehicule = models.CharField(max_length=30, choices=TypeVehicule.choices)
    capacite_kg = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "La capacité doit être strictement supérieure à 0 kg.")]
    )
    disponible = models.BooleanField(default=True)

    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules',
        limit_choices_to={'type_entreprise': 'transporteur'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.immatriculation} ({self.get_type_vehicule_display()})"

    def clean(self):
        super().clean()
        if self.capacite_kg is not None and self.capacite_kg <= 0:
            raise ValidationError({
                'capacite_kg': "Une capacité nulle ne peut pas être acceptée."
            })
        if self.entreprise_id:
            if self.entreprise.type_entreprise != 'transporteur':
                raise ValidationError({
                    'entreprise': "Un véhicule doit appartenir à une entreprise de type transporteur."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)