from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = 'proposee', 'Proposée'
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'
        RETIREE = 'retiree', 'Retirée'
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.PositiveIntegerField(validators=[ MinValueValidator(1, "Le délai doit être supérieur ou égal à 1 jour.")])
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
def clean(self):
        super().clean()

        if self.transporteur_id:
            if self.transporteur.type_entreprise != 'transporteur':
                raise ValidationError({
                    'transporteur':
                        "Une offre ne peut être créée que par "
                        "une entreprise de type transporteur."})

        if self.expedition_id:
            if self.expedition.statut != 'publiee':
                if not self.pk:
                    raise ValidationError({
                        'expedition':
                            "Une nouvelle offre ne peut être créée "
                            "que pour une expédition publiée."
                    })

        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule':
                        "Le véhicule doit appartenir à la même "
                        "entreprise que le transporteur de l'offre."
                })

        if self.vehicule_id:
            if not self.vehicule.disponible:
                raise ValidationError({
                    'vehicule':
                        "Un véhicule indisponible ne peut pas être "
                        "proposé sur une nouvelle offre."
                })

        if self.vehicule_id and self.expedition_id:
            poids = float(self.expedition.poids_kg)
            type_vehicule = self.vehicule.type_vehicule
            limites = {
                'camionnette': (0, 1500),
                'fourgon': (0, 3500),
                'camion_porteur': (3500, 19000),
                'semi_remorque': (19000, 26000),
            }

            min_poids, max_poids = limites[type_vehicule]
            if poids > max_poids or poids < min_poids:
                raise ValidationError({
                    'vehicule':
                        f"Le véhicule de type {type_vehicule} "
                        f"n'est pas compatible avec le poids "
                        f"de l'expédition ({poids} kg)."
                })

            if self.vehicule.capacite_kg < poids:
                raise ValidationError({
                    'vehicule':
                        "La capacité du véhicule est insuffisante "
                        "pour transporter cette expédition."
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        ancienne_offre = None
        if self.pk:
            try:
                ancienne_offre = Offre.objects.get(pk=self.pk)
            except Offre.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if (
            self.statut == self.Statut.ACCEPTEE
            and (
                ancienne_offre is None
                or ancienne_offre.statut != self.Statut.ACCEPTEE
            )
        ):

            self.expedition.statut = 'attribuee'
            self.expedition.save(
                update_fields=['statut', 'updated_at']
            )

            Offre.objects.filter(
                expedition=self.expedition,
                statut=self.Statut.PROPOSEE
            ).exclude(
                pk=self.pk
            ).update(
                statut=self.Statut.REFUSEE
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'expedition',
                    'transporteur'
                ],
                condition=models.Q(
                    statut='proposee'
                ),
                name='une_offre_proposee_par_transporteur_par_expedition'
            )

        ]