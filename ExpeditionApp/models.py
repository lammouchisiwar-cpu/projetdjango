from django.db import models

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
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
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

   