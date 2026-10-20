from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = 'proposee', 'Proposée'
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'
        RETIREE = 'retiree', 'Retirée'

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), "Le prix doit être strictement supérieur à 0.")]
    )
    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Le délai doit être supérieur ou égal à 1 jour.")]
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PROPOSEE
    )
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(
        'ExpeditionApp.Expedition',
        on_delete=models.CASCADE,
        related_name='offres'
    )
    transporteur = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='offres_transporteur',
        limit_choices_to={'type_entreprise': 'transporteur'}
    )
    vehicule = models.ForeignKey(
        'VehiculeApp.Vehicule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offres_vehicule',
        limit_choices_to={'disponible': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['expedition', 'transporteur'],
                condition=models.Q(statut='proposee'),
                name='une_offre_proposee_par_transporteur_par_expedition'
            )
        ]

    def __str__(self):
        return f"Offre {self.pk or ''} - {self.prix} DT ({self.get_statut_display()})"

    def clean(self):
        super().clean()

        # Validateur prix > 0
        if self.prix is not None and self.prix <= 0:
            raise ValidationError({
                'prix': "Le prix doit être strictement supérieur à 0."
            })

        # Validateur delai_jours >= 1
        if self.delai_jours is not None and self.delai_jours < 1:
            raise ValidationError({
                'delai_jours': "Le délai doit être supérieur ou égal à 1 jour."
            })

        # Règle 1 : Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur
        if self.transporteur_id:
            if self.transporteur.type_entreprise != 'transporteur':
                raise ValidationError({
                    'transporteur': "Une offre ne peut être créée que par une entreprise de type transporteur."
                })

        # Règle 2 : Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur de l'offre
        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule': "Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur de l'offre."
                })

        # Règle 3 : Une expédition ne peut recevoir de nouvelles offres que si son statut est publiee
        if self.expedition_id:
            is_new = not self.pk or self._state.adding
            if is_new and self.expedition.statut != 'publiee':
                raise ValidationError({
                    'expedition': "Une expédition ne peut recevoir de nouvelles offres que si son statut est publiee."
                })

        # Règle 4 : Une entreprise ne peut pas avoir deux offres au statut proposee actives simultanément sur la même expédition
        if self.statut == self.Statut.PROPOSEE and self.expedition_id and self.transporteur_id:
            qs = Offre.objects.filter(
                expedition_id=self.expedition_id,
                transporteur_id=self.transporteur_id,
                statut=self.Statut.PROPOSEE
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Une entreprise ne peut pas avoir deux offres au statut proposee actives simultanément sur la même expédition."
                )

        # Règle 6 : Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre
        if self.vehicule_id:
            is_new = not self.pk or self._state.adding
            if is_new and not self.vehicule.disponible:
                raise ValidationError({
                    'vehicule': "Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre."
                })

        # Règle 7 : L'attribut type_vehicule conditionne la compatibilité avec le poids d'une expédition
        if self.vehicule_id and self.expedition_id:
            poids = float(self.expedition.poids_kg)
            type_vehicule = self.vehicule.type_vehicule
            limites = {
                'camionnette': (0, 1500),
                'fourgon': (0, 3500),
                'camion_porteur': (3500, 19000),
                'semi_remorque': (19000, 26000),
            }

            if type_vehicule in limites:
                min_poids, max_poids = limites[type_vehicule]
                if poids < min_poids or poids > max_poids:
                    raise ValidationError({
                        'vehicule': (
                            f"Le véhicule de type '{type_vehicule}' n'est pas compatible avec le poids "
                            f"de l'expédition ({poids} kg). Plage acceptée : {min_poids} kg à {max_poids} kg."
                        )
                    })

            if self.vehicule.capacite_kg < poids:
                raise ValidationError({
                    'vehicule': (
                        f"La capacité du véhicule ({self.vehicule.capacite_kg} kg) est insuffisante "
                        f"pour transporter cette expédition ({poids} kg)."
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        ancienne_offre = None
        if self.pk:
            try:
                ancienne_offre = Offre.objects.get(pk=self.pk)
            except Offre.DoesNotExist:
                pass

        with transaction.atomic():
            super().save(*args, **kwargs)

            # Règle 5 : Cascade à l'acceptation
            # quand une offre passe au statut « acceptee », l'expédition associée passe
            # automatiquement à « attribuee », et toutes les autres offres « proposee »
            # sur cette même expédition passent automatiquement à « refusee ».
            if (
                self.statut == self.Statut.ACCEPTEE
                and (
                    ancienne_offre is None
                    or ancienne_offre.statut != self.Statut.ACCEPTEE
                )
            ):
                self.expedition.statut = 'attribuee'
                self.expedition.save(update_fields=['statut', 'updated_at'])

                Offre.objects.filter(
                    expedition=self.expedition,
                    statut=self.Statut.PROPOSEE
                ).exclude(
                    pk=self.pk
                ).update(
                    statut=self.Statut.REFUSEE
                )