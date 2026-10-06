from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here
    

class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = 'publiee', 'Publiée'
        ATTRIBUEE = 'attribuee', 'Attribuée'
        EN_COURS = 'en_cours', 'En cours'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'
    reference = models.CharField(max_length=32, unique=True, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2,validators=MinLengthValidator(0.001,"le poids doit etre superieur a 0 kg"))
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PUBLIEE
    )
    
    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expedition',
        limit_choices_to={'type_entreprise': 'chargeur'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
def clean (self):
    super().clean()
    if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
        raise ValidationError({
            'entreprise':'une expedition ne peut etre cree que par un chargeur'
        })
@classmethod
def _generate_reference(cls):
    annee=timezone.now().strftime('%y')
    prefixe=f"EXP_{annee}_"
    dernier=(cls.objects.filter(reference_stratswitch=prefixe).order_by('reference').last())#select* from objet (cls.objects.all()) avec un filtre on utilise .filtrer(),last importe dernier expedition ajoute
    compteur=(
        int(dernier.reference[-5:])+1 if dernier 
        else 1
    )
    if computer > 99999:
        raise ValidationError("limit exceeded")
    return f"{prefixe}{compteur:05d}"



def save(self, *args,**kwargs):
    if not self.reference:
        self.reference=self._generate_reference()
    self.full_clean()
    super().save(*args,**kwargs)