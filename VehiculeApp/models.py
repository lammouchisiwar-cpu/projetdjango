from django.db import models
from django.core.validators import ValidationError
from django.core.validators import MinValueValidator
# Create your models here.
class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = 'camionnette', 'Camionnette'
        FOURGON = 'fourgon', 'Fourgon'
        CAMION_PORTEUR = 'camion_porteur', 'Camion porteur'
        SEMI_REMORQUE = 'semi_remorque', 'Semi-remorque'
    immatriculation = models.CharField(max_length=30, unique=True)
    type_vehicule = models.CharField(max_length=30, choices=TypeVehicule.choices)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(100,"la capacite doit etre superieure a 0 kg")])
    disponible = models.BooleanField(default=True)
    
    entreprise = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules',
        limit_choices_to={'type_entreprise': 'transporteur'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        if self.entreprise_id:
            if self.entreprise.type_entreprise != 'transporteur':
                raise ValidationError({
                    'entreprise':
                        "Un véhicule doit appartenir à une "
                        "entreprise de type transporteur."
                })