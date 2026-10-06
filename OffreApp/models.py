from django.db import models

# Create your models here.
 class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = 'proposee', 'Proposée'
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'
        RETIREE = 'retiree', 'Retirée'
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.PositiveIntegerField()
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PROPOSEE
    )
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(
        'ExpeditionsApp.Expedition',
        on_delete=models.CASCADE,
        related_name='offres'
    )
    transporteur = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='offres_transporteur',
        limit_choices_to={'type_entreprise': 'transporteur'}
    )
    vehicule = models.ForeignKey(
        'VehiculesApp.Vehicule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offres_vehicule',
        limit_choices_to={'disponible': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
